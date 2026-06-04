from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import json

class JobPosting(BaseModel):
    id: str
    title: str
    company: Optional[str] = "Unknown"
    location: Optional[str] = "Unknown"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = "Unknown"
    contract_type: Optional[str] = "Unknown"
    created: Optional[str] = None
    redirect_url: Optional[str] = None
    search_role: str
    search_location: str
    ingested_at: str

    @field_validator("title")
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("company", mode="before")
    def extract_company(cls, v):
        if isinstance(v, dict):
            return v.get("display_name", "Unknown")
        return v or "Unknown"

    @field_validator("location", mode="before")
    def extract_location(cls, v):
        if isinstance(v, dict):
            return v.get("display_name", "Unknown")
        return v or "Unknown"

    @field_validator("category", mode="before")
    def extract_category(cls, v):
        if isinstance(v, dict):
            return v.get("label", "Unknown")
        return v or "Unknown"


def validate_jobs(raw_jobs: list) -> tuple:
    valid = []
    failed = 0
    for job in raw_jobs:
        try:
            validated = JobPosting(
                id=job.get("id", ""),
                title=job.get("title", ""),
                company=job.get("company", "Unknown"),
                location=job.get("location", "Unknown"),
                salary_min=job.get("salary_min"),
                salary_max=job.get("salary_max"),
                description=job.get("description", ""),
                category=job.get("category", "Unknown"),
                contract_type=job.get("contract_type", "Unknown"),
                created=job.get("created", ""),
                redirect_url=job.get("redirect_url", ""),
                search_role=job.get("search_role", ""),
                search_location=job.get("search_location", ""),
                ingested_at=job.get("ingested_at", "")
            )
            valid.append(validated.model_dump())
        except Exception as e:
            failed += 1
    print(f"✅ Valid jobs: {len(valid)}")
    print(f"❌ Failed validation: {failed}")
    print(f"📊 Success rate: {round(len(valid)/(len(valid)+failed)*100, 2)}%")
    return valid, failed


if __name__ == "__main__":
    with open("raw_jobs.json", "r") as f:
        raw_jobs = json.load(f)
    print(f"📥 Loaded {len(raw_jobs)} raw jobs")
    valid_jobs, failed = validate_jobs(raw_jobs)
    with open("validated_jobs.json", "w") as f:
        json.dump(valid_jobs, f, indent=2)
    print("✅ Saved to validated_jobs.json")