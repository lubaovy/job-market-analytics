import json

INPUT_FILE = "processed_data/normalized_jobs_with_skills.jsonl"
OUTPUT_FILE = "processed_data/job_skills_flat.jsonl"


def flatten_jobs():
    total_jobs = 0
    total_rows = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as fout:

        for line in fin:
            if not line.strip():
                continue

            job = json.loads(line)
            total_jobs += 1

            skills = job.get("skills") or []

            # skip job không có skill
            if not skills:
                continue

            for skill in skills:
                row = {
                    "platform": job.get("platform"),
                    "job_url": job.get("job_url"),
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "skill": skill.strip(),
                }

                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                total_rows += 1

    print(f"✅ Flatten done")
    print(f"• Jobs processed: {total_jobs}")
    print(f"• Skill rows created: {total_rows}")


if __name__ == "__main__":
    flatten_jobs()
