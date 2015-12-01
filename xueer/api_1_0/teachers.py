# coding: utf-8

from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Teachers
from xueer.api_1_0.authentication import auth


@auth.login_required
@api.route('/teachers/<int:id>')
def get_teacher_id(id):
    """
    根据id获取老师信息
    :param id:
    :return:
    """
    teacher = Teachers.query.get_or_404(id)
    return jsonify(teacher.to_json())
