# Project 11: Real-Time Fraud Detection Engine

## 🚀 Overview
Një sistem enterprise për zbulimin e mashtrimeve financiare në kohë reale. Përdor arkitekturën **Event-Driven** me **Apache Kafka**, **Redis** për state management me latencë të ulët, dhe **Machine Learning** për detektimin e anomalive.

## 🏗️ Arkitektura
1. **Ingestion**: Transaksionet hyjnë në Kafka (`transactions-topic`).
2. **Stream Processing**:
   - **Rules Engine**: Kontrollon shpejtësinë (velocity) dhe pragjet e shumës.
   - **ML Model**: Llogarit skorin e rrezikut (Isolation Forest).
3. **Action**:
   - `Approved`: Transaksioni vazhdon.
   - `Flagged`: Krijon alert për rishikim manual.
   - `Rejected`: Bllokon transaksionin menjëherë.
4. **Storage**: Të dhënat ruhen në Postgres për auditim.

## 🛠️ Si ta Ekzekutoni

1. **Nisja:**
   ```bash
   docker-compose up -d --build