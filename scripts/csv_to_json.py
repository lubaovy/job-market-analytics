# scripts/csv_to_dashboard_json.py
import csv, json

INPUT = "processed_data/job_skills_flat.csv"
OUTPUT = "dashboard/src/data/jobs.json"

jobs = {}

with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row["platform"], row["title"], row["location"])
        if key not in jobs:
            jobs[key] = {
                "platform": row["platform"],
                "title": row["title"],
                "location": row["location"],
                "skills": [],
            }
        jobs[key]["skills"].append(row["skill"])

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(list(jobs.values()), f, ensure_ascii=False, indent=2)

print("Done")
