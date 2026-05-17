# Project 3: n8n Lead & Support Workflow Suite (Enterprise)

## 🚀 Overview
Një platformë e plotë automatizimi për menaxhimin e cikleve të jetës së klientëve (Lead Lifecycle Management). Ky sistem integron validimin e të dhënave, kualifikimin me AI (Lead Scoring), dhe rutimin inteligjent drejt ekipeve të shitjeve.

**Status:** ✅ Production-Ready Demo | 🔒 Security Hardened | 📊 Data-Driven

## 🏗️ Arkitektura e Zgjidhjes
Sistemi ndjek një arkitekturë **Event-Driven** me një database qendror PostgreSQL:

1.  **Ingestion & Validation:** Lead-et hyjnë (manual/CSV/API), pastrohen dhe validohen sipas rregullave biznesore (Email Regex, Company Size).
2.  **AI Enrichment:** Një agjent AI analizon kontekstin, cakton një **Lead Score (0-100)**, klasifikon intencën dhe sugjeron veprimin tjetër.
3.  **Routing & Notification:** Lead-et me score të lartë (>80) njoftojnë menjëherë ekipin e shitjeve në Slack.
4.  **Audit & Analytics:** Çdo vendim i AI regjistrohet për transparencë dhe përmirësim të modelit.

## 💎 Veçoritë Enterprise
- **Human-in-the-Loop:** Validim i dyfishtë për vendimet kritike.
- **Data Integrity:** Constraint-e të rrepta në database dhe transaction logs.
- **Security:** Izolim rrjeti, kredenciale të enkriptuara, dhe mbrojtje nga injection.
- **Observability:** Logjim i detajuar i çdo hapësirë vendimmarrjeje të AI.

## 🛠️ Si ta Ekzekutoni

### 1. Konfigurimi
```bash
cp .env.example .env
# Redaktoni .env me çelësat tuaj (OpenAI, Slack, DB Passwords)