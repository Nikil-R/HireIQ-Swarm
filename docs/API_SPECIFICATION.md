# 🔌 API Specification (FastAPI)

## Task Management

### 1. Execute Quest
`POST /execute`
- **Body:** `{ "goal": "string" }`
- **Returns:** `{ "task_id": "uuid" }`
- **Logic:** Initializes the LangGraph thread and launches the background agent swarm.

### 2. Poll Status
`GET /status/{task_id}`
- **Returns:**
```json
{
  "task_id": "string",
  "status": "running | completed | failed",
  "current_node": "string",
  "percentage_complete": 75,
  "execution_plan": [ { "step": 1, "description": "..." } ]
}
```

### 3. Retrieve Report
`GET /report/{task_id}`
- **Returns:** `{ "report": "markdown string" }`

### 4. Fetch History
`GET /tasks`
- **Returns:** List of the 10 most recent research missions.

## Tech Specs
- **CORS:** Enabled for local development (Port 5173).
- **JSON Validation:** Handled by Pydantic v2.
- **Backgrounding:** Uses standard Python threading for the LangGraph loop to avoid blocking the API worker.
