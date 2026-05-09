# 🧠 Memory Strategy & Persistence

## Dual-Persistence Architecture
HireIQ utilizes two distinct databases to handle structured and unstructured data efficiently.

### 1. Relational Layer (SQLite + SQLAlchemy)
- **Purpose:** History logging and state tracking.
- **Tables:**
    - `tasks`: Stores `task_id`, `goal`, `status`, and `percentage_complete`.
    - `reports`: Stores the final Markdown synthesis and execution metadata.
- **Why SQLite?** Zero-configuration, file-based persistence ideal for edge-ready demonstration.

### 2. Vector Layer (ChromaDB)
- **Purpose:** Semantic Memory and Cost Optimization.
- **Mechanism:**
    - Uses `sentence-transformers/all-MiniLM-L6-v2` to embed research goals.
    - Before execution, a "Vector Similarity Search" is performed.
    - Result: If a user asks "Java roles in Bangalore" and a similar query exists, the system reuses knowledge instead of burning tokens.

## Scaling to Production
To scale this memory architecture to millions of users, we recommend:
1. **Relational:** PostgreSQL (Amazon RDS or Neon.tech).
2. **Vector:** Pinecone or Milvus (Serverless Vector Storage).
3. **Cache:** Redis for real-time task status polling.
