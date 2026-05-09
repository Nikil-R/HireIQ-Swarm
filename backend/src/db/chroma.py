import chromadb
import os

# Use /data/chroma_db if the persistent volume exists (Render), otherwise fallback to local
if os.path.exists("/data"):
    CHROMA_PATH = "/data/chroma_db"
else:
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Get or create collection for storing reports
collection = client.get_or_create_collection(name="hireiq_reports")

def store_report_embedding(task_id: str, goal: str, report: str):
    """Embeds the report and stores it with the goal as metadata."""
    collection.add(
        documents=[report],
        metadatas=[{"goal": goal}],
        ids=[task_id]
    )

def find_similar_goals(query_goal: str, n_results: int = 2):
    """Searches for semantically similar past goals/reports."""
    results = collection.query(
        query_texts=[query_goal],
        n_results=n_results
    )
    
    similar_reports = []
    if results['documents'] and len(results['documents'][0]) > 0:
        for i in range(len(results['documents'][0])):
            distance = results['distances'][0][i] if 'distances' in results and results['distances'] else None
            
            # Filter out weak matches if needed (lower distance is better in ChromaDB by default)
            # if distance and distance > 1.0: continue
            
            similar_reports.append({
                "task_id": results['ids'][0][i],
                "goal": results['metadatas'][0][i]["goal"],
                "report_snippet": results['documents'][0][i][:200] + "...",
                "distance": distance
            })
            
    return similar_reports
