from flask import Flask
from flask_migrate import Migrate

from .config import settings
from .models import db

app = Flask(__name__)
app.config.from_object(settings)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    from . import routes
    db.create_all()
