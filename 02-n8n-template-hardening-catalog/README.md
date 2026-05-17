# Project 2: n8n Template Hardening Catalog

## 🚀 Overview
Një mjet automatik sigurie (CLI) që skanon workflow-et e n8n përpara se ato të importohen në mjedisin e prodhimit. Zbulon kredenciale të hardkoduar, webhook-e të pasigurta dhe mungesë trajtimi gabimesh.

## 🔍 Çfarë Skanon?
- 🔑 **Hardcoded Secrets**: Fjalëkalime, API Keys (OpenAI, Slack, AWS) të shkruara direkt në kod.
- 🔓 **Public Webhooks**: Webhooks pa validim header-i.
- ⚠️ **Missing Error Handling**: Mungesa e rrugëve alternative kur një hap dështon.
- 📉 **Configuration Issues**: Cilësime të dobëta ekzekutimi.

## 🛠️ Si ta Përdorni

1. **Instaloni varjet:**
   ```bash
   pip install -r requirements.txt