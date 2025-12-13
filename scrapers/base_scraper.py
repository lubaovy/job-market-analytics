import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import time
import random
from typing import List, Dict, Optional

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BaseScraper(ABC):
    """
    Base class cho toàn bộ scraper (ITViec, TopCV, VietnamWorks).
    """

    def __init__(
        self,
        base_url: str,
        use_selenium: bool = False,
        selenium_mode: str = "reuse",
        retries: int = 2,
        wait_time: int = 12,
    ):
        self.base_url = base_url
        self.use_selenium = use_selenium
        self.selenium_mode = selenium_mode  # "reuse" hoặc "fresh"

        # Defaults luôn hợp lệ
        self.retries = retries or 2
        self.wait_time = wait_time or 12

        # Requests session
        self.session = self._setup_requests_session()

        # Selenium driver (only reuse mode)
        if use_selenium and selenium_mode == "reuse":
            self.driver = self._setup_selenium_driver()

    # ============================================================
    # Unified entrypoint
    # ============================================================
    def get_page(
        self,
        url: str,
        retries: Optional[int] = None,
        wait_selector: Optional[str] = None,
    ) -> BeautifulSoup:

        retries = retries or self.retries

        if self.use_selenium:
            return self._get_page_selenium(url, retries, wait_selector)
        return self._get_page_requests(url, retries)

    # ============================================================
    # Requests section
    # ============================================================
    def _setup_requests_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
            }
        )
        return session

    def _get_page_requests(self, url: str, retries: int) -> BeautifulSoup:
        for attempt in range(1, retries + 1):
            try:
                print(f"➡️ [Requests] GET {url} (Attempt {attempt})")

                r = self.session.get(url, timeout=15)
                r.raise_for_status()

                return BeautifulSoup(r.text, "html.parser")

            except Exception as e:
                print(f"❌ Requests failed {attempt}: {e}")
                if attempt == retries:
                    raise
                time.sleep(random.uniform(1, 2))

    # ============================================================
    # Selenium section
    # ============================================================
    def _setup_selenium_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    def _get_page_selenium(
        self,
        url: str,
        retries: int,
        wait_selector: Optional[str],
    ) -> BeautifulSoup:

        for attempt in range(1, retries + 1):
            driver = None
            try:
                print(
                    f"🌐 [Selenium] GET {url} (Attempt {attempt}, mode={self.selenium_mode})"
                )

                # If fresh → create new driver each request
                if self.selenium_mode == "fresh":
                    driver = self._setup_selenium_driver()
                else:
                    driver = self.driver

                driver.get(url)

                if wait_selector:
                    WebDriverWait(driver, self.wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                    )

                time.sleep(1.5)
                return BeautifulSoup(driver.page_source, "html.parser")

            except Exception as e:
                print(f"❌ Selenium failed {attempt}: {e}")
                if attempt == retries:
                    raise

            finally:
                if self.selenium_mode == "fresh" and driver:
                    driver.quit()

    # ============================================================
    # Cleanup
    # ============================================================
    def close(self):
        if self.use_selenium and self.selenium_mode == "reuse":
            if hasattr(self, "driver"):
                self.driver.quit()
                print("🔒 Selenium driver closed.")

    # ============================================================
    # ABSTRACT METHODS
    # ============================================================
    @abstractmethod
    def scrape_job_list(self, url: str) -> List[Dict]:
        pass

    @abstractmethod
    def scrape_job_detail(self, job_url: str) -> Dict:
        pass
