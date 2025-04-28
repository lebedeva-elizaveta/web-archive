import time
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from app.config import settings
from app.services.selenium_service import wait_for_element_to_be_clickable, wait_for_element_to_be_present, \
    find_element_if_exists


class AuthService:
    def __init__(self, driver, credentials=None):
        self.driver = driver
        self._provided_credentials = credentials or {}
        self.credentials = {}

    def _build_credentials_for_site(self, site):
        if site in self.credentials:
            return

        if site == 'moodle':
            self.credentials['moodle'] = {
                'login': self._provided_credentials.get('login', settings.USERNAME_MOODLE),
                'password': self._provided_credentials.get('password', settings.PASSWORD_MOODLE),
            }
        elif site == 'brs':
            self.credentials['brs'] = {
                'login': self._provided_credentials.get('login', settings.USERNAME_BRS),
                'password': self._provided_credentials.get('password', settings.PASSWORD_BRS),
            }
        elif site == 'vk':
            self.credentials['vk'] = {
                'login': self._provided_credentials.get('login', settings.VK_PHONE),
                'password': self._provided_credentials.get('password', settings.VK_PASSWORD),
                'code': self._provided_credentials.get('code', settings.VK_CODE),
            }

    def login(self, login_url):
        if "cs" in login_url:
            self._build_credentials_for_site('brs')
            return self._login_brs(login_url)
        elif "edu" in login_url:
            self._build_credentials_for_site('moodle')
            return self._login_moodle(login_url)
        elif "vk" in login_url:
            self._build_credentials_for_site('vk')
            return self._login_vk(login_url)

    def _perform_login_steps(self, steps, need_cookies=True):
        for step in steps:
            element = WebDriverWait(self.driver, 10).until(step["wait_condition"])
            if step.get("action"):
                step["action"](element)
        time.sleep(2)
        if need_cookies:
            cookies = self.driver.get_cookies()
            return cookies

    def _login_moodle(self, login_url):
        creds = self.credentials['moodle']
        self.driver.get(login_url)
        steps = [
            {
                "wait_condition": wait_for_element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, 'login/index.php')]")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "username")),
                "action": lambda elem: elem.send_keys(creds['login']),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "password")),
                "action": lambda elem: elem.send_keys(creds['password']),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable((By.ID, "loginbtn")),
                "action": lambda elem: elem.click(),
            },
        ]
        return self._perform_login_steps(steps)

    def _login_brs(self, login_url):
        creds = self.credentials['brs']
        self.driver.get(login_url)
        steps = [
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "login")),
                "action": lambda elem: elem.send_keys(creds['login']),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.NAME, "password")),
                "action": lambda elem: elem.send_keys(creds['password']),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable((By.ID, "button_login")),
                "action": lambda elem: elem.click(),
            },
        ]
        return self._perform_login_steps(steps)

    def _login_vk(self, login_url):
        creds = self.credentials['vk']
        self.driver.get(login_url)

        login_button = find_element_if_exists(
            self.driver,
            (By.XPATH,"//button[@class='quick_login_button flat_button button_wide']")
        )
        if login_button:
            self.driver.execute_script("arguments[0].click();", login_button)

        steps = [
            {
                "wait_condition": wait_for_element_to_be_clickable(
                    (By.XPATH, "//button[@data-testid='enter-another-way']")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='login']")),
                "action": lambda elem: elem.send_keys(creds['login']),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='login']")),
                "action": lambda elem: elem.send_keys(Keys.ENTER),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Подтвердить другим способом')]")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Резервный код')]")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='otp']")),
                "action": lambda elem: elem.send_keys(creds['code']),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='otp']")),
                "action": lambda elem: elem.send_keys(Keys.ENTER),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='password']")),
                "action": lambda elem: elem.send_keys(creds['password']),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='password']")),
                "action": lambda elem: elem.send_keys(Keys.ENTER),
            },
            {
                "wait_condition": EC.url_contains("vk.com"),
                "action": None,
            },
        ]
        return self._perform_login_steps(steps, need_cookies=False)
