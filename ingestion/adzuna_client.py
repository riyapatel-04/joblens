import requests
import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search"

ROLES = [
    "data engineer",
    "data analyst",
    "analytics engineer",
    "BI developer",
    "machine learning engineer"
]

LOCATIONS = [
    # Northeast
    "boston", "new york", "philadelphia", 
    "washington dc", "baltimore", "pittsburgh",

    # Southeast
    "atlanta", "miami", "charlotte", "raleigh", 
    "orlando", "nashville", "tampa",

    # Midwest
    "chicago", "detroit", "columbus", 
    "indianapolis", "minneapolis", "kansas city",

    # Southwest
    "dallas", "austin", "houston", 
    "phoenix", "denver", "san antonio",

    # West Coast
    "san francisco", "los angeles", "seattle", 
    "san diego", "portland"
]

def fetch_jobs(role: str, location: str, page: int = 1, results_per_page: int = 50):
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": role,
        "where": location,
        "content-type": "application/json"
    }
    response = requests.get(f"{BASE_URL}/{page}", params=params)
    response.raise_for_status()
    return response.json()

def fetch_all_jobs():
    all_jobs = []
    for role in ROLES:
        for location in LOCATIONS:
            try:
                data = fetch_jobs(role, location)
                jobs = data.get("results", [])
                for job in jobs:
                    job["search_role"] = role
                    job["search_location"] = location
                    job["ingested_at"] = datetime.now(timezone.utc).isoformat()
                all_jobs.extend(jobs)
                print(f"✅ {role} | {location} → {len(jobs)} jobs")
            except Exception as e:
                print(f"❌ {role} | {location} → {e}")
    return all_jobs

if __name__ == "__main__":
    jobs = fetch_all_jobs()
    print(f"\nTotal jobs fetched: {len(jobs)}")
    with open("raw_jobs.json", "w") as f:
        json.dump(jobs, f, indent=2)
    print("✅ Saved to raw_jobs.json")