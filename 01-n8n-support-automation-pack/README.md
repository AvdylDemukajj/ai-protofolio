# Project 1: n8n Support & Email Automation Pack

## 🚀 Overview
Një sistem enterprise për automatizimin e suportit të klientëve. Klasifikon email-et me AI, ruan të dhënat në PostgreSQL me auditim të plotë, dhe përgatit rrugëzimin për agjentët njerëzorë.

## 🏗️ Arkitektura
- **n8n**: Motori i automatizimit.
- **PostgreSQL**: Bazë e të dhënave për bileta dhe audit logs.
- **Security**: Izolim rrjeti, Basic Auth, dhe enkriptim i kredencialeve.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Redaktoni .env dhe vendosni fjalëkalime të forta