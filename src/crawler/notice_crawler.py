import json
import re
import webbrowser
from datetime import datetime
import time
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER

from config.settings import USER_AGENT

LOGGER.setLevel(logging.WARNING)

class NoticeCrawler:
    def __init__(self):
        self.driver = self._configure_selenium_driver()

    def _configure_selenium_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument(f"user-agent={USER_AGENT}")
        service = Service()
        return webdriver.Chrome(service=service, options=options)

    def _extract_token_names_from_title(self, title):
        pattern = r"\((.*?)\)"
        return re.findall(pattern, title)

    def _is_future_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date() >= datetime.now().date()
        except Exception:
            return True

    def get_notices(self, open_browser=False):
        """
        빗썸 공지사항에서 에어드랍 관련 공지를 크롤링합니다.
        """
        self.driver.set_page_load_timeout(10)
        summary = []

        try:
            self.driver.get("https://feed.bithumb.com/notice")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "__NEXT_DATA__"))
            )

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            script = soup.find("script", {"id": "__NEXT_DATA__"})
            if not script:
                print("[❌] __NEXT_DATA__ 스크립트 태그를 찾을 수 없습니다.")
                return []

            data = json.loads(script.string)
            notices = data.get("props", {}).get("pageProps", {}).get("noticeList", [])

            for item in notices:
                title = item.get("title", "").strip()
                if "에어드랍" not in title:
                    continue

                date = item.get("publicationDateTime", "").split(" ")[0]
                if not self._is_future_date(date):
                    continue

                tokens = self._extract_token_names_from_title(title)
                nid = item.get("id")
                if nid and open_browser:
                    url = f"https://feed.bithumb.com/notice/{nid}"
                    webbrowser.open(url)
                    print(f"[🌐] 상세 페이지 이동: {url}")

                for token in tokens:
                    summary.append(f"{token}\t{date}")

            if summary:
                print("\n📌 에어드랍 이벤트 요약:\n")
                for s in summary:
                    print(s)
            else:
                print("에어드랍 공지 없음")

            return summary

        finally:
            self.driver.quit() 