from ipwhois import ipwhois
from sqlalchemy.exc import SQLAlchemyError
from whois import whois
import whois
import socket
import ipwhois

from main import app
from models import db


def clear_tables():
    with app.app_context():
        try:
            sql_query = "TRUNCATE TABLE archived_page RESTART IDENTITY CASCADE"
            db.session.execute(db.text(sql_query))
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")


def get_domain_info(url):
    domain_info = {'ip_address': ''}
    try:
        whois_data = whois.whois(url)
        domain_info['whois_protocol'] = whois_data.text if whois_data else ''
        domain_info['domain'] = whois_data.domain
        try:
            ip_address = socket.gethostbyname(domain_info['domain'])
            domain_info['ip_address'] = ip_address
            ipwhois_data = ipwhois.IPWhois(ip_address)
            network_info = ipwhois_data.lookup_rdap()
            network_name = network_info.get('network', {}).get('name', '')
            domain_info['network_info'] = network_name
        except Exception as e:
            app.logger.error('Error resolving IP address for %s: %s', domain_info['domain'], str(e))
            domain_info['ip_address'] = f"Error: {str(e)}"
            domain_info['network_info'] = f"Error: {str(e)}"
    except Exception as e:
        app.logger.error('Error during get_domain_info: %s', str(e))
        domain_info['domain'] = f"Error: {str(e)}"
        domain_info['whois_protocol'] = f"Error: {str(e)}"

    return domain_info
