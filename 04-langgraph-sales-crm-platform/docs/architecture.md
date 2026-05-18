# Architecture

## State machine (LangGraph)

```text
[research] → [strategy] ──score≥70──► [draft] → END
                │
                ├──score 40-69──► [research] (max 2 iterations)
                └──score<40────► END (reject)
```

### Nodes

| Node | Responsibility |
|------|----------------|
| `research` | Company analysis, pain points, lead score, intent |
| `strategy` | Route to draft, more research, or reject |
| `draft` | Generate email subject/body for human review |

### State (`AgentState`)

- `company_info`, `analysis`, `draft`, `decision`, `messages`, `research_iterations`

## Application layers

```text
Streamlit UI ──HTTP──► FastAPI ──invoke──► LangGraph
                          │
                          ▼
                     PostgreSQL
                    (leads, audit, interactions)
```

## Data flow

1. `POST /leads/` creates DB row (`status=processing`)
2. Agent runs synchronously (typical run 5–30s with OpenAI)
3. Results persisted; draft stored in `interactions`
4. Slack notify if high-score pending review
5. Human approves via UI or `POST /leads/{id}/approve`

## Mock vs live LLM

`settings.use_mock_llm` is true when:

- `ENVIRONMENT=test`, or
- No API key / dummy key prefix

Ensures portfolio demos work offline while production uses OpenAI structured JSON prompts.
