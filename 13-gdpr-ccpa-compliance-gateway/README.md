# Project 13: GDPR/CCPA Compliance Gateway

## 🚀 Overview
Një gateway qendror për menaxhimin e kërkesave të privatësisë (Right to be Forgotten). Zbaton **Saga Pattern** për të garantuar fshirjen e të dhënave në mënyrë të konsistente nëpër sisteme të shumta (DB, S3, Analytics) me mekanizma automatikë **Rollback**.

## 🏗️ Arkitektura
- **Saga Orchestrator**: Koordinon hapat e fshirjes.
- **Connectors**: Adapterë për PostgreSQL, AWS S3, dhe API të jashtëm.
- **Audit Logger**: Regjistron çdo veprim për compliance (SOC2/GDPR).
- **Anonymizer**: Pseudonimizim i të dhënave për të ruajtur integritetin referencial.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni kredencialet AWS dhe DB