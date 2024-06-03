from flask import request, jsonify, render_template
from .main import app, db
from .models import ArchivedPage, DomainInfo
from . import service
import logging
import sys
from urllib.parse import unquote


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/archive', methods=['POST'])
def archive_page():
    return service.archive_page()


@app.route('/view/<path:encoded_url>')
def view_page(encoded_url):
    return service.view_page(encoded_url)


@app.route('/show_page/<int:page_id>')
def show_page(page_id):
    return service.show_page(page_id)


@app.route('/view_domain_info/<path:encoded_url>')
def view_domain_info(encoded_url):
    return service.view_domain_info(encoded_url)
