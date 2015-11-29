# coding:utf-8

from flask import jsonify, url_for, request, current_app
from ..models import Tags
from . import api


@api.route('/tags/<int:page>')
def get_tags():
    page = request.args.get('page', 1, type=int)
    pagination = Tags.query.order_by(Tags.courses.count()).paginate(
        page,
        per_page=current_app.config['XUEER_TAGS_PER_PAGE'],
        error_out=False
    )
    tags = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_tags', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_tags', page=page + 1, _external=True)
    return jsonify({
        'course': [tag.to_json() for tag in tags],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/tags/<int:id>/courses/<int:page>?<string:sort>&<int:main_cat>&<int:ts_cat>')
def get_tags_id():
    pass
