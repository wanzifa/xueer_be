# coding: utf-8

from flask import current_app, request, url_for, jsonify
from . import api
from werkzeug.security import generate_password_hash
from ..models import User, Courses, Comments
from xueer.api_1_0.authentication import auth
from xueer.decorators import admin_required
from xueer import db
import json


@api.route('/users/', methods=["GET"])
def get_users():
    """
    获取所有标签信息
    :return:
    """
    page = request.args.get('page', 1, type=int)
    if request.args.get('roleid'):
        roleid = request.args.get('roleid')
        pagination = User.query.filter_by(role_id=roleid).paginate(
            page,
            per_page=current_app.config['XUEER_USERS_PER_PAGE'],
            error_out=False
        )
    else:
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
    return json.dumps(
        [user.to_json() for user in users],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/users/<int:id>/')
def get_user_id(id):
    """
    获取特定id用户的信息
    :param id:
    :return:
    """
    user = User.query.get_or_404(id)
    return jsonify(user.to_json2())


@api.route('/users/', methods=["GET", "POST"])
@admin_required
def new_user():
    """
    创建一个用户
    :return:
    """
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id}), 201, {
        'location': url_for('api.get_user_id', id=user.id, _external=True)
    }


@api.route('/users/<int:id>/', methods=["GET", "PUT"])
@auth.login_required
def update_user(id):
    """
    更新一个用户
    :return:
    """
    user = User.query.get_or_404(id)  # 待更新的用户
    if request.method == 'PUT':
        data_dict = eval(request.data)
        user.username = data_dict.get('username', user.username)
        user.email = data_dict.get('email', user.email)
        if data_dict.get('password'):
            user.password_hash = generate_password_hash(data_dict.get('password'))
        user.qq = data_dict.get('qq', user.qq)
        user.phone = data_dict.get('phone', user.phone)
        user.major = data_dict.get('major', user.major)
        db.session.add(user)
        db.session.commit()
    return jsonify({'update': id}), 200, {
        'location': url_for('api.get_user_id', id=id, _external=True)
    }


@api.route('/users/<int:id>/', methods=["DELETE", "GET"])
@admin_required
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


@api.route('/comments/<int:id>/users/', methods=["GET"])
def get_comments_id_users(id):
    """
    获取特定id的评论的作者
    :param id:
    :return:
    """
    comments = Comments.query.get_or_404(id)
    user = User.query.filter_by(id=comments.user_id).first()
    return jsonify(user.to_json())

