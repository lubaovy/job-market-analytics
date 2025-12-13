from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, quote_plus
import time


class VietnamWorksScraper(BaseScraper):
    def __init__(self, use_selenium=False):
        super().__init__(
            base_url="https://www.vietnamworks.com", use_selenium=use_selenium
        )

    # -----------------------------------------------------
    # JOB LIST - FIXED VERSION WITH SCROLL
    # -----------------------------------------------------
    def scrape_job_list(self, url: str, use_scroll: bool = True) -> List[Dict]:
        """
        Scrape job list với tùy chọn scroll để load thêm jobs

        Args:
            url: URL cần scrape
            use_scroll: True = dùng Selenium scroll, False = chỉ lấy jobs đầu
        """
        if use_scroll and self.use_selenium:
            return self._scrape_with_scroll(url)

        # Fallback: Chỉ lấy jobs có sẵn
        soup = self.get_page(url)
        if not soup:
            print("❌ Không thể load trang")
            return []

        return self._parse_jobs_from_soup(soup)

    def _scrape_with_scroll(self, url: str, max_scrolls: int = 5) -> List[Dict]:
        """Scroll để load thêm jobs"""
        from selenium.webdriver.common.by import By
        import time

        driver = self.driver
        driver.get(url)

        print("⏳ Đang load trang...")
        time.sleep(3)

        last_height = driver.execute_script("return document.body.scrollHeight")
        jobs_count = 0

        for i in range(max_scrolls):
            # Đếm jobs hiện tại
            current_jobs = driver.find_elements(
                By.CSS_SELECTOR, "div.search_list.view_job_item.new-job-card"
            )
            print(f"📜 Scroll {i+1}/{max_scrolls} - Tìm thấy {len(current_jobs)} jobs")

            # Scroll xuống cuối
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Kiểm tra xem có load thêm không
            new_height = driver.execute_script("return document.body.scrollHeight")
            new_jobs = driver.find_elements(
                By.CSS_SELECTOR, "div.search_list.view_job_item.new-job-card"
            )

            if new_height == last_height and len(new_jobs) == jobs_count:
                print("✅ Đã load hết jobs")
                break

            last_height = new_height
            jobs_count = len(new_jobs)

        # Parse HTML sau khi scroll
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(driver.page_source, "html.parser")
        return self._parse_jobs_from_soup(soup)

    def _parse_jobs_from_soup(self, soup) -> List[Dict]:
        """Parse jobs từ BeautifulSoup object"""

        # 🔥 Thử nhiều selector khác nhau
        selectors = [
            "div.search_list.view_job_item.new-job-card",
            "div.new-job-card",
            "div[class*='job-card']",
            "div[class*='job-item']",
        ]

        job_cards = []
        for selector in selectors:
            job_cards = soup.select(selector)
            if job_cards:
                print(f"✅ Tìm thấy {len(job_cards)} jobs với selector: {selector}")
                break

        if not job_cards:
            print("❌ Không tìm thấy job nào với các selector")
            # Debug: In ra HTML để kiểm tra
            print("🔍 HTML preview:")
            print(soup.prettify()[:2000])
            return []

        results = []

        for idx, job in enumerate(job_cards, 1):
            try:
                # Thử nhiều selector cho title
                title_el = (
                    job.select_one("h2 a")
                    or job.select_one("a[class*='title']")
                    or job.select_one("h3 a")
                )

                # Thử nhiều selector cho company
                company_el = (
                    job.select_one(".sc-jBqsNv a")
                    or job.select_one("a[class*='company']")
                    or job.select_one(".company-name")
                )

                salary_el = job.select_one(".sc-cdaca-d") or job.select_one(
                    "[class*='salary']"
                )

                location_el = job.select_one(".sc-idnGQK") or job.select_one(
                    "[class*='location']"
                )

                job_url = (
                    urljoin(self.base_url, title_el["href"])
                    if title_el and title_el.get("href")
                    else None
                )

                job_data = {
                    "title": title_el.get_text(strip=True) if title_el else None,
                    "company": company_el.get_text(strip=True) if company_el else None,
                    "location": (
                        location_el.get_text(strip=True) if location_el else None
                    ),
                    "salary": salary_el.get_text(strip=True) if salary_el else None,
                    "job_url": job_url,
                }

                results.append(job_data)
                print(f"✅ Job {idx}: {job_data['title']}")

            except Exception as e:
                print(f"⚠️ Lỗi khi parse job {idx}: {str(e)}")
                continue

        print(f"\n📊 Tổng cộng scrape được: {len(results)} jobs")
        return results

    # -----------------------------------------------------
    # JOB LIST WITH SELENIUM (for infinite scroll)
    # -----------------------------------------------------
    def scrape_job_list_selenium(self, url: str, max_scrolls: int = 5) -> List[Dict]:
        """
        Dùng khi VietnamWorks load jobs bằng infinite scroll
        """
        if not self.use_selenium:
            print("⚠️ Cần bật Selenium để dùng chức năng này")
            return self.scrape_job_list(url)

        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        driver = self.driver
        driver.get(url)

        print("⏳ Đang load trang...")
        time.sleep(3)

        # Scroll để load thêm jobs
        for i in range(max_scrolls):
            print(f"📜 Scroll lần {i+1}/{max_scrolls}")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Kiểm tra xem có nút "Load more" không
            try:
                load_more = driver.find_element(
                    By.CSS_SELECTOR, "button[class*='load-more']"
                )
                if load_more:
                    load_more.click()
                    time.sleep(2)
            except:
                pass

        # Parse HTML sau khi scroll
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Dùng lại logic parse như trên
        job_cards = soup.select("div.search_list.view_job_item.new-job-card")
        print(f"✅ Tìm thấy {len(job_cards)} jobs sau khi scroll")

        results = []
        for idx, job in enumerate(job_cards, 1):
            try:
                title_el = job.select_one("h2 a")
                company_el = job.select_one(".sc-jBqsNv a")
                salary_el = job.select_one(".sc-cdaca-d")
                location_el = job.select_one(".sc-idnGQK")

                job_url = (
                    urljoin(self.base_url, title_el["href"])
                    if title_el and title_el.get("href")
                    else None
                )

                results.append(
                    {
                        "title": title_el.get_text(strip=True) if title_el else None,
                        "company": (
                            company_el.get_text(strip=True) if company_el else None
                        ),
                        "location": (
                            location_el.get_text(strip=True) if location_el else None
                        ),
                        "salary": salary_el.get_text(strip=True) if salary_el else None,
                        "job_url": job_url,
                    }
                )

            except Exception as e:
                print(f"⚠️ Lỗi job {idx}: {str(e)}")
                continue

        return results

    # -----------------------------------------------------
    # EXTRACT BENEFITS
    # -----------------------------------------------------
    def _extract_benefits(self, soup):
        benefits = []
        benefit_items = soup.select("div[data-benefit-name]")

        for item in benefit_items:
            title_tag = item.select_one("p.sc-ab270149-0")
            title = title_tag.get_text(strip=True) if title_tag else None

            desc_tag = item.select_one("div.sc-c683181c-2")
            desc = desc_tag.get_text(strip=True) if desc_tag else None

            if title or desc:
                benefits.append({"title": title, "description": desc})

        return benefits

    # -----------------------------------------------------
    # JOB DETAIL
    # -----------------------------------------------------
    def scrape_job_detail(self, job_url: str) -> Dict:
        job_url = urljoin(self.base_url, job_url)
        soup = self.get_page(job_url, wait_selector="h2.sc-1671001a-5")

        if not soup:
            return {}

        sections = soup.select("div.sc-1671001a-4.gDSEwb")

        description = None
        requirements = None

        for sec in sections:
            title_el = sec.select_one("h2.sc-1671001a-5")
            content_el = sec.select_one("div.sc-1671001a-6")

            if not title_el or not content_el:
                continue

            title = title_el.get_text(strip=True)
            content = content_el.get_text("\n", strip=True)

            if "Mô tả công việc" in title:
                description = content
            elif "Yêu cầu công việc" in title:
                requirements = content

        benefits = self._extract_benefits(soup)

        return {
            "description": description,
            "requirements": requirements,
            "benefits": benefits,
            "job_url": job_url,
            "source": "vietnamworks",
        }
