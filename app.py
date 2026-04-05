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

# Grant Mode
use_grant_mode = st.checkbox("Enable Grant Mode (NGO / Government Submissions)", value=False)

# ====================== PREDICTION ENGINE ======================
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

inputs = {}
weighted_scores = {}
aspect_data = []

for name, data in aspects.items():
    score = st.slider(f"{name}", 1, 10, 7, help=data["desc"], key=name)
    inputs[name] = score
    weighted_scores[name] = score * data["weight"]
    aspect_data.append({"Aspect": name, "Score": score, "Weight": data["weight"]})

total_weighted = sum(weighted_scores.values())
max_weight = sum(a["weight"] for a in aspects.values())
predictive_index = round(total_weighted / max_weight, 1)

if predictive_index >= 8.5:
    status = "🟢 GREEN – Strong Likelihood of Success"
    color = "#00CC00"
    advice_level = "Strong position – proceed with confidence."
elif predictive_index >= 6.5:
    status = "🟡 YELLOW – Moderate Risk – Strengthen Now"
    color = "#FFAA00"
    advice_level = "Address gaps proactively."
else:
    status = "🔴 RED – High Risk – Re-baseline Immediately"
    color = "#FF4444"
    advice_level = "Immediate corrective actions required."

st.subheader("🎯 Predictive Analysis Result")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<h2 style='color:{color};'>{status}</h2>", unsafe_allow_html=True)
with col2:
    st.metric("Success Predictive Index", f"{predictive_index}/10.0")
st.progress(predictive_index / 10)

st.subheader("🔧 Responsive Advice")
weak_aspects = [(a, s, aspects[a]["weight"]) for a, s in inputs.items() if s <= 5]
weak_aspects.sort(key=lambda x: x[2], reverse=True)

if weak_aspects:
    st.markdown("**Focus here first (highest impact issues):**")
    for aspect, score, wt in weak_aspects[:7]:
        st.warning(f"**{aspect}** (Score: {score}/10, Weight: {wt:.2f}) – {aspects[aspect]['desc']}")
        if aspect in ["WBS Completeness", "Schedule Baseline Quality", "Risk Identification & Response"]:
            st.info("→ Run Sticky Shuffle + add contingency buffer immediately.")
        elif any(k in aspect for k in ["Compliance", "Grant", "Outcomes", "Funding"]):
            st.info("→ Strengthen grant-specific elements.")
        else:
            st.info("→ Proactive fix now.")
else:
    st.success("All aspects strong – Excellent foundation!")

st.markdown(f"**Overall Guidance:** {advice_level}")

# Charts
st.subheader("📊 Visual Project Aspects Analysis")
df_aspects = pd.DataFrame(aspect_data).sort_values("Score", ascending=True)
fig_bar = px.bar(df_aspects, x="Score", y="Aspect", orientation='h',
                 title="Aspect Scores (Higher = Better)",
                 color="Score", color_continuous_scale="RdYlGn")
fig_bar.update_layout(height=500)
st.plotly_chart(fig_bar, use_container_width=True)

# ====================== EXPORT REPORT BUTTON ======================
if st.button("📄 Export Full Project Report (Markdown)"):
    report_md = f"# Centergy Group Project Success Simulator Report\n\n"
    report_md += f"**Project:** {st.session_state.current_project_name}\n"
    report_md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_md += f"**Grant Mode:** {'Yes' if use_grant_mode else 'No'}\n\n"
    
    report_md += f"## 🎯 Predictive Analysis Result\n"
    report_md += f"**Status:** {status}\n"
    report_md += f"**Success Predictive Index:** {predictive_index}/10.0\n\n"
    
    report_md += f"## 🔧 Responsive Advice\n"
    if weak_aspects:
        report_md += "**Priority Issues:**\n"
        for aspect, score, wt in weak_aspects[:7]:
            report_md += f"- **{aspect}** (Score: {score}/10) – {aspects[aspect]['desc']}\n"
    else:
        report_md += "All aspects are strong – Excellent foundation!\n"
    
    report_md += f"\n**Overall Guidance:** {advice_level}\n\n"
    
    report_md += f"## 📊 Aspect Scores\n"
    report_md += "| Aspect | Score | Weight |\n"
    report_md += "|--------|-------|--------|\n"
    for row in aspect_data:
        report_md += f"| {row['Aspect']} | {row['Score']} | {row['Weight']:.2f} |\n"
    
    report_md += f"\n## 📋 Feedback History\n"
    feedback_response = supabase.table("feedback").select("*").eq("project_id", st.session_state.current_project_id).execute()
    feedback_data = feedback_response.data if feedback_response.data else []
    if feedback_data:
        df_feedback = pd.DataFrame(feedback_data)
        report_md += df_feedback[["timestamp", "predictive_index", "actual_outcome", "notes"]].to_markdown(index=False)
    else:
        report_md += "No feedback recorded yet.\n"
    
    st.download_button(
        label="⬇️ Download Report Now",
        data=report_md,
        file_name=f"Centergy_PSSA_Report_{st.session_state.current_project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )
    st.success("Report generated! Click the download button above to save it.")

# ====================== FEEDBACK SECTION ======================
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

st.caption("PSSA v3.2 – Export Report Added | Centergy Reality-Based Controls")