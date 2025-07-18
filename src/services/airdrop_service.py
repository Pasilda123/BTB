import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

class AirdropService:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-popup-blocking')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = None
        self.max_retries = 3
        self.retry_delay = 2

    def initialize_driver(self):
        for attempt in range(self.max_retries):
            try:
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=self.options)
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        })
                    '''
                })
                return True
            except Exception as e:
                print(f"⚠️ ChromeDriver 초기화 시도 {attempt + 1}/{self.max_retries} 실패: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
        return False

    def get_airdrop_info(self):
        try:
            if not self.initialize_driver():
                print("❌ ChromeDriver 초기화 실패")
                return False
            
            print("📱 최신 에어드랍 공지 확인 중...")
            self.driver.get("https://www.bithumb.com/notice/notice_list")
            time.sleep(3)
            
                                  
            
        except Exception as e:
            print(f"⚠️ 에어드랍 정보 수집 중 오류 발생: {str(e)}")
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None 