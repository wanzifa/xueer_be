# coding: utf-8

from flask import current_app, request, url_for, jsonify
from . import api
from werkzeug.security import generate_password_hash
from ..models import User, Courses
from xueer import db


@api.route('/users/', methods=["GET"])
def get_users():
    """
    获取所有标签信息
    :return:
    """
    page = request.args.get('page', 1, type=int)
    # pagination = Tags.query.order_by(Tags.courses.count()).paginate(
    pagination = User.query.paginate(
        page,
        per_page=current_app.config['XUEER_USERS_PER_PAGE'],
        error_out=False
    )
    users = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_users', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_users', page=page+1, _external=True)
    users_count = len(User.query.all())
    page_count = users_count//current_app.config['XUEER_USERS_PER_PAGE'] + 1
    last = url_for('api.get_users', page=page_count, _external=True)
    return jsonify({
        'course': [user.to_json() for user in users],
        'prev': prev,
        'next': next,
        'count': pagination.total
    }), 200, {'Link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/users/<int:id>/')
def get_user_id(id):
    """
    获取特定id用户的信息
    :param id:
    :return:
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/', methods=["GET", "POST"])
def new_user():
    """
    创建一个用户
    :return:
    """
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json()), 201, {
        'location': url_for('api.get_user_id', id=user.id, _external=True)
    }


@api.route('/users/<int:id>/', methods=["GET", "PUT"])
def update_user(id):
    """
    更新一个用户
    :return:
    """
    user = User.query.get_or_404(id)  # 待更新的用户
    if request.json.get('username'):
        user.username = request.json.get('username')
    if request.json.get('role_id'):
        user.role_id = request.json.get('role_id')
    if request.json.get('email'):
        user.email = request.json.get('email')
    if request.json.get('password'):
        user.password_hash = generate_password_hash(request.json.get('password'))
    if request.json.get('qq'):
        user.qq = request.json.get('qq')
    if request.json.get('phone'):
        user.phone = request.json.get('phone')
    if request.json.get('major'):
        user.major = request.json.get('major')
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json()), 200, {
        'location': url_for('api.get_user_id', id=id, _external=True)
    }


@api.route('/users/<int:id>/', methods=["DELETE", "GET"])
def delete_user(id):
    """
    删除一个用户
    :param id:
    :return:
    """
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({
        'message': '该用户已经被移除'
    })


@api.route('/courses/<int:id>/users/', methods=["GET"])
def get_like_courses_id_users(id):
    """
    获取点赞特定id课程的用户
    :param id:
    :return:
    """
    courses = Courses.query.get_or_404(id)
    return jsonify({
        'users': [user.to_json() for user in courses.users.all()]
    })
