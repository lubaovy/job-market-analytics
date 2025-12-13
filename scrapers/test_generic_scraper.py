import json
import os
import time

# Import tất cả scrapers
from scrapers.itviec_scraper import ITviecScraper
from scrapers.topcv_scraper import TopCVScraper
from scrapers.vietnamworks_scraper import VietnamWorksScraper

###############################################################################
# CONFIG SCRAPERS
###############################################################################

SCRAPERS = {
    # "itviec": ITviecScraper,
    # "topcv": TopCVScraper,
    "vietnamworks": VietnamWorksScraper,
}

###############################################################################
# TEST: SCRAPE JOB LIST
###############################################################################


def test_job_list(scraper_name, keyword="python"):
    print("\n" + "=" * 80)
    print(f"TEST 1: JOB LIST — {scraper_name.upper()}")
    print("=" * 80)

    ScraperClass = SCRAPERS[scraper_name]
    scraper = ScraperClass(use_selenium=True)

    try:
        jobs = scraper.scrape_job_list(keyword=keyword, page=1)

        if not jobs:
            print("❌ Không scrape được job nào — có thể selector sai.")
            return []

        print(f"✅ Found {len(jobs)} jobs.")

        # Warn
        missing_title = sum(1 for j in jobs if not j.get("title"))
        missing_url = sum(1 for j in jobs if not j.get("job_url"))

        if missing_title or missing_url:
            print("⚠️ Selector Warning:")
            print(f"   Missing title: {missing_title}")
            print(f"   Missing job_url: {missing_url}")

        # Save
        os.makedirs("output", exist_ok=True)
        out = f"output/{scraper_name}_job_list.json"
        json.dump(jobs, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=2)
        print(f"💾 Saved → {out}")

        return jobs

    finally:
        scraper.close()


###############################################################################
# TEST: SCRAPE JOB DETAILS
###############################################################################


def test_job_detail(scraper_name, jobs, max_details=3):
    print("\n" + "=" * 80)
    print(f"TEST 2: JOB DETAILS — {scraper_name.upper()}")
    print("=" * 80)

    ScraperClass = SCRAPERS[scraper_name]
    scraper = ScraperClass(use_selenium=True)

    success, fail = 0, 0
    results = []

    try:
        jobs_to_scrape = jobs[:max_details]

        for i, job in enumerate(jobs_to_scrape, 1):
            url = job["job_url"]
            print(f"[{i}] Scraping detail: {url}")

            try:
                detail = scraper.scrape_job_detail(url)
                merged = {**job, **detail}

                # ---- Score dựa trên field hiện có ----
                score = 0
                if merged.get("description"):
                    score += 40
                if merged.get("requirements"):
                    score += 30
                if merged.get("benefits"):
                    score += 10
                if merged.get("company_info"):
                    score += 10
                if merged.get("job_overview"):
                    score += 10

                merged["__score"] = score

                if score >= 75:
                    print(f"   ✅ Good (score {score}/100)")
                else:
                    print(f"   ⚠️ Weak (score {score}/100)")

                results.append(merged)
                success += 1

            except Exception as e:
                print(f"❌ Detail scrape failed: {e}")
                fail += 1

            time.sleep(2)

        # Save
        out = f"output/{scraper_name}_job_details.json"
        json.dump(
            results, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=2
        )

        print("\n📊 SUMMARY")
        print(f"   Success: {success}")
        print(f"   Failed : {fail}")

        return results

    finally:
        scraper.close()


###############################################################################
# MAIN
###############################################################################


def main():
    print("\n" + "🚀" * 30)
    print("     UNIVERSAL SCRAPER TEST SUITE")
    print("🚀" * 30)

    for scraper_name in SCRAPERS.keys():
        print("\n" + "=" * 100)
        print(f"RUNNING TEST FOR: {scraper_name.upper()}")
        print("=" * 100)

        jobs = test_job_list(scraper_name)

        if not jobs:
            print("❌ Skip detail test vì không có job list")
            continue

        test_job_detail(scraper_name, jobs, max_details=3)

    print("\n🎉 DONE — tất cả scrapers đã được test!")


if __name__ == "__main__":
    main()
