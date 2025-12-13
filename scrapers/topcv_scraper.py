from .base_scraper import BaseScraper
from bs4 import BeautifulSoup


class TopCVScraper(BaseScraper):

    BASE_URL = "https://www.topcv.vn"

    def __init__(self, use_selenium=True):
        super().__init__(self.BASE_URL, use_selenium, selenium_mode="fresh")

    def scrape_job_list(self, url: str):
        # url = f"https://www.topcv.vn/tim-viec-lam-{keyword}?type_keyword=1&sba=1&saturday_status=0"

        soup = self.get_page(url)

        jobs_html = soup.select("div.job-item-search-result")
        print(f"🔍 Found {len(jobs_html)} jobs on TopCV")

        jobs = []
        for item in jobs_html:
            try:
                title_el = item.select_one("h3.title span")
                link_el = item.select_one("div.title-block a[href]")
                company_el = item.select_one("a.company span.company-name")
                salary_el = item.select_one("label.title-salary")
                location_el = item.select_one("label.address .city-text")
                exp_el = item.select_one("label.exp span")

                job = {
                    "title": title_el.get_text(strip=True) if title_el else None,
                    "company": company_el.get_text(strip=True) if company_el else None,
                    "location": (
                        location_el.get_text(strip=True) if location_el else None
                    ),
                    "salary": salary_el.get_text(strip=True) if salary_el else None,
                    "experience": exp_el.get_text(strip=True) if exp_el else None,
                    "job_url": (
                        link_el["href"]
                        if link_el and link_el["href"].startswith("http")
                        else f"{self.BASE_URL}{link_el['href']}" if link_el else None
                    ),
                }

                jobs.append(job)

            except Exception as e:
                print(f"⚠️ Error parsing job card: {e}")

        return jobs

    def scrape_job_detail(self, job_url):
        soup = self.get_page(
            job_url, wait_selector=".job-detail__information-container"
        )

        return {
            "description": self._extract_section(soup, "Mô tả công việc"),
            "requirements": self._extract_section(soup, "Yêu cầu ứng viên"),
            "benefits": self._extract_section(soup, "Quyền lợi"),
            "location": self._extract_section(soup, "Địa điểm làm việc"),
            "working_time": self._extract_section(soup, "Thời gian làm việc"),
        }

    def _extract_section(self, soup, title_text):
        block = soup.select_one(
            f".job-description__item h3:-soup-contains('{title_text}')"
        )
        if not block:
            return None

        content = block.find_next("div", class_="job-description__item--content")
        if not content:
            return None

        return "\n".join(
            [p.get_text(strip=True) for p in content.find_all(["p", "li", "div"])]
        )
