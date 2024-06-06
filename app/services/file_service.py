import os
import uuid

from app.config import FOLDER_FILES


class FileService:
    @staticmethod
    def save_file(html_content, upload_folder):
        file_processor = FileProcessor(html_content, upload_folder)
        return file_processor.save()

    @staticmethod
    def open(filename):
        full_file_path = os.path.join(FOLDER_FILES, filename)

        if not os.path.exists(full_file_path):
            raise FileNotFoundError(f"Файл {full_file_path} не найден")

        with open(full_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        return html_content


class FileProcessor:
    def __init__(self, html_content, upload_folder):
        self.html_content = html_content
        self.upload_folder = upload_folder

    def save(self):
        unique_filename = str(uuid.uuid4()) + '.html'
        processed_file_path = os.path.join(self.upload_folder, unique_filename)
        with open(processed_file_path, 'w+', encoding="utf-8") as output_file:
            output_file.write(self.html_content)
        return processed_file_path
