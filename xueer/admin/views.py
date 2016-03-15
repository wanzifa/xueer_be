# coding: utf-8

from . import admin
from flask import render_template
from flask_login import login_required
# from xueer.decorators import admin_login


@admin.route('/')
@login_required
def index():
    return render_template("admin/index.html")

