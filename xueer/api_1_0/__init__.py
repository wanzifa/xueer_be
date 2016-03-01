# coding: utf-8
"""
    api: rest api

        restfull_rest

    学而后台 API 模块
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, comments, courses, decorators, errors, register, tags, teachers, tips, users, like, search, category, test
