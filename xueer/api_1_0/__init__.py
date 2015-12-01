# coding: utf-8
"""
api:

学而后台 API 模块
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, comments, courses, decorators, errors, teachers, users
