import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 🔒 Unlock the .env file
load_dotenv()

print("🧠 Booting NETRA Neural Engine...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Grab the keys from the vault
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL and QDRANT_API_KEY:
    print(f"🌐 Connecting to Qdrant Managed AWS Cloud Cluster...")
    qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    print("⚠️ Cloud keys missing. Falling back to local memory.")
    qdrant = QdrantClient(":memory:")

COLLECTION_NAME = "bns_legal_codes"

# ... (Keep the exact same collection_exists logic you already have below this) ...

# 🔥 THE VERSION-SAFE ENTERPRISE FIX 🔥
# 1. Ask Qdrant for a list of all its current collections
existing_collections_response = qdrant.get_collections()
# 2. Extract just the names into a Python list
existing_collection_names = [c.name for c in existing_collections_response.collections]

# 3. Check if our collection is missing from that list
if COLLECTION_NAME not in existing_collection_names:
    print(f"📦 Creating '{COLLECTION_NAME}' collection in Qdrant...")
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    bns_laws = [
        {
            "id": 1,
            "section": "BNS Section 319",
            "title": "Cheating by personation",
            "text": "A person is said to 'cheat by personation' if he cheats by pretending to be some other person, or by knowingly substituting one person for another, or representing that he or any other person is a person other than he or such other person really is. This includes impersonating police, CBI, or customs officials."
        },
        {
            "id": 2,
            "section": "BNS Section 318",
            "title": "Cheating and dishonestly inducing delivery of property",
            "text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment."
        },
        {
            "id": 3,
            "section": "Supreme Court Advisory 2024",
            "title": "Invalidity of Digital Arrests",
            "text": "There is no provision in Indian criminal law that allows for a 'Digital Arrest'. Law enforcement agencies such as the CBI, ED, or local police cannot legally detain, interrogate, or demand bail money from citizens via Skype, WhatsApp, or other video conferencing platforms."
        }
    ]

    print("📚 Ingesting BNS Legal Codes into Vector Space...")
    points = []
    for law in bns_laws:
        vector = model.encode(law["text"]).tolist()
        points.append(PointStruct(
            id=law["id"], 
            vector=vector, 
            payload={"section": law["section"], "title": law["title"], "text": law["text"]}
        ))

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
else:
    print(f"✅ Vector Collection '{COLLECTION_NAME}' already exists. Skipping ingestion.")

def search_legal_database(user_query: str, top_k: int = 1):
    query_vector = model.encode(user_query).tolist()
    response = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    return response.points