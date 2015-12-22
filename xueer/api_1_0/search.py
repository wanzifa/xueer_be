# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories
from . import api
from xueer import db
import json
from sqlalchemy import desc



@api.route('/search/<string:keywords>', methods=['GET'])
def get_search(keywords):
    """
    获取搜索结果
    :param keywords:
    :return:
    """
    page = request.args.get('page', 1, type=int)
    if request.args.get('sort') == 'view':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                pagination = Courses.query.whoosh_search('keywords').filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                ).order_by(desc(Courses.count)).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
            else:
                pagination = Courses.query.whoosh_search('keywords').filter_by(
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
        else:
            pagination = Courses.query.whoosh_search('keywords').order_by(desc(Courses.count)).paginate(
                page,
                per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                error_out=False
            )
    elif request.args.get('sort') == 'like':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                pagination = Courses.query.whoosh_search('keywords').filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
            else:
                pagination = Courses.query.whoosh_search('keywords').filter_by(
                        category_id=request.args.get('main_cat')
                ).paginate(
                        page,
                        per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                        error_out=False
                )
        else:
            pagination = Courses.query.whoosh_search('keywords').order_by(desc(Courses.likes)).paginate(
                page,
                per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
                error_out=False
            )
    else:
        pagination = Courses.query.whoosh_search('keywords').paginate(
            # 查询对象query具有paginate属性
            page,
            per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
            error_out=False
        )
    courses = pagination.items
    # <> 当页面不存在是返回空
    prev = ""  # should init
    if pagination.has_prev:
        prev = url_for('api.get_search', keywords=keywords, page=page - 1, _external=True)
    next = ""
    if pagination.has_next:
        next = url_for('api.get_search', keywords=keywords, page=page + 1, _external=True)
    courses_count = len(Courses.query.whoosh_search('keywords').all())
    if courses_count%current_app.config['XUEER_COURSES_PER_PAGE'] == 0:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']
    else:
        page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']+1
    last = url_for('api.get_search', keywords=keywords, page=page_count, _external=True)
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200, {'Link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


#@api.route('/search/prefetch/<string:keywords>')
#def get_research2(keywords):

