from scrapers.itviec_scraper import ITviecScraper
import json
import os
import time


def test_scrape_job_list_only():
    print("=" * 70)
    print("TEST 1: SCRAPING JOB LIST ONLY")
    print("=" * 70)

    scraper = ITviecScraper(use_selenium=True)

    try:
        jobs = scraper.scrape_job_list(keyword="python", page=1)

        if not jobs:
            print("❌ ERROR: Không scrape được job nào (selector sai, HTML thay đổi?)")
            return []

        print(f"✅ Found {len(jobs)} jobs\n")

        # ---- NEW: Kiểm tra selector lỗi ----
        missing_title = sum(1 for j in jobs if not j.get("title"))
        missing_company = sum(1 for j in jobs if not j.get("company"))
        missing_url = sum(1 for j in jobs if not j.get("job_url"))

        if missing_title or missing_company or missing_url:
            print("⚠️  Selector Warning:")
            print(f"   - Missing title:    {missing_title}")
            print(f"   - Missing company:  {missing_company}")
            print(f"   - Missing job_url:  {missing_url}")

        # ---- Lưu file ----
        os.makedirs("output", exist_ok=True)
        out = "output/itviec_jobs_list.json"
        json.dump(jobs, open(out, "w", encoding="utf8"), ensure_ascii=False, indent=2)
        print(f"💾 Saved job list → {out}")

        return jobs

    finally:
        scraper.close()


def test_scrape_job_details(jobs, max_details=3):
    print("\n" + "=" * 70)
    print(f"TEST 2: SCRAPING JOB DETAILS (First {max_details} jobs)")
    print("=" * 70)

    scraper = ITviecScraper(use_selenium=True)

    try:
        jobs_to_scrape = jobs[:max_details]
        jobs_with_details = []

        success, fail = 0, 0

        for i, job in enumerate(jobs_to_scrape, 1):
            url = job["job_url"]
            print(f"[{i}] Scraping detail: {url}")

            try:
                detail = scraper.scrape_job_detail(url)
                merged = {**job, **detail}

                # ---- NEW: Tự đánh giá độ đầy đủ ----
                score = 0
                if merged.get("description"):
                    score += 30
                if merged.get("requirements"):
                    score += 30
                if merged.get("skills"):
                    score += 20
                if merged.get("benefits"):
                    score += 10
                if merged.get("company_info"):
                    score += 10

                merged["__score"] = score

                if score < 60:
                    print(f"⚠️  Weak detail (score {score}/100)")
                else:
                    print(f"    ✅ OK (score {score}/100)")

                jobs_with_details.append(merged)
                success += 1

            except Exception as e:
                print(f"❌ Detail scrape failed: {e}")
                jobs_with_details.append(job)
                fail += 1

            time.sleep(2)

        # ---- SAVE ----
        os.makedirs("output", exist_ok=True)
        out = "output/itviec_jobs_complete.json"
        json.dump(
            jobs_with_details,
            open(out, "w", encoding="utf8"),
            ensure_ascii=False,
            indent=2,
        )

        print("\n📊 SUMMARY")
        print(f"   Success: {success}")
        print(f"   Failed : {fail}")

        # ---- NEW: Tổng điểm scraper ----
        valid = [j["__score"] for j in jobs_with_details if "__score" in j]
        if valid:
            avg_score = sum(valid) / len(valid)
            print(f"\n🏆 SCRAPER HEALTH SCORE: {avg_score:.1f}/100")

            if avg_score >= 85:
                print("➡️  Status: EXCELLENT")
            elif avg_score >= 70:
                print("➡️  Status: GOOD")
            else:
                print("➡️  Status: NEED FIX SELECTORS")

        return jobs_with_details

    finally:
        scraper.close()


# def test_analyze_complete_data(jobs_with_details):
#     """
#     Test 3: Phân tích dữ liệu đầy đủ
#     """
#     print("\n" + "=" * 70)
#     print("TEST 3: DATA ANALYSIS")
#     print("=" * 70)

#     if not jobs_with_details:
#         print("⚠️  No data to analyze")
#         return

#     # Analyze first job in detail
#     if jobs_with_details:
#         print("\n📄 DETAILED VIEW OF FIRST JOB")
#         print("─" * 70)

#         job = jobs_with_details[0]

#         print(f"\n🎯 BASIC INFO:")
#         print(f"   Title:    {job.get('title', 'N/A')}")
#         print(f"   Company:  {job.get('company', 'N/A')}")
#         print(f"   Location: {job.get('location', 'N/A')}")
#         print(f"   Source:   {job.get('source', 'N/A')}")

#         # Salary
#         salary = job.get("salary")
#         if salary:
#             print(f"\n💰 SALARY:")
#             print(f"   Type:     {salary.get('type', 'N/A')}")
#             print(f"   Raw:      {salary.get('raw', 'N/A')}")
#             if salary.get("min"):
#                 print(f"   Min:      {salary['min']} {salary.get('currency', '')}")
#             if salary.get("max"):
#                 print(f"   Max:      {salary['max']} {salary.get('currency', '')}")

#         # Tags from job list
#         tags = job.get("tags", [])
#         if tags:
#             print(f"\n🏷️  TAGS (from job list): {len(tags)} items")
#             print(f"   {', '.join(tags[:10])}")
#             if len(tags) > 10:
#                 print(f"   + {len(tags) - 10} more...")

#         # Description
#         description = job.get("description", "")
#         if description:
#             print(f"\n📝 DESCRIPTION: {len(description)} characters")
#             print(f"   Preview: {description[:200]}...")
#         else:
#             print(f"\n📝 DESCRIPTION: Not found")

#         # Requirements
#         requirements = job.get("requirements", [])
#         if requirements:
#             print(f"\n✅ REQUIREMENTS: {len(requirements)} items")
#             for req in requirements[:5]:
#                 print(f"   • {req[:80]}{'...' if len(req) > 80 else ''}")
#             if len(requirements) > 5:
#                 print(f"   + {len(requirements) - 5} more...")
#         else:
#             print(f"\n✅ REQUIREMENTS: Not found")

#         # Skills from job detail
#         skills = job.get("skills", [])
#         if skills:
#             print(f"\n🔧 SKILLS (from job detail): {len(skills)} items")
#             print(f"   {', '.join(skills[:15])}")
#             if len(skills) > 15:
#                 print(f"   + {len(skills) - 15} more...")
#         else:
#             print(f"\n🔧 SKILLS: Not found")

#         # Benefits
#         benefits = job.get("benefits", [])
#         if benefits:
#             print(f"\n🎁 BENEFITS: {len(benefits)} items")
#             for benefit in benefits[:5]:
#                 print(f"   • {benefit[:80]}{'...' if len(benefit) > 80 else ''}")
#             if len(benefits) > 5:
#                 print(f"   + {len(benefits) - 5} more...")
#         else:
#             print(f"\n🎁 BENEFITS: Not found")

#         # Company info
#         company_info = job.get("company_info", {})
#         if company_info:
#             print(f"\n🏢 COMPANY INFO:")
#             if company_info.get("name"):
#                 print(f"   Name:     {company_info['name']}")
#             if company_info.get("type"):
#                 print(f"   Type:     {company_info['type']}")
#             if company_info.get("size"):
#                 print(f"   Size:     {company_info['size']}")
#             if company_info.get("industry"):
#                 print(f"   Industry: {company_info['industry']}")
#             if company_info.get("country"):
#                 print(f"   Country:  {company_info['country']}")

#         # Job overview
#         job_overview = job.get("job_overview", {})
#         if job_overview:
#             print(f"\n📋 JOB OVERVIEW:")
#             if job_overview.get("work_type"):
#                 print(f"   Work Type: {job_overview['work_type']}")
#             if job_overview.get("detailed_location"):
#                 print(f"   Location:  {job_overview['detailed_location']}")
#             if job_overview.get("domain"):
#                 print(f"   Domain:    {job_overview['domain']}")

#     # Overall statistics
#     print("\n" + "=" * 70)
#     print("📊 OVERALL STATISTICS")
#     print("=" * 70)

#     total = len(jobs_with_details)

#     # Count fields
#     has_description = sum(1 for j in jobs_with_details if j.get("description"))
#     has_requirements = sum(1 for j in jobs_with_details if j.get("requirements"))
#     has_skills_detail = sum(1 for j in jobs_with_details if j.get("skills"))
#     has_benefits = sum(1 for j in jobs_with_details if j.get("benefits"))
#     has_company_info = sum(1 for j in jobs_with_details if j.get("company_info"))

#     print(f"\nField Coverage:")
#     print(
#         f"  Description:   {has_description}/{total} ({has_description/total*100:.1f}%)"
#     )
#     print(
#         f"  Requirements:  {has_requirements}/{total} ({has_requirements/total*100:.1f}%)"
#     )
#     print(
#         f"  Skills:        {has_skills_detail}/{total} ({has_skills_detail/total*100:.1f}%)"
#     )
#     print(f"  Benefits:      {has_benefits}/{total} ({has_benefits/total*100:.1f}%)")
#     print(
#         f"  Company Info:  {has_company_info}/{total} ({has_company_info/total*100:.1f}%)"
#     )

#     # Aggregate all skills
#     print(f"\n🔝 TOP SKILLS MENTIONED (from both tags + detail skills):")
#     from collections import Counter

#     all_skills = []

#     for job in jobs_with_details:
#         # Skills from tags
#         all_skills.extend(job.get("tags", []))
#         # Skills from detail
#         all_skills.extend(job.get("skills", []))

#     if all_skills:
#         skill_counter = Counter(all_skills)
#         for skill, count in skill_counter.most_common(15):
#             bar = "█" * int(count / max(skill_counter.values()) * 30)
#             print(f"  {skill:<20} {bar} {count}")
#     else:
#         print("  No skills data available")


def main():
    """
    Chạy tất cả tests theo thứ tự.

    Flow:
    1. Test scrape job list (nhanh)
    2. Test scrape job details (chậm)
    3. Analyze complete data
    """

    print("\n" + "🚀" * 35)
    print("ITVIEC SCRAPER - COMPLETE TEST SUITE")
    print("🚀" * 35 + "\n")

    start_time = time.time()

    try:
        # Test 1: Scrape job list
        jobs = test_scrape_job_list_only()

        if not jobs:
            print("\n❌ No jobs found in list. Stopping tests.")
            return

        # Test 2: Scrape job details (chỉ scrape 3 jobs đầu để test)
        # Thay đổi max_details=5 hoặc max_details=10 để scrape nhiều hơn
        jobs_with_details = test_scrape_job_details(jobs, max_details=3)

        # Test 3: Analyze data
        test_analyze_complete_data(jobs_with_details)

        # Final summary
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 70)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 70)
        print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
        print(f"📁 Output files:")
        print(f"   - output/itviec_jobs_list.json (job list only)")
        print(f"   - output/itviec_jobs_complete.json (with details)")
        print("\n💡 Next steps:")
        print("   1. Review JSON files to check data quality")
        print("   2. Fix any selectors that didn't work")
        print("   3. Increase max_details to scrape more jobs")
        print("   4. Move on to building the database!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
