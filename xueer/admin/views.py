# coding: utf-8

from . import admin
from flask import render_template, request
from flask_login import login_required
# from xueer.decorators import admin_login


@admin.route('/')
@login_required
def index():
    args = request.args
    return render_template("admin/index.html")

