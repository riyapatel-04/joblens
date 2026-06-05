import snowflake.connector
import os
import json
from datetime import datetime, timezone
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

def load_jobs_to_snowflake(validated_jobs: list):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Get all current active IDs from Snowflake
    cursor.execute("SELECT ID FROM RAW_JOBS WHERE STATUS = 'active'")
    existing_active_ids = set(row[0] for row in cursor.fetchall())
    print(f"📊 Currently active jobs in Snowflake: {len(existing_active_ids)}")

    # Get IDs from today's fresh fetch
    fresh_ids = set(job.get("id", "") for job in validated_jobs)
    print(f"📥 Fresh jobs fetched today: {len(fresh_ids)}")

    # Jobs in Snowflake but NOT in today's fetch = expired
    expired_ids = existing_active_ids - fresh_ids
    print(f"❌ Jobs to mark as expired: {len(expired_ids)}")

    # Mark expired jobs
    if expired_ids:
        expired_list = "', '".join(expired_ids)
        cursor.execute(f"""
            UPDATE RAW_JOBS 
            SET STATUS = 'expired' 
            WHERE ID IN ('{expired_list}')
        """)
        print(f"✅ Marked {len(expired_ids)} jobs as expired")

    # Get ALL existing IDs to avoid duplicates
    cursor.execute("SELECT ID FROM RAW_JOBS")
    all_existing_ids = set(row[0] for row in cursor.fetchall())

    # Insert new jobs
    insert_query = """
        INSERT INTO RAW_JOBS (
            ID, TITLE, COMPANY, LOCATION,
            SALARY_MIN, SALARY_MAX, DESCRIPTION,
            CATEGORY, CONTRACT_TYPE, CREATED,
            REDIRECT_URL, SEARCH_ROLE, SEARCH_LOCATION, 
            INGESTED_AT, STATUS, LAST_SEEN_AT
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """

    # Update last_seen_at for existing active jobs
    if fresh_ids:
        fresh_list = "', '".join(fresh_ids)
        cursor.execute(f"""
            UPDATE RAW_JOBS 
            SET LAST_SEEN_AT = '{now}',
                STATUS = 'active'
            WHERE ID IN ('{fresh_list}')
        """)

    # Insert brand new jobs
    batch = []
    skipped = 0
    for job in validated_jobs:
        if job.get("id") in all_existing_ids:
            skipped += 1
            continue
        batch.append((
            job.get("id", ""),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("salary_min"),
            job.get("salary_max"),
            job.get("description", ""),
            job.get("category", ""),
            job.get("contract_type", ""),
            job.get("created", ""),
            job.get("redirect_url", ""),
            job.get("search_role", ""),
            job.get("search_location", ""),
            now,
            "active",
            now
        ))

    if batch:
        cursor.executemany(insert_query, batch)
        print(f"✅ Loaded {len(batch)} NEW jobs into Snowflake")
    else:
        print("⏭️ No new jobs to load today")

    print(f"⏭️ Skipped {skipped} existing jobs")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    with open("validated_jobs.json", "r") as f:
        validated_jobs = json.load(f)
    print(f"📤 Processing {len(validated_jobs)} jobs...")
    load_jobs_to_snowflake(validated_jobs)
    print("✅ Done!")