# Project 5: Agentic RAG Support Triage

## 🚀 Overview
Një sistem suportimi i bazuar në **RAG (Retrieval-Augmented Generation)** që siguron përgjigje të sakta duke u mbështetur vetëm në dokumentet e kompanisë. Përfshin mekanizma anti-hallucination dhe logjim të plotë.

## 🏗️ Arkitektura
- **Backend**: FastAPI + LangChain.
- **Database**: PostgreSQL me zgjerimin `pgvector` për kërkim semantik.
- **AI**: OpenAI (GPT-4 + Embeddings).
- **Validation**: Shtresë e dyfishtë validimi për sigurinë dhe saktësinë.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni OPENAI_API_KEY tuaj