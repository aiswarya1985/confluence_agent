from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from app.config import settings

QDRANT_URL = settings.QADRANT_API_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY
COLLECTION_NAME = "confluence_knowledge_base"

qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

encoder = SentenceTransformer('all-MiniLM-L6-v2') 

# Initialize Collection
if not qdrant_client.collection_exists(COLLECTION_NAME):
    print(f"Creating collection: {COLLECTION_NAME}")
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

# Global counter to ensure every single point pushed across all documents has a unique ID
GLOBAL_POINT_ID = 1

# ==========================================
# 2. SEPARATE QDRANT PUSH FUNCTION
# ==========================================
def push_to_qdrant(text_chunks, page_id, title):
    """
    Takes a list of text chunks, generates embeddings, 
    constructs Qdrant points, and pushes them to the cluster.
    """
    global GLOBAL_POINT_ID
    points = []
    
    for index, chunk in enumerate(text_chunks):
        # 1. Convert text to numerical coordinates
        vector = encoder.encode(chunk).tolist()
        
        # 2. Build the structured data point
        point = PointStruct(
            id=GLOBAL_POINT_ID,
            vector=vector,
            payload={
                "page_id": page_id,
                "title": title,
                "chunk_index": index,
                "text": chunk
            }
        )
        points.append(point)
        GLOBAL_POINT_ID += 1
        
    # 3. Batch upload points to the cluster
    if points:
        response = qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        return response
    return None