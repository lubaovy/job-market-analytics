import json
import glob
import os
import re
from typing import Any, List, Dict

RAW_DIR = "raw_data"
OUTPUT_FILE = "processed_data/normalized_jobs.jsonl"


# =========================
# Helpers
# =========================


def normalize_text_list(field: Any) -> List[str]:
    """
    Chuẩn hoá requirements / benefits
    -> luôn trả về list[str]
    """
    if not field:
        return []

    if isinstance(field, str):
        return [x.strip() for x in field.split("\n") if x.strip()]

    if isinstance(field, list):
        result = []
        for item in field:
            if isinstance(item, str):
                result.append(item.strip())
            elif isinstance(item, dict):
                text = item.get("description") or item.get("title")
                if text:
                    result.append(text.strip())
        return [x for x in result if x]

    return []


def normalize_salary(salary_raw: Any) -> Dict[str, Any]:
    """
    Chuẩn hoá salary về min / max / avg (VND)
    """
    salary = {"raw": None, "min": None, "max": None, "avg": None}

    # itviec (object)
    if isinstance(salary_raw, dict):
        salary["raw"] = salary_raw.get("raw")
        return salary

    # string salary
    if isinstance(salary_raw, str):
        salary["raw"] = salary_raw

        # Thoả thuận
        if "thoả thuận" in salary_raw.lower():
            return salary

        # 22tr-24tr
        numbers = re.findall(r"\d+", salary_raw)
        values = [int(n) * 1_000_000 for n in numbers]

        if len(values) >= 1:
            salary["min"] = values[0]
        if len(values) >= 2:
            salary["max"] = values[1]
        if salary["min"] and salary["max"]:
            salary["avg"] = int((salary["min"] + salary["max"]) / 2)

    return salary


# =========================
# Core normalize
# =========================


def normalize_record(raw: Dict) -> Dict:
    job = raw.get("job_list_item", {})
    detail = raw.get("job_detail", {})

    return {
        "platform": raw.get("platform"),
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "job_url": job.get("job_url"),
        "timestamp": raw.get("timestamp"),
        "salary": normalize_salary(job.get("salary")),
        "description": detail.get("description"),
        "requirements": normalize_text_list(detail.get("requirements")),
        "benefits": normalize_text_list(detail.get("benefits")),
    }


# =========================
# Main
# =========================


def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    files = glob.glob(os.path.join(RAW_DIR, "*_raw.jsonl"))

    total = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for file in files:
            with open(file, encoding="utf-8") as f:
                for line in f:
                    raw = json.loads(line)
                    norm = normalize_record(raw)
                    out.write(json.dumps(norm, ensure_ascii=False) + "\n")
                    total += 1

    print(f"✅ Normalization completed | records: {total}")


if __name__ == "__main__":
    main()
