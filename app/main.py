from flask import Flask
from flask_migrate import Migrate

from app.config import settings
from app.models import db
from app.services.selenium_service import get_driver

app = Flask(__name__)
app.config.from_object(settings)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    from app import routes
    db.create_all()


@app.teardown_appcontext
def shutdown_driver(exception=None):
    """ Закрытие драйвера после завершения работы приложения """
    if driver:
        driver.quit()
        print('end')
