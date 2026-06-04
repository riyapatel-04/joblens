import streamlit as st
import pandas as pd
import plotly.express as px
import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="JobLens — Job Market Intelligence",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    df = pd.read_sql("SELECT * FROM RAW_JOBS", conn)
    conn.close()
    df.columns = [col.lower() for col in df.columns]
    return df

SKILLS_LIST = [
    "python", "sql", "snowflake", "dbt", "spark", "airflow",
    "azure", "aws", "tableau", "power bi", "databricks",
    "kafka", "docker", "kubernetes", "scala", "machine learning"
]

def extract_skills(df):
    skill_counts = {}
    for skill in SKILLS_LIST:
        count = df['description'].str.lower().str.contains(skill, na=False).sum()
        if count > 0:
            skill_counts[skill.upper()] = int(count)
    return dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))

# Load data
df = load_data()

# Header
st.markdown('<p class="main-header">🔍 JobLens — Job Market Intelligence</p>', unsafe_allow_html=True)
st.markdown("*Real-time insights from live job postings across the US*")
st.divider()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    active_jobs = len(df[df['status'] == 'active']) if 'status' in df.columns else len(df)
    st.metric("🟢 Active Postings", f"{active_jobs:,}")
with col2:
    total_jobs = len(df)
    st.metric("📊 Total Jobs Tracked", f"{total_jobs:,}")
with col3:
    st.metric("🏙️ Cities Covered", df['search_location'].nunique())
with col4:
    st.metric("🏢 Unique Companies", df['company'].nunique())

st.divider()

# Filter to active jobs only for charts
active_df = df[df['status'] == 'active'] if 'status' in df.columns else df

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Market Overview",
    "🔥 Skills Intelligence",
    "💰 Salary Insights",
    "🤖 AI Chatbot"
])

# Tab 1 - Market Overview
with tab1:
    st.subheader("Job Postings by Role")
    role_counts = active_df['search_role'].value_counts().reset_index()
    role_counts.columns = ['Role', 'Count']
    fig1 = px.bar(role_counts, x='Role', y='Count',
                  color='Count', color_continuous_scale='blues',
                  title="Active Job Postings by Role")
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Hiring Cities")
        city_counts = active_df['search_location'].value_counts().head(10).reset_index()
        city_counts.columns = ['City', 'Count']
        fig2 = px.bar(city_counts, x='Count', y='City',
                      orientation='h', color='Count',
                      color_continuous_scale='teal',
                      title="Top 10 Hiring Cities")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Top Hiring Companies")
        company_counts = active_df['company'].value_counts().head(10).reset_index()
        company_counts.columns = ['Company', 'Count']
        fig3 = px.pie(company_counts, values='Count', names='Company',
                      title="Top 10 Companies by Active Job Postings")
        st.plotly_chart(fig3, use_container_width=True)

# Tab 2 - Skills Intelligence
with tab2:
    st.subheader("🔥 Most In-Demand Skills")
    skill_counts = extract_skills(active_df)
    skill_df = pd.DataFrame(list(skill_counts.items()), columns=['Skill', 'Job Count'])

    fig4 = px.bar(skill_df, x='Job Count', y='Skill',
                  orientation='h', color='Job Count',
                  color_continuous_scale='reds',
                  title="Skills Demand Across Active Job Postings")
    fig4.update_layout(height=600)
    st.plotly_chart(fig4, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Skills by Role")
        selected_role = st.selectbox("Select Role", active_df['search_role'].unique())
        role_df = active_df[active_df['search_role'] == selected_role]
        role_skills = {}
        for skill in SKILLS_LIST:
            count = role_df['description'].str.lower().str.contains(skill, na=False).sum()
            if count > 0:
                role_skills[skill.upper()] = int(count)
        role_skills = dict(sorted(role_skills.items(), key=lambda x: x[1], reverse=True)[:10])
        if role_skills:
            fig5 = px.bar(
                x=list(role_skills.values()),
                y=list(role_skills.keys()),
                orientation='h',
                title=f"Top Skills for {selected_role}"
            )
            st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.subheader("Skills by City")
        selected_city = st.selectbox("Select City", active_df['search_location'].unique())
        city_df = active_df[active_df['search_location'] == selected_city]
        city_skills = {}
        for skill in SKILLS_LIST:
            count = city_df['description'].str.lower().str.contains(skill, na=False).sum()
            if count > 0:
                city_skills[skill.upper()] = int(count)
        city_skills = dict(sorted(city_skills.items(), key=lambda x: x[1], reverse=True)[:10])
        if city_skills:
            fig6 = px.bar(
                x=list(city_skills.values()),
                y=list(city_skills.keys()),
                orientation='h',
                title=f"Top Skills in {selected_city}"
            )
            st.plotly_chart(fig6, use_container_width=True)

# Tab 3 - Salary Insights
with tab3:
    st.subheader("💰 Salary Analysis")
    salary_df = active_df[
        (active_df['salary_min'].notna()) &
        (active_df['salary_max'].notna()) &
        (active_df['salary_min'] > 0) &
        (active_df['salary_max'] > 0)
    ].copy()
    salary_df['salary_avg'] = (salary_df['salary_min'] + salary_df['salary_max']) / 2

    if len(salary_df) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Salary", f"${salary_df['salary_avg'].mean():,.0f}")
        with col2:
            st.metric("Highest Salary", f"${salary_df['salary_max'].max():,.0f}")
        with col3:
            st.metric("Lowest Salary", f"${salary_df['salary_min'].min():,.0f}")

        col1, col2 = st.columns(2)
        with col1:
            avg_by_role = salary_df.groupby('search_role')['salary_avg'].mean().reset_index()
            avg_by_role.columns = ['Role', 'Avg Salary']
            avg_by_role = avg_by_role.sort_values('Avg Salary', ascending=False)
            fig7 = px.bar(avg_by_role, x='Role', y='Avg Salary',
                          color='Avg Salary', color_continuous_scale='greens',
                          title="Average Salary by Role")
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            avg_by_city = salary_df.groupby('search_location')['salary_avg'].mean().reset_index()
            avg_by_city.columns = ['City', 'Avg Salary']
            avg_by_city = avg_by_city.sort_values('Avg Salary', ascending=False)
            fig8 = px.bar(avg_by_city, x='City', y='Avg Salary',
                          color='Avg Salary', color_continuous_scale='purples',
                          title="Average Salary by City")
            st.plotly_chart(fig8, use_container_width=True)

        fig9 = px.scatter(salary_df, x='salary_min', y='salary_max',
                          color='search_role', hover_data=['title', 'company'],
                          title="Salary Range Distribution by Role")
        st.plotly_chart(fig9, use_container_width=True)
    else:
        st.info("Limited salary data available in current active job postings.")

# Tab 4 - AI Chatbot
with tab4:
    st.subheader("🤖 Ask JobLens AI")
    st.markdown("Ask anything about the job market based on real job postings data!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about the job market..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing job market data..."):
                from ai.chatbot import answer_question
                response = answer_question(prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})