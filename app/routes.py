import os
from flask import render_template, request, redirect, send_from_directory, render_template_string, url_for, \
    session, flash, jsonify
from marshmallow import ValidationError

from app.exceptions import UserAlreadyExistsException
from app.main import app
from app.models import db
from app.schemas import ArchivedPageSchema, DomainInfoSchema
from app.services.archive_service import ArchiveService
from app.services.user_service import UserService

user_service_ex = UserService(db)


@app.route('/')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        try:
            if UserService.if_exist(email):
                raise UserAlreadyExistsException()
            user_service_ex.create_user(email, password)
            return jsonify({"success": True, "message": "Регистрация успешна! Теперь вы можете войти."}), 200
        except UserAlreadyExistsException:
            return jsonify({"success": False, "message": "Пользователь с таким email уже зарегистрирован."}), 400
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        result, user_id = user_service_ex.login_user(email, password)
        if result:
            session['user_id'] = user_id
            session['logged_in'] = True
            return jsonify({"success": True, "message": "Вы вошли успешно!"}), 200
        else:
            return jsonify({"success": False, "message": "Неправильный email или пароль"}), 401

    return render_template('login.html')



@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('vk_cookies', None)
    session.pop('moodle_cookies', None)
    session.pop('brs_cookies', None)
    session.pop('_flashes', None)
    return jsonify({'success': True, 'message': 'Вы вышли из системы'})


@app.route('/archive', methods=['POST'])
def archive_page():
    data = request.json
    url = data.get('url')
    is_protected = data.get('protected', False)
    user_id = session.get('user_id')
    try:
        ArchivedPageSchema().load({'url': url, 'html': '<dummy>', 'user_id': user_id, 'protected': is_protected})
    except ValidationError:
        message = 'Некорректный URL'
        flash(message, 'error')
        return jsonify({'success': False, 'error': message}), 400
    success, message = ArchiveService.add_archive_page(url, user_id, is_protected)
    if success:
        flash(message, 'success')
        return jsonify({'success': True, 'message': message}), 200
    else:
        flash(message, 'error')
        return jsonify({'success': False, 'error': message}), 400


@app.route('/view/<path:url>')
def view_pages(url):
    user_id = session.get('user_id')
    if not url:
        flash('Введите URL', 'error')
        return redirect(url_for('index'))
    success, result = ArchiveService.view_all_pages(url, user_id)
    if success:
        archived_page_schema = ArchivedPageSchema(many=True)
        serialized_result = archived_page_schema.dump(result)
        return render_template('list_pages.html', archived_pages=serialized_result)
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


@app.route('/get_domain_info/<int:page_id>')
def get_domain_info(page_id):
    user_id = session.get('user_id')
    success, domain_info = ArchiveService.get_domain_info(page_id, user_id)
    if success:
        domain_info_schema = DomainInfoSchema()
        domain_info_serialized = domain_info_schema.dump(domain_info)
        return render_template('domain_info.html', domain_info=domain_info_serialized)
    else:
        return render_template('error_page.html', error=domain_info), 404


@app.route('/uploads/files/<filename>')
def download_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'app', 'uploads', 'files'), filename)
