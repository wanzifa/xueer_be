# coding:utf-8

from flask import jsonify, url_for, request, current_app
from ..models import Tags, Courses
from . import api
from xueer.api_1_0.authentication import auth


@api.route('/tags/')
def get_tags():
    """
    获取所有标签信息
    :return:
    """
    page = request.args.get('page', 1, type=int)
    # pagination = Tags.query.order_by(Tags.courses.count()).paginate(
    pagination = Tags.query.paginate(
        page,
        per_page=current_app.config['XUEER_TAGS_PER_PAGE'],
        error_out=False
    )
    tags = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_tags', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_tags', page=page+1, _external=True)
    return jsonify({
        'course': [tag.to_json() for tag in tags],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/tags/<int:id>/')
def get_tags_id(id):
    """
    获取特定id的标签
    """
    tags = Tags.query.get_or_404(id)
    return jsonify(tags.to_json())


@api.route('/courses/<int:id>/tags/')
def get_courses_id_tags(id):
    """
    获取特定id课程的所有标签
    """
    courses = Courses.query.get_or_404(id)
    return jsonify({
        'tags': [tag.to_json() for tag in courses.tags.all()]
    })
