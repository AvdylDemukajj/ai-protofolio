# Project 7: Invoice Parser & Approval Workflow

## 🚀 Overview
Një sistem end-to-end për përpunimin e faturave. Përdor **OCR** dhe **LLM** për nxjerrjen e të dhënave, **Validim Deterministik** për saktësi matematikore, dhe një **Dashboard Njerëzor** për miratim.

## 🏗️ Arkitektura
- **Backend**: FastAPI + Pdfplumber + LangChain.
- **Frontend**: Streamlit për rishikim manual.
- **Validation**: Logjikë biznesi për të parandaluar gabimet financiare.
- **Workflow**: Uploaded -> Processed -> Needs Review (nëse confidence < 0.85 ose math fail) -> Approved/Rejected.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni OPENAI_API_KEY