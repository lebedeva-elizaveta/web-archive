import imghdr
import re

import requests
import base64
from urllib.parse import urljoin

from app.config import FOLDER_FILES
from app.main import app
from app.services.file_service import FileService


class HTMLProcessor:
    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    def process_and_save_html(self):
        try:
            processed_html = str(self.soup)
            html_filename = FileService.save_file(processed_html, FOLDER_FILES) if processed_html else None
            return html_filename
        except Exception as e:
            app.logger.error('Ошибка при сохранении HTML в файл: %s', str(e))
            return None

    def process_css(self):
        for link_tag in self.soup.find_all('link', rel='stylesheet'):
            href = link_tag.get('href')
            if href:
                self._process_css_link(href, link_tag)

    def process_images(self):
        for img_tag in self.soup.find_all('img'):
            src = img_tag.get('src')
            if src:
                self._process_image(src, img_tag)

    def process_scripts(self):
        for script_tag in self.soup.find_all('script'):
            if 'src' in script_tag.attrs:
                src = script_tag['src']
                self._process_script(src, script_tag)
            else:
                self._process_script_content(script_tag)

    def process_inline_styles(self):
        for div_tag in self.soup.find_all('div', style=True):
            self._process_inline_style(div_tag)

    def process_icons(self):
        for icon_tag in self.soup.find_all('i', class_='icon'):
            self._process_icon(icon_tag)

    def _process_css_link(self, href, link_tag):
        try:
            css_response = requests.get(urljoin(self.url, href))
            css_response.raise_for_status()
            css_data = base64.b64encode(css_response.content).decode('utf-8')
            link_tag['href'] = f'data:text/css;base64,{css_data}'
        except requests.RequestException as css_req_err:
            app.logger.warning('Ошибка при загрузке CSS: %s', str(css_req_err))

    def _process_script(self, src, script_tag):
        try:
            js_response = requests.get(urljoin(self.url, src))
            js_response.raise_for_status()
            js_data = base64.b64encode(js_response.content).decode('utf-8')
            new_script_tag = self.soup.new_tag('script')
            new_script_tag.string = f'/*<![CDATA[*/{js_data}/*]]>*/'
            script_tag.replace_with(new_script_tag)

        except requests.RequestException as js_req_err:
            app.logger.warning('Ошибка при загрузке JavaScript: %s', str(js_req_err))

    def _process_script_content(self, script_tag):
        js_content = script_tag.string
        if js_content:
            new_script_tag = self.soup.new_tag('script')
            new_script_tag.string = f'/*<![CDATA[*/{js_content}/*]]>*/'
            script_tag.replace_with(new_script_tag)

    def _process_image(self, src, img_tag):
        try:
            if src.startswith('//'):
                src = 'https:' + src
            img_response = requests.get(urljoin(self.url, src))
            img_response.raise_for_status()
            img_data = base64.b64encode(img_response.content).decode('utf-8')
            img_format = imghdr.what(None, h=img_response.content)

            if img_format:
                img_tag['src'] = f'data:image/{img_format};base64,{img_data}'

        except requests.RequestException as img_req_err:
            app.logger.warning('Ошибка загрузки изображения: %s', str(img_req_err))

    def _process_inline_style(self, div_tag):
        style_value = div_tag.get('style', '')
        if 'background-image' in style_value:
            image_url = style_value.split('url("', 1)[-1].split('")')[0]
            if image_url.startswith('//'):
                image_url = 'https:' + image_url
            try:
                img_response = requests.get(urljoin(self.url, image_url))
                img_response.raise_for_status()
                img_data = base64.b64encode(img_response.content).decode('utf-8')
                div_tag['style'] = f'background-image:url(data:image/png;base64,{img_data})'
            except requests.RequestException as img_req_err:
                app.logger.warning('Ошибка загрузки изображения: %s', str(img_req_err))

    def _process_icon(self, icon_tag):
        icon_classes = icon_tag.get('class', [])
        fa_class_pattern = re.compile(r'fa-[a-zA-Z0-9-]+')
        fa_classes = [cls for cls in icon_classes if fa_class_pattern.match(cls)]

        if fa_classes:
            icon_name = fa_classes[0][3:]
            icon_url = f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/svgs/{icon_name}.svg'
            head_tag = self.soup.head
            style_tag = self.soup.new_tag('link')
            style_tag['rel'] = 'stylesheet'
            style_tag['type'] = 'text/css'
            style_tag['href'] = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
            head_tag.append(style_tag)
            try:
                if icon_url.startswith('//'):
                    icon_url = 'https:' + icon_url
                icon_response = requests.get(icon_url)
                icon_response.raise_for_status()
                icon_data = base64.b64encode(icon_response.content).decode('utf-8')
                icon_tag['class'] = []
                icon_tag[
                    'style'] = f'background-image: url(data:image/svg+xml;base64,{icon_data}); background-size: contain; display: inline-block; width: 1em; height: 1em;'
            except requests.RequestException as icon_req_err:
                app.logger.warning('Ошибка при загрузке иконки: %s', str(icon_req_err))
