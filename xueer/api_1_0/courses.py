# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from ..models import Courses, User
from . import api
from xueer import db


@api.route('courses/<int:page>?<string:sort>&<int:main_cat>&<int:ts_cat>')
def get_courses():
    page = request.args.get('page', 1, type=int)
    pagination = Courses.query.order_by(Courses.comment.count()).paginate(
        page,
        per_page=current_app.config['FLASKY_COURSES_PER_PAGE'],
        error_out=False
    )
    courses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_courses', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_courses', page=page + 1, _external=True)
    return jsonify({
        'course': [course.to_json() for course in courses],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/course/<int:id>')
def get_course_id(id):
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())


@api.route('/courses/<int:id>/like', methods=['POST', 'GET'])
def course_like():
    course = Courses.query.get_or_404(id)
    user = User.query.filter_by(id=current_user.id).first()
    course.user.all().append(user)
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_json()), 200
