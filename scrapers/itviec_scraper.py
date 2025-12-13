from .base_scraper import BaseScraper
from typing import List, Dict
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ITviecScraper(BaseScraper):
    def __init__(self, use_selenium: bool = False):
        """
        Args:
            use_selenium: True = dùng Selenium, False = dùng requests
        """
        super().__init__(
            "https://itviec.com", use_selenium=use_selenium, selenium_mode="fresh"
        )

    def scrape_job_list(self, url: str) -> List[Dict]:
        """
        Scrape danh sách jobs từ trang search.

        Flow:
        1. Tạo URL search với keyword
        2. Parse HTML để lấy danh sách job cards
        3. Extract thông tin từ mỗi card
        4. Return list of job dicts
        """

        # Build URL
        # search_url = f"{self.base_url}/it-jobs/{keyword}?page={page}"

        # Get page HTML
        soup = self.get_page(url)

        # Find tất cả job cards
        job_cards = soup.select("div.job-card")

        jobs = []
        for card in job_cards:
            try:
                job_data = {
                    "title": self._extract_title(card),
                    "company": self._extract_company(card),
                    "location": self._extract_location(card),
                    "salary": self._extract_salary(card),
                    "job_url": self._extract_url(card),
                    # "posted_date": self._extract_date(card),
                    "tags": self._extract_tags(card),
                    "source": "itviec",
                }
                jobs.append(job_data)

            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        return jobs

    def _extract_title(self, card) -> str:
        title_elem = card.select_one("h3")
        return title_elem.text.strip() if title_elem else None

    def _extract_company(self, card) -> str:
        """
        Extract company name từ job card.

        HTML structure:
        <a class="text-rich-grey" href="/companies/...">Viettel Group</a>

        Có 2 links với href="/companies/":
        1. Link wrapper của logo (không có text)
        2. Link text company name (có text)

        → Cần selector CHỈ ĐỊNH class để tránh lấy nhầm
        """
        company_elem = card.select_one('a.text-rich-grey[href*="/companies/"]')
        return company_elem.text.strip() if company_elem else None

    def _extract_location(self, card) -> str:
        """
        Extract location (city) từ job card.

        Lưu ý: Có 2 divs với class text-rich-grey:
        - "At office" (work type)
        - "Ha Noi" (location thật)

        Chiến lược: Lọc ra chỉ lấy cities, bỏ qua work types.
        """
        location_elems = card.select("div.text-rich-grey")

        # Danh sách cities hợp lệ
        VALID_CITIES = [
            "Ho Chi Minh",
            "Ha Noi",
            "Da Nang",
            "Can Tho",
            "Hai Phong",
            "Binh Duong",
            "Dong Nai",
        ]

        for elem in location_elems:
            text = elem.text.strip()

            # ✅ CHỈ check cities, KHÔNG check "office"
            if text in VALID_CITIES:
                return text

        return None

    def _extract_salary(self, card) -> Dict:
        """
        Extract và parse salary từ job card.

        Các trường hợp xử lý:
        1. "You'll love it" - Mức lương hấp dẫn
        2. "Up to $2200" - Mức lương cụ thể
        3. "Sign in to view salary" - Cần đăng nhập
        4. Các format khác: "$1500 - $2000", "15-20 triệu", etc.
        """

        # Tìm phần tử chứa thông tin lương
        salary_div = card.select_one("div.salary")
        if not salary_div:
            return None

        # Lấy toàn bộ text trong salary section
        salary_text = salary_div.get_text(strip=True)

        # Trường hợp 1: "You'll love it" - Mức lương hấp dẫn
        if "You'll love it" in salary_text:
            return {
                "type": "competitive",
                "raw": "You'll love it",
                "description": "Competitive salary with attractive benefits",
            }

        # Trường hợp 2: "Up to $XXXX" - Mức lương tối đa
        match_up_to = re.search(r"Up to\s*\$?(\d+[.,]?\d*)", salary_text)
        if match_up_to:
            amount = float(match_up_to.group(1).replace(",", ""))
            return {
                "type": "up_to",
                "min": None,
                "max": amount,
                "currency": "USD",
                "raw": salary_text,
            }

        # Trường hợp 3: "Sign in to view salary" - Cần đăng nhập
        sign_in_elem = card.select_one("a.sign-in-view-salary")
        if sign_in_elem or "sign in" in salary_text.lower():
            return {
                "type": "login_required",
                "raw": "Sign in to view salary",
                "description": "Salary information requires login",
            }

        # Trường hợp 4: Khoảng lương "$1500 - $2000"
        match_range_usd = re.search(
            r"\$?(\d+[.,]?\d*)\s*-\s*\$?(\d+[.,]?\d*)", salary_text
        )
        if match_range_usd:
            min_amount = float(match_range_usd.group(1).replace(",", ""))
            max_amount = float(match_range_usd.group(2).replace(",", ""))
            return {
                "type": "range",
                "min": min_amount,
                "max": max_amount,
                "currency": "USD",
                "raw": salary_text,
            }

        # Trường hợp 5: Khoảng lương VND "15-20 triệu"
        match_range_vnd = re.search(r"(\d+)[-\s]*(\d+)\s*[Tt]ri[eệ]u", salary_text)
        if match_range_vnd:
            min_amount = float(match_range_vnd.group(1)) * 1_000_000
            max_amount = float(match_range_vnd.group(2)) * 1_000_000
            return {
                "type": "range",
                "min": min_amount,
                "max": max_amount,
                "currency": "VND",
                "raw": salary_text,
                "description": f"{match_range_vnd.group(1)}-{match_range_vnd.group(2)} triệu VND",
            }

        # Trường hợp 6: Lương cố định "$1500"
        match_single = re.search(r"\$?(\d+[.,]?\d*)\b", salary_text)
        if match_single:
            amount = float(match_single.group(1).replace(",", ""))
            return {
                "type": "fixed",
                "min": amount,
                "max": amount,
                "currency": "USD" if "$" in salary_text else "VND",
                "raw": salary_text,
            }

        # Trường hợp 7: Text mô tả khác
        if salary_text and len(salary_text) > 3:
            return {
                "type": "descriptive",
                "raw": salary_text,
                "description": "Descriptive salary information",
            }

        return None

    def _extract_url(self, card) -> str:
        raw_url = card.get("data-search--job-selection-job-url-value")
        if not raw_url:
            return None

        # Ví dụ raw_url:
        # /it-jobs/senior-back-end-python-developer-fastapi-aws-outpost24-2217/content?job_index=0&locale=en&page=1

        # Cắt phần sau slug
        clean_url = raw_url.split("/content")[0]

        return f"{self.base_url}{clean_url}"

    # def _extract_date(self, card) -> str:
    #     date_elem = card.select_one("span.small-text:text-contains(Posted)")
    #     if date_elem:
    #         date_text = date_elem.text.strip()
    #         posted_match = re.search(r"Posted\s+(.+)", date_text)
    #         return posted_match.group(1) if posted_match else date_text
    #     return None

    def _extract_tags(self, card) -> List[str]:
        tags = []
        tag_elems = card.select("a.itag")
        for tag in tag_elems:
            tag_text = tag.text.strip()
            if tag_text:
                tags.append(tag_text)
        return tags

    def scrape_job_detail(self, job_url: str) -> Dict:
        soup = self.get_page(job_url)
        return {
            "description": self._extract_description(soup),
            "requirements": self._extract_requirements(soup),
            # "skills": self._extract_skills(soup),
            "benefits": self._extract_benefits(soup),
            "company_info": self._extract_company_info(soup),
            "job_overview": self._extract_job_overview(soup),
            # "full_text": self._extract_full_text(soup),
        }

    def _extract_section_by_heading(self, soup, heading_text):
        heading = soup.find(
            "h2", string=lambda t: t and heading_text.lower() in t.lower()
        )
        if not heading:
            return ""

        container = heading.find_parent("div", class_="paragraph")
        if not container:
            return ""

        return container.get_text("\n", strip=True)

    def _extract_description(self, soup) -> str:
        # desc_section = soup.select_one("section.job-description div.paragraph")
        # if desc_section:
        #     return desc_section.get_text(separator="\n").strip()

        # # Fallback: tìm bất kỳ phần nào chứa mô tả công việc
        # desc_elem = soup.find(
        #     ["div", "section"], string=re.compile(r"[Jj]ob [Dd]escription")
        # )
        # if desc_elem:
        #     next_para = desc_elem.find_next("div", class_="paragraph")
        #     return next_para.get_text(separator="\n").strip() if next_para else None

        # return None
        return self._extract_section_by_heading(soup, "Job description")

    def _extract_requirements(self, soup) -> List[str]:
        # requirements = []

        # exp_section = soup.select_one("section.job-experiences div.paragraph")
        # if exp_section:
        #     list_items = exp_section.select("li")
        #     for item in list_items:
        #         req_text = item.get_text(strip=True)
        #         if req_text:
        #             requirements.append(req_text)

        # # Fallback: tìm các phần requirements khác
        # if not requirements:
        #     req_elems = soup.select("section div.parapraph li, .requirement li ")
        #     for elem in req_elems:
        #         req_text = elem.get_text(strip=True)
        #         if req_text and len(req_text) > 10:  # Lọc text quá ngắn
        #             requirements.append(req_text)

        # return requirements
        content = self._extract_section_by_heading(soup, "Your skills and experience")
        return [line.strip() for line in content.split("\n") if line.strip()]

    # def _extract_skills(self, soup) -> List[str]:
    #     skills = []

    #     skills_section = soup.select("select.preview-job-overview a,itag")
    #     for skill_elem in skills_section:
    #         skill_name = skill_elem.get_text(strip=True)
    #         if skill_name and skill_name not in skills:
    #             skills.append(skill_name)

    #     # 2. Extract từ job expertise
    #     expertise_elems = soup.select('a[title], a[href*="/it-jobs/"]')
    #     for elem in expertise_elems:
    #         skill_name = elem.get_text(strip=True)
    #         if (
    #             skill_name
    #             and skill_name not in skills
    #             and len(skill_name) > 2
    #             and len(skill_name) < 50
    #         ):
    #             skills.append(skill_name)

    #     return skills

    def _extract_benefits(self, soup) -> List[str]:
        # """Extract job benefits từ job detail."""
        # benefits = []

        # # Tìm section "Why you'll love working here"
        # benefits_section = soup.select_one("section.job-why-love-working div.paragraph")
        # if benefits_section:
        #     list_items = benefits_section.select("li")
        #     for item in list_items:
        #         benefit_text = item.get_text(strip=True)
        #         if benefit_text:
        #             benefits.append(benefit_text)

        # # Tìm section "Top 3 reasons to join us"
        # reasons_section = soup.select_one("section.reasons-join-us ul.paragraph")
        # if reasons_section:
        #     list_items = reasons_section.select("li")
        #     for item in list_items:
        #         reason_text = item.get_text(strip=True)
        #         if reason_text and reason_text not in benefits:
        #             benefits.append(reason_text)

        # return benefits
        content = self._extract_section_by_heading(soup, "Why you'll love working here")
        return [line.strip() for line in content.split("\n") if line.strip()]

    def _extract_company_info(self, soup) -> Dict:
        company_info = {}

        try:
            # Company name
            name_elem = soup.select_one("section.job-show-employer-info h3 a")
            company_info["name"] = name_elem.get_text(strip=True) if name_elem else None

            # Company description (p ngay dưới logo)
            desc_elem = soup.select_one("section.job-show-employer-info p")
            company_info["description"] = (
                desc_elem.get_text(strip=True) if desc_elem else None
            )

            # Thông tin chi tiết
            rows = soup.select("section.job-show-employer-info .row")
            for row in rows:
                label_elem = row.select_one(".col.text-dark-grey")
                value_elem = row.select_one(".col.text-end.text-it-black")

                if not label_elem or not value_elem:
                    continue

                label = label_elem.get_text(strip=True).lower()
                value = value_elem.get_text(" ", strip=True)

                if "company type" in label:
                    company_info["type"] = value
                elif "company industry" in label:
                    company_info["industry"] = value
                elif "company size" in label:
                    company_info["size"] = value
                elif "country" in label:
                    company_info["country"] = value
                elif "working days" in label:
                    company_info["working_days"] = value
                elif "overtime policy" in label:
                    company_info["overtime_policy"] = value

        except Exception as e:
            print(f"Error extracting company info: {e}")

        return company_info

    def _extract_job_overview(self, soup) -> Dict:
        overview = {}

        try:
            # 1. Địa điểm
            location_elem = soup.select_one(
                "div.job-show-info span.normal-text.text-rich-grey"
            )
            overview["detailed_location"] = (
                location_elem.get_text(strip=True) if location_elem else None
            )

            # 2. Work type (At office / Remote / Hybrid)
            work_type_elem = soup.find("div", class_="preview-header-item").find(
                "span", class_="normal-text"
            )
            overview["work_type"] = (
                work_type_elem.get_text(strip=True) if work_type_elem else None
            )

            # 3. Thời gian đăng (Posted X ago)
            posted_elem = soup.find(
                "span", string=lambda text: text and "ago" in text.lower()
            )
            overview["posted_time_detail"] = (
                posted_elem.get_text(strip=True) if posted_elem else None
            )

            # 4. Domain (nhiều thẻ)
            domain_elems = soup.select("div.itag.bg-light-grey.itag-sm.cursor-default")
            overview["domain"] = (
                [d.get_text(strip=True) for d in domain_elems] if domain_elems else []
            )

            # 5. Job Expertise
            expertise_elem = soup.select_one("a.itag.itag-light.itag-sm[title]")
            overview["expertise"] = (
                expertise_elem.get_text(strip=True) if expertise_elem else None
            )

            # 6. Skill tags
            skill_elems = soup.select("div.job-show-info a.itag.itag-light.itag-sm")
            overview["skills"] = [s.get_text(strip=True) for s in skill_elems]

        except Exception as e:
            print(f"Error extracting job overview: {e}")

        return overview

    # def _extract_full_text(self, soup) -> str:
    #     """Extract toàn bộ text của job detail để backup analysis."""
    #     main_content = soup.select_one("div.preview-job-content, .job-detail-content")
    #     if main_content:
    #         return main_content.get_text(separator="\n", strip=True)

    #     return None
