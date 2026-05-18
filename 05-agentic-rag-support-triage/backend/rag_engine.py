"""RAG retrieval and grounded answer generation."""

from __future__ import annotations

from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlalchemy import or_, text

from backend.config import settings
from backend.database import SessionLocal
from backend.models import KnowledgeDocument


class RAGEngine:
    def __init__(self) -> None:
        self._embeddings = None
        self._llm = None
        if not settings.use_mock_llm:
            self._embeddings = OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY,
            )
            self._llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=0,
                api_key=settings.OPENAI_API_KEY,
            )

    def retrieve_context(self, query: str, k: int = 3) -> list[str]:
        db = SessionLocal()
        try:
            if settings.use_mock_llm or self._embeddings is None:
                pattern = f"%{query.split()[0] if query.split() else query}%"
                docs = (
                    db.query(KnowledgeDocument)
                    .filter(
                        or_(
                            KnowledgeDocument.content.ilike(pattern),
                            KnowledgeDocument.title.ilike(pattern),
                            KnowledgeDocument.category.ilike(pattern),
                        )
                    )
                    .limit(k)
                    .all()
                )
                if not docs:
                    docs = db.query(KnowledgeDocument).limit(k).all()
                return [f"[{d.category}] {d.title}: {d.content}" for d in docs]

            query_vector = self._embeddings.embed_query(query)
            results = (
                db.query(KnowledgeDocument)
                .order_by(KnowledgeDocument.embedding.cosine_distance(query_vector))
                .limit(k)
                .all()
            )
            return [f"[{doc.category}] {doc.title}: {doc.content}" for doc in results]
        finally:
            db.close()

    def generate_answer(self, query: str, context: list[str]) -> str:
        if not context:
            return (
                "I do not have enough information in the knowledge base to answer that question. "
                "Please contact support for assistance."
            )

        context_text = "\n\n".join(context)
        if settings.use_mock_llm or self._llm is None:
            snippet = context[0].split(":", 1)[-1].strip()[:400]
            return (
                f"Based on our documentation: {snippet}\n\n"
                f"(This is a grounded summary for: {query})"
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a support assistant. Answer ONLY using the provided context. "
                    "If the answer is not in the context, say you do not know.",
                ),
                ("human", "Context:\n{context}\n\nQuestion: {question}"),
            ]
        )
        chain = prompt | self._llm | StrOutputParser()
        return chain.invoke({"context": context_text, "question": query})

    def index_markdown_folder(self, folder: Path | None = None) -> int:
        """Embed all markdown files under knowledge_base/ into Postgres."""
        folder = folder or Path(__file__).resolve().parent.parent / "knowledge_base"
        if settings.use_mock_llm:
            return self._index_mock(folder)
        if self._embeddings is None:
            raise RuntimeError("OpenAI API key required for embedding index.")

        db = SessionLocal()
        count = 0
        try:
            db.execute(text("DELETE FROM knowledge_documents"))
            db.commit()
            for path in folder.glob("*.md"):
                content = path.read_text(encoding="utf-8")
                title = path.stem.replace("_", " ").title()
                category = path.stem
                embedding = self._embeddings.embed_query(content[:8000])
                db.add(
                    KnowledgeDocument(
                        category=category,
                        title=title,
                        content=content,
                        embedding=embedding,
                    )
                )
                count += 1
            db.commit()
        finally:
            db.close()
        return count

    def _index_mock(self, folder: Path) -> int:
        db = SessionLocal()
        count = 0
        try:
            db.execute(text("DELETE FROM knowledge_documents"))
            for path in folder.glob("*.md"):
                content = path.read_text(encoding="utf-8")
                doc = KnowledgeDocument(
                    category=path.stem,
                    title=path.stem.replace("_", " ").title(),
                    content=content,
                    embedding=None,
                )
                db.add(doc)
                count += 1
            db.commit()
        finally:
            db.close()
        return count


rag_engine = RAGEngine()
