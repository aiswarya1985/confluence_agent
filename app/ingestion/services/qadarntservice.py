import uuid
import numpy as np
import logfire

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from app.config import settings

QDRANT_URL = settings.QADRANT_API_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
COLLECTION_NAME = "confluence_knowledge_base"

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

encoder = SentenceTransformer('all-MiniLM-L6-v2') 

with logfire.span("qdarnt service started"):
# Initialize Collection
 if not qdrant_client.collection_exists(COLLECTION_NAME):
    print(f"Creating collection: {COLLECTION_NAME}")
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

def get_text_embedding(text: str) -> np.ndarray:
    """
    Generates a dense vector embedding for a single text string 
    using the global encoder instance.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty or whitespace.")
        
    # Directly uses the 'encoder' variable initialized outside the function
    embedding = encoder.encode(text, convert_to_numpy=True)
    logfire.info("embedding generated successfully.",embedding=embedding.tolist())
    logfire.info(
    "Generated embedding of length {length} for text: {sample}...", 
    length=len(embedding), 
    sample=text[:30]
   )
    return embedding

# ==========================================
# 2. SEPARATE QDRANT PUSH FUNCTION
# ==========================================
def push_to_qdrant(text_chunks, page_id, title):
    """
    Takes a list of text chunks, generates embeddings, 
    constructs Qdrant points, and pushes them to the cluster.
    """
   
    points = []
    
    for index, chunk in enumerate(text_chunks):
        # 1. Convert text to numerical coordinates
        vector = encoder.encode(chunk).tolist()
        string_id = str(uuid.uuid4())
        
        # 2. Build the structured data point
        point = PointStruct(
            id=string_id,
            vector=vector,
            payload={
                "page_id": page_id,
                "title": title,
                "chunk_index": index,
                "text": chunk
            }
        )
        points.append(point)       
        
    # 3. Batch upload points to the cluster
    if points:
        response = qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        return response
    return None

def search_enterprise_knowledge(query: str, limit: int = 8):
    """
    Performs a high-precision search in the enterprise knowledge base.
    Uses the modern query_points interface.
    """
    try:
        query_vector = get_text_embedding(query)
        logfire.info("Query vector generated successfully", vector_dimensions=len(query_vector))

        # Using query_points - the modern standard for Qdrant
        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            with_payload=True # JSON
        )
        logfire.info(f"Qdrant search returned {len(response.points)} results for query: '{query}'")

        results = []
        for res in response.points:
            results.append({
                "content": res.payload.get("text", ""),
                "source": res.payload.get("title", "Unknown"),
                "score": res.score
            })
        
        return results
    except Exception as e:
        logfire.error("Qdrant Search Failed", error=str(e))
        return []