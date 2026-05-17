# Project 8: Financial Data Extraction & Observability Pipeline

## 🚀 Overview
Një pipeline e fortë ETL për përpunimin e dokumenteve financiare. Përdor **Redis Queues** për menaxhimin e ngarkesës, **MinIO** për ruajtje, dhe **Prometheus/Grafana** për observabilitet të plotë. Nëse një dokument dështon, ai ripërpunohet automatikisht deri në 3 herë, pastaj dërgohet në **Dead Letter Queue (DLQ)**.

## 🏗️ Arkitektura
- **API**: Pranon skedarët dhe i dërgon në radhë.
- **Worker**: Konsumon radhën, kryen OCR, ekstragon të dhënat.
- **Retry Mechanism**: Logjikë eksponenciale për dështimet e përkohshme.
- **Observability**: Metrika në kohë reale për latency, throughput dhe gabime.

## 🛠️ Si ta Ekzekutoni

1. **Nisja:**
   ```bash
   docker-compose up -d --build