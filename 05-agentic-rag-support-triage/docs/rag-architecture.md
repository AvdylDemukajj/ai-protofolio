# RAG Architecture Details

## Flow
1. **User Query**: Receives question via API.
2. **Embedding**: Converts query to vector (1536 dims).
3. **Vector Search**: Queries Postgres `ivfflat` index for top-3 similar documents.
4. **Context Injection**: Injects retrieved text into LLM prompt.
5. **Generation**: LLM generates answer constrained by context.
6. **Validation**: Heuristic checks ensure answer matches context keywords.

## Why PGVector?
Using PostgreSQL with `pgvector` allows us to keep operational data and vector embeddings in a single database, simplifying infrastructure and backup strategies compared to separate vector DBs like Pinecone.