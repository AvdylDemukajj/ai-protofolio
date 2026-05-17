# Architecture Diagram & Explanation

## Components
1. **Ingestion Layer**: n8n Webhooks ose Manual Triggers.
2. **Processing Layer**: 
   - **AI Node**: Analizon tekstin (Sentiment, Category).
   - **Logic Node**: Vendos prioritetin bazuar në rregulla biznesi.
3. **Persistence Layer**: 
   - **Tickets Table**: Të dhënat kryesore.
   - **Audit Logs**: Gjurmë e pandryshueshme e vendimeve.

## Data Flow
User Email -> n8n Webhook -> AI Classification -> DB Insert -> Slack Notification (if High Priority).

## Security Measures
- **Network**: Docker network i izoluar (`n8n-network`).
- **Auth**: Basic Auth për UI, Credentials store për DB.
- **Data**: Input hashing për auditim pa ekspozuar PII të plotë.