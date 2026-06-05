# JobLens — Job Market Intelligence

I built this while job hunting because I was tired of not knowing what skills actually matter, which cities pay well, and whether my resume even stands a chance. So I built a pipeline that pulls real job data every day and lets me ask an AI those exact questions.

**Live:** https://riyapatel-04-joblens-dashboardapp-zw9bzh.streamlit.app/

---

## What it does

Pulls thousands of job postings daily from 30 US cities, loads them into Snowflake, and surfaces insights through a dashboard — skill trends, salary benchmarks, resume gap analysis, and an AI chatbot that answers questions using the actual data.

---

## Numbers

- 6,700+ active job postings tracked
- 30 US cities covered
- 2,000+ unique companies
- Pipeline runs every day at 8am EST automatically
- 100% data validation rate

---

## How it works

```
Adzuna API → Python scraper → Pydantic validation → Azure Blob
                                                         ↓
                                                Snowflake warehouse
                                                         ↓
                                               dbt (staging → marts)
                                                         ↓
                                    HuggingFace embeddings → ChromaDB
                                    LangChain + Groq → RAG chatbot
                                                         ↓
                                            Streamlit dashboard
                                                         ↓
                              GitHub Actions runs this whole thing daily
```

---

## Features

### Market Overview
Real-time breakdown of who's hiring, where, and how many roles. Bar charts for roles and cities, pie chart for top companies. All from live Snowflake data.

**Stack:** Snowflake, Pandas, Plotly, Streamlit

---

### Skills Intelligence
Scans job descriptions to show which skills companies are actually asking for — filterable by role and city. So instead of guessing, you can see that Databricks shows up in 60% of data engineer JDs in Chicago.

**Stack:** Snowflake, Pandas, Plotly, Streamlit

---

### Salary Insights
Salary benchmarks by role and city using real posting data. Filters out bad data (hourly rates showing as annual, extreme outliers) so the numbers are actually useful.

**Stack:** Snowflake, Pandas, Plotly, Streamlit

---

### AI Chatbot
Ask anything about the job market — "what skills do data engineers need in Boston?" or "which companies pay the most for analytics engineers?" — and it answers using your actual pipeline data, not the internet.

Built with RAG: job descriptions are embedded into ChromaDB, LangChain retrieves the relevant ones, and Groq's Llama model generates the answer.

**Stack:** HuggingFace Embeddings, ChromaDB, LangChain, Groq (Llama 3.1), FastAPI

---

### Personal Fit Score
Enter your skills, pick a role, and see what percentage of active job postings you match. Shows which of your skills are in demand and which ones you're missing, with a breakdown by role.

**Stack:** Pandas, Plotly, Streamlit

---

### Resume Gap Analyzer
Two modes:
- Upload your resume → compare it against the full job market for your target role and city
- Paste a specific JD → get a targeted match score and missing skills

After the analysis, Groq generates personalized advice: honest assessment, top 3 skills to learn, realistic timeline, and one actionable tip.

**Stack:** PyPDF2, Pandas, Plotly, LangChain, Groq, Streamlit

---

### Job Alerts
Subscribe with your email, role, and city. Every morning when the pipeline runs, if there are new matching jobs, you get an email with titles, companies, salaries, and apply links.

Subscriptions stored in Snowflake. Emails sent via Gmail SMTP. Triggered automatically by GitHub Actions.

**Stack:** Snowflake, Gmail SMTP, GitHub Actions, Streamlit

---

### Funded Startups
Shows recently funded data and AI companies — because companies that just raised money are usually hiring aggressively. Combines a curated list of known companies with live TechCrunch RSS data.

**Stack:** feedparser, Pandas, Streamlit

---

### Job Board
A searchable, filterable table of all active job postings with direct apply links. Filter by role, city, company, keyword, salary range, and sort however you want.

**Stack:** Snowflake, Pandas, Streamlit

---

## Tech Stack

| Layer | Tools |
|---|---|
| Ingestion | Python, Adzuna API, Requests, Pydantic |
| Storage | Azure Blob Storage, Snowflake |
| Transformation | dbt, SQL |
| AI | LangChain, ChromaDB, HuggingFace, Groq |
| Backend | FastAPI, Uvicorn |
| Dashboard | Streamlit, Plotly |
| Automation | GitHub Actions, Apache Airflow |
| Email | Gmail SMTP |
| Deployment | Streamlit Cloud |

---

## Project Structure

```
joblens/
├── .github/workflows/daily_pipeline.yml   # Runs every day at 8am EST
├── ingestion/
│   ├── adzuna_client.py      # Fetches jobs from Adzuna API
│   ├── validator.py          # Pydantic validation
│   ├── azure_uploader.py     # Uploads raw JSON to Azure Blob
│   ├── snowflake_loader.py   # Loads new jobs, marks expired ones
│   ├── alerts.py             # Email alert system
│   └── startups.py           # Funded startups scraper
├── dbt_joblens/models/
│   ├── staging/stg_jobs.sql          # Cleans raw data
│   └── marts/mart_skill_trends.sql   # Skill trend aggregations
├── ai/
│   ├── embeddings.py   # Builds ChromaDB vector store
│   ├── chatbot.py      # LangChain + Groq RAG pipeline
│   └── api.py          # FastAPI endpoints
├── dashboard/app.py    # All 9 tabs
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/riyapatel-04/joblens.git
cd joblens
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
AZURE_CONNECTION_STRING=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_DATABASE=JOBLENS
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_WAREHOUSE=JOBLENS_WH
GROQ_API_KEY=
GMAIL_USER=
GMAIL_APP_PASSWORD=
```

Run it:
```bash
python ingestion/adzuna_client.py
python ingestion/validator.py
python ingestion/snowflake_loader.py
python ai/embeddings.py
streamlit run dashboard/app.py
```

---

## Author

Riya Patel — MS Information Systems, Northeastern University

[LinkedIn](https://www.linkedin.com/in/patelriyas) · [GitHub](https://github.com/riyapatel-04)
