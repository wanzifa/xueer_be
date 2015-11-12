from flask import jsonify, url_for, request, current_app
from ..models import Courses


@api.route('/courses')
def get_courses():
    page = request.args.get('page', 1, type = int)
    pagination = Courses.query.paginate(
        page,
        per_page = current_app.config['FLASKY_COURSES_PER_PAGE'],
        error_out = False
    )
    courses = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_courses', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_courses', page=page+1, _external=True)
    return jsonify({
        'course': [course.to_json() for course in courses],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/courses/<int:id>')
def get_course_id():
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())
