# 🏗️ System Design: HireIQ Autonomous Swarm

## High-Level Architecture
HireIQ follows a **Decoupled Agentic Architecture**, separating user intent from execution through a structured Graph-based workflow.

### Component Breakdown
1. **Frontend (React 19 + Tailwind v4):** A state-aware dashboard that visualizes the agent's internal thought process via real-time polling.
2. **Orchestration Layer (LangGraph):** A Directed Acyclic Graph (DAG) that manages state, cycles, and persistence.
3. **Inference Layer (Groq + Llama 3 70B):** Optimized for low-latency reasoning across multi-agent turns.
4. **Tooling Layer (Tavily AI):** Real-time web discovery infrastructure.
5. **Persistence Layer (Hybrid):**
    - **Relational (SQLite):** For structured metadata and execution logs.
    - **Vector (ChromaDB):** For semantic memory and high-similarity retrieval.

## Why this Stack?
- **LangGraph vs Linear Chains:** Linear chains fail when data is ambiguous. HireIQ uses cyclic loops to backtrack and "self-heal" research paths.
- **Groq over OpenAI:** For multi-agent systems, latency is the primary bottleneck. Groq's LPU allows for sub-second reasoning steps, making the 7-node swarm feel responsive.
- **Semantic Caching:** By using vector embeddings, we reduce costs by 90%+ for repeated market research queries.

---

## Data Flow (Macro)
1. User enters a research goal.
2. **Semantic Memory Check:** Checks ChromaDB for similar past reports.
3. **Swarm Execution:** If cache miss, the 6-agent swarm executes the research cycle.
4. **Synthesis:** Findings are normalized into Markdown.
5. **Final Storage:** Report is saved to SQLite and embedded into ChromaDB.
