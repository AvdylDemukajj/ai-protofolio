# Project 9: Local AI Invoice Intelligence Dashboard

## 🚀 Overview
Një platformë **Full-Stack** për automatizimin e faturave që kombinon **OCR**, **LLM Lokal (Ollama)** dhe **Human-in-the-Loop** review. E ndërtuar për privatësi të plotë të të dhënave financiare.

## 💎 Veçoritë Enterprise
- **Local AI Processing**: Asnjë të dhënë nuk largohet nga rrjeti lokal.
- **Confidence-Based Routing**: Faturat me besueshmëri të ulët dërgohen për rishikim manual.
- **Math Validation**: Kontroll automatik i llogaritjeve (Subtotal + Tax = Total).
- **Audit Trail**: Regjistrim i çdo vendimi miratimi/refuzimi.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni USE_LOCAL_LLM=true