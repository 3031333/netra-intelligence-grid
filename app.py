import streamlit as st
import requests
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# ---------------------------------------------------------------------
# 🌐 SaaS ROUTING TABLE
# Use Localhost while testing inside Docker.
# Before deploying to Streamlit Cloud, activate your Render URL!
# ---------------------------------------------------------------------
API_BASE_URL = "https://netra-backend-api.onrender.com"
# API_BASE_URL = "https://your-render-app-name.onrender.com"

st.set_page_config(page_title="NETRA SaaS | Public Safety Grid", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# =====================================================================
# 🔐 THE GATEWAY (LOGIN vs REGISTRATION TABS)
# =====================================================================
if not st.session_state.token:
    spacer_left, col_login, spacer_right = st.columns([1, 2, 1])
    
    with col_login:
        st.title("🛡️ NETRA IAM Gateway")
        st.caption("Central Law Enforcement Telemetry & RAG Triage Grid")
        st.divider()

        tab_auth, tab_register = st.tabs(["🔑 Officer Login", "📝 Register New Officer ID"])

        # --- TAB 1: LOGIN ---
        with tab_auth:
            with st.form("login_form"):
                username = st.text_input("Officer ID", placeholder="e.g. officer_hyd_01")
                password = st.text_input("Passcode", type="password")
                submit_login = st.form_submit_button("Initiate Cryptographic Handshake", use_container_width=True)

                if submit_login:
                    if not username or not password:
                        st.warning("⚠️ Please provide both your Officer ID and Passcode.")
                    else:
                        with st.spinner("Verifying JWT signature with identity provider..."):
                            res = requests.post(f"{API_BASE_URL}/login", data={"username": username, "password": password})
                            if res.status_code == 200:
                                st.session_state.token = res.json()["access_token"]
                                st.session_state.logged_in_user = username
                                st.success("Handshake accepted. Decrypting dashboard...")
                                st.rerun()
                            else:
                                st.error(f"❌ Access Denied: {res.json().get('detail', 'Unauthorized credentials')}")

        # --- TAB 2: REGISTER ---
        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Define Officer ID (Username)", placeholder="investigator_cyber_04")
                new_pass = st.text_input("Define Passcode", type="password")
                new_pass_confirm = st.text_input("Confirm Passcode", type="password")
                submit_register = st.form_submit_button("Provision Account in Neon Cloud DB", use_container_width=True)

                if submit_register:
                    if not new_user or not new_pass:
                        st.warning("⚠️ All parameter fields are required.")
                    elif new_pass != new_pass_confirm:
                        st.error("❌ Passcodes do not match.")
                    else:
                        with st.spinner("Writing encrypted identity to AWS Postgres..."):
                            res = requests.post(f"{API_BASE_URL}/register/", json={"username": new_user, "password": new_pass})
                            if res.status_code == 200:
                                st.success(f"✅ Success: {res.json()['message']}")
                                st.info("Account provisioned! Please switch to the 'Officer Login' tab to authenticate.")
                            else:
                                st.error(f"❌ Registration Failed: {res.json().get('detail', 'Bad request')}")

# =====================================================================
# 🚀 THE SECURE ENTERPRISE DASHBOARD
# =====================================================================
else:
    header_left, header_right = st.columns([0.85, 0.15])
    with header_left:
        st.subheader("🚨 NETRA: Distributed Threat Intelligence Platform")
    with header_right:
        st.caption(f"👤 Active ID: **{st.session_state.logged_in_user}**")
        if st.button("🔒 Lock Session", use_container_width=True):
            st.session_state.token = None
            st.session_state.logged_in_user = None
            st.rerun()

    st.divider()

    # EVERY API CALL INGESTS THIS VIP TOKEN automatically
    secure_headers = {"Authorization": f"Bearer {st.session_state.token}"}

    tab_interceptor, tab_mapper, tab_shield = st.tabs(["🎙️ In-Flight Interceptor", "🕸️ Live Syndicate Topology", "🛡️ Citizen RAG Shield"])

    # --- TAB 1: WIRE TAP BUFFER (Multi-file enabled) ---
    with tab_interceptor:
        st.markdown("### 📡 Wiretap Stream Buffer")
        st.caption("Drop intercepted audio byte-streams here. Transmits to Celery/FastAPI asynchronous background processing pool.")
        
        # Upgraded to accept arrays of files natively
        audio_files = st.file_uploader("Upload Audio Intercept Payloads", type=["mp3", "wav"], accept_multiple_files=True)

        if audio_files:
            st.write(f"**Loaded Payloads in Memory Buffer ({len(audio_files)}):**")
            for audio_file in audio_files:
                st.audio(audio_file)

            if st.button("⚡ Transmit Payloads to Async Cluster", type="primary"):
                success_count = 0
                with st.spinner("Streaming binary files across container network..."):
                    for audio_file in audio_files:
                        dummy_phone = "+91-98XXX" + str(abs(hash(audio_file.name)))[-4:]
                        
                        res = requests.post(
                            f"{API_BASE_URL}/upload-audio/",
                            params={"file_name": audio_file.name, "target_phone": dummy_phone},
                            headers=secure_headers
                        )
                        if res.status_code == 200: # Note: uvicorn maps our 202 string to a 200 status code
                            success_count += 1

                if success_count == len(audio_files):
                    st.success(f"🟢 All {success_count} payloads successfully queued for background biometrics.")
                    st.info("⏳ Processing threads active. Relational DB will reflect new nodes in exactly 10 seconds.")
                else:
                    st.warning(f"⚠️ Network degradation: Only {success_count}/{len(audio_files)} reached the queue.")

    # --- TAB 2: NETWORK MAPPER (Deep container diagnostics enabled) ---
    with tab_mapper:
        st.markdown("### 🕸️ Global Threat Topology")
        
        if st.button("🗺️ Fetch Palantir Graph from Cloud DB", type="primary", use_container_width=True):
            with st.spinner("Querying relational joins in Neon AWS Postgres..."):
                res = requests.get(f"{API_BASE_URL}/generate-syndicate-map/", headers=secure_headers)

                if res.status_code == 200:
                    data = res.json()
                    if "network_data" in data:
                        st.success(f"Graph Compiled by: **{data.get('generated_by', 'Admin')}** | Active Nodes: **{data['total_nodes']}** | Tracked Syndicates: **{data['identified_syndicates']}**")
                        
                        G = nx.Graph()
                        for node in data["network_data"]["nodes"]:
                            color = "#ff4b4b" if node["attributes"].get("type") == "Threat_Actor" else "#00cc96"
                            size = 25 if node["attributes"].get("type") == "Threat_Actor" else 15
                            G.add_node(node["id"], size=size, color=color, title=f"Entity: {node['attributes'].get('type')} | Threat: {node['attributes'].get('risk', 'N/A')}")
                            
                        for edge in data["network_data"]["edges"]:
                            G.add_edge(edge["source"], edge["target"])
                            
                        nt = Network(height="550px", width="100%", bgcolor="#0e1117", font_color="white")
                        nt.from_nx(G)
                        nt.repulsion(node_distance=160, spring_length=220)
                        nt.save_graph("live_threat_map.html")
                        
                        with open("live_threat_map.html", 'r', encoding='utf-8') as map_file:
                            components.html(map_file.read(), height=600)
                    else:
                        st.info(data.get("message", "No node vectors returned."))
                else:
                    st.error(f"❌ Cluster API Failure (HTTP Status: {res.status_code})")
                    with st.expander("🔍 Inspect Raw Container Stack Trace"):
                        try:
                            st.json(res.json())
                        except:
                            st.code(res.text)

    # --- TAB 3: CITIZEN SHIELD ---
    with tab_shield:
        st.markdown("### 🛡️ Autonomous RAG Legal Triage")
        st.caption("Zero-hallucination semantic query engine connected to the Bharatiya Nyaya Sanhita (BNS) space in Frankfurt.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if citizen_query := st.chat_input("Paste flagged SMS, transcript, or VoIP threat string here..."):
            st.chat_message("user").markdown(citizen_query)
            st.session_state.chat_history.append({"role": "user", "content": citizen_query})

            with st.chat_message("assistant"):
                with st.spinner("Calculating cosine distance in Qdrant Vector Cloud..."):
                    res = requests.post(
                        f"{API_BASE_URL}/triage-scam/",
                        json={"message": citizen_query},
                        headers=secure_headers
                    )

                    if res.status_code == 200:
                        triage_data = res.json()
                        reply = f"""
                        **Triage Assessment:** {triage_data['verdict']} *(AI Confidence: {triage_data['ai_confidence_score']})*
                        
                        * **Statutory Violation:** `{triage_data['primary_violation']}`
                        * **Legal Grounding:** "{triage_data['statutory_grounding']}"
                        
                        ---
                        *Triage dispatched by logged Officer:* **{triage_data['dispatched_by_officer']}**
                        """
                        st.markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    else:
                        st.error(f"Vector Database connection lost (HTTP {res.status_code})")