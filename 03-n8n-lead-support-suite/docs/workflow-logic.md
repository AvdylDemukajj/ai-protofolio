# Workflow Logic & Business Rules

## 1. Intake & Validation (Workflow 01)
- **Trigger:** Manual ose Schedule (çdo 15 min).
- **Rule 1 (Email):** Duhet të përputhet me regex standard. Nëse jo -> `rejected`.
- **Rule 2 (Size):** Kompania duhet të ketë >= 10 punonjës për të kaluar në fazën e kualifikimit. Nëse jo -> `rejected`.
- **Outcome:** Vetëm lead-et e validuara (`status='validated'`) kalojnë te Workflow 02.

## 2. AI Scoring & Routing (Workflow 02)
- **Trigger:** Schedule (çdo 15 min).
- **AI Prompt:** Analizon emrin, kompaninë dhe mesazhin. Kërkon output strikt JSON.
- **Decision Tree:**
  - **Score >= 80:** "Hot Lead" -> Dërgo njoftim Slack -> Update status `qualified`.
  - **Score < 80:** Update status `qualified` (pa njoftim urgjent) për ndjekje të mëvonshme.
  - **Confidence < 0.6:** Shëno për rishikim manual (`requires_human_review = true`).

## 3. Error Handling
- Nëse API e OpenAI dështon, workflow ndalon dhe lë status-in `validated` për provë të mëvonshme (nuk hedh poshtë lead-in).
- Gabimet e DB regjistrohen në logjet e ekzekutimit të n8n.