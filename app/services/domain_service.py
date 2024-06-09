from ipwhois import ipwhois
from whois import whois
import whois
import ipwhois
import socket
import logging


class DomainService:
    def __init__(self, url):
        self.url = url
        self.domain_info = {
            'domain': '',
            'ip_address': '',
            'whois_protocol': '',
            'network_info': ''
        }
        self.logger = logging.getLogger(__name__)

    def _handle_error(self, context, e):
        error_message = f"Error {context} for {self.url}: {str(e)}"
        self.logger.error(error_message)
        return error_message

    def _get_whois_info(self):
        try:
            whois_data = whois.whois(self.url)
            self.domain_info['whois_protocol'] = self._format_whois(whois_data) if whois_data else ''
            self.domain_info['domain'] = whois_data.domain if whois_data else ''
        except Exception as e:
            self.domain_info['whois_protocol'] = self._handle_error('getting WHOIS information', e)
            self.domain_info['domain'] = self._handle_error('getting WHOIS information', e)

    @staticmethod
    def _format_whois(whois_data):
        whois_lines = [
            f"domain: {whois_data.domain}",
            f"nserver: {' '.join(whois_data.name_servers)}",
            f"state: {whois_data.status}",
            f"admin-contact: {whois_data.emails if whois_data.emails else ''}",
            f"org: {whois_data.org}",
            f"registrar: {whois_data.registrar}",
            f"created: {whois_data.creation_date.strftime('%Y.%m.%d') if whois_data.creation_date else ''}",
            f"paid-till: {whois_data.expiration_date.strftime('%Y.%m.%d') if whois_data.expiration_date else ''}",
            f"source: {whois_data.source if hasattr(whois_data, 'source') else 'Unknown'}",
        ]
        return '\n'.join(whois_lines)

    def _get_ip_info(self):
        try:
            ip_address = socket.gethostbyname(self.domain_info['domain'])
            self.domain_info['ip_address'] = ip_address
            ipwhois_data = ipwhois.IPWhois(ip_address)
            network_info = ipwhois_data.lookup_rdap()
            network_name = network_info.get('network', {}).get('name', '')
            self.domain_info['network_info'] = network_name
        except socket.gaierror as e:
            self.domain_info['ip_address'] = self._handle_error('resolving IP address', e)
            self.domain_info['network_info'] = self._handle_error('resolving IP address', e)
        except Exception as e:
            self.domain_info['ip_address'] = self._handle_error('getting IP information', e)
            self.domain_info['network_info'] = self._handle_error('getting IP information', e)

    def get_domain_info(self):
        self._get_whois_info()
        self._get_ip_info()
        return self.domain_info
