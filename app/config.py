import os
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


settings = Config()

FOLDER_FILES = 'app/uploads/files/'
