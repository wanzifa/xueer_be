# coding: utf-8

from flask import current_app, request, url_for, jsonify
from . import api
from ..models import User


@api.route('/users/<int:id>/')
def get_user_id(id):
    """
    获取特定id用户的信息
    :param id:
    :return:
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())
