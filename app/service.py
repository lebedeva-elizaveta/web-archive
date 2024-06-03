import imghdr
import re
import validators
import requests
from flask import request, jsonify, render_template
from ipwhois import ipwhois
from whois import whois
import whois
import socket
import ipwhois
import base64
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote


from .main import app
from .models import ArchivedPage, DomainInfo
from .models import db


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


def archive_page():
    try:
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'Требуется URL'})

        if not validators.url(url):
            print(f"Invalid URL: {url}")
            return jsonify({'success': False, 'error': 'Некорректный URL'})

        try:
            response = requests.get(url)
            response.raise_for_status()
            html_code = response.text

            soup = BeautifulSoup(html_code, 'html.parser')

            # CSS
            for link_tag in soup.find_all('link', rel='stylesheet'):
                href = link_tag.get('href')
                if href:
                    try:
                        css_response = requests.get(urljoin(url, href))
                        css_response.raise_for_status()
                        css_data = base64.b64encode(css_response.content).decode('utf-8')
                        link_tag['href'] = f'data:text/css;base64,{css_data}'
                    except requests.RequestException as css_req_err:
                        app.logger.warning('Ошибка при загрузке CSS: %s', str(css_req_err))

            for img_tag in soup.find_all('img'):
                src = img_tag.get('src')
                if src:
                    try:
                        img_response = requests.get(urljoin(url, src))
                        img_response.raise_for_status()
                        img_data = base64.b64encode(img_response.content).decode('utf-8')

                        # расширение - ?
                        img_format = imghdr.what(None, h=img_response.content)

                        if img_format:
                            img_tag['src'] = f'data:image/{img_format};base64,{img_data}'
                        else:
                            app.logger.warning('Неизвестный формат изображения: %s', urljoin(url, src))

                    except requests.RequestException as img_req_err:
                        app.logger.warning('Ошибка загрузки изображения: %s', str(img_req_err))

            for script_tag in soup.find_all('script'):
                # внешние скрипты src
                if 'src' in script_tag.attrs:
                    src = script_tag['src']
                    try:
                        js_response = requests.get(urljoin(url, src))
                        js_response.raise_for_status()
                        js_data = base64.b64encode(js_response.content).decode('utf-8')

                        new_script_tag = soup.new_tag('script')
                        new_script_tag.string = f'/*<![CDATA[*/{js_data}/*]]>*/'
                        script_tag.replace_with(new_script_tag)

                    except requests.RequestException as js_req_err:
                        app.logger.warning('Ошибка при загрузке JavaScript: %s', str(js_req_err))
                # встроенные скрипты
                else:
                    js_content = script_tag.string
                    if js_content:
                        try:
                            new_script_tag = soup.new_tag('script')
                            new_script_tag.string = f'/*<![CDATA[*/{js_content}/*]]>*/'
                            script_tag.replace_with(new_script_tag)
                        except requests.RequestException as js_req_err:
                            app.logger.warning('Ошибка при загрузке JavaScript: %s', str(js_req_err))

            # стили с изображениями
            for div_tag in soup.find_all('div', style=True):
                style_value = div_tag.get('style', '')
                if 'background-image' in style_value:
                    image_url = style_value.split('url("', 1)[-1].split('")')[0]
                    try:
                        img_response = requests.get(urljoin(url, image_url))
                        img_response.raise_for_status()
                        img_data = base64.b64encode(img_response.content).decode('utf-8')
                        div_tag['style'] = f'background-image:url(data:image/png;base64,{img_data})'
                    except requests.RequestException as img_req_err:
                        app.logger.warning('Ошибка загрузки изображения: %s', str(img_req_err))
            # иконки
            for icon_tag in soup.find_all('i', class_='icon'):
                icon_classes = icon_tag.get('class', [])

                fa_class_pattern = re.compile(r'fa-[a-zA-Z0-9-]+')
                fa_classes = [cls for cls in icon_classes if fa_class_pattern.match(cls)]

                if fa_classes:
                    icon_name = fa_classes[0][3:]

                    icon_url = f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/svgs/{icon_name}.svg'

                    head_tag = soup.head
                    style_tag = soup.new_tag('link')
                    style_tag['rel'] = 'stylesheet'
                    style_tag['type'] = 'text/css'
                    style_tag['href'] = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
                    head_tag.append(style_tag)

                    try:
                        icon_response = requests.get(icon_url)
                        icon_response.raise_for_status()
                        icon_data = base64.b64encode(icon_response.content).decode('utf-8')

                        icon_tag['class'] = []
                        icon_tag[
                            'style'] = f'background-image: url(data:image/svg+xml;base64,{icon_data}); background-size: contain; display: inline-block; width: 1em; height: 1em;'
                    except requests.RequestException as icon_req_err:
                        app.logger.warning('Error fetching icon: %s', str(icon_req_err))

            html_code = str(soup)

        except requests.RequestException as req_err:
            return jsonify({'success': False, 'error': f'Ошибка получения HTML: {str(req_err)}'})

        domain_info_data = get_domain_info(url)
        domain_info = DomainInfo(
            domain=domain_info_data.get('domain', ''),
            ip_address=domain_info_data.get('ip_address', ''),
            whois_protocol=domain_info_data.get('whois_protocol', ''),
            network_info=domain_info_data.get('network_info', '')
        )

        db.session.add(domain_info)
        db.session.commit()

        archived_page = ArchivedPage(url=url, html_code=html_code)
        archived_page.domain_info = domain_info

        db.session.add(archived_page)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Страница успешно сохранена'})
    except Exception as e:
        app.logger.error('Error during archive_page: %s', str(e))
        return jsonify({'success': False, 'error': 'Не удалось сохранить'})


def view_page(encoded_url):
    try:
        decoded_url = unquote(encoded_url)
        print(f"Requested URL: {decoded_url}")
        archived_pages = ArchivedPage.query.filter_by(url=decoded_url).order_by(ArchivedPage.timestamp.desc()).all()

        if archived_pages:
            return render_template('list_pages.html', archived_pages=archived_pages)
        else:
            return render_template('error_list_page.html')
    except Exception as e:
        app.logger.error('Ошибка отображения страницы: %s', str(e))
        return render_template('error_page.html', error=str(e))


def show_page(page_id):
    try:
        archived_page = ArchivedPage.query.get(page_id)

        if archived_page:
            return render_template('view_page.html', archived_page=archived_page)
        else:
            return render_template('error_page.html')
    except Exception as e:
        app.logger.error('Error during show_page: %s', str(e))
        return render_template('error_page.html', error=str(e))


def view_domain_info(encoded_url):
    try:
        decoded_url = unquote(encoded_url)
        print(f"Requested URL: {decoded_url}")
        domain_info_data = get_domain_info(decoded_url)
        return render_template('domain_info.html', domain_info=domain_info_data)
    except Exception as e:
        app.logger.error('Error during view_domain_info: %s', str(e))
        return render_template('error_page.html', error=str(e))
