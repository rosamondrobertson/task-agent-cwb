# 📊 Task Progress Agent

> **Partner:** SJ Group | **Problem Statement:** SJ Project Planner Agent — Agentic AI for Task-Progress and Project Tracking
> **Built for:** Code Without Barriers Hackathon

---

## 📌 About the Project

The **Task Progress Agent** is the heart of SJ Group's Project Planner — an interactive Streamlit dashboard that consolidates all project tasks, surfaces risks autonomously, and generates executive-grade status reports on demand. Built to scale across SJ Group's portfolio of large infrastructure projects (metro, highways, ports, smart cities).

### What This Agent Does

- 📋 **Unified Task Board** — All projects, owners, statuses, blockers in one filterable view
- 📈 **Real-Time Analytics** — Status distribution, progress by project, Gantt timelines (Plotly)
- 🤖 **AI Status Reports** — Agent generates structured executive briefings (Exec Summary → On-Track → Critical Risks → Blockers → Actions)
- ⚠️ **AI Risk Scoring** — Per-task 0-100 risk scoring with factors and mitigation strategies
- 💬 **Conversational Queries** — Natural-language questions over the portfolio (*"who has the most overdue tasks?"*)

### Why "Agent" and Not Just a Dashboard?

A dashboard shows numbers. An **agent**:

- **Synthesizes** raw task data into executive narratives
- **Scores** risk by reasoning over deadlines, blockers, owner workload
- **Recommends** specific mitigations per risk
- **Answers** open-ended business questions over the corpus

---

## 🏗️ Architecture

```
┌──────────────────────────────┐
│  Streamlit Dashboard         │
│  • Task board                │
│  • Plotly analytics          │
│  • AI report generator       │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Project Agent Core          │
│  • Status report synth.      │
│  • Risk scoring engine       │
│  • Q&A over project corpus   │
└──────────┬───────────────────┘
           │
           ├──→ Azure AI Foundry (LLM)
           ├──→ Azure Database for PostgreSQL
           ├──→ Power BI (embedded charts)
           └──→ Microsoft Agent Framework
```

---

## ☁️ Microsoft Azure Integration

| Azure Service                           | Role                              |
| --------------------------------------- | --------------------------------- |
| **Microsoft Agent Framework**     | Agent orchestration               |
| **Azure AI Foundry**              | LLM for reports + risk reasoning  |
| **Azure Database for PostgreSQL** | Project + task persistence        |
| **Power BI**                      | Embedded executive dashboards     |
| **Azure Cosmos DB**               | Status report archive             |
| **Azure Blob Storage**            | Document attachments              |
| **GitHub**                        | Source control + CI/CD            |
| **Power Automate**                | Auto-notifications on risk events |
| **Azure AI Search**               | Index project documents for RAG   |

---

## ⚙️ Setup Instructions

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your .env file (one-time)
cp .env.example .env

# 3. Edit .env with your actual keys (use any text editor)
#    Example .env contents:
#      AI_ENDPOINT=https://your-endpoint/v1
#      AI_API_KEY=your-api-key
#      AI_MODEL=meta/llama-3.1-70b-instruct

# 4. Run the agent
streamlit run app.py
```

Open `http://localhost:8501`

---


## 📂 Files

```
05_task_progress/
├── app.py
├── requirements.txt
└── README.md
```
