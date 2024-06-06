from datetime import datetime

import pytz as pytz
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import sqltypes

moscow_tz = pytz.timezone('Europe/Moscow')
db = SQLAlchemy()


class ArchivedPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    html = db.Column(db.String, nullable=False)
    timestamp = db.Column(sqltypes.TIMESTAMP(timezone=True), default=datetime.utcnow().astimezone(moscow_tz))


class DomainInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))
    whois_protocol = db.Column(db.Text)
    network_info = db.Column(db.Text)
    archived_page_id = db.Column(db.Integer, db.ForeignKey('archived_page.id'))

    archived_page = db.relationship('ArchivedPage', backref=db.backref('pages', lazy='dynamic'))
