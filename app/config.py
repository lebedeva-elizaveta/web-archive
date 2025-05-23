import os
import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    IS_DOCKER = os.getenv('IS_DOCKER')
    SITES = []
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
            cls.SITES = []
            cls.URL_NAME_MAPPING = {}

    @classmethod
    def find_name_by_url(cls, url: str) -> str | None:
        for config_url, name in cls.URL_NAME_MAPPING.items():
            if config_url in url:
                return name
        return None

    @classmethod
    def update_sites(cls, new_site: dict):
        existing_sites_by_name = {site['name']: site for site in cls.SITES}

        name = new_site.get('name')
        if not name:
            print("Warning: site without name skipped")
        if name in existing_sites_by_name:
            existing_sites_by_name[name] = new_site
        else:
            existing_sites_by_name[name] = new_site
        cls.SITES = list(existing_sites_by_name.values())
        cls.URL_NAME_MAPPING = {
            site["url"]: site["name"]
            for site in cls.SITES
            if site.get("name") != "vk"
        }


Config.load_yaml()
settings = Config()

FOLDER_FILES = 'app/uploads/files/'
