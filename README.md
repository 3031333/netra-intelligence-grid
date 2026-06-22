# NETRA: Distributed Threat Intelligence Platform

NETRA (Network Extraction & Threat Resolution Architecture) is a platform designed to track, map, and legally triage cyber-syndicates for law enforcement. It allows officers to intercept telemetry, maintain dynamic threat topologies, and utilize an autonomous Retrieval-Augmented Generation (RAG) shield connected to the Bharatiya Nyaya Sanhita (BNS) penal code.

**Live Application:** [https://netra-intelligence-grid-dpnq7jvoikdeu3c79jzrf3.streamlit.app/](https://netra-intelligence-grid-dpnq7jvoikdeu3c79jzrf3.streamlit.app/)

> ### 🔑 INSTANT EVALUATION CREDENTIALS
> To bypass the IAM registration process and test the live grid immediately, use the following provisioned credentials on the **Officer Login** tab:
> * **Officer ID:** `User_Git`
> * **Passcode:** `Git_User`

## Project Structure

### Backend

The backend is built with Python, FastAPI, and Neon Serverless Postgres. It handles secure user authentication, asynchronous audio telemetry processing, relational graph generation, and fault-tolerant vector database queries via Qdrant and Hugging Face.

#### Setup

Install dependencies:

```bash
pip install -r requirements.txt

```

Create a `.env` file with the following content:

```env
DATABASE_URL=<your_neon_postgres_uri>
QDRANT_URL=<your_qdrant_cloud_url>
QDRANT_API_KEY=<your_qdrant_api_key>
HF_TOKEN=<your_huggingface_token>
SECRET_KEY=<your_jwt_secret_key>

```

Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

#### Routes

* **Main Application & Routes:** `main.py`
* Auth & Registration: `/login`, `/register/`, `/register-admin/`
* RAG Triage: `/triage-scam/`
* Audio Intercept: `/upload-audio/`
* Topology Mapping: `/generate-syndicate-map/`


* **Security & Auth Logic:** `auth.py`
* **Vector Search & AI Engine:** `rag_engine.py`

#### Models

* **Database Configuration & Models:** `database.py`
* User Model: `User` (Handles Officer IAM and encrypted credentials)
* Intercept Log Model: `InterceptRecord` (Handles raw telemetry and threat entities)
* Offline Lexical Database: `bns_database.json` (Decoupled legal statutes)



### Frontend

The frontend is a decoupled microservice built with Python, Streamlit, and PyVis. It provides a secure, interactive dashboard for law enforcement to authenticate, visualize network graphs, and query the RAG shield.

#### Setup

*(Note: Ensure the backend is running and `API_BASE_URL` in `app.py` points to your backend server)*

Install dependencies (if not already installed):

```bash
pip install -r requirements.txt

```

Start the development server:

```bash
streamlit run app.py

```

#### Components

* **Main Application Interface:** `app.py`
* **Login Component:** IAM Gateway (Handles JWT cryptographic handshakes)
* **Signup Component:** Officer Registration form
* **In-Flight Interceptor Component:** Handles asynchronous multi-file audio payload uploads to the backend.
* **Live Syndicate Topology Component:** Fetches relational data and renders an interactive NetworkX/PyVis HTML map (`live_threat_map.html`).
* **Citizen RAG Shield Component:** A conversational interface for zero-hallucination semantic legal triage against BNS codes.
