import json
from collections import Counter

INPUT_FILE = "processed_data/normalized_jobs.jsonl"
OUTPUT_FILE = "processed_data/skill_frequency.json"

SKILLS = [
    "python",
    "java",
    "javascript",
    "react",
    "sql",
    "aws",
    "docker",
    "kubernetes",
    "machine learning",
    "data science",
    "devops",
    "tester",
    "qa",
]


def normalize_text(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        texts = []
        for item in value:
            if isinstance(item, dict):
                texts.extend(str(v) for v in item.values() if v)
            else:
                texts.append(str(item))
        return " ".join(texts)

    if isinstance(value, dict):
        return " ".join(str(v) for v in value.values() if v)

    return str(value)


def extract_skills(text):
    text = text.lower()
    return [s for s in SKILLS if s in text]


def main():
    counter = Counter()

    with open(INPUT_FILE, encoding="utf-8") as f:
        for line in f:
            job = json.loads(line)

            text = " ".join(
                [
                    normalize_text(job.get("description")),
                    normalize_text(job.get("requirements")),
                    normalize_text(job.get("benefits")),
                ]
            )

            skills = extract_skills(text)
            counter.update(skills)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(counter.most_common(), f, ensure_ascii=False, indent=2)

    print("✅ Skill extraction completed")


if __name__ == "__main__":
    main()
