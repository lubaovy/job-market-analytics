import json
import os
import hashlib
import time
from dotenv import load_dotenv
from openai import OpenAI

# =========================
# CONFIG
# =========================

INPUT_FILE = "processed_data/normalized_jobs.jsonl"
OUTPUT_FILE = "processed_data/job_skills.jsonl"
CACHE_FILE = "processed_data/skill_cache.json"

MODEL_NAME = "gpt-4.1-mini"
MAX_AI_CALLS = float("inf")
SLEEP_BETWEEN_CALLS = 1

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# PROMPT
# =========================

SYSTEM_PROMPT = """
You are a technical skill extraction AI.

Extract ONLY technical / professional skills explicitly mentioned.
DO NOT include soft skills, responsibilities, benefits, or personality traits.
DO NOT guess.

Return JSON array ONLY.
"""

# =========================
# HELPERS
# =========================


def build_text(job: dict) -> str:
    """
    Build text STRICTLY based on normalized_job schema
    """
    parts = []

    def add(title, content):
        if content:
            parts.append(f"## {title}")
            parts.append(str(content))

    add("Job Title", job.get("title"))
    add("Job Description", job.get("description"))

    reqs = job.get("requirements")
    if isinstance(reqs, list):
        add("Requirements", "\n".join(reqs))

    return "\n\n".join(parts)


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def call_ai_extract(text: str) -> list:
    prompt = f"""
Extract technical skills from the text below.

Rules:
- Extract tools, technologies, platforms, programming languages, frameworks
- Ignore soft skills
- Ignore responsibilities
- Normalize names (Python3 → Python, JS → JavaScript)

Text:
{text}

Return JSON array only:
["Skill A", "Skill B"]
"""

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    try:
        data = json.loads(resp.choices[0].message.content)
        return data if isinstance(data, list) else []
    except Exception:
        return []


# =========================
# MAIN
# =========================


def main():
    cache = load_cache()
    ai_calls = 0

    with open(INPUT_FILE, encoding="utf-8") as f:
        jobs = [json.loads(line) for line in f]

    results = []

    for job in jobs:
        text = build_text(job)
        if not text.strip():
            continue

        h = text_hash(text)

        if h in cache:
            skills = cache[h]
        else:

            skills = call_ai_extract(text)
            cache[h] = skills
            save_cache(cache)

            ai_calls += 1
            time.sleep(SLEEP_BETWEEN_CALLS)

        results.append(
            {
                # "job_url": job.get("job_url"),
                "title": job.get("title"),
                "skills": skills,
            }
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("✅ DONE")
    print(f"Jobs processed: {len(results)}")
    print(f"AI calls used: {ai_calls}")


if __name__ == "__main__":
    main()
