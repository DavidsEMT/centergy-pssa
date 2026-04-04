import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import plotly.express as px
import uuid

st.set_page_config(page_title="Centergy Group Project Success Simulator", layout="centered", page_icon="🟢")

# Supabase Client (using secrets)
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None
if "current_project_name" not in st.session_state:
    st.session_state.current_project_name = None

# ====================== LOGIN / SIGN-UP SCREEN ======================
if not st.session_state.user:
    st.image("centergy_logo.png", width=400)
    st.title("Centergy Group Project Success Simulator")
    st.markdown("Sign in to access your personalized projects")

    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In", key="btn_login"):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = response.user
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Account", key="btn_signup"):
            try:
                response = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Please check your email to confirm the account.")
            except Exception as e:
                st.error(f"Sign-up failed: {str(e)}")

    st.stop()  # Stop here until logged in

# ====================== MAIN APP (Logged In) ======================
st.image("centergy_logo.png", width=300)
st.title(f"Centergy Group Project Success Simulator – {st.session_state.user.email}")

# Sidebar - Project Management
with st.sidebar:
    st.header("My Projects")
    
    # Fetch user's projects
    projects_response = supabase.table("projects").select("*").eq("user_id", st.session_state.user.id).execute()
    projects = projects_response.data if projects_response.data else []

    for proj in projects:
        if st.button(proj["name"], key=f"proj_{proj['id']}"):
            st.session_state.current_project_id = proj["id"]
            st.session_state.current_project_name = proj["name"]
            st.rerun()

    if st.button("➕ New Project"):
        new_name = st.text_input("Project Name", key="new_proj_name")
        if st.button("Create", key="create_new_proj"):
            if new_name:
                new_id = str(uuid.uuid4())
                supabase.table("projects").insert({
                    "id": new_id,
                    "user_id": st.session_state.user.id,
                    "name": new_name,
                    "created_at": datetime.now().isoformat()
                }).execute()
                st.success(f"Project '{new_name}' created!")
                st.rerun()

# If no project selected
if not st.session_state.current_project_id:
    st.info("Please create or select a project from the sidebar to begin analysis.")
    st.stop()

st.subheader(f"Current Project: {st.session_state.current_project_name}")

# ====================== YOUR EXISTING PREDICTION ENGINE ======================
# (This section will be fully wired to the current project in the next message)
st.success("✅ Authentication + Project Selection Active")
st.info("Per-project isolation is now enabled. The prediction engine is being wired to your selected project.")

# Placeholder for the full prediction, aspects, charts, feedback, export
# We will expand this in the next step once you confirm the login works.

st.caption("PSSA v2.0 – Authentication + Per-Project Segmentation | Centergy Reality-Based Controls")