# coding: utf-8

from flask import jsonify, url_for, request, current_app
# from flask_login import current_user
from .authentication import auth
from sqlalchemy import desc
from ..models import Courses, User, Tags, CourseCategories, CourseTypes, Permission, Search
from . import api
from xueer import db
import json
from xueer.decorators import admin_required
import jieba


@api.route('/courses/', methods=["GET"])  # ?string=sort&main_cat&ts_cat
def get_courses():
    """
    获取全部课程
    """
    global pagination
    page = request.args.get('page', 1, type=int)
    num = request.args.get('num', type=int)
    if num:
        current_app.config['XUEER_COURSES_PER_PAGE'] = num
    else:
        current_app.config['XUEER_COURSES_PER_PAGE'] = 20
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
                ).order_by(desc(Courses.count)).paginate(
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
            pagination = Courses.query.order_by(desc(Courses.count)).paginate(
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
            pagination = Courses.query.order_by(desc(Courses.likes)).paginate(
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
        prev = url_for('api.get_courses', page=page - 1)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_courses', page=page + 1)
    courses_count = len(Courses.query.all())
    if courses_count%current_app.config['XUEER_COURSES_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']+1
    last = url_for('api.get_courses', page=page_count, _external=True)
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


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
@admin_required
def new_course():
    """
    创建一个新的课程
    :return:
    """
    # request.get_json.get('item', 'default')
    if request.method == "POST":
        course = Courses.from_json(request.get_json())
        db.session.add(course)
        db.session.commit()
        generator = jieba.cut_for_search(course.name)
        seg_list = '/'.join(generator)
        results = seg_list.split('/')
        if course.name not in results:
            results.append(course.name)
        for seg in results:
            s = Search.query.filter_by(name=seg).first()
            if not s:
                s = Search(name=seg)
            s.courses.append(course)
            db.session.add(s)
            db.session.commit()
        return jsonify({
            'id': course.id
        }), 201


@api.route('/courses/<int:id>/', methods=["GET", "PUT"])
@admin_required
def put_course(id):
    """
    更新一门课
    """
    course = Courses.query.get_or_404(id)
    if request.method == "PUT":
        data_dict = eval(request.data)
        course.name = data_dict.get('name', course.name)
        course.teacher = data_dict.get('teacher', course.teacher)
        course.category_id = data_dict.get('category_id', course.category_id)
        course.subcategory_id = data_dict.get('sub_category_id', course.subcategory_id)
        course.type_id = data_dict.get('type_id', course.type_id)
        db.session.add(course)
        db.session.commit()
        generator = jieba.cut_for_search(course.name)
        seg_list = '/'.join(generator)
        results = seg_list.split('/')
        if course.name not in results:
            results.append(course.name)
        for seg in results:
            s = Search.query.filter_by(name=seg).first()
            if not s:
                s = Search(name=seg)
            s.courses.append(course)
            db.session.add(s)
            db.session.commit()
    return jsonify({'update': id}), 200


@api.route('/courses/<int:id>/', methods=['GET', 'DELETE'])
@admin_required
def delete_course(id):
    """
    删除一个课程
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    if request.method == "DELETE":
        db.session.delete(course)
        db.session.commit()
        return jsonify({
            'message': '该课程已被删除'
        })


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
        prev = url_for('api.get_tags_id_courses', id=id, page=page-1)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_tags_id_courses', id=id, page=page+1)
    courses_count = tag.courses.count()
    if courses_count % current_app.config['XUEER_TAGS_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_TAGS_PER_PAGE']+1
    last = url_for('api.get_tags_id_courses', id=id, page=page_count)
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}
