import os
import requests
from bs4 import BeautifulSoup
from marshmallow import ValidationError

from app.models import DomainInfo, ArchivedPage, db
from .file_service import FileService
from .html_service import HTMLProcessor
from .domain_service import DomainService
from ..schemas import ArchivedPageSchema, DomainInfoSchema


class ArchiveService:
    model_page = ArchivedPage
    model_domain_info = DomainInfo

    @classmethod
    def create_page(cls, data):
        try:
            validated_data = ArchivedPageSchema().load(data)
        except ValidationError:
            raise
        new_page = cls.model_page(**validated_data)
        db.session.add(new_page)
        db.session.commit()
        return new_page

    @classmethod
    def create_domain_info(cls, data):
        try:
            validated_data = DomainInfoSchema().load(data)
        except ValidationError:
            raise
        new_info = cls.model_domain_info(**validated_data)
        db.session.add(new_info)
        db.session.commit()
        return new_info

    @staticmethod
    def add_archive_page(url):
        html_code = ArchiveService._fetch_html(url)
        if not html_code:
            return False, 'Ошибка получения HTML'
        processed_html = ArchiveService._process_html(html_code, url)
        if not processed_html:
            return False, 'Ошибка обработки HTML'
        new_page = ArchiveService._save_archived_page(url, processed_html)
        domain_info = ArchiveService._save_domain_info(url, new_page.id)
        if not domain_info:
            return False, 'Ошибка сохранения информации о домене'
        return True, 'Страница успешно сохранена'

    @staticmethod
    def view_all_pages(url):
        try:
            archived_pages = ArchiveService._get_archived_pages(url)
            if archived_pages:
                return True, archived_pages
            else:
                return False, 'Страницы не найдены'
        except Exception as e:
            return False, str(e)

    @classmethod
    def show_page(cls, page_id):
        try:
            archived_page = cls.model_page.query.get(page_id)
            if archived_page:
                success, file_path = ArchiveService.load_page_from_file(archived_page.html)
                if success:
                    return True, file_path
                else:
                    return False, 'Ошибка при загрузке HTML из файла'
            else:
                return False, 'Страница не найдена'
        except Exception as e:
            return False, str(e)

    @staticmethod
    def view_domain_info(url):
        try:
            domain_info = ArchiveService._get_domain_info(url)
            return True, domain_info
        except Exception as e:
            return False, str(e)

    @staticmethod
    def _fetch_html(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f'Ошибка получения HTML: {str(e)}')

    @staticmethod
    def _process_html(html_code, url):
        try:
            soup = BeautifulSoup(html_code, 'html.parser')
            html_processor = HTMLProcessor(soup, url)
            html_processor.process_css()
            html_processor.process_images()
            html_processor.process_scripts()
            html_processor.process_inline_styles()
            html_processor.process_icons()
            result = html_processor.process_and_save_html()
            return result
        except Exception as e:
            raise Exception(f'Ошибка обработки HTML: {str(e)}')

    @staticmethod
    def _save_domain_info(url, page_id):
        domain_service = DomainService(url)
        domain_info_data = domain_service.get_domain_info()
        domain_info_data["archived_page_id"] = page_id
        result = ArchiveService.create_domain_info(domain_info_data)
        return result

    @staticmethod
    def _save_archived_page(url, html_path):
        data = {
            "url": url,
            "html": html_path
        }
        result = ArchiveService.create_page(data)
        return result

    @classmethod
    def _get_archived_pages(cls, url):
        try:
            return cls.model_page.query.filter_by(url=url).order_by(
                cls.model_page.timestamp.desc()
            ).all()
        except Exception as e:
            raise Exception(f'Ошибка получения архивных страниц: {str(e)}')

    @staticmethod
    def _get_domain_info(url):
        try:
            domain_service = DomainService(url)
            domain_info_data = domain_service.get_domain_info()
            return domain_info_data
        except Exception as e:
            raise Exception(f'Ошибка получения информации о домене: {str(e)}')

    @staticmethod
    def load_page_from_file(html_code):
        try:
            filename = os.path.basename(html_code)
            result = FileService.open(filename)
            return True, result
        except Exception as e:
            return False, str(e)
