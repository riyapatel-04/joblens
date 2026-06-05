import feedparser
import re
from dotenv import load_dotenv

load_dotenv()

# Curated list of well-known recently funded data/AI startups
KNOWN_FUNDED_STARTUPS = [
    {"company": "Anthropic", "amount": "$2.75B", "round": "Series E", "domain": "AI/LLM", "link": "https://techcrunch.com/2024/03/04/anthropic-raises-another-2-75-billion/"},
    {"company": "Mistral AI", "amount": "$1.1B", "round": "Series B", "domain": "AI/LLM", "link": "https://techcrunch.com/2024/06/11/mistral-ai-raises-640-million/"},
    {"company": "Groq", "amount": "$640M", "round": "Series D", "domain": "AI Infrastructure", "link": "https://techcrunch.com/2024/08/05/groq-raises-640-million/"},
    {"company": "Databricks", "amount": "$500M", "round": "Series J", "domain": "Data Engineering", "link": "https://techcrunch.com/2024/09/24/databricks-raises-500m/"},
    {"company": "Cohere", "amount": "$270M", "round": "Series C", "domain": "AI/NLP", "link": "https://techcrunch.com/2024/07/22/cohere-raises-270-million/"},
    {"company": "Scale AI", "amount": "$1B", "round": "Series F", "domain": "AI Data", "link": "https://techcrunch.com/2024/05/21/scale-ai-raises-1-billion/"},
    {"company": "Weights & Biases", "amount": "$200M", "round": "Series C", "domain": "MLOps", "link": "https://techcrunch.com/2023/08/01/weights-biases-raises-200m/"},
    {"company": "Astronomer", "amount": "$213M", "round": "Series C", "domain": "Data Engineering", "link": "https://techcrunch.com/2022/03/28/astronomer-raises-213-million/"},
    {"company": "Monte Carlo", "amount": "$135M", "round": "Series D", "domain": "Data Observability", "link": "https://techcrunch.com/2022/11/08/monte-carlo-raises-135-million/"},
    {"company": "Fivetran", "amount": "$565M", "round": "Series D", "domain": "Data Integration", "link": "https://techcrunch.com/2021/09/14/fivetran-raises-565-million/"},
    {"company": "dbt Labs", "amount": "$222M", "round": "Series D", "domain": "Analytics Engineering", "link": "https://techcrunch.com/2022/02/24/dbt-labs-raises-222-million/"},
    {"company": "Starburst", "amount": "$250M", "round": "Series D", "domain": "Data Analytics", "link": "https://techcrunch.com/2022/01/19/starburst-raises-250-million/"},
    {"company": "Airbyte", "amount": "$150M", "round": "Series B", "domain": "Data Integration", "link": "https://techcrunch.com/2022/12/06/airbyte-raises-150-million/"},
    {"company": "Hightouch", "amount": "$80M", "round": "Series B", "domain": "Data Activation", "link": "https://techcrunch.com/2022/07/13/hightouch-raises-80-million/"},
    {"company": "Hex Technologies", "amount": "$52M", "round": "Series B", "domain": "Data Analytics", "link": "https://techcrunch.com/2022/01/18/hex-raises-52-million/"},
]

FUNDING_FEEDS = [
    "https://techcrunch.com/category/venture/feed/",
]

def fetch_funded_startups(max_results: int = 20):
    """Return curated funded startups + latest from TechCrunch."""
    startups = []

    # Add curated startups first
    for s in KNOWN_FUNDED_STARTUPS:
        startups.append({
            "company": s["company"],
            "amount": s["amount"],
            "round": s["round"],
            "domain": s["domain"],
            "is_data_related": True,
            "link": s["link"],
            "summary": f"{s['company']} is a {s['domain']} company that recently raised {s['amount']}.",
            "published": "Recently"
        })

    # Try to get fresh ones from TechCrunch
    try:
        feed = feedparser.parse(FUNDING_FEEDS[0])
        for entry in feed.entries[:10]:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            combined = f"{title} {summary}".lower()

            funding_keywords = ["raises", "raised", "series a", "series b", "series c", "seed round"]
            data_keywords = ["data", "ai", "analytics", "machine learning", "cloud", "saas"]

            is_funding = any(kw in combined for kw in funding_keywords)
            is_data = any(kw in combined for kw in data_keywords)

            if is_funding and is_data:
                # Extract company name — first word(s) before "raises"
                company = title.split(" raises")[0].split(" Raises")[0]
                company = company.split(",")[0].split(" gets")[0].strip()
                # Only add if company name looks clean (less than 4 words)
                if len(company.split()) <= 4:
                    amount = _parse_amount(f"{title} {summary}")
                    startups.append({
                        "company": company,
                        "amount": amount,
                        "round": _parse_round(combined),
                        "domain": "Tech/AI",
                        "is_data_related": True,
                        "link": link,
                        "summary": summary[:200],
                        "published": entry.get('published', '')
                    })
    except Exception as e:
        print(f"RSS fetch error: {e}")

    return startups[:max_results]

def _parse_amount(text):
    patterns = [
        (r'\$(\d+(?:\.\d+)?)\s*billion', 'B'),
        (r'\$(\d+(?:\.\d+)?)\s*million', 'M'),
        (r'\$(\d+(?:\.\d+)?)B', 'B'),
        (r'\$(\d+(?:\.\d+)?)M', 'M'),
    ]
    for pattern, suffix in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"${match.group(1)}{suffix}"
    return "Amount Not Disclosed"

def _parse_round(text):
    rounds = ["Series D", "Series C", "Series B", "Series A", "Seed", "Pre-Seed"]
    for r in rounds:
        if r.lower() in text.lower():
            return r
    return "Funding Round"

def match_startups_with_jobs(startups: list, active_df):
    """Cross-reference funded startups with job postings."""
    matched = []
    for startup in startups:
        company_name = startup['company'].lower()
        matching_jobs = active_df[
            active_df['company'].str.lower().str.contains(
                company_name[:8], na=False
            )
        ]
        startup['open_jobs'] = len(matching_jobs)
        startup['job_roles'] = list(matching_jobs['search_role'].unique()) if len(matching_jobs) > 0 else []
        matched.append(startup)
    return matched

if __name__ == "__main__":
    startups = fetch_funded_startups()
    print(f"Found {len(startups)} funded startups")
    for s in startups[:10]:
        print(f"- {s['company']} | {s['amount']} | {s['round']} | {s['domain']}")