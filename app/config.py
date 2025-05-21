import os

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    USERNAME_MOODLE = os.getenv('USERNAME_MOODLE')
    PASSWORD_MOODLE = os.getenv('PASSWORD_MOODLE')
    USERNAME_BRS = os.getenv('USERNAME_BRS')
    PASSWORD_BRS = os.getenv('PASSWORD_BRS')
    VK_PHONE = os.getenv('VK_PHONE')
    VK_CODE = os.getenv('VK_CODE')
    VK_PASSWORD = os.getenv('VK_PASSWORD')
    IS_DOCKER = os.getenv('IS_DOCKER')
    SITES = {}
    URL_NAME_MAPPING = {}

    @classmethod
    def load_yaml(cls, path='sites_config.yaml'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cls.SITES = yaml.safe_load(f)
                cls.URL_NAME_MAPPING = {
                    site["url"]: site["name"]
                    for site in cls.SITES
                    if site.get("name") != "vk"
                }
        except Exception as e:
            print(f"Ошибка загрузки YAML-конфига: {e}")
            cls.SITES = {}
            cls.URL_NAME_MAPPING = {}

    @classmethod
    def find_name_by_url(cls, url: str) -> str | None:
        for config_url, name in cls.URL_NAME_MAPPING.items():
            if config_url in url:
                return name
        return None


Config.load_yaml()

settings = Config()

FOLDER_FILES = 'app/uploads/files/'
