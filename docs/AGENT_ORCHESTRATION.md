# 🤖 Agent Orchestration & Graph Logic

## The "Thinking" Swarm
HireIQ is powered by a **LangGraph State Machine**. Each node in the graph represents a specialized agent or tool execution step.

### Node Definitions
1. **Goal Parser:** Extracts Pydantic schemas (Role, Skills, Location) from unstructured user input.
2. **The Architect:** Dynamically constructs the search strategy based on the parsed intent.
3. **The Worker:** Executes parallel search queries via Tavily AI.
4. **The Judge (Verifier):** Critically evaluates the findings. If "Salary" or "Skills" are missing, it forces a backtrack to the Worker node.
5. **The Brain (Synthesizer):** Performs semantic grouping and trend analysis on raw search data.
6. **The Writer:** Compiles the findings into a professional recruitment intelligence briefing.

## The Backtracking Mechanism
One of the most complex features of HireIQ is the **Autonomous Backtrack**.

```python
# Conceptual logic in verifier.py
if missing_data_detected:
    return "execute_correction" # Returns state to Worker node
else:
    return "synthesize" # Advances to Brain node
```

### State Management
The `AgentState` object is passed through each node, accumulating:
- `raw_data`: List of all web snippets found.
- `evaluation`: Critique from the Judge node.
- `retry_count`: Prevents infinite loops by capping autonomous retries.
