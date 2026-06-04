import snowflake.connector
import os
import json
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

    insert_query = """
        INSERT INTO RAW_JOBS (
            ID, TITLE, COMPANY, LOCATION,
            SALARY_MIN, SALARY_MAX, DESCRIPTION,
            CATEGORY, CONTRACT_TYPE, CREATED,
            REDIRECT_URL, SEARCH_ROLE, SEARCH_LOCATION, INGESTED_AT
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    batch = []
    for job in validated_jobs:
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
            job.get("ingested_at", "")
        ))

    cursor.executemany(insert_query, batch)
    conn.commit()
    print(f"✅ Loaded {len(batch)} jobs into Snowflake RAW_JOBS table")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    with open("validated_jobs.json", "r") as f:
        validated_jobs = json.load(f)
    print(f"📤 Loading {len(validated_jobs)} jobs into Snowflake...")
    load_jobs_to_snowflake(validated_jobs)
    print("✅ Done!")