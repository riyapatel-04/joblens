import os
import smtplib
import snowflake.connector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )

def get_new_jobs(role: str, location: str, hours: int = 24):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    query = f"""
        SELECT TITLE, COMPANY, LOCATION, REDIRECT_URL, SALARY_MIN, SALARY_MAX
        FROM RAW_JOBS
        WHERE STATUS = 'active'
        AND SEARCH_ROLE ILIKE '%{role}%'
        AND SEARCH_LOCATION ILIKE '%{location}%'
        AND INGESTED_AT >= '{cutoff}'
        LIMIT 10
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def send_alert_email(to_email: str, role: str, location: str, jobs: list):
    if not jobs:
        return False

    jobs_html = ""
    for job in jobs:
        title, company, loc, url, sal_min, sal_max = job
        salary = ""
        if sal_min and sal_max:
            salary = f"<span style='color: #2e7d32;'>💰 ${int(sal_min):,} - ${int(sal_max):,}</span>"

        jobs_html += f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 10px 0;">
            <h3 style="color: #1f77b4; margin: 0 0 5px 0;">{title}</h3>
            <p style="margin: 3px 0; color: #555;">🏢 {company}</p>
            <p style="margin: 3px 0; color: #555;">📍 {loc}</p>
            {f'<p style="margin: 3px 0;">{salary}</p>' if salary else ''}
            <a href="{url}" style="display: inline-block; margin-top: 8px; padding: 6px 14px; background: #1f77b4; color: white; border-radius: 4px; text-decoration: none; font-size: 0.85rem;">View Job →</a>
        </div>
        """

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1f77b4; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 1.5rem;">🔍 JobLens Daily Alert</h1>
            <p style="color: #e0e0e0; margin: 5px 0 0 0;">Your daily job market update</p>
        </div>
        <div style="padding: 20px; background: #f9f9f9;">
            <p style="color: #444;">Hi! Here are <strong>{len(jobs)} new {role} jobs</strong> in <strong>{location}</strong>:</p>
            {jobs_html}
        </div>
        <div style="padding: 15px; background: #eee; border-radius: 0 0 8px 8px; text-align: center;">
            <p style="margin: 0; color: #888; font-size: 0.8rem;">Powered by JobLens — Job Market Intelligence</p>
        </div>
    </div>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔍 JobLens Alert: {len(jobs)} new {role} jobs in {location}!"
        msg['From'] = os.getenv("GMAIL_USER")
        msg['To'] = to_email

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(
                os.getenv("GMAIL_USER"),
                os.getenv("GMAIL_APP_PASSWORD")
            )
            server.sendmail(
                os.getenv("GMAIL_USER"),
                to_email,
                msg.as_string()
            )

        print(f"✅ Alert sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def save_alert_subscription(email: str, role: str, location: str):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS JOB_ALERTS (
            EMAIL VARCHAR,
            ROLE VARCHAR,
            LOCATION VARCHAR,
            CREATED_AT VARCHAR,
            IS_ACTIVE BOOLEAN DEFAULT TRUE
        )
    """)

    cursor.execute(f"""
        SELECT COUNT(*) FROM JOB_ALERTS
        WHERE EMAIL = '{email}'
        AND ROLE = '{role}'
        AND LOCATION = '{location}'
        AND IS_ACTIVE = TRUE
    """)

    count = cursor.fetchone()[0]
    if count > 0:
        cursor.close()
        conn.close()
        return False, "Already subscribed!"

    cursor.execute(f"""
        INSERT INTO JOB_ALERTS (EMAIL, ROLE, LOCATION, CREATED_AT, IS_ACTIVE)
        VALUES ('{email}', '{role}', '{location}', '{datetime.utcnow().isoformat()}', TRUE)
    """)
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Subscribed successfully!"

def run_daily_alerts():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EMAIL, ROLE, LOCATION FROM JOB_ALERTS WHERE IS_ACTIVE = TRUE")
    subscribers = cursor.fetchall()
    cursor.close()
    conn.close()

    print(f"📧 Found {len(subscribers)} active subscribers")

    sent = 0
    for email, role, location in subscribers:
        jobs = get_new_jobs(role, location, hours=24)
        print(f"Found {len(jobs)} new jobs")
        if jobs:
            success = send_alert_email(email, role, location, jobs)
            if success:
                sent += 1
        else:
            print(f"⏭️ No new jobs for {email}")

    print(f"📧 Total alerts sent: {sent}")

if __name__ == "__main__":
    run_daily_alerts()