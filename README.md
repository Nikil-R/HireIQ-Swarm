# HireIQ: Autonomous Multi-Agent Research Swarm 🛡️🚀

**HireIQ** is a production-grade recruitment intelligence platform that utilizes an autonomous swarm of AI agents to perform deep-market research, skill-gap analysis, and salary benchmarking. 

Built with **LangGraph**, **Groq**, and **ChromaDB**, it features a self-healing agentic loop, semantic memory caching, and full observability.

---

## 🏗️ The Engineering Swarm (1% Architecture)

Unlike standard "linear" AI chains, HireIQ uses a **Stateful Directed Acyclic Graph (DAG)** to orchestrate 6 specialized agents:

1.  **The Parser:** Extracts Pydantic-validated intent from unstructured goals.
2.  **The Architect:** Dynamically generates a custom research strategy.
3.  **The Worker:** Executes high-speed web discovery via **Tavily AI**.
4.  **The Judge:** An autonomous verifier that triggers **recursive backtracking** if data is missing or inconsistent.
5.  **The Brain:** Performs semantic synthesis and market trend analysis.
6.  **The Writer:** Compiles a professional Intelligence Briefing in Markdown.

---

## 📊 System Performance & Efficiency

| Metric | With Cold Cache (New Quest) | With Semantic Memory (Hit) | Improvement |
| :--- | :--- | :--- | :--- |
| **Total Latency** | ~42.5 Seconds | **~100 Milliseconds** | **99.8% Faster** |
| **LLM Token Cost** | ~$0.12 (Input + Output) | **$0.00** | **100% Saved** |
| **Web API Usage** | 5-10 Search Calls | **0 Calls** | **Infinitely Scalable** |

---

## 🛠️ Key Technical Highlights

### 1. Observability with LangSmith 🕵️‍♂️
HireIQ is fully integrated with **LangSmith**. This provides a full "black box recorder" for every agentic thought, tool call, and trace.
- **Traceability:** Monitor sub-second reasoning steps across the multi-agent swarm.
- **Hallucination Monitoring:** Use the LangSmith dashboard to score and verify agent outputs in real-time.

### 2. Reliability & E2E Testing 🧪
We implemented a professional **Reliability Suite** using **Playwright + Pytest**:
- **Backend Tests:** Validates FastAPI endpoints and task status polling.
- **E2E Tests:** Browser-based tests that simulate user behavior, verify the **React Flow** graph animations, and validate report generation.

### 3. Semantic Memory & Hybrid Persistence 🧠
- **ChromaDB:** Implements a semantic cache layer using `all-MiniLM-L6-v2` embeddings to reuse knowledge and slash costs.
- **SQLite:** Handles relational task history and execution plans for persistent state tracking.

### 4. Interactive UI (React Flow + Streaming) ⚡
- **Real-time Swarm Map:** A dynamic SVG graph that lights up as the agent moves through nodes.
- **Smart Typewriter:** Reports stream in real-time to simulate live synthesis.

---

## 🛤️ Evolution & Documentation
This project has undergone a significant engineering journey. For a deep-dive into the development process and technical blueprints, see:
- [**JOURNEY.md**](./JOURNEY.md): The historical log of every engineering phase and major change.
- [**/docs/SYSTEM_DESIGN.md**](./docs/SYSTEM_DESIGN.md): The high-level architectural blueprint.
- [**/docs/AGENT_ORCHESTRATION.md**](./docs/AGENT_ORCHESTRATION.md): Deep-dive into LangGraph and backtracking logic.
- [**/docs/MEMORY_STRATEGY.md**](./docs/MEMORY_STRATEGY.md): Hybrid persistence and semantic caching logic.

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Configure Environment
Create a `.env` file in the `backend` folder based on `.env.example`:
```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
LANGCHAIN_API_KEY=your_langsmith_key
```

### 3. Run
```bash
# Terminal 1 (Backend)
python -m uvicorn src.api.main:app --reload

# Terminal 2 (Frontend)
npm run dev
```

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
