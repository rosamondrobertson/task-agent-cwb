"""
SJ Project Planner - Task Progress Agent
SJ Group | Agentic AI for Task-Progress and Project Tracking
"""

import os
import json
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ------------------------------------------------------------------ #
# CONFIG — hardcoded for macOS reliability, no dotenv dependency
# ------------------------------------------------------------------ #
AI_ENDPOINT = "https://integrate.api.nvidia.com/v1"
AI_API_KEY  = "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"
AI_MODEL    = "meta/llama-3.1-70b-instruct"

client = OpenAI(base_url=AI_ENDPOINT, api_key=AI_API_KEY)

# ------------------------------------------------------------------ #
# PAGE CONFIG
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="SJ Project Planner",
    page_icon=":bar_chart:",
    layout="wide"
)

# ------------------------------------------------------------------ #
# SESSION STATE DEFAULTS
# ------------------------------------------------------------------ #
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": "T-001", "project": "Mumbai Metro Phase 3",   "task": "Foundation excavation - Sector A", "owner": "Raj Kumar",    "status": "Completed",   "progress": 100, "due": "2026-04-25", "priority": "High",     "blockers": ""},
        {"id": "T-002", "project": "Mumbai Metro Phase 3",   "task": "Tunnel boring - East corridor",    "owner": "Priya Shah",   "status": "In Progress", "progress": 65,  "due": "2026-05-15", "priority": "Critical", "blockers": "Geological survey delays"},
        {"id": "T-003", "project": "Mumbai Metro Phase 3",   "task": "Station design approval",          "owner": "Anand Verma",  "status": "In Progress", "progress": 40,  "due": "2026-05-08", "priority": "High",     "blockers": ""},
        {"id": "T-004", "project": "Bangalore Highway",      "task": "Land acquisition - Phase 2",       "owner": "Meera Iyer",   "status": "Blocked",     "progress": 30,  "due": "2026-04-30", "priority": "Critical", "blockers": "Awaiting govt clearance"},
        {"id": "T-005", "project": "Bangalore Highway",      "task": "Asphalt laying - Section 5",       "owner": "Vikram Rao",   "status": "Not Started", "progress": 0,   "due": "2026-06-01", "priority": "Medium",   "blockers": ""},
        {"id": "T-006", "project": "Chennai Port Expansion", "task": "Dredging operations",              "owner": "Sanjay Menon", "status": "In Progress", "progress": 80,  "due": "2026-05-05", "priority": "High",     "blockers": ""},
        {"id": "T-007", "project": "Chennai Port Expansion", "task": "Crane installation",               "owner": "Kavita Singh", "status": "Delayed",     "progress": 25,  "due": "2026-04-28", "priority": "Critical", "blockers": "Equipment shipping delay"},
        {"id": "T-008", "project": "Delhi Smart City",       "task": "IoT sensor deployment",            "owner": "Arjun Nair",   "status": "In Progress", "progress": 55,  "due": "2026-05-20", "priority": "Medium",   "blockers": ""},
        {"id": "T-009", "project": "Delhi Smart City",       "task": "Data center commissioning",        "owner": "Neha Gupta",   "status": "Not Started", "progress": 0,   "due": "2026-06-15", "priority": "High",     "blockers": ""},
        {"id": "T-010", "project": "Hyderabad Metro",        "task": "Track laying - Line 2",            "owner": "Rohit Sharma", "status": "In Progress", "progress": 70,  "due": "2026-05-10", "priority": "High",     "blockers": ""},
    ]

if "report" not in st.session_state:
    st.session_state.report = None

if "chat_answer" not in st.session_state:
    st.session_state.chat_answer = None

# ------------------------------------------------------------------ #
# AI HELPERS
# ------------------------------------------------------------------ #
def call_ai(prompt, max_tokens=1500, temperature=0.3):
    try:
        r = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def get_status_report(tasks_df):
    prompt = (
        "You are SJ Group's Project Planning Agent. "
        "Generate an executive weekly status report using markdown.\n\n"
        f"Tasks: {json.dumps(tasks_df.to_dict('records'), default=str)}\n\n"
        "Sections to include:\n"
        "## Executive Summary\n"
        "## On-Track Highlights\n"
        "## Critical Risks (with task IDs)\n"
        "## Active Blockers (with task IDs and escalations)\n"
        "## Recommended Actions This Week\n\n"
        "Be specific. Reference task IDs and owner names."
    )
    return call_ai(prompt, max_tokens=1500, temperature=0.3)


def get_risk_score(task):
    prompt = (
        f"Score the risk of this project task 0-100.\n"
        f"Task: {json.dumps(task, default=str)}\n"
        f"Today: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        'Return ONLY valid JSON: {"risk_score": 75, "risk_factors": ["reason1"], "mitigation": "action"}'
    )
    content, err = call_ai(prompt, max_tokens=300, temperature=0.2)
    if err:
        return {"risk_score": 50, "risk_factors": ["API error"], "mitigation": "Review manually"}, err
    try:
        start = content.find("{")
        end   = content.rfind("}") + 1
        return json.loads(content[start:end]), None
    except Exception:
        return {"risk_score": 50, "risk_factors": ["Parse error"], "mitigation": "Review manually"}, "JSON parse failed"


def get_chat_answer(question, tasks_df):
    prompt = (
        "You are SJ Group's Project Agent. Answer concisely using the task data below.\n\n"
        f"Tasks: {json.dumps(tasks_df.to_dict('records'), default=str)}\n\n"
        f"Question: {question}\n\n"
        "Reference task IDs and owner names where relevant."
    )
    return call_ai(prompt, max_tokens=600, temperature=0.3)


# ------------------------------------------------------------------ #
# HEADER
# ------------------------------------------------------------------ #
st.title("SJ Project Planner Agent")
st.caption("Agentic AI for Task-Progress and Project Tracking | SJ Group")
st.divider()

df = pd.DataFrame(st.session_state.tasks)

# ------------------------------------------------------------------ #
# KPI ROW
# ------------------------------------------------------------------ #
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Tasks",     len(df))
k2.metric("In Progress",     len(df[df["status"] == "In Progress"]))
k3.metric("Completed",       len(df[df["status"] == "Completed"]))
k4.metric("Blocked/Delayed", len(df[df["status"].isin(["Blocked", "Delayed"])]))
overdue = len(df[
    (pd.to_datetime(df["due"]) < datetime.now()) &
    (df["status"] != "Completed")
])
k5.metric("Overdue", overdue, delta=f"-{overdue}" if overdue else None, delta_color="inverse")

st.divider()

# ------------------------------------------------------------------ #
# TABS
# ------------------------------------------------------------------ #
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Task Board",
    "Analytics",
    "AI Status Report",
    "Risk Analysis",
    "Ask the Agent",
])

# ======================== TAB 1 — Task Board ========================
with tab1:
    st.subheader("Project Task Board")

    c1, c2, c3 = st.columns(3)
    proj_f   = c1.multiselect("Project",  sorted(df["project"].unique()),  default=sorted(df["project"].unique()))
    stat_f   = c2.multiselect("Status",   sorted(df["status"].unique()),   default=sorted(df["status"].unique()))
    pri_f    = c3.multiselect("Priority", sorted(df["priority"].unique()), default=sorted(df["priority"].unique()))

    mask     = df["project"].isin(proj_f) & df["status"].isin(stat_f) & df["priority"].isin(pri_f)
    filtered = df[mask].reset_index(drop=True)

    STATUS_COLORS = {
        "Completed":   "background-color:#28a745;color:white",
        "In Progress": "background-color:#007bff;color:white",
        "Not Started": "background-color:#6c757d;color:white",
        "Blocked":     "background-color:#dc3545;color:white",
        "Delayed":     "background-color:#fd7e14;color:white",
    }

    st.caption("Colour-coded view:")
    st.dataframe(
        filtered.style
            .format({"progress": "{:.0f}%"})
            .map(lambda v: STATUS_COLORS.get(v, ""), subset=["status"]),
        use_container_width=True,
        height=300,
    )

    st.caption("Edit tasks inline:")
    edited = st.data_editor(
        filtered,
        use_container_width=True,
        height=300,
        num_rows="fixed",
        key="task_editor",
        column_config={
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Not Started", "In Progress", "Completed", "Blocked", "Delayed"],
            ),
            "priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["Low", "Medium", "High", "Critical"],
            ),
            "progress": st.column_config.NumberColumn("Progress %", min_value=0, max_value=100, step=5),
            "due":      st.column_config.TextColumn("Due Date (YYYY-MM-DD)"),
        },
    )

    # Persist edits back to session state by matching task ID
    if edited is not None:
        for _, row in edited.iterrows():
            for i, task in enumerate(st.session_state.tasks):
                if task["id"] == row["id"]:
                    st.session_state.tasks[i] = row.to_dict()
                    break

# ======================== TAB 2 — Analytics =========================
with tab2:
    st.subheader("Project Analytics")

    a1, a2 = st.columns(2)

    sc = df["status"].value_counts().reset_index()
    sc.columns = ["status", "count"]
    a1.plotly_chart(
        px.pie(sc, values="count", names="status", title="Status Distribution",
               color_discrete_sequence=px.colors.qualitative.Set2),
        use_container_width=True,
    )

    pp = df.groupby("project")["progress"].mean().reset_index()
    a2.plotly_chart(
        px.bar(pp, x="project", y="progress", title="Avg Progress by Project (%)",
               color="progress", color_continuous_scale="Blues", range_y=[0, 100]),
        use_container_width=True,
    )

    gantt = df.copy()
    gantt["end"]   = pd.to_datetime(gantt["due"])
    gantt["start"] = gantt.apply(
        lambda r: pd.to_datetime(r["due"]) - timedelta(days=max(7, int(r["progress"] * 0.3))),
        axis=1,
    )
    fig3 = px.timeline(gantt, x_start="start", x_end="end", y="task",
                       color="status", title="Task Timeline", height=480)
    fig3.update_yaxes(autorange="reversed")
    st.plotly_chart(fig3, use_container_width=True)

# ======================== TAB 3 — AI Status Report ==================
with tab3:
    st.subheader("AI-Generated Executive Status Report")

    b1, b2 = st.columns([3, 1])
    gen   = b1.button("Generate Weekly Status Report", type="primary")
    clear = b2.button("Clear Report")

    if clear:
        st.session_state.report = None
        st.rerun()

    if gen:
        with st.spinner("Agent analysing tasks..."):
            report, err = get_status_report(df)
        if err:
            st.error(f"API Error: {err}")
        else:
            st.session_state.report = report

    if st.session_state.report:
        st.markdown(st.session_state.report)
        st.download_button(
            "Download Report (.md)",
            data=st.session_state.report,
            file_name=f"sj_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        )
    elif not gen:
        st.info("Click 'Generate' to produce an AI executive briefing across all projects.")

# ======================== TAB 4 — Risk Analysis =====================
with tab4:
    st.subheader("AI Risk Scoring")
    st.caption("Scores each task 0-100 with risk factors and mitigation steps.")

    if st.button("Run Risk Analysis", type="primary"):
        bar    = st.progress(0)
        total  = len(df)
        rows   = []
        errors = []

        for idx, (_, row) in enumerate(df.iterrows()):
            result, err = get_risk_score(row.to_dict())
            if err:
                errors.append(f"{row['id']}: {err}")
            rows.append({
                "ID":         row["id"],
                "Task":       row["task"][:38] + ".." if len(row["task"]) > 38 else row["task"],
                "Owner":      row["owner"],
                "Risk Score": result["risk_score"],
                "Top Risk":   result["risk_factors"][0] if result["risk_factors"] else "-",
                "Mitigation": result["mitigation"],
            })
            bar.progress((idx + 1) / total)

        if errors:
            st.warning("Fallback scores used for: " + ", ".join(errors))

        risk_df = pd.DataFrame(rows).sort_values("Risk Score", ascending=False)

        def risk_color(v):
            if v >= 70: return "background-color:#dc3545;color:white"
            if v >= 40: return "background-color:#fd7e14;color:white"
            return "background-color:#28a745;color:white"

        st.dataframe(
            risk_df.style.map(risk_color, subset=["Risk Score"]),
            use_container_width=True,
            height=420,
        )

# ======================== TAB 5 — Ask the Agent =====================
with tab5:
    st.subheader("Ask the Agent")
    st.caption("Ask anything about your project portfolio in plain English.")

    examples = [
        "What are my biggest risks this week?",
        "Which owner has the most overdue tasks?",
        "Summarise the Chennai Port Expansion.",
    ]
    e1, e2, e3 = st.columns(3)
    for col, ex in zip([e1, e2, e3], examples):
        if col.button(ex, use_container_width=True):
            with st.spinner("Agent reasoning..."):
                ans, err = get_chat_answer(ex, df)
            if err:
                st.error(f"API Error: {err}")
            else:
                st.session_state.chat_answer = ans

    st.divider()

    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input("Your question", placeholder="e.g. Who owns the most blocked tasks?")
        submitted = st.form_submit_button("Ask", type="primary")

    if submitted and question:
        with st.spinner("Agent reasoning..."):
            ans, err = get_chat_answer(question, df)
        if err:
            st.error(f"API Error: {err}")
        else:
            st.session_state.chat_answer = ans

    if st.session_state.chat_answer:
        st.success(st.session_state.chat_answer)