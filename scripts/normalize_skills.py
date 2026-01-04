import json
import os
import re

INPUT_FILE = "processed_data/job_skills.jsonl"
OUTPUT_FILE = "processed_data/job_skills_normalized.jsonl"

# =========================
# SKILL ALIAS MAP
# =========================

SKILL_ALIASES = {
    # Programming languages
    "go": "Golang",
    "golang": "Golang",
    "python3": "Python",
    # Frontend
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vuejs": "Vue.js",
    # Backend / Platform
    ".net": ".NET",
    ".net core": ".NET Core",
    "nodejs": "Node.js",
    # DevOps
    "gitlab": "GitLab",
    "github": "GitHub",
    "git ci/cd": "CI/CD",
    # Testing
    "unit tests": "Unit Testing",
    "unit testing": "Unit Testing",
    "e2e testing": "E2E Testing",
    "end-to-end testing": "E2E Testing",
    # Data / AI
    "machine learning": "Machine Learning",
    "artificial intelligence": "AI",
    "large language models": "LLM",
    "gpt": "GPT",
    # Cloud
    "amazon web services": "AWS",
    "google cloud platform": "GCP",
}

# =========================
# NORMALIZATION LOGIC
# =========================


def normalize_skill(skill: str) -> str:
    s = skill.strip()

    # remove extra spaces
    s = re.sub(r"\s+", " ", s)

    key = s.lower()

    # alias mapping
    if key in SKILL_ALIASES:
        return SKILL_ALIASES[key]

    # standard casing
    return s.title() if s.islower() else s


def normalize_skills(skills: list) -> list:
    normalized = []
    seen = set()

    for skill in skills:
        if not skill or not isinstance(skill, str):
            continue

        s = normalize_skill(skill)

        key = s.lower()
        if key not in seen:
            normalized.append(s)
            seen.add(key)

    return normalized


# =========================
# MAIN
# =========================


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    count = 0

    with open(INPUT_FILE, encoding="utf-8") as fin, open(
        OUTPUT_FILE, "w", encoding="utf-8"
    ) as fout:

        for line in fin:
            job = json.loads(line)

            skills = job.get("skills", [])
            job["skills"] = normalize_skills(skills)

            fout.write(json.dumps(job, ensure_ascii=False) + "\n")
            count += 1

    print("✅ Skill normalization done")
    print(f"   Jobs processed: {count}")
    print(f"   Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
