# Project 14: Multi-Tenant SaaS Platform

## 🚀 Overview
Një platformë e plotë **SaaS (Software as a Service)** e ndërtuar për të suportuar shumë klientë (tenants) në një instancë të vetme aplikacioni, duke garantuar **izolim të plotë të të dhënave** (Schema-per-Tenant) dhe **fakturim të automatizuar** bazuar në përdorim.

## 🏗️ Arkitektura e Izolimit
- **Schema-per-Tenant**: Çdo klient ka skemën e tij të veçantë në PostgreSQL.
- **Dynamic Routing**: Middleware-i `tenant_resolver` lexon `Host Header` dhe vendos `search_path` në DB.
- **Security**: Një gabim në kod nuk mund të shkaktojë rrjedhje të dhënash midis klientëve.

## 💰 Motori i Fakturimit
- Gjurmon çdo thirrje API dhe MB ruajtje.
- Llogarit koston mujore automatikisht bazuar në planin (Free/Pro/Enterprise) + mbi-përdorimin.

## 🛠️ Si ta Ekzekutoni

1. **Nisja e Infrastrukturës:**
   ```bash
   docker-compose up -d --build