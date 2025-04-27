from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.config import settings


def get_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if settings.IS_DOCKER == 'true':
        driver = webdriver.Remote(
            command_executor='http://selenium:4444/wd/hub',
            options=options
        )
    else:
        # Локально используем стандартный драйвер
        driver = webdriver.Chrome(options=options)
    return driver


def wait_for_element_to_be_present(locator):
    """
    Ожидание появления элемента на странице.
    """
    return EC.presence_of_element_located(locator)


def wait_for_element_to_be_clickable(locator):
    """
    Ожидание, когда элемент станет кликабельным.
    """
    return EC.element_to_be_clickable(locator)


def find_element_if_exists(driver, locator):
    """
    Ищет элемент, и если он существует, возвращает его, иначе возвращает None.
    """
    elements = driver.find_elements(*locator)
    if elements:
        return elements[0]
    return None


def wait_for_script_condition(driver, script):
    """
    Ожидает выполнения условия, переданного в виде скрипта JavaScript.
    """
    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script(script)
    )

def wait_for_element_to_disappear(driver, locator):
    """
    Ожидает, когда элемент исчезнет с экрана.
    """
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located(locator)
    )
