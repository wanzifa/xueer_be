# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from ..models import Courses, User, Tags
from . import api
from xueer import db
import json


@api.route('/courses/', methods=["GET"])  # ?string=sort&main_cat&ts_cat
def get_courses():
    """
    获取全部课程
    排序存在问题
    """
    global pagination
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
    # <> 当页面不存在是返回空
    prev = ""  # should init
    if pagination.has_prev:
        prev = url_for('api.get_courses', page=page - 1, _external=True)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_courses', page=page + 1, _external=True)
    courses_count = len(Courses.query.all())
    if courses_count%current_app.config['XUEER_COURSES_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']+1
    last = url_for('api.get_courses', page=page_count, _external=True)
    return json.dumps(
        [course.to_json() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'Link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}



@api.route('/courses/<int:id>/', methods=["GET"])
def get_course_id(id):
    """
    获取特定id课程的信息
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    return jsonify(course.to_json())


@api.route('/courses/', methods=["GET", "POST"])
def new_course():
    """
    创建一个新的课程
    :return:
    """
    course = Courses.from_json(request.json)
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_json()), 201, {
        'location': url_for('api.get_course_id', id=course.id, _external=True)
    }


@api.route('/courses/<int:id>/', methods=["GET", "PUT"])
def put_course(id):
    """
    更新一门课
    :return:
    """
    course = Courses.query.get_or_404(id)
    if request.json.get('name'):
        course.name = request.json.get('name')
    if request.json.get('teacher_id'):
        course.teacher_id = request.json.get('teacher_id')
    if request.json.get('introduction'):
        course.introduction = request.json.get('introduction')
    if request.json.get('category_id'):
        course.category_id = request.json.get('category_id')
    if request.json.get('credit'):
        course.credit = request.json.get('credit')
    if request.json.get('type_id'):
        course.type_id = request.json.get('type_id')
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_json()), 200


@api.route('/courses/<int:id>/', methods=['GET', 'DELETE'])
def delete_course(id):
    """
    删除一个课程
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({
        'message': '该课程已被删除'
    })

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
        return jsonify({'error':'你还未点赞哦'}), 403  # forbidden
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
    # 根据id获取tag
    tag = Tags.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = tag.courses.paginate(
        page,
        per_page=current_app.config["XUEER_COURSES_PER_PAGE"],
        error_out=False
    )
    courses = pagination.items  # 获取分页的courses对象
    prev = ""
    if pagination.has_prev:
        prev = url_for('api.get_tags_id_courses', id=id, page=page-1, _external=True)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_tags_id_courses', id=id, page=page+1, _external=True)
    courses_count = tag.courses.count()
    if courses_count % current_app.config['XUEER_TAGS_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']+1
    last = url_for('api.get_tags_id_courses', id=id, page=page_count, _external=True)
    return json.dumps(
        [course.to_json() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'Link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}




@api.route('/users/<int:id>/courses/')
def get_user_like_courses(id):
    """
    获取特定id用户点赞的所有课程
    :param id:
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
    ), 200, {'Link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}

