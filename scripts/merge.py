import json

normalized_file = "processed_data/normalized_jobs.jsonl"
skills_file = "processed_data/job_skills_normalized.jsonl"
output_file = "processed_data/normalized_jobs_with_skills.jsonl"

with open(normalized_file, encoding="utf-8") as f1, open(
    skills_file, encoding="utf-8"
) as f2, open(output_file, "w", encoding="utf-8") as out:

    for idx, (line_job, line_skill) in enumerate(zip(f1, f2), start=1):
        job = json.loads(line_job)
        skill_data = json.loads(line_skill)

        job["skills"] = skill_data.get("skills", [])

        out.write(json.dumps(job, ensure_ascii=False) + "\n")

print("✅ Merge xong, giữ đúng thứ tự dòng")
