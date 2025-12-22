import json
import os
import time
from scrapers.itviec_scraper import ITviecScraper
from scrapers.topcv_scraper import TopCVScraper
from scrapers.vietnamworks_scraper import VietnamWorksScraper

RAW_DIR = "raw_data"
os.makedirs(RAW_DIR, exist_ok=True)


def save_jsonl(path: str, data: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


# ============================================================
# SCRAPE CATEGORY — FIXED JOB COUNT (500 / PLATFORM)
# ============================================================
def crawl_category_by_url(
    scraper,
    platform_name: str,
    base_url: str,
    target_jobs: int = 500,
):
    print(f"\n============================")
    print(f"📂 SCRAPING CATEGORY — {platform_name}")
    print(f"🎯 TARGET JOBS: {target_jobs}")
    print(f"============================\n")

    output_file = os.path.join(RAW_DIR, f"{platform_name}_raw.jsonl")

    page = 1
    collected = 0

    while collected < target_jobs:
        # 🔥 GIỮ NGUYÊN LOGIC NÀY
        if page == 1:
            page_url = base_url
        else:
            page_url = (
                f"{base_url}&page={page}"
                if "?" in base_url
                else f"{base_url}?page={page}"
            )

        print(f"\n📄 Page {page} — {page_url}")

        try:
            job_list = scraper.scrape_job_list(page_url)
        except Exception as e:
            print(f"❌ Error loading page {page}: {e}")
            break

        if not job_list:
            print("⚠ No more jobs → stop.")
            break

        for job in job_list:
            if collected >= target_jobs:
                break

            job_url = job.get("job_url")
            if not job_url:
                continue

            print(f"👉 Detail ({collected+1}/{target_jobs}): {job_url}")

            try:
                detail = scraper.scrape_job_detail(job_url)
            except Exception as e:
                print(f"❌ Error scraping detail: {e}")
                continue

            raw_item = {
                "platform": platform_name,
                "job_list_item": job,
                "job_detail": detail,
                "timestamp": int(time.time()),
            }

            save_jsonl(output_file, raw_item)
            collected += 1
            print("   ✔ Saved")

            time.sleep(1.2)

        page += 1

    print(f"\n🎉 FINISHED {platform_name}: {collected} jobs\n")


# ============================================================
# MAIN
# ============================================================
def main():
    TARGET_JOBS = 500

    URL_ITVIEC = "https://itviec.com/it-jobs"
    URL_TOPCV = "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=1&sba=1&category_family=r257&saturday_status=0"
    URL_VNW = "https://www.vietnamworks.com/viec-lam?g=5&ignoreLocation=true"

    itviec = ITviecScraper(use_selenium=True)
    topcv = TopCVScraper(use_selenium=True)
    vnw = VietnamWorksScraper(use_selenium=True)

    try:
        crawl_category_by_url(itviec, "itviec", URL_ITVIEC, TARGET_JOBS)
        crawl_category_by_url(topcv, "topcv", URL_TOPCV, TARGET_JOBS)
        crawl_category_by_url(vnw, "vietnamworks", URL_VNW, TARGET_JOBS)

    finally:
        itviec.close()
        topcv.close()
        vnw.close()


if __name__ == "__main__":
    main()
