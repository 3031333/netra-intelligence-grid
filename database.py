import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# 🔒 Unlock the .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ... (Keep your InterceptRecord and User tables the same below this) ...
# ==========================================
# 🗄️ DATABASE TABLES
# ==========================================

class InterceptRecord(Base):
    __tablename__ = "intercept_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    target_phone = Column(String, index=True)
    origin_node = Column(String)
    threat_level = Column(String)
    extracted_entities = Column(JSON) 

# 🔥 THE MISSING SECURITY TABLE 🔥
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="officer")