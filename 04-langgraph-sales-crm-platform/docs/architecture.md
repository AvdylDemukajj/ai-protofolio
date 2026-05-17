# Architecture Details

## State Machine
The agent follows a cyclic graph:
1. **Entry**: Receive Lead Info.
2. **Strategy Node**: Analyze score.
   - If Score < 40 -> Reject.
   - If Score 40-70 -> Research More.
   - If Score > 70 -> Draft Email.
3. **Draft Node**: Generate content using LLM.
4. **Exit**: Return state to API for user review.

## Data Flow
User Input -> API -> LangGraph Invoker -> DB (Log) -> Streamlit (Review) -> Send.