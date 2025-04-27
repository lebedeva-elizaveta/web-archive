import time
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from app.config import settings
from app.services.selenium_service import wait_for_element_to_be_clickable, wait_for_element_to_be_present, \
    find_element_if_exists


class AuthService:
    def __init__(self, driver):
        self.driver = driver
        self.username_moodle = settings.USERNAME_MOODLE
        self.password_moodle = settings.PASSWORD_MOODLE
        self.username_brs = settings.USERNAME_BRS
        self.password_brs = settings.PASSWORD_BRS
        self.vk_phone = settings.VK_PHONE
        self.vk_code = settings.VK_CODE
        self.vk_password = settings.VK_PASSWORD

    def login(self, login_url):
        if "cs" in login_url:
            return self.login_brs(login_url)
        elif "edu" in login_url:
            return self.login_moodle(login_url)
        elif "vk" in login_url:
            return self.login_vk(login_url)
        else:
            raise Exception("Неизвестный сайт для авторизации!")

    def _perform_login_steps(self, steps):
        for step in steps:
            element = WebDriverWait(self.driver, 10).until(step["wait_condition"])
            if step.get("action"):
                step["action"](element)
        time.sleep(2)
        cookies = self.driver.get_cookies()
        return cookies

    def login_moodle(self, login_url):
        self.driver.get(login_url)
        steps = [
            {
                "wait_condition": wait_for_element_to_be_clickable((By.XPATH, "//a[contains(@href, 'login/index.php')]")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "username")),
                "action": lambda elem: elem.send_keys(self.username_moodle),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "password")),
                "action": lambda elem: elem.send_keys(self.password_moodle),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable((By.ID, "loginbtn")),
                "action": lambda elem: elem.click(),
            },
        ]
        return self._perform_login_steps(steps)

    def login_brs(self, login_url):
        self.driver.get(login_url)
        steps = [
            {
                "wait_condition": wait_for_element_to_be_present((By.ID, "login")),
                "action": lambda elem: elem.send_keys(self.username_brs),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.NAME, "password")),
                "action": lambda elem: elem.send_keys(self.password_brs),
            },
            {
                "wait_condition": wait_for_element_to_be_clickable((By.ID, "button_login")),
                "action": lambda elem: elem.click(),
            },
        ]
        return self._perform_login_steps(steps)

    def login_vk(self, login_url):
        self.driver.get(login_url)

        # Проверяем наличие первой кнопки, если она есть - кликаем по ней
        login_button = find_element_if_exists(self.driver,
            (By.XPATH, "//button[@class='quick_login_button flat_button button_wide']"))
        if login_button:
            self.driver.execute_script("arguments[0].click();", login_button)

        # Переходим ко второму действию, независимо от того, была ли кнопка или нет
        steps = [
            {
                "wait_condition": wait_for_element_to_be_clickable(
                    (By.XPATH, "//button[@data-testid='enter-another-way']")),
                "action": lambda elem: elem.click(),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='login']")),
                "action": lambda elem: elem.send_keys(self.vk_phone),
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
                "action": lambda elem: elem.send_keys(self.vk_code),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='otp']")),
                "action": lambda elem: elem.send_keys(Keys.ENTER),
            },
            {
                "wait_condition": wait_for_element_to_be_present((By.XPATH, "//input[@name='password']")),
                "action": lambda elem: elem.send_keys(self.vk_password),
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
        return self._perform_login_steps(steps)
