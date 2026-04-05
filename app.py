import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import plotly.express as px
import uuid

st.set_page_config(page_title="Centergy Group Project Success Simulator", layout="centered", page_icon="🟢")

supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if "user" not in st.session_state:
    st.session_state.user = None
if "current_project_id" not in st.session_state:
    st.session_state.current_project_id = None
if "current_project_name" not in st.session_state:
    st.session_state.current_project_name = None

# ====================== LOGIN SCREEN ======================
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
                st.success("Account created! Please check your email to confirm.")
            except Exception as e:
                st.error(f"Sign-up failed: {str(e)}")

    st.stop()

# ====================== MAIN APP ======================
st.image("centergy_logo.png", width=300)
st.title(f"Centergy Group Project Success Simulator – {st.session_state.user.email}")

# Sidebar
with st.sidebar:
    st.header("My Projects")
    
    projects_response = supabase.table("projects").select("*").eq("user_id", st.session_state.user.id).execute()
    projects = projects_response.data if projects_response.data else []

    for proj in projects:
        if st.button(proj["name"], key=f"proj_{proj['id']}"):
            st.session_state.current_project_id = proj["id"]
            st.session_state.current_project_name = proj["name"]
            st.rerun()

    st.subheader("New Project")
    new_name = st.text_input("Project Name", key="new_proj_name")
    if st.button("Create Project", key="create_new_proj"):
        if new_name:
            try:
                new_id = str(uuid.uuid4())
                supabase.table("projects").insert({
                    "id": new_id,
                    "user_id": st.session_state.user.id,
                    "name": new_name,
                    "created_at": datetime.now().isoformat()
                }).execute()
                st.success(f"Project '{new_name}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create project: {str(e)}")

    st.divider()
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.current_project_id = None
        st.session_state.current_project_name = None
        st.rerun()

if not st.session_state.current_project_id:
    st.info("Please create or select a project from the sidebar to begin analysis.")
    st.stop()

st.subheader(f"Current Project: {st.session_state.current_project_name}")

use_grant_mode = st.checkbox("Enable Grant Mode (NGO / Government Submissions)", value=False)

# Prediction Engine (unchanged from previous stable version)
st.subheader("Rate Each Project Aspect (1–10)")

aspects = { ... }  # (same aspects dict as before – kept for brevity)

# [Prediction calculation, status, advice, charts – same as v3.0]

# ====================== FEEDBACK SECTION (Form-based for stability) ======================
st.subheader("📊 Actual Outcome Feedback (Help the App Learn)")

with st.form("feedback_form"):
    col_fb1, col_fb2 = st.columns(2)
    with col_fb1:
        actual_result = st.selectbox("Actual Project Outcome", 
            ["Success (Green)", "Partial Success (Yellow)", "Failure (Red)", "Not yet complete"])
    with col_fb2:
        notes = st.text_area("Notes / Lessons Learned", 
            placeholder="What actually happened? (Grant-specific insights welcome)")
    
    submitted = st.form_submit_button("Submit Feedback & Update Model")
    if submitted:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            supabase.table("feedback").insert({
                "project_id": st.session_state.current_project_id,
                "timestamp": now,
                "predictive_index": predictive_index,
                "actual_outcome": actual_result,
                "notes": notes,
                "grant_mode": use_grant_mode
            }).execute()
            st.success("✅ Feedback saved successfully for this project!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save feedback: {str(e)}")

# View Feedback
st.subheader("📋 View Feedback for This Project")
feedback_response = supabase.table("feedback").select("*").eq("project_id", st.session_state.current_project_id).execute()
feedback_data = feedback_response.data if feedback_response.data else []

if feedback_data:
    df_feedback = pd.DataFrame(feedback_data)
    st.dataframe(df_feedback[["timestamp", "predictive_index", "actual_outcome", "notes"]])
else:
    st.info("No feedback recorded for this project yet.")

st.caption("PSSA v3.1 – Clean Restart with Form-Based Feedback | Centergy Reality-Based Controls")