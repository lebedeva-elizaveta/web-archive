import os
from flask import render_template, request, jsonify, redirect, send_from_directory, render_template_string

from app.main import app
from app.services.archive_service import ArchiveService


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/archive', methods=['POST'])
def archive_page():
    data = request.json
    url = data.get('url')
    success, message = ArchiveService.add_archive_page(url)
    if success:
        return jsonify({'success': True, 'message': message}), 200
    else:
        return jsonify({'success': False, 'error': message}), 400


@app.route('/view/<path:url>')
def view_page(url):
    success, result = ArchiveService.view_all_pages(url)
    if success:
        return render_template('list_pages.html', archived_pages=result)
    else:
        return render_template('error_page.html', error=result), 404


@app.route('/show_page/<int:page_id>')
def show_page(page_id):
    success, result = ArchiveService.show_page(page_id)
    if not success:
        return render_template('error_page.html', error=result), 404
    return render_template_string(result)


@app.route('/view_domain_info/<path:url>')
def view_domain_info(url):
    success, result = ArchiveService.view_domain_info(url)
    if success:
        return render_template('domain_info.html', domain_info=result)
    else:
        return render_template('error_page.html', error=result), 404


@app.route('/uploads/files/<filename>')
def download_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'app', 'uploads', 'files'), filename)
