# Data Model Dictionary

## Table: `leads`
Tabela kryesore që ruan informacionin e klientëve potencialë dhe rezultatet e analizës së AI.

- `id` (UUID): Identifikues unik.
- `email` (TEXT, Unique): Kontakti primar, përdoret për deduplikim.
- `company_size` (INT): Përdoret për të filtruar klientët e vegjël (SMB vs Enterprise).
- `lead_score` (INT 0-100): Rezultati i besueshmërisë nga AI.
- `intent_category` (TEXT): Kategorizimi semantik (high_buying, spam, etj.).
- `status` (TEXT): Makina e gjendjes së workflow-it (new -> validated -> qualified).

## Table: `lead_audit_log`
Regjistron çdo ndërveprim të AI për qëllime compliance dhe debug.

- `ai_output_json` (JSONB): Ruan përgjigjen e plotë të modelit për analizë të mëvonshme.
- `input_hash` (TEXT): Hash i të dhënave hyrëse për të verifikuar integritetin pa ruajtur PII të plotë në logje.