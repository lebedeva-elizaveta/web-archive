import time

from flask import session
from selenium.webdriver.common.by import By
from app.services.auth_service import AuthService
from app.services.selenium_service import get_driver, wait_for_script_condition, wait_for_element_to_disappear


def authorize_and_fetch_html(url, protected, credentials):
    if "vk.com" in url and protected:
        return _fetch_vk_html(url, credentials)
    cookies = None
    if protected:
        cookies = get_cookies(url)
        if not cookies:
            cookies = _authorize_and_get_cookies(url, credentials)
    return fetch_html(url, cookies)


def _fetch_vk_html(url, credentials):
    driver = get_driver(headless=False)
    try:
        auth_service = AuthService(driver, credentials)
        auth_service.login(url)
        html_code = load_and_fetch_html(driver, url)
        return html_code
    finally:
        driver.quit()


def _authorize_and_get_cookies(url, credentials):
    driver = get_driver(headless=False)
    try:
        auth_service = AuthService(driver, credentials)
        cookies = auth_service.login(url)
        if "edu" in url:
            session['moodle_cookies'] = cookies
        elif "cs" in url:
            session['brs_cookies'] = cookies
        return cookies
    finally:
        if 'vk.com' not in url:
            driver.quit()


def get_cookies(url):
    cookies_mapping = {
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
        driver.get(url)
        if cookies:
            _add_cookies(driver, cookies)
        return load_and_fetch_html(driver, url)
    finally:
        driver.quit()


def load_and_fetch_html(driver, url):
    driver.get(url)
    time.sleep(2)
    _wait_for_jquery(driver)
    return driver.page_source


def _add_cookies(driver, cookies):
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
