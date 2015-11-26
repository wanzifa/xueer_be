# coding: utf-8

from flask import request, jsonify, url_for, current_app, g
from .. import db
from ..models import Comments, Courses, User, Permission
from . import api
from .decorators import permission_required


@api.route('/courses/<int:id>/comments')
def get_comments_id(id):
    course = Courses.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = course.comment.order_by(Comments.timastamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'posts':[comment.to_json for comment in comments],
        'prev': prev,
        'next': next,
        'conut': pagination.total
    })


@api.route('/courses/<int:id>/comments', methods = ['POST', 'GET'])
@permission_required(Permission.COMMENT)
def new_comment(id):
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
