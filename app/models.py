from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ArchivedPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    html = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, default=db.func.now())
    domain_info = db.relationship('DomainInfo', backref='archived_page', uselist=False)


class DomainInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))
    whois_protocol = db.Column(db.Text)
    network_info = db.Column(db.Text)
    archived_page_id = db.Column(db.Integer, db.ForeignKey('archived_page.id'))
