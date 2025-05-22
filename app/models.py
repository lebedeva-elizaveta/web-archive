from datetime import datetime, timezone
from email.policy import default

import pytz as pytz
from flask_sqlalchemy import SQLAlchemy

moscow_tz = pytz.timezone('Europe/Moscow')
db = SQLAlchemy()

def current_utc_time():
    return datetime.now(timezone.utc)


class ArchivedPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    html = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    protected = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', backref=db.backref('pages', lazy=True))


class DomainInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(100))
    whois_protocol = db.Column(db.Text)
    network_info = db.Column(db.Text)
    archived_page_id = db.Column(db.Integer, db.ForeignKey('archived_page.id'))

    archived_page = db.relationship('ArchivedPage', backref=db.backref('domains', lazy=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
