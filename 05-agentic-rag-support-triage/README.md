# Project 5: Agentic RAG Support Triage

**Status:** Production-ready | pgvector RAG | Grounding validation | Mock + OpenAI modes

Support triage API that retrieves grounded answers from a knowledge base, validates responses for hallucination/safety, and logs every interaction.

## Stack

- **FastAPI** — `/ask`, `/health`, `/admin/reindex`
- **PostgreSQL + pgvector** — document embeddings
- **LangChain + OpenAI** — embeddings and generation (optional)
- **Mock mode** — keyword retrieval without API key

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8005/health
curl -X POST http://localhost:8005/ask -H "Content-Type: application/json" \
  -d '{"question": "What is your return policy?"}'
```

API port **8005** (avoids conflict with project 4 on 8000). Postgres host port **5436**.

## Index knowledge base

On first startup, markdown files in `knowledge_base/` are indexed automatically.

Manual reindex:

```bash
curl -X POST http://localhost:8005/admin/reindex -H "X-API-Key: YOUR_KEY"
```

With `OPENAI_API_KEY` set, documents receive real 1536-d embeddings.

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Documentation

- [docs/rag-architecture.md](docs/rag-architecture.md)
- [docs/citation-policy.md](docs/citation-policy.md)
