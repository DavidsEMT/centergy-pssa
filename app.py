import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import plotly.express as px
import uuid

st.set_page_config(page_title="Centergy Group Project Success Simulator", layout="wide", page_icon="🟢")

supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# Robust session state initialization
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
                st.success("✅ Account created! Please check your email for the confirmation link, click it, then return here and Sign In.")
            except Exception as e:
                st.error(f"Sign-up failed: {str(e)}")

    st.stop()

# ====================== MAIN APP ======================
st.image("centergy_logo.png", width=250)
st.title(f"Centergy Group Project Success Simulator – {st.session_state.user.email}")

tab_main, tab_admin = st.tabs(["📊 Main Simulator", "📈 Admin Dashboard"])

# ====================== ADMIN DASHBOARD ======================
with tab_admin:
    if st.session_state.user.email not in ["dmook@centergygroup.com", "jdaniels@centergygroup.com"]:
        st.error("🔒 Admin Dashboard is restricted to Centergy administrators only.")
        st.stop()

    st.subheader("📈 Centergy Admin Overview Dashboard")
    all_projects = supabase.table("projects").select("id, name, user_id, created_at").execute().data
    total_projects = len(all_projects) if all_projects else 0

    all_feedback = supabase.table("feedback").select("*").execute().data
    df_feedback = pd.DataFrame(all_feedback) if all_feedback else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", total_projects)
    with col2:
        avg_index = round(df_feedback["predictive_index"].mean(), 1) if not df_feedback.empty else 0
        st.metric("Organization Avg Index", f"{avg_index}/10")
    with col3:
        green_count = len(df_feedback[df_feedback.get("actual_outcome", "").str.contains("Green", na=False)]) if not df_feedback.empty else 0
        st.metric("Green Outcomes", green_count)
    with col4:
        red_count = len(df_feedback[df_feedback.get("actual_outcome", "").str.contains("Red", na=False)]) if not df_feedback.empty else 0
        st.metric("Red Outcomes", red_count)

    if not df_feedback.empty:
        st.subheader("📈 Predictive Index Trend Over Time")
        df_feedback["timestamp"] = pd.to_datetime(df_feedback["timestamp"], errors='coerce')
        df_feedback = df_feedback.dropna(subset=["timestamp"])
        fig_trend = px.line(df_feedback, x="timestamp", y="predictive_index", title="Average Predictive Index Trend", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    if not df_feedback.empty:
        st.subheader("Success Distribution")
        outcome_counts = df_feedback["actual_outcome"].value_counts()
        fig_pie = px.pie(names=outcome_counts.index, values=outcome_counts.values, title="Actual Outcomes Across All Projects")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Recent Projects")
    if all_projects:
        df_projects = pd.DataFrame(all_projects)
        st.dataframe(df_projects[["name", "created_at"]].sort_values("created_at", ascending=False).head(10))

    st.caption("Admin Dashboard – Visible only to Centergy administrators")

# ====================== MAIN SIMULATOR ======================
with tab_main:
    # Sidebar
    with st.sidebar:
        st.header("My Projects")
        if st.button("🔄 Refresh Projects", key="refresh_projects"):
            st.rerun()
        
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
        st.info("👈 Please create or select a project from the sidebar to begin analysis.")
        st.stop()

    st.subheader(f"Current Project: {st.session_state.current_project_name}")

    # DETAILED SCORING GUIDE – PERMANENTLY VISIBLE AT THE TOP
    st.subheader("📖 Detailed Scoring Guide – How to Rate Each Aspect")
    st.markdown("""
    **Centergy-aligned scenario-based rubric for consistent scoring:**

    | Aspect | Low (1–3) | Medium (4–6) | High (7–10) |
    |--------|-----------|--------------|-------------|
    | **WBS Completeness** | No WBS defined or only a high-level list of major deliverables | WBS is high-level with less than 10 elements, missing detailed constituents | WBS has depth, fully deliverables-oriented, with element constituents defined and validated by team/sponsor |
    | **Stakeholder Alignment** | Little to no buy-in from key parties, stakeholders not engaged | Some engagement but not full commitment from all stakeholders | Clear, documented buy-in from team, client, sponsor, and all key stakeholders |
    | **Schedule Baseline Quality** | No baseline schedule or critical path unknown | Rough schedule exists but Sticky Shuffle not run | Critical Path fully validated via Sticky Shuffle with realistic contingencies |
    | **Cost Control Baseline** | No budget or only rough estimate | Basic budget exists with limited EVM-style tracking | Full budget with EVM-style forecasts, variance tracking, and cash-flow plan |
    | **Risk Identification & Response** | No Risk Log or risks not documented | Basic risks listed without mitigation plans | Full Risk Log with Darwinian mitigation strategies, owners, and contingency reserves |
    | **Team Experience & Capacity** | Major skill gaps and high learning curve | Adequate skills but some capacity constraints | Strong skills, low learning curve, and sufficient capacity confirmed |
    | **Requirements Stability** | Requirements changing frequently with no control | Some changes expected and partially tracked | Requirements well-controlled with clear change management process |
    | **Resource Availability** | Major shortages of people, tools, or funding | Partial availability with some gaps | People, tools, and funding fully secured and confirmed |
    | **Lessons Learned Integration** | No review of past failures | Some lessons considered informally | Past failures proactively reviewed and avoided in current plan |
    | **Communication & PUF Plan** | No formal communication plan | Basic updates planned | Full PUF-style proactive communication plan with regular updates |
    | **Executive Support** | Little to no sponsor visibility or commitment | Moderate sponsor support | Strong, visible sponsor commitment with regular engagement |

    **Grant Mode Aspects** (when enabled) use the same 1–10 scale with extra emphasis on compliance, outcomes, funding certainty, and funder alignment.
    """)

    use_grant_mode = st.checkbox("Enable Grant Mode (NGO / Government Submissions)", value=False)

    # Stable form for sliders - this is the key fix for kick-outs
    st.subheader("Rate Each Project Aspect (1–10)")

    aspects = {
        "WBS Completeness": {"weight": 0.13, "desc": "Deliverables-oriented WBS defined and validated?"},
        "Stakeholder Alignment": {"weight": 0.10, "desc": "Clear buy-in and engagement from team, client, and sponsor?"},
        "Schedule Baseline Quality": {"weight": 0.12, "desc": "Critical Path validated via Sticky Shuffle?"},
        "Cost Control Baseline": {"weight": 0.10, "desc": "Budget and EVM-style forecasts established?"},
        "Risk Identification & Response": {"weight": 0.13, "desc": "Risk Log with Darwinian mitigation strategies?"},
        "Team Experience & Capacity": {"weight": 0.09, "desc": "Skills, learning curve, and capacity addressed?"},
        "Requirements Stability": {"weight": 0.08, "desc": "Changing requirements identified and controlled?"},
        "Resource Availability": {"weight": 0.08, "desc": "People, tools, and funding secured?"},
        "Lessons Learned Integration": {"weight": 0.05, "desc": "Past failures proactively avoided?"},
        "Communication & PUF Plan": {"weight": 0.06, "desc": "PUF-style updates and proactive communication planned?"},
        "Executive Support": {"weight": 0.00, "desc": "Strong sponsor commitment and visibility?"},
    }

    if use_grant_mode:
        aspects.update({
            "Grant Compliance & Reporting Readiness": {"weight": 0.10, "desc": "NOFO/RFA guidelines, reporting, and audit readiness fully addressed?"},
            "Measurable Outcomes & Evaluation Plan": {"weight": 0.09, "desc": "Clear baseline data, KPIs, and success indicators defined?"},
            "Funding Certainty & Matching Requirements": {"weight": 0.08, "desc": "Budget realistic with secured matching funds and cash flow?"},
            "Proposal Alignment with Funder Priorities": {"weight": 0.08, "desc": "Project clearly ties to funder goals and priorities?"},
        })

    score_key = f"scores_{st.session_state.current_project_id}"
    if score_key not in st.session_state:
        st.session_state[score_key] = {name: 7 for name in