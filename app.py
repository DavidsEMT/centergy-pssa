import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
st.write("v2.0 Authentication Test - " + datetime.now().strftime("%H:%M:%S"))
# Page config with custom title
st.set_page_config(page_title="Centergy Group Project Success Simulator", layout="centered", page_icon="🟢")

# Display Centergy Group Logo at the top
try:
    st.image("centergy_logo.png", width=400)
except:
    st.markdown("### Centergy Group")

st.title("Centergy Group Project Success Simulator")
st.markdown("**Reality-Based Predictive Analysis** – Centergy Group Training + Darwinian Learning + Visual Metrics")

# Database Setup
conn = sqlite3.connect('pssa_feedback.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS feedback 
             (timestamp TEXT, predictive_index REAL, actual_outcome TEXT, notes TEXT, grant_mode INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS aspects 
             (id INTEGER PRIMARY KEY, name TEXT, description TEXT, weight REAL, is_grant_only INTEGER)''')
conn.commit()

# Load or Initialize Aspects (tweaked defaults)
def load_aspects():
    df = pd.read_sql_query("SELECT * FROM aspects", conn)
    if df.empty:
        defaults = [
            ("WBS Completeness", "Deliverables-oriented WBS defined and validated?", 0.13, 0),
            ("Stakeholder Alignment", "Clear buy-in and engagement from team, client, and sponsor?", 0.10, 0),
            ("Schedule Baseline Quality", "Critical Path validated via Sticky Shuffle?", 0.12, 0),
            ("Cost Control Baseline", "Budget and EVM-style forecasts established?", 0.10, 0),
            ("Risk Identification & Response", "Risk Log with Darwinian mitigation strategies?", 0.13, 0),
            ("Team Experience & Capacity", "Skills, learning curve, and capacity addressed?", 0.09, 0),
            ("Requirements Stability", "Changing requirements identified and controlled?", 0.08, 0),
            ("Resource Availability", "People, tools, and funding secured?", 0.08, 0),
            ("Lessons Learned Integration", "Past failures proactively avoided?", 0.05, 0),
            ("Communication & PUF Plan", "PUF-style updates and proactive communication planned?", 0.06, 0),
            ("Executive Support", "Strong sponsor commitment and visibility?", 0.00, 0),
            # Grant-specific
            ("Grant Compliance & Reporting Readiness", "NOFO/RFA guidelines, reporting, and audit readiness fully addressed?", 0.10, 1),
            ("Measurable Outcomes & Evaluation Plan", "Clear baseline data, KPIs, and success indicators defined?", 0.09, 1),
            ("Funding Certainty & Matching Requirements", "Budget realistic with secured matching funds and cash flow?", 0.08, 1),
            ("Proposal Alignment with Funder Priorities", "Project clearly ties to funder goals and priorities?", 0.08, 1)
        ]
        for name, desc, weight, grant_only in defaults:
            c.execute("INSERT INTO aspects (name, description, weight, is_grant_only) VALUES (?, ?, ?, ?)",
                      (name, desc, weight, grant_only))
        conn.commit()
        df = pd.read_sql_query("SELECT * FROM aspects", conn)
    return df

aspects_df = load_aspects()

# Grant Mode
use_grant_mode = st.checkbox("Enable Grant Mode (NGO / Government Submissions)", value=False,
                             help="Shows grant-specific aspects and adjusts emphasis")

# Manage Aspects
with st.expander("⚙️ Manage Aspects (Add / Edit / Delete)"):
    st.markdown("Customize for any project type. Changes are saved automatically.")

    with st.form("add_aspect"):
        new_name = st.text_input("New Aspect Name")
        new_desc = st.text_input("Description")
        new_weight = st.slider("Weight (0.00 - 0.20)", 0.0, 0.20, 0.08, 0.01)
        is_grant = st.checkbox("Grant-specific only")
        if st.form_submit_button("Add New Aspect"):
            if new_name and new_desc:
                c.execute("INSERT INTO aspects (name, description, weight, is_grant_only) VALUES (?, ?, ?, ?)",
                          (new_name, new_desc, new_weight, int(is_grant)))
                conn.commit()
                st.success(f"Added: {new_name}")
                st.rerun()

    for idx, row in aspects_df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 3, 1.5, 1])
        with col1:
            name = st.text_input("Name", value=row["name"], key=f"name_{row['id']}")
        with col2:
            desc = st.text_input("Description", value=row["description"], key=f"desc_{row['id']}")
        with col3:
            weight = st.number_input("Weight", value=float(row["weight"]), min_value=0.0, max_value=0.20, step=0.01, key=f"wt_{row['id']}")
        with col4:
            if st.button("Delete", key=f"del_{row['id']}"):
                c.execute("DELETE FROM aspects WHERE id=?", (row["id"],))
                conn.commit()
                st.rerun()

    if st.button("Save All Changes"):
        for idx, row in aspects_df.iterrows():
            c.execute("UPDATE aspects SET name=?, description=?, weight=? WHERE id=?",
                      (st.session_state[f"name_{row['id']}"], 
                       st.session_state[f"desc_{row['id']}"], 
                       st.session_state[f"wt_{row['id']}"], 
                       row["id"]))
        conn.commit()
        st.success("All changes saved!")
        st.rerun()

# Load current aspects for prediction
current_aspects = {}
for _, row in aspects_df.iterrows():
    if not use_grant_mode and row["is_grant_only"] == 1:
        continue
    current_aspects[row["name"]] = {"desc": row["description"], "weight": row["weight"]}

# Main Prediction Section
st.subheader("Rate Each Project Aspect (1–10)")
inputs = {}
weighted_scores = {}
aspect_data = []

for name, data in current_aspects.items():
    score = st.slider(f"{name}", 1, 10, 7, help=data["desc"], key=name)
    inputs[name] = score
    weighted_scores[name] = score * data["weight"]
    aspect_data.append({"Aspect": name, "Score": score, "Weight": data["weight"]})

total_weighted = sum(weighted_scores.values())
max_weight = sum(a["weight"] for a in current_aspects.values()) if current_aspects else 1
predictive_index = round(total_weighted / max_weight, 1) if max_weight > 0 else 0

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
weak_aspects = [(a, s, current_aspects[a]["weight"]) for a, s in inputs.items() if s <= 5]
weak_aspects.sort(key=lambda x: x[2], reverse=True)

if weak_aspects:
    st.markdown("**Focus here first (highest impact issues):**")
    for aspect, score, wt in weak_aspects[:7]:
        st.warning(f"**{aspect}** (Score: {score}/10, Weight: {wt:.2f}) – {current_aspects[aspect]['desc']}")
        if aspect in ["WBS Completeness", "Schedule Baseline Quality", "Risk Identification & Response"]:
            st.info("→ Run Sticky Shuffle + add contingency buffer immediately.")
        elif any(k in aspect for k in ["Compliance", "Grant", "Outcomes", "Funding"]):
            st.info("→ Strengthen grant-specific elements (NOFO compliance, KPIs, cash flow).")
        else:
            st.info("→ Proactive fix now.")
else:
    st.success("All aspects strong – Excellent foundation!")

st.markdown(f"**Overall Guidance:** {advice_level}")

# Visual Charts
st.subheader("📊 Visual Project Aspects Analysis")
df_aspects = pd.DataFrame(aspect_data).sort_values("Score", ascending=True)
fig_bar = px.bar(df_aspects, x="Score", y="Aspect", orientation='h',
                 title="Aspect Scores (Higher = Better)",
                 color="Score", color_continuous_scale="RdYlGn")
fig_bar.update_layout(height=500)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📈 Historical Predictive Index Trend")
df_feedback = pd.read_sql_query("SELECT timestamp, predictive_index FROM feedback ORDER BY timestamp", conn)
if not df_feedback.empty:
    df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
    fig_trend = px.line(df_feedback, x="timestamp", y="predictive_index",
                        title="Predictive Index Trend from Actual Outcomes",
                        markers=True)
    fig_trend.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig_trend, use_container_width=True)

# Feedback Loop
st.subheader("📊 Actual Outcome Feedback (Help the App Learn)")

if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = 0

col_fb1, col_fb2 = st.columns(2)
with col_fb1:
    actual_result = st.selectbox("Actual Project Outcome", 
        ["Success (Green)", "Partial Success (Yellow)", "Failure (Red)", "Not yet complete"],
        key=f"outcome_{st.session_state.reset_trigger}")
with col_fb2:
    notes = st.text_area("Notes / Lessons Learned", 
        placeholder="What actually happened? (Grant-specific insights welcome)",
        key=f"notes_{st.session_state.reset_trigger}")

if st.button("Submit Feedback & Update Model"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO feedback VALUES (?, ?, ?, ?, ?)", 
              (now, predictive_index, actual_result, notes, int(use_grant_mode)))
    conn.commit()
    st.success("✅ Feedback saved successfully! Form cleared.")
    st.session_state.reset_trigger += 1
    st.rerun()

# Export
st.subheader("📄 Export Report")
if st.button("⬇️ Download Markdown Report"):
    report_md = f"""# Centergy Group Project Success Simulator Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Prediction Result
**{status}**  
**Success Predictive Index:** {predictive_index}/10.0

## Overall Guidance
{advice_level}

## Key Issues to Address
"""
    for aspect, score, wt in weak_aspects[:7]:
        report_md += f"- **{aspect}** (Score: {score}/10) — {current_aspects[aspect]['desc']}\n"

    report_md += f"\n## Grant Mode: {'Enabled' if use_grant_mode else 'Disabled'}\n\n"

    report_md += "### Aspect Scores\n"
    for item in aspect_data:
        report_md += f"- {item['Aspect']}: {item['Score']}/10 (Weight: {item['Weight']:.2f})\n"

    df_raw = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 10", conn)
    report_md += "\n## Recent Feedback\n\n"
    report_md += "| Timestamp | Predictive Index | Outcome | Notes | Grant Mode |\n"
    report_md += "|-----------|------------------|---------|-------|------------|\n"
    for _, row in df_raw.iterrows():
        report_md += f"| {row['timestamp']} | {row['predictive_index']:.1f} | {row['actual_outcome']} | {row['notes'] or ''} | {'Yes' if row['grant_mode'] else 'No'} |\n"

    st.download_button(
        label="Save Report (Markdown)",
        data=report_md,
        file_name=f"Centergy_PSSA_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )
    st.success("✅ Report downloaded to your Downloads folder.")

st.info("**To create a clean PDF:** Download the Markdown, open in Typora (recommended), then File → Export → PDF. Or use browser Print (⌘P) → Save as PDF on this page for a quick version with charts.")

with st.expander("📋 View Raw Feedback Data"):
    df_raw = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 20", conn)
    if not df_raw.empty:
        st.dataframe(df_raw)

st.caption("PSSA v1.6 – Centergy Group Edition with Logo & Custom Title | Reality-Based Project Controls")
conn.close()