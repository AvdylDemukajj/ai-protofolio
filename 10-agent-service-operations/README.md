# Project 10: Agent Service Operations Assistant

## 🚀 Overview
Një agjent AI operacional i aftë të kryejë veprime reale (Tool Calling) në sistemet e suportit, i mbrojtur nga **Guardrails** të rrepta që parandalojnë veprimet e rrezikshme ose të paautorizuara.

## 🔒 Siguria & Guardrails
- **Policy Enforcement**: Ndalimi i veprimeve shkruese (`WRITE`/`DELETE`) në mjedise jo-prodhim.
- **Injection Protection**: Zbulimi i përpjekjeve për "Prompt Injection".
- **Audit Trail**: Çdo vendim dhe bllokim regjistrohet në database.

## 🛠️ Si ta Ekzekutoni

1. **Konfigurimi:**
   ```bash
   cp .env.example .env
   # Vendosni ALLOW_DESTRUCTIVE_ACTIONS=false për testimin e sigurisë