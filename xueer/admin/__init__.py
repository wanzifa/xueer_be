# coding: utf-8
"""
    admin: admin site for xueer

    学而管理后台
"""

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views, forms
