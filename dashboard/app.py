import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
import snowflake.connector
import PyPDF2
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def count_entry_level_jobs(df):
    entry_keywords = [
        "entry level", "entry-level", "junior", "associate", 
        "0-2 years", "0 to 2 years", "new grad", "recent graduate",
        "early career", "1-2 years", "1 to 2 years"
    ]
    mask = df['description'].str.lower().apply(
        lambda x: any(keyword in str(x) for keyword in entry_keywords)
    )
    return mask.sum()

# Load data
df = load_data()
active_jobs = len(df[df['status'] == 'active']) if 'status' in df.columns else len(df)

# Header
st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0 0.5rem 0;">
    <div style="flex: 1;">
        <h1 style="font-size: 3rem; font-weight: 800; color: #1f77b4; margin-bottom: 0.3rem;">
            🔍 JobLens — Job Market Intelligence
        </h1>
        <p style="font-size: 1.2rem; color: #444; margin-bottom: 0.8rem;">
            Real-time insights from <strong style="color: #1f77b4;">{active_jobs:,} active job postings</strong> across <strong style="color: #1f77b4;">{df['search_location'].nunique()} US cities</strong>
        </p>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <span style="background-color: #e8f4fd; color: #1f77b4; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">📊 Hiring Trends</span>
            <span style="background-color: #fff3e0; color: #e65100; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">🔥 Skill Demand</span>
            <span style="background-color: #e8f5e9; color: #2e7d32; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">💰 Salary Benchmarks</span>
            <span style="background-color: #f3e5f5; color: #6a1b9a; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">🎯 Fit Score</span>
            <span style="background-color: #fce4ec; color: #880e4f; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">📄 Resume Gap Analysis</span>
            <span style="background-color: #e8f5e9; color: #1b5e20; padding: 4px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">🤖 AI Career Advisor</span>
        </div>
    </div>
    <div style="flex: 0.4; text-align: center; padding: 0 1rem;">
        <svg viewBox="0 0 200 120" width="280" height="180" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="120" rx="10" fill="#f0f7ff"/>
            <line x1="20" y1="20" x2="20" y2="95" stroke="#ccc" stroke-width="0.5"/>
            <line x1="20" y1="95" x2="185" y2="95" stroke="#ccc" stroke-width="0.5"/>
            <line x1="20" y1="70" x2="185" y2="70" stroke="#eee" stroke-width="0.5"/>
            <line x1="20" y1="50" x2="185" y2="50" stroke="#eee" stroke-width="0.5"/>
            <line x1="20" y1="30" x2="185" y2="30" stroke="#eee" stroke-width="0.5"/>
            <rect x="30" y="45" width="22" height="50" rx="3" fill="#1f77b4" opacity="0.85"/>
            <rect x="60" y="35" width="22" height="60" rx="3" fill="#1f77b4" opacity="0.85"/>
            <rect x="90" y="55" width="22" height="40" rx="3" fill="#1f77b4" opacity="0.85"/>
            <rect x="120" y="25" width="22" height="70" rx="3" fill="#1f77b4" opacity="0.85"/>
            <rect x="150" y="40" width="22" height="55" rx="3" fill="#1f77b4" opacity="0.85"/>
            <polyline points="41,45 71,35 101,45 131,25 161,30" fill="none" stroke="#e65100" stroke-width="2" stroke-dasharray="3,2"/>
            <circle cx="41" cy="45" r="3" fill="#e65100"/>
            <circle cx="71" cy="35" r="3" fill="#e65100"/>
            <circle cx="101" cy="45" r="3" fill="#e65100"/>
            <circle cx="131" cy="25" r="3" fill="#e65100"/>
            <circle cx="161" cy="30" r="3" fill="#e65100"/>
            <text x="100" y="113" text-anchor="middle" font-size="8" fill="#888">Job Market Trends</text>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)
st.divider()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    active_jobs = len(df[df['status'] == 'active']) if 'status' in df.columns else len(df)
    st.metric("🟢 Active Postings", f"{active_jobs:,}")
with col2:
    st.metric("🏙️ Cities Covered", df['search_location'].nunique())
with col3:
    st.metric("🏢 Unique Companies", df['company'].nunique())
with col4:
    entry_count = count_entry_level_jobs(df)
    st.metric("🎓 Entry Level Jobs", f"{entry_count:,}")

st.divider()

# Filter to active jobs only
active_df = df[df['status'] == 'active'] if 'status' in df.columns else df

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Market Overview",
    "🔥 Skills Intelligence",
    "💰 Salary Insights",
    "🤖 AI Chatbot",
    "🎯 Personal Fit Score",
    "📄 Resume Gap Analyzer",
    "🔔 Job Alerts"
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
    (active_df['salary_min'] >= 40000) &    # minimum realistic entry level
    (active_df['salary_max'] <= 300000) &   # max realistic for data roles
    (active_df['salary_max'] > active_df['salary_min']) &  # max must be > min
    (active_df['salary_max'] - active_df['salary_min'] < 150000)  # realistic range gap
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
            avg_by_role['Avg Salary'] = avg_by_role['Avg Salary'].round(0)
            avg_by_role = avg_by_role.sort_values('Avg Salary', ascending=False)
            fig7 = px.bar(avg_by_role, x='Role', y='Avg Salary',
              color='Avg Salary', color_continuous_scale='greens',
              title="Average Salary by Role")
            fig7.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')
            st.plotly_chart(fig7, use_container_width=True)

        with col2:
            avg_by_city = salary_df.groupby('search_location')['salary_avg'].mean().reset_index()
            avg_by_city.columns = ['City', 'Avg Salary']
            avg_by_city['Avg Salary'] = avg_by_city['Avg Salary'].round(0)
            avg_by_city = avg_by_city.sort_values('Avg Salary', ascending=False)
            fig8 = px.bar(avg_by_city, x='City', y='Avg Salary',
              color='Avg Salary', color_continuous_scale='purples',
              title="Average Salary by City")
            fig8.update_traces(texttemplate='$%{y:,.0f}', textposition='outside')
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

# Tab 5 - Personal Fit Score
with tab5:
    st.subheader("🎯 Personal Fit Score")
    st.markdown("Enter your skills and see how you match against active job postings!")

    col1, col2 = st.columns([2, 1])
    with col1:
        user_skills_input = st.text_area(
            "Enter your skills (comma separated)",
            placeholder="e.g. Python, SQL, Snowflake, dbt, Power BI, Azure",
            height=100
        )
    with col2:
        target_role = st.selectbox(
            "Target Role",
            ["All Roles"] + list(active_df['search_role'].unique())
        )
        analyze_btn = st.button("🔍 Analyze My Fit", type="primary")

    if analyze_btn and user_skills_input:
        user_skills = [s.strip().lower() for s in user_skills_input.split(",") if s.strip()]

        if target_role != "All Roles":
            analysis_df = active_df[active_df['search_role'] == target_role]
        else:
            analysis_df = active_df

        total_jobs = len(analysis_df)

        if total_jobs == 0:
            st.warning("No jobs found for selected role.")
        else:
            matched_jobs = 0
            skill_presence = {}
            skill_gaps = {}

            for _, job in analysis_df.iterrows():
                desc = str(job.get('description', '')).lower()
                job_matched = any(skill in desc for skill in user_skills)
                if job_matched:
                    matched_jobs += 1

            for skill in SKILLS_LIST:
                jobs_needing_skill = analysis_df['description'].str.lower().str.contains(skill, na=False).sum()
                user_has_skill = any(skill.lower() in us for us in user_skills)

                if jobs_needing_skill > 0:
                    if user_has_skill:
                        skill_presence[skill.upper()] = int(jobs_needing_skill)
                    else:
                        skill_gaps[skill.upper()] = int(jobs_needing_skill)

            fit_score = round((matched_jobs / total_jobs) * 100, 1)

            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                if fit_score >= 70:
                    st.success(f"### 🎯 Fit Score: {fit_score}%")
                elif fit_score >= 40:
                    st.warning(f"### 🎯 Fit Score: {fit_score}%")
                else:
                    st.error(f"### 🎯 Fit Score: {fit_score}%")
            with col2:
                st.metric("Jobs You Match", f"{matched_jobs:,}")
            with col3:
                st.metric("Total Jobs Analyzed", f"{total_jobs:,}")

            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("✅ Skills You Have")
                if skill_presence:
                    presence_df = pd.DataFrame(
                        list(skill_presence.items()),
                        columns=['Skill', 'Jobs Requiring It']
                    ).sort_values('Jobs Requiring It', ascending=False)
                    fig_presence = px.bar(
                        presence_df, x='Jobs Requiring It', y='Skill',
                        orientation='h',
                        color='Jobs Requiring It',
                        color_continuous_scale='greens',
                        title="Your Skills in Demand"
                    )
                    st.plotly_chart(fig_presence, use_container_width=True)
                else:
                    st.info("None of your skills matched our tracked skills list.")

            with col2:
                st.subheader("❌ Skill Gaps")
                if skill_gaps:
                    gaps_df = pd.DataFrame(
                        list(skill_gaps.items()),
                        columns=['Skill', 'Jobs Requiring It']
                    ).sort_values('Jobs Requiring It', ascending=False)
                    fig_gaps = px.bar(
                        gaps_df.head(10), x='Jobs Requiring It', y='Skill',
                        orientation='h',
                        color='Jobs Requiring It',
                        color_continuous_scale='reds',
                        title="Top Skills You're Missing"
                    )
                    st.plotly_chart(fig_gaps, use_container_width=True)

                    st.subheader("🚀 Top 3 Skills to Learn Next")
                    top_gaps = gaps_df.head(3)
                    for i, (_, row) in enumerate(top_gaps.iterrows(), 1):
                        st.markdown(f"**{i}. {row['Skill']}** — appears in **{row['Jobs Requiring It']:,}** job postings")
                else:
                    st.success("🎉 You have all the tracked skills!")

            if target_role == "All Roles":
                st.divider()
                st.subheader("📊 Your Fit Score by Role")
                role_scores = []
                for role in active_df['search_role'].unique():
                    role_df = active_df[active_df['search_role'] == role]
                    role_total = len(role_df)
                    role_matched = 0
                    for _, job in role_df.iterrows():
                        desc = str(job.get('description', '')).lower()
                        if any(skill in desc for skill in user_skills):
                            role_matched += 1
                    role_score = round((role_matched / role_total) * 100, 1) if role_total > 0 else 0
                    role_scores.append({'Role': role, 'Fit Score %': role_score, 'Matching Jobs': role_matched})

                role_scores_df = pd.DataFrame(role_scores).sort_values('Fit Score %', ascending=False)
                fig_roles = px.bar(
                    role_scores_df, x='Role', y='Fit Score %',
                    color='Fit Score %',
                    color_continuous_scale='blues',
                    title="Your Fit Score by Role"
                )
                st.plotly_chart(fig_roles, use_container_width=True)

    elif analyze_btn and not user_skills_input:
        st.warning("Please enter at least one skill!")

# Tab 6 - Resume Gap Analyzer
with tab6:
    st.subheader("📄 Resume Gap Analyzer")
    st.markdown("Analyze your resume against the entire job market or a specific job description.")

    mode = st.radio(
        "Choose analysis mode:",
        ["🌍 Compare against entire job market", "🎯 Compare against a specific job description"],
        horizontal=True
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Your Resume")
        resume_input_mode = st.radio(
            "How do you want to add your resume?",
            ["📁 Upload PDF", "✏️ Paste Text"],
            horizontal=True,
            key="resume_input_mode"
        )

        resume_text = ""

        if resume_input_mode == "📁 Upload PDF":
            uploaded_resume = st.file_uploader(
                "Upload your resume (PDF)",
                type=["pdf"],
                key="resume_upload"
            )
            if uploaded_resume:
                try:
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_resume.read()))
                    resume_text = ""
                    for page in pdf_reader.pages:
                        resume_text += page.extract_text()
                    st.success(f"✅ Resume uploaded — {len(pdf_reader.pages)} page(s) detected")
                    with st.expander("Preview extracted text"):
                        st.text(resume_text[:500] + "...")
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
        else:
            resume_text = st.text_area(
                "Paste your resume text",
                placeholder="Paste your full resume text here...",
                height=300
            )

    with col2:
        if mode == "🎯 Compare against a specific job description":
            st.markdown("#### 💼 Paste Job Description")
            jd_text = st.text_area(
                "Job description",
                placeholder="Paste the job description here...",
                height=300
            )
        else:
            st.markdown("#### 🎯 Target Role")
            target_role_gap = st.selectbox(
                "Which role are you targeting?",
                ["All Roles"] + list(active_df['search_role'].unique()),
                key="gap_role"
            )
            st.markdown("#### 🏙️ Target City")
            target_city_gap = st.selectbox(
                "Which city are you targeting?",
                ["All Cities"] + list(active_df['search_location'].unique()),
                key="gap_city"
            )

    analyze_gap_btn = st.button("🔍 Analyze Resume Gaps", type="primary")

    if analyze_gap_btn and resume_text:
        resume_lower = resume_text.lower()

        with st.spinner("Analyzing your resume..."):

            if mode == "🎯 Compare against a specific job description":
                if not jd_text:
                    st.warning("Please paste a job description!")
                else:
                    jd_lower = jd_text.lower()
                    jd_skills = [s for s in SKILLS_LIST if s.lower() in jd_lower]
                    matched_skills = [s for s in jd_skills if s.lower() in resume_lower]
                    missing_skills = [s for s in jd_skills if s.lower() not in resume_lower]
                    match_pct = round(len(matched_skills) / len(jd_skills) * 100, 1) if jd_skills else 0

                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if match_pct >= 70:
                            st.success(f"### ✅ Match Score: {match_pct}%")
                        elif match_pct >= 40:
                            st.warning(f"### ⚠️ Match Score: {match_pct}%")
                        else:
                            st.error(f"### ❌ Match Score: {match_pct}%")
                    with col2:
                        st.metric("Skills Matched", f"{len(matched_skills)}/{len(jd_skills)}")
                    with col3:
                        st.metric("Skills Missing", len(missing_skills))

                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("✅ Skills You Have")
                        for skill in matched_skills:
                            st.success(f"✅ {skill.upper()}")
                        if not matched_skills:
                            st.info("No matching skills found")
                    with col2:
                        st.subheader("❌ Skills You're Missing")
                        for skill in missing_skills:
                            st.error(f"❌ {skill.upper()}")
                        if not missing_skills:
                            st.success("🎉 You have all required skills!")

                    st.divider()
                    st.subheader("🤖 AI Career Advice")
                    with st.spinner("Getting AI insights..."):
                        from ai.chatbot import answer_question
                        prompt = f"""
                        A candidate has these skills: {', '.join(matched_skills)}
                        They are missing these skills from the job description: {', '.join(missing_skills)}
                        The job description is: {jd_text[:500]}
                        Give them:
                        1. Honest assessment of their chances
                        2. Top 3 skills to learn first and why
                        3. How long it would take to be ready
                        4. One actionable tip to improve their application now
                        """
                        advice = answer_question(prompt)
                        st.markdown(advice)

            else:
                if target_role_gap != "All Roles":
                    analysis_df = active_df[active_df['search_role'] == target_role_gap]
                else:
                    analysis_df = active_df

                if target_city_gap != "All Cities":
                    analysis_df = analysis_df[analysis_df['search_location'] == target_city_gap]

                total = len(analysis_df)
                market_skills = {}
                for skill in SKILLS_LIST:
                    count = analysis_df['description'].str.lower().str.contains(skill, na=False).sum()
                    if count > 0:
                        market_skills[skill] = int(count)

                you_have = {s: c for s, c in market_skills.items() if s.lower() in resume_lower}
                you_missing = {s: c for s, c in market_skills.items() if s.lower() not in resume_lower}
                you_have = dict(sorted(you_have.items(), key=lambda x: x[1], reverse=True))
                you_missing = dict(sorted(you_missing.items(), key=lambda x: x[1], reverse=True))
                coverage = round(len(you_have) / len(market_skills) * 100, 1) if market_skills else 0

                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    if coverage >= 70:
                        st.success(f"### ✅ Market Coverage: {coverage}%")
                    elif coverage >= 40:
                        st.warning(f"### ⚠️ Market Coverage: {coverage}%")
                    else:
                        st.error(f"### ❌ Market Coverage: {coverage}%")
                with col2:
                    st.metric("Skills You Have", f"{len(you_have)}/{len(market_skills)}")
                with col3:
                    st.metric("Jobs Analyzed", f"{total:,}")

                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("✅ Your Skills in Demand")
                    if you_have:
                        have_df = pd.DataFrame(
                            list(you_have.items()),
                            columns=['Skill', 'Jobs Requiring It']
                        )
                        fig_have = px.bar(
                            have_df, x='Jobs Requiring It', y='Skill',
                            orientation='h',
                            color='Jobs Requiring It',
                            color_continuous_scale='greens',
                            title="Your Skills vs Market Demand"
                        )
                        st.plotly_chart(fig_have, use_container_width=True)

                with col2:
                    st.subheader("❌ Your Skill Gaps")
                    if you_missing:
                        missing_df = pd.DataFrame(
                            list(you_missing.items()),
                            columns=['Skill', 'Jobs Requiring It']
                        ).head(10)
                        fig_missing = px.bar(
                            missing_df, x='Jobs Requiring It', y='Skill',
                            orientation='h',
                            color='Jobs Requiring It',
                            color_continuous_scale='reds',
                            title="Top Skills You're Missing"
                        )
                        st.plotly_chart(fig_missing, use_container_width=True)

                st.divider()
                st.subheader("🚀 Top 3 Skills to Learn Next")
                top_missing = list(you_missing.items())[:3]
                for i, (skill, count) in enumerate(top_missing, 1):
                    pct = round(count / total * 100, 1)
                    st.markdown(f"**{i}. {skill.upper()}** — needed in **{count:,} jobs** ({pct}% of postings)")

                st.divider()
                st.subheader("🤖 AI Career Advice")
                with st.spinner("Getting personalized advice..."):
                    from ai.chatbot import answer_question
                    prompt = f"""
                    A candidate targeting {target_role_gap} roles in {target_city_gap} has these skills: {', '.join(you_have.keys())}
                    They are missing: {', '.join(list(you_missing.keys())[:5])}
                    Give them:
                    1. Honest assessment of their market readiness
                    2. Top 3 skills to learn first and why
                    3. Realistic timeline to be job-ready
                    4. One specific actionable tip for their job search right now
                    """
                    advice = answer_question(prompt)
                    st.markdown(advice)

    elif analyze_gap_btn and not resume_text:
        st.warning("Please upload or paste your resume first!")

# Tab 7 - Job Alerts
with tab7:
    st.subheader("🔔 Job Alerts")
    st.markdown("Get daily email alerts when new jobs matching your preferences are posted!")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📧 Subscribe to Job Alerts")
        alert_email = st.text_input(
            "Your email address",
            placeholder="you@email.com"
        )
        alert_role = st.selectbox(
            "Role you're interested in",
            list(active_df['search_role'].unique()),
            key="alert_role"
        )
        alert_city = st.selectbox(
            "City you're targeting",
            list(active_df['search_location'].unique()),
            key="alert_city"
        )
        subscribe_btn = st.button("🔔 Subscribe to Alerts", type="primary")

        if subscribe_btn:
            if not alert_email:
                st.warning("Please enter your email!")
            else:
                from ingestion.alerts import save_alert_subscription
                success, message = save_alert_subscription(
                    alert_email, alert_role, alert_city
                )
                if success:
                    st.success(f"✅ {message} You'll receive daily alerts for **{alert_role}** jobs in **{alert_city}**!")
                else:
                    st.warning(f"⚠️ {message}")

    with col2:
        st.markdown("#### ℹ️ How It Works")
        st.markdown("""
        **1. Subscribe** — Enter your email, target role and city

        **2. Daily Pipeline Runs** — Every morning at 8am our pipeline fetches fresh job postings

        **3. You Get Notified** — If new jobs match your preferences, you get an email with:
        - Job title and company
        - Location and salary range
        - Direct link to apply

        **4. Stay Ahead** — Get notified before other candidates even see the posting!
        """)

        st.info("📬 Emails are sent daily at 8am EST when new matching jobs are found.")