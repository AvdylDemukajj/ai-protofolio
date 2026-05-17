# Project 6: Multi-Agent SaaS Support Router

## 🚀 Overview
Një sistem **Multi-Agent Orchestration** që rrugëzon inteligjentisht kërkesat e suportit drejt agjentëve specializuar (Billing, Technical, Refunds). Sistemi përdor **LangGraph** për menaxhimin e gjendjes dhe **Guardrails** të rrepta për siguri.

## 🏗️ Arkitektura
- **Router Agent**: Analizon intent-in dhe sentimentin.
- **Specialized Agents**: Çdo agjent ka akses vetëm në bazën e tij të njohurive.
- **Safety Layer**: Validon çdo përgjigje përpara se të dalë tek përdoruesi.
- **Audit Trail**: Çdo vendim regjistrohet në PostgreSQL.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni OPENAI_API_KEY