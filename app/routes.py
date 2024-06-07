import os
from flask import render_template, request, redirect, send_from_directory, render_template_string, url_for, \
    session, flash, jsonify

from app.exceptions import UserAlreadyExistsException
from app.main import app
from app.models import db
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
        email = request.form['email']
        password = request.form['password']
        try:
            if UserService.if_exist(email):
                raise UserAlreadyExistsException()
            user_service_ex.create_user(email, password)
            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('login'))
        except UserAlreadyExistsException:
            flash('Пользователь с таким email уже зарегистрирован', 'error')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        result, user_id = user_service_ex.login_user(email, password)
        if result:
            session['user_id'] = user_id
            session['logged_in'] = True
            flash('Вы вошли успешно!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неправильный email или пароль', 'error')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))


@app.route('/archive', methods=['POST'])
def archive_page():
    data = request.json
    url = data.get('url')
    user_id = session.get('user_id')
    success, message = ArchiveService.add_archive_page(url, user_id)
    if success:
        flash(message, 'success')
        return jsonify({'success': True, 'message': message}), 200
    else:
        flash(message, 'error')
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
