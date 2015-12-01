# coding: utf-8
"""
评论API模块
"""

from flask import request, jsonify, url_for, current_app, g
from .. import db
from flask_login import current_user
from ..models import Comments, Courses, User, Permission
from . import api
from .decorators import permission_required


@api.route('/courses/<int:id>/comments/')
def get_comments_id(id):
    """
    获取特定id课程的评论
    :param id: 课程的id
    :return: 评论json数据
    """
    course = Courses.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = course.comment.order_by(Comments.timastamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1, _external=True)
    return jsonify({
        'posts': [comment.to_json for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/courses/<int:id>/comments/hot/')
def hot_comments(id):
    """
    获取特定id课程的热门评论(以3作为热门鉴定)
    :param id: 课程id
    :return: 评论 json 数据
    """
    course = Courses.query.get_or_404(id)
    comments = course.comment.order_by(course.comment.user.count()).all()
    for comment in course.comment:
        if comment.likes > 3:
            comments.append(comment)

    return jsonify({
        'posts': [comment.to_json for comment in comments]
    })


@api.route('/courses/<int:id>/comments/', methods=['POST', 'GET'])
@permission_required(Permission.COMMENT)
def new_comment(id):
    """
    向特定id的课程发布一个评论
    :param id: 课程id
    :return:
    """
    comment = Comments.from_json(request.json)
    comment.author = g.current_user
    comment.course_id = id
    db.session.add(comment)
    db.session.commit()
    return jsonify(
        comment.to_json()), 201, {
               'Location': url_for(
                    'api.get_comments_id',
                    id=comment.course_id, _external=True
               )
           }


@api.route('/comments/<int:id>/like/', methods=['POST', 'GET'])
@permission_required(Permission.COMMENT)
def comment_like(id):
    """
    对特定id的评论点赞
    :param id:
    :return:
    """
    comment = Comments.query.get_or_404(id)
    user = User.filter_by(id=current_user.id).first()
    comment.user.all().append(user)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 200
