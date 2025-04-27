import filetype
import re
import base64
import asyncio
import aiohttp
from urllib.parse import urljoin
from app.config import FOLDER_FILES
from app.main import app
from app.services.file_service import FileService


class HTMLProcessor:
    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    async def process_all(self):
        await self.process_css()
        await self.process_images()
        await self.process_scripts()
        await self.process_inline_styles()
        await self.process_icons()
        return await self.process_and_save_html()

    async def process_and_save_html(self):
        try:
            processed_html = str(self.soup)
            html_filename = FileService.save_file(processed_html, FOLDER_FILES) if processed_html else None
            return html_filename
        except Exception as e:
            app.logger.error('Ошибка при сохранении HTML в файл: %s', str(e))
            return None

    async def process_css(self):
        tasks = []
        for link_tag in self.soup.find_all('link', rel='stylesheet'):
            href = link_tag.get('href')
            if href:
                tasks.append(self._process_css_link(href, link_tag))
        await asyncio.gather(*tasks)

    async def process_images(self):
        tasks = []
        for img_tag in self.soup.find_all('img'):
            src = img_tag.get('src')
            if src:
                tasks.append(self._process_image(src, img_tag))
        await asyncio.gather(*tasks)

    async def process_scripts(self):
        tasks = []
        for script_tag in self.soup.find_all('script'):
            if 'src' in script_tag.attrs:
                src = script_tag['src']
                tasks.append(self._process_script(src, script_tag))
            else:
                tasks.append(self._process_script_content(script_tag))
        await asyncio.gather(*tasks)

    async def process_inline_styles(self):
        tasks = []
        for div_tag in self.soup.find_all('div', style=True):
            tasks.append(self._process_inline_style(div_tag))
        await asyncio.gather(*tasks)

    async def process_icons(self):
        tasks = []
        for icon_tag in self.soup.find_all('i', class_='icon'):
            tasks.append(self._process_icon(icon_tag))
        await asyncio.gather(*tasks)

    async def _process_css_link(self, href, link_tag):
        href = self._normalize_url(href)
        css_content = await self._fetch_url_content(href)
        if css_content:
            css_data_base64 = self._base64_encode(css_content)
            link_tag['href'] = f'data:text/css;base64,{css_data_base64}'

    async def _process_script(self, src, script_tag):
        src = self._normalize_url(src)
        js_content = await self._fetch_url_content(src)
        if js_content:
            js_data_base64 = self._base64_encode(js_content)
            new_script_tag = self.soup.new_tag('script')
            new_script_tag.string = f'/*<![CDATA[*/{js_data_base64}/*]]>*/'
            script_tag.replace_with(new_script_tag)

    async def _process_script_content(self, script_tag):
        js_content = script_tag.string
        if js_content:
            new_script_tag = self.soup.new_tag('script')
            new_script_tag.string = f'/*<![CDATA[*/{js_content}/*]]>*/'
            script_tag.replace_with(new_script_tag)

    async def _process_image(self, src, img_tag):
        src = self._normalize_url(src)
        img_content = await self._fetch_url_content(src)
        if img_content:
            kind = filetype.guess(img_content)
            if kind and kind.mime.startswith('image/'):
                img_data_base64 = self._base64_encode(img_content)
                img_format = kind.extension
                img_tag['src'] = f'data:image/{img_format};base64,{img_data_base64}'

    async def _process_inline_style(self, div_tag):
        style_value = div_tag.get('style', '')
        if 'background-image:url(' in style_value:
            image_url = self._extract_image_url(style_value)
            if image_url:
                image_url = self._normalize_url(image_url)
                img_content = await self._fetch_url_content(image_url)
                if img_content:
                    self._update_div_tag_with_base64_image(div_tag, style_value, img_content)

    @staticmethod
    def _extract_image_url(style_value):
        start_index = style_value.find('background-image:url(') + len('background-image:url(')
        end_index = style_value.find(')', start_index)
        if end_index != -1:
            return style_value[start_index:end_index].strip('\'"')
        return None

    def _update_div_tag_with_base64_image(self, div_tag, style_value, img_content):
        kind = filetype.guess(img_content)
        if kind and kind.mime.startswith('image/'):
            img_format = kind.extension
            img_data_base64 = self._base64_encode(img_content)
            start_index = style_value.find('background-image:url(') + len('background-image:url(')
            end_index = style_value.find(')', start_index)
            div_tag['style'] = (
                    style_value[:start_index] +
                    f'data:image/{img_format};base64,{img_data_base64})' +
                    style_value[end_index + 1:]
            )

    async def _process_icon(self, icon_tag):
        icon_classes = icon_tag.get('class', [])
        fa_class_pattern = re.compile(r'fa-[a-zA-Z0-9-]+')
        fa_classes = [cls for cls in icon_classes if fa_class_pattern.match(cls)]

        if fa_classes:
            icon_name = fa_classes[0][3:]
            icon_url = f'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/svgs/{icon_name}.svg'
            await self._ensure_stylesheet_link()
            icon_content = await self._fetch_url_content(icon_url)
            if icon_content:
                icon_data_base64 = self._base64_encode(icon_content)
                icon_tag['class'] = []
                icon_tag['style'] = f'background-image: url(data:image/svg+xml;base64,{icon_data_base64}); ' \
                                    f'background-size: contain; display: inline-block; width: 1em; height: 1em;'

    @staticmethod
    def _normalize_url(url):
        if url.startswith('//'):
            url = 'https:' + url
        return url

    async def _fetch_url_content(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(urljoin(self.url, url)) as response:
                    response.raise_for_status()
                    return await response.read()
            except aiohttp.ClientError as e:
                app.logger.warning(f'Ошибка при загрузке содержимого по адресу {url}: {e}')
                return None

    @staticmethod
    def _base64_encode(content):
        return base64.b64encode(content).decode('utf-8')

    async def _ensure_stylesheet_link(self):
        if not self.soup.find('link', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'):
            head_tag = self.soup.head
            style_tag = self.soup.new_tag('link')
            style_tag['rel'] = 'stylesheet'
            style_tag['type'] = 'text/css'
            style_tag['href'] = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
            head_tag.append(style_tag)
