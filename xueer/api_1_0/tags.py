# coding:utf-8

from flask import jsonify, url_for, request, current_app
from ..models import Tags, Courses, Search
from . import api
from xueer import db
import json
from xueer.api_1_0.authentication import auth
import jieba


@api.route('/tags/', methods=["GET"])
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
    prev = ""
    if pagination.has_prev:
        prev = url_for('api.get_tags', page=page-1, _external=True)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_tags', page=page+1, _external=True)
    tags_count = len(Tags.query.all())
    if tags_count % current_app.config['XUEER_TAGS_PER_PAGE'] == 0:
        page_count = tags_count//current_app.config['XUEER_TAGS_PER_PAGE']
    else:
        page_count = tags_count//current_app.config['XUEER_TAGS_PER_PAGE']+1
    last = url_for('api.get_tags', page=page_count, _external=True)
    return json.dumps(
        [tag.to_json() for tag in tags],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/tags/<int:id>/', methods=["GET"])
def get_tags_id(id):
    """
    获取特定id的标签
    """
    tags = Tags.query.get_or_404(id)
    return jsonify(tags.to_json())


@api.route('/tags/', methods=["GET", "POST"])
def new_tag(id):
    """
    向特定的课程创建一个新的tag
    """
    if request.method == "POST":
        tag = Tags.from_json(request.json)
        tag.course_id = id
        db.session.add(tag)
        db.session.commit()
        return jsonify({'id': tag.id}), 201, {
            # location 会自动写在头部
            'location': url_for('api.get_tags_id', id=tag.id, _external=True)
        }


@api.route('/tags/<int:id>', methods=["GET", "DELETE"])
def delete_tags(id):
    tag = Tags.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(tag)
        db.session.commit()
        return jsonify({
            'message': '该标签已移除'
        })


@api.route('/courses/<int:id>/tags/')
def get_courses_id_tags(id):
    """
    获取特定id课程的所有标签
    """
    courses = Courses.query.get_or_404(id)
    return jsonify({
        'tags': [tag.to_json() for tag in courses.tags.all()]
    })
