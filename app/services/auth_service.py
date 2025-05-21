import time
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from app.services.selenium_service import (
    wait_for_first_visible_element,
    wait_for_element_to_be_present,
    find_element_if_exists
)
from app.config import settings



class AuthService:
    def __init__(self, driver, credentials=None):
        self.driver = driver
        self.credentials = credentials or {}

    def _build_locator(self, element: dict):
        by = element.get('by')
        if by == 'xpath':
            return self._build_xpath_locator(element)
        return self._build_simple_locator(element)

    def _build_xpath_locator(self, element: dict):
        element_type = element.get('type')
        text_value = element.get('value')
        if element_type and text_value:
            xpath = f"//{element_type}[contains(text(),'{text_value}')]"
        elif text_value:
            xpath = text_value
        else:
            raise ValueError("Для xpath должен быть хотя бы value")
        return By.XPATH, xpath

    def _build_simple_locator(self, element: dict):
        value = element.get('value')
        if not value:
            raise ValueError("Для локатора по не xpath обязательно указать 'value'")
        by_const = getattr(By, element.get('by').upper())
        return by_const, value

    def _wait_for_element(self, element: dict, action_type: str, optional: bool = False):
        by = element.get('by')
        value = element.get('value')

        if by == 'url_contains':
            if not value:
                raise ValueError("Для url_contains должен быть указан 'value'")
            try:
                WebDriverWait(self.driver, 10).until(EC.url_contains(value))
            except Exception:
                if not optional:
                    raise Exception(f"URL не содержит {value}")
            return

        locator = self._build_locator(element)

        try:
            if action_type == 'click':
                el = wait_for_first_visible_element(self.driver, locator, timeout=10)
                if el is None and not optional:
                    raise Exception(f"Видимый элемент для клика по локатору {locator} не найден за timeout")
            else:
                WebDriverWait(self.driver, 10).until(wait_for_element_to_be_present(locator))
        except Exception:
            if not optional:
                raise Exception(f"Элемент {locator} не появился за timeout")

    def _find_element(self, wait_condition: dict, optional: bool, action_type: str):
        self._wait_for_element(wait_condition, action_type, optional=optional)

        if wait_condition.get('by') == 'url_contains':
            return None

        locator = self._build_locator(wait_condition)

        if optional:
            return find_element_if_exists(self.driver, locator)

        elements = self.driver.find_elements(*locator)
        if not elements:
            raise Exception(f"Элементы по локатору {locator} не найдены")

        if action_type == 'click':
            for el in elements:
                if el.is_displayed():
                    return el
            raise Exception(f"Нет видимого элемента по локатору {locator} для клика")

        if action_type == 'js_click':
            return elements[0]

        for el in elements:
            if el.is_displayed():
                return el

        raise Exception(f"Элемент не найден или не видим: {locator}")

    def _perform_action(self, element, action: dict):
        if not action or element is None:
            return

        act_type = action.get('type')

        if act_type == 'click':
            element.click()
        elif act_type == 'js_click':
            self.driver.execute_script("arguments[0].click();", element)
        elif act_type == 'send_keys':
            self._send_keys_action(element, action)
        # неизвестные action игнорируем

    def _send_keys_action(self, element, action: dict):
        value = action.get('value')
        value_from_creds = action.get('value_from_credentials')

        if value_from_creds:
            value = self.credentials.get(value_from_creds, '')

        if value is None:
            value = ''

        if value == 'ENTER':
            element.send_keys(Keys.ENTER)
        else:
            element.send_keys(value)

    def _find_site_config(self, login_url):
        for site in settings.SITES:
            if site['url'] in login_url:
                return site
        raise ValueError(f"Конфигурация для URL {login_url} не найдена")

    def login(self, login_url):
        site_config = self._find_site_config(login_url)
        self.driver.get(login_url)
        time.sleep(2)

        last_element = None
        for step in site_config.get('steps', []):
            optional = step.get('optional', False)
            element = step.get('element')
            action = step.get('action')

            action_type = action.get('type') if action else None

            if element:
                new_element = self._find_element(element, optional, action_type)
                if optional and new_element is None:
                    continue  # пропускаем optional шаг без элемента
                last_element = new_element
            else:
                new_element = last_element  # используем предыдущий элемент, если нет нового

            self._perform_action(new_element, action)

        time.sleep(2)

        if site_config.get('need_cookies', True):
            return self.driver.get_cookies()
        return None
