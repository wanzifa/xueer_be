# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from ..models import Courses, User, Tags
from . import api
from xueer import db
from xueer.api_1_0.authentication import auth


@api.route('/courses/')  # ?string=sort&main_cat&ts_cat
def get_courses():
    """
    获取全部课程
    排序存在问题
    """
    page = request.args.get('page', 1, type=int)
    if request.args.get('teacher'):
        # /api/v1.0/courses/?teacher=1
        # 获取id为1的老师教学的所有课
        pagination = Courses.query.filter_by(teacher_id=request.args.get('teacher')).paginate(
            page,
            per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
            error_out=False
        )
    if request.args.get('sort') == 'view':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                pagination = Courses.query.filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
            else:
                pagination = Courses.query.filter_by(
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
    elif request.args.get('sort') == 'like':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                pagination = Courses.query.filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
            else:
                pagination = Courses.query.filter_by(
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
    else:
        pagination = Courses.query.paginate(
            # 查询对象query具有paginate属性
            page,
            per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
            error_out=False
        )
    courses = pagination.items
    prev = None  # should init
    if pagination.has_prev:
        prev = url_for('api.get_courses', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_courses', page=page + 1, _external=True)
    return jsonify({
        'course': [course.to_json() for course in courses],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/courses/<int:id>/')
def get_course_id(id):
    """
    获取特定id课程的信息
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())


@api.route('/courses/<int:id>/like/', methods=['GET', 'PUT'])
def course_like(id):
    """
    向特定id的课程点赞
    更新资源
    登录用户都可以点赞
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    course.users.all().append(current_user)
    db.session.add(course)
    db.session.commit()
    # PUT 更新资源返回 200 状态码
    return jsonify(course.to_json()), 200


@api.route('/courses/<int:id>/like/', methods=['GET', 'DELETE'])
def delete_course_like(id):
    """
    登录用户可以取消点赞
    """
    course = Courses.query.get_or_404(id)
    if current_user not in course.users.all():
        return jsonify({'error':'你还未点赞哦'}), 403
    else:
        course.users.all().remove(current_user)
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_json()), 200


@api.route('/tags/<int:id>/courses/')
def get_tags_id_courses(id):
    """
    获取特定id的tag对应的所有课程
    :param id: tag的id
    :return: 该id tag对应的所有课程
    """
    tags = Tags.query.get_or_404(id)
    return jsonify({
        'courses': [course.to_json for course in tags.courses.all()]
    })
