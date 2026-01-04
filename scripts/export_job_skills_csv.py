import json
import csv

INPUT_FILE = "processed_data/job_skills_flat.jsonl"
OUTPUT_FILE = "processed_data/job_skills_flat.csv"


FIELDS = ["platform", "job_url", "title", "company", "location", "skill"]


def export_csv():
    rows = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, open(
        OUTPUT_FILE, "w", encoding="utf-8", newline=""
    ) as fout:

        writer = csv.DictWriter(fout, fieldnames=FIELDS)
        writer.writeheader()

        for line in fin:
            if not line.strip():
                continue

            item = json.loads(line)

            writer.writerow(
                {
                    "platform": item.get("platform"),
                    "job_url": item.get("job_url"),
                    "title": item.get("title"),
                    "company": item.get("company"),
                    "location": item.get("location"),
                    "skill": item.get("skill"),
                }
            )

            rows += 1

    print(f"✅ CSV exported")
    print(f"• Rows written: {rows}")
    print(f"• File: {OUTPUT_FILE}")


if __name__ == "__main__":
    export_csv()
