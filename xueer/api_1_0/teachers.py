# coding: utf-8

from flask import jsonify, request, current_app, url_for
from . import api
from ..models import Teachers
from xueer import db
from xueer.api_1_0.authentication import auth


@api.route('/teachers/<int:id>/', methods=["GET"])
def get_teacher_id(id):
    """
    根据id获取老师信息
    :param id:
    :return:
    """
    teacher = Teachers.query.get_or_404(id)
    return jsonify(teacher.to_json())


@api.route('/teachers/', methods=["GET", "POST"])
def new_teacher():
    """
    创建一个老师
    :return:
    """
    teacher = Teachers.from_json(request.json)
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.to_json()), 201, {
        'location': url_for('api.get_teacher_id', id=teacher.id, _external=True)
    }


@api.route('/teachers/<int:id>', methods=["GET", "PUT"])
def update_teacher(id):
    """
    更新一个老师
    :param id:
    :return:
    """
    teacher = Teachers.query.get_or_404(id)
    if request.args.get('name'):
        teacher.name = request.args.get('name')
    if request.args.get('department'):
        teacher.department = request.args.get('department')
    if request.args.get('introduction'):
        teacher.introduction = request.args.get('introduction')
    if request.args.get('phone'):
        teacher.phone = request.args.get('phone')
    if request.args.get('weibo'):
        teacher.weibo = request.args.get('weibo')
    db.session.add(teacher)
    db.session.commit()
    return jsonify(teacher.to_json()), 200


@api.route('/teachers/<int:id>', methods=["GET", "DELETE"])
def delete_teacher(id):
    """
    删除一个用户
    :param id:
    :return:
    """
    teacher = Teachers.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    return jsonify({
        'message': '这个老师已经被删了'
    })
