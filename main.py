import os
import time
import random
import networkx as nx
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# 🔒 1. Pull secret keys from the .env file
load_dotenv()

# 📦 2. Internal DB & Security Modules
from database import engine, Base, SessionLocal, InterceptRecord, User
from rag_engine import search_legal_database
from auth import get_password_hash, verify_password, create_access_token, verify_token

# Automatically spin up any missing tables in your Neon Cloud Postgres DB
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NETRA Intelligence Grid API",
    description="Enterprise Law Enforcement SaaS Backend (v2.0 - Public Cloud Edition)",
    version="2.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- VALIDATION SCHEMAS ---
class CitizenPrompt(BaseModel):
    message: str

class UserCreate(BaseModel):
    username: str
    password: str

# ==========================================
# 🔐 PUBLIC GATEWAY (IAM ENDPOINTS)
# ==========================================

@app.post("/register/")
def register_new_officer(user: UserCreate, db: Session = Depends(get_db)):
    """Allows new Law Enforcement Officers to provision an account in the cloud."""
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Officer ID already registered in the central grid."
        )
        
    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw, role="officer")
    db.add(new_user)
    db.commit()
    return {"message": f"Officer descriptor '{user.username}' successfully provisioned in Neon Postgres."}


@app.post("/register-admin/")
def register_master_admin(db: Session = Depends(get_db)):
    """Emergency bootstrap route to recreate the master admin."""
    user = db.query(User).filter(User.username == "admin").first()
    if user:
        return {"message": "Master Admin already exists in Cloud DB."}
        
    hashed_pw = get_password_hash("netra2026")
    new_user = User(username="admin", hashed_password=hashed_pw, role="admin")
    db.add(new_user)
    db.commit()
    return {"message": "Master Admin provisioned! (User: admin / Pass: netra2026)"}


@app.post("/login")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Trades valid Officer credentials for a cryptographically signed JWT Token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Officer ID or passcode",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# ⚙️ ASYNCHRONOUS BACKGROUND THREADS
# ==========================================

def analyze_heavy_audio_file(file_name: str, target_phone: str):
    print(f"⚙️ [ASYNC WORKER] Extracting vocal biometrics from {file_name}...")
    time.sleep(10) # Simulating heavy 10s AI voice model inference
    
    db = SessionLocal()
    try:
        print(f"⚙️ [ASYNC WORKER] Pushing telemetry for {target_phone} to Neon DB...")
        extracted_data = {
            "scam_type": "Syndicate Impersonation (AI Voice Match)", 
            "impersonation": "Directorate of Revenue Intelligence",
            "voice_biometric_confidence": random.randint(88, 99)
        }
        
        new_record = InterceptRecord(
            target_phone=target_phone, 
            origin_node="VoIP_Relay_Frankfurt",
            threat_level="CRITICAL", 
            extracted_entities=extracted_data
        )
        db.add(new_record)
        db.commit()
        print(f"✅ [ASYNC WORKER DONE] Audio record {file_name} locked into cloud persistence.")
    finally:
        db.close()


# ==========================================
# 🚀 SECURED BUSINESS LOGIC (JWT REQUIRED)
# ==========================================

@app.get("/")
def health_check():
    return {
        "grid_status": "🟢 ONLINE", 
        "vector_storage": "Qdrant AWS Frankfurt", 
        "relational_storage": "Neon Postgres Virginia",
        "iam_bouncer": "Active"
    }


@app.post("/triage-scam/")
def triage_citizen_message(payload: CitizenPrompt, current_user: str = Depends(verify_token)):
    hits = search_legal_database(payload.message, top_k=1)
    
    if not hits:
        return {"verdict": "UNKNOWN", "risk_level": "LOW", "legal_grounding": "None"}
        
    top_match = hits[0]
    law = top_match.payload
    confidence_pct = round(top_match.score * 100, 1)
    is_critical = confidence_pct > 45.0

    return {
        "verdict": "🚨 CONFIRMED SYNDICATE SCAM" if is_critical else "⚠️ SUSPICIOUS ACTIVITY",
        "risk_level": "CRITICAL" if is_critical else "ELEVATED",
        "ai_confidence_score": f"{confidence_pct}%",
        "primary_violation": f"{law['section']} ({law['title']})",
        "statutory_grounding": law['text'],
        "dispatched_by_officer": current_user
    }


@app.post("/upload-audio/")
def upload_intercepted_audio(
    file_name: str, 
    target_phone: str, 
    background_tasks: BackgroundTasks,
    current_user: str = Depends(verify_token)
):
    background_tasks.add_task(analyze_heavy_audio_file, file_name, target_phone)
    
    return {
        "status": "202 Accepted",
        "message": f"Audio payload '{file_name}' registered by Officer '{current_user}'. Worker dispatched.",
        "tracking_id": f"REQ-{random.randint(10000, 99999)}"
    }


@app.get("/generate-syndicate-map/")
def generate_threat_graph(db: Session = Depends(get_db), current_user: str = Depends(verify_token)):
    records = db.query(InterceptRecord).all()
    
    if not records:
        return {"message": "No telemetry in Neon DB yet. Ingest an audio file first."}

    G = nx.Graph()
    
    for record in records:
        G.add_node(record.target_phone, type="Victim", risk=record.threat_level)
        G.add_node(record.origin_node, type="Threat_Actor")
        G.add_edge(record.origin_node, record.target_phone, call_id=record.id)
    
    syndicates = list(nx.connected_components(G))
    
    payload = {
        "generated_by": current_user,
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "identified_syndicates": len(syndicates),
        "network_data": {
            "nodes": [{"id": node, "attributes": G.nodes[node]} for node in G.nodes],
            "edges": [{"source": u, "target": v} for u, v in G.edges]
        }
    }
    
    return payload