import os
import time
import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

# 🔒 Unlock the .env file
load_dotenv()

print("🧠 Booting NETRA Neural Engine (Serverless API Mode)...")

# Grab the keys from the vault
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

def get_qdrant_client():
    if QDRANT_URL and QDRANT_API_KEY:
        print(f"🌐 Connecting to Qdrant Managed AWS Cloud Cluster...")
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print("⚠️ Cloud keys missing. Falling back to local memory.")
    return QdrantClient(":memory:")

qdrant = get_qdrant_client()
COLLECTION_NAME = "bns_legal_codes"

# ==========================================
# 🧠 REMOTE EMBEDDING ENGINE
# ==========================================
def get_embedding(text: str):
    """Fetches vector embeddings using Hugging Face's free Inference API"""
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(
        api_url, 
        headers=headers, 
        json={"inputs": [text], "options": {"wait_for_model": True}}
    )
    
    if response.status_code == 200:
        return response.json()[0]
    else:
        print(f"⚠️ HF API Error: {response.text}")
        return [0.0] * 384 # Fallback empty vector

# ==========================================
# 📚 CLOUD DATABASE INITIALIZATION
# ==========================================
existing_collections = [c.name for c in qdrant.get_collections().collections]

if COLLECTION_NAME not in existing_collections:
    print(f"📦 Creating '{COLLECTION_NAME}' collection in Qdrant...")
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 🚨 DECOUPLED DATA ARCHITECTURE: Load from JSON
    try:
        with open("bns_database.json", "r", encoding="utf-8") as file:
            bns_laws = json.load(file)
            
        print(f"📚 Ingesting {len(bns_laws)} BNS Legal Codes into Vector Space...")
        points = []
        for index, law in enumerate(bns_laws):
            vector = get_embedding(law["text"])
            points.append(PointStruct(
                id=law["id"], 
                vector=vector, 
                payload={"section": law["section"], "title": law["title"], "text": law["text"]}
            ))
            
            # Rate limiting to protect the free HF API endpoint
            if index % 10 == 0 and index != 0:
                print(f"   ...Indexed {index} laws. Pausing briefly for API limits...")
            time.sleep(0.3) 

        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print("✅ Vector DB fully populated!")
        
    except FileNotFoundError:
        print("⚠️ CRITICAL: 'bns_database.json' file not found. Engine is running empty.")

else:
    print(f"✅ Vector Collection '{COLLECTION_NAME}' already exists. Skipping ingestion.")

def search_legal_database(user_query: str, top_k: int = 1):
    query_vector = get_embedding(user_query)
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    return response.points