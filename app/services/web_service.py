import time

from flask import session
from selenium.webdriver.common.by import By
from app.services.auth_service import AuthService
from app.services.selenium_service import get_driver, wait_for_script_condition, wait_for_element_to_disappear


def authorize_and_get_cookies(url):
    driver = get_driver(headless=False)
    auth_service = AuthService(driver)
    cookies = auth_service.login(url)
    driver.quit()
    if "vk.com" in url:
        session['vk_cookies'] = cookies
    elif "edu" in url:
        session['moodle_cookies'] = cookies
    elif "cs" in url:
        session['brs_cookies'] = cookies
    return cookies


def get_cookies(url):
    cookies_mapping = {
        "vk.com": 'vk_cookies',
        "edu": 'moodle_cookies',
        "cs": 'brs_cookies'
    }

    for key, session_key in cookies_mapping.items():
        if key in url:
            return session.get(session_key)

    return None

def fetch_html(url, cookies=None):
    driver = get_driver(headless=False)
    try:
        driver.delete_all_cookies()
        _handle_cookies(driver, url, cookies)
        driver.get(url)
        time.sleep(5)
        _wait_for_jquery(driver)
        return driver.page_source
    finally:
        driver.quit()


def _handle_cookies(driver, url, cookies=None):
    if cookies and "vk.com" in url:
        _add_vk_cookies(driver, cookies)
    else:
        driver.get(url)
        if cookies:
            _add_standard_cookies(driver, cookies)


def _add_vk_cookies(driver, cookies):
    driver.get("https://vk.com")  # Сначала базовый домен
    time.sleep(2)

    for cookie in cookies:
        cookie_dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": ".vk.com",  # Обязательно для ВК
            "path": "/",
            "secure": cookie.get("secure", False),
            "httpOnly": cookie.get("httpOnly", False),
            "expiry": cookie.get("expiry")
        }
        cookie_dict = {k: v for k, v in cookie_dict.items() if v is not None}
        driver.add_cookie(cookie_dict)


def _add_standard_cookies(driver, cookies):
    for cookie in cookies:
        cookie_dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "path": "/"
        }
        driver.add_cookie(cookie_dict)


def _wait_for_jquery(driver):
    jquery_check_script = 'return typeof jQuery !== "undefined"'
    is_jquery_present = driver.execute_script(jquery_check_script)

    if is_jquery_present:
        wait_for_script_condition(driver, 'return jQuery.active == 0')
    else:
        wait_for_script_condition(driver, 'return document.readyState == "complete"')
    wait_for_element_to_disappear(driver, (By.CSS_SELECTOR, ".loading-spinner-class"))
