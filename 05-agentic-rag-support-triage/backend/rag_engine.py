from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.config import settings
from backend.database import SessionLocal
from backend.models import KnowledgeDocument
from sqlalchemy.orm import Session
import numpy as np

class RAGEngine:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        self.llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)

    def retrieve_context(self, query: str, k: int = 3) -> list:
        """Retrieves top-k relevant documents using vector similarity."""
        db = SessionLocal()
        try:
            # Generate embedding for query
            query_vector = self.embeddings.embed_query(query)
            
            # Perform cosine similarity search in Postgres
            results = db.query(KnowledgeDocument).order_by(
                KnowledgeDocument.embedding.cosine_distance(query_vector)
            ).limit(k).all()
            
            return [doc.content for doc in results]
        finally:
            db.close()

    def generate_answer(self, query: str, context: list) -> str:
        """Generates a grounded answer based on context."""
        if not context:
            return "I do not have enough information to answer that question based on our current knowledge base."

        context_text = "\n\n".join(context)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful support assistant. Answer the user's question ONLY using the provided context. If the answer is not in the context, state that you don't know. Cite the source if possible."),
            ("human", "Context:\n{context}\n\nQuestion: {question}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"context": context_text, "question": query})

rag_engine = RAGEngine()