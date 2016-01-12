# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories
from . import api
from xueer import db
import json
from sqlalchemy import desc



@api.route('/search/', methods=['GET'])
def get_search():
    """
    获取搜索结果
    :param keywords:
    :return:
    """
    if request.args.get('keywords'):
        keywords = request.args.get('keywords')
    if request.args.get('sort') == 'view':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                course1 = Courses.query.whoosh_search(keywords).filter_by(
                    type_id=request.args.get('ts_cat'),
                    category_id=request.args.get('main_cat')
                ).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc=tag.courses.filter_by(
                    type_id=request.args.get('ts_cat'),
                    category_id=request.args.get('main_cat')
                ).all()
                    course2 += tc
                course0 = course1 + course2
                courses =sorted(course0,  key=lambda course : course.count, reverse=True)

            else:
                course1 = Courses.query.whoosh_search(keywords).filter_by(
                        category_id=request.args.get('main_cat')).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc = tag.courses.filter_by(
                    category_id=request.args.get('main_cat')
                ).all()
                    course2 += tc
                course0 = course1+course2
                courses =sorted(course0,  key=lambda course : course.count, reverse=True)

        else:
            course1 = Courses.query.whoosh_search(keywords).all()
            tags = Tags.query.whoosh_search(keywords).all()
            course2 = []
            for tag in tags:
                tc=tag.courses.all()
                course2 += tc
            course0 = course1 + course2
            courses =sorted(course0,  key=lambda course : course.count, reverse=True)

    elif request.args.get('sort') == 'like':
        if request.args.get('main_cat'):
            if request.args.get('ts_cat'):
                course1 = Courses.query.whoosh_search(keywords).filter_by(
                    type_id=request.args.get('ts_cat'),
                    category_id=request.args.get('main_cat')
                ).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc = tag.courses.filter_by(
                    type_id=request.args.get('ts_cat'),
                    category_id=request.args.get('main_cat')
                ).all()
                    course2 += tc
                course0 = course1 + course2
                courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
            else:
                course1 = Courses.query.whoosh_search(keywords).filter_by(
                        category_id=request.args.get('main_cat')).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc = tag.courses.filter_by(
                    category_id=request.args.get('main_cat')
                ).all()
                    course2 += tc
                course0 = course1 + course2
                courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
        else:
            course1 = Courses.query.whoosh_search(keywords).all()
            tags = Tags.query.whoosh_search(keywords).all()
            course2 = []
            for tag in tags:
                tc=tag.courses.all()
                course2 += tc
            course0 = course1 + course2
            courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
    else:
        course1 = Courses.query.whoosh_search(keywords).all()
        tags = Tags.query.whoosh_search(keywords).all()
        course2 = []
        for tag in tags:
            tc=tag.courses.all()
            course2 += tc
        courses = course1 + course2
    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200



@api.route('/search/prefetch/', methods=['GET', 'POST'])
def get_research2():
    keywords = request.args.get('keywords')
    if request.method == 'POST':
        if request.args.get('keywords'):
            keywords = request.args.get('keywords')
        if request.args.get('sort') == 'view':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    course1 = Courses.query.whoosh_search(keywords).filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                        ).all()
                    tags = Tags.query.whoosh_search(keywords).all()
                    course2 = []
                    for tag in tags:
                        tc=tag.courses.filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                        ).all()
                    course2 += tc
                    course0 = course1 + course2
                    courses =sorted(course0,  key=lambda course : course.count, reverse=True)

                else:
                    course1 = Courses.query.whoosh_search(keywords).filter_by(
                    category_id=request.args.get('main_cat')).all()
                    tags = Tags.query.whoosh_search(keywords).all()
                    course2 = []
                    for tag in tags:
                        tc = tag.courses.filter_by(
                        category_id=request.args.get('main_cat')
                        ).all()
                        course2 += tc
                    course0 = course1+course2
                    courses =sorted(course0,  key=lambda course : course.count, reverse=True)

            else:
                course1 = Courses.query.whoosh_search(keywords).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc=tag.courses.all()
                    course2 += tc
                course0 = course1 + course2
                courses =sorted(course0,  key=lambda course : course.count, reverse=True)

        elif request.args.get('sort') == 'like':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    course1 = Courses.query.whoosh_search(keywords).filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                    ).all()
                    tags = Tags.query.whoosh_search(keywords).all()
                    course2 = []
                    for tag in tags:
                        tc = tag.courses.filter_by(
                        type_id=request.args.get('ts_cat'),
                        category_id=request.args.get('main_cat')
                    ).all()
                        course2 += tc
                    course0 = course1 + course2
                    courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
                else:
                    course1 = Courses.query.whoosh_search(keywords).filter_by(
                            category_id=request.args.get('main_cat')).all()
                    tags = Tags.query.whoosh_search(keywords).all()
                    course2 = []
                    for tag in tags:
                        tc = tag.courses.filter_by(
                        category_id=request.args.get('main_cat')
                    ).all()
                        course2 += tc
                    course0 = course1 + course2
                    courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
            else:
                course1 = Courses.query.whoosh_search(keywords).all()
                tags = Tags.query.whoosh_search(keywords).all()
                course2 = []
                for tag in tags:
                    tc=tag.courses.all()
                    course2 += tc
                course0 = course1 + course2
                courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
        else:
            course1 = Courses.query.whoosh_search(keywords).all()
            tags = Tags.query.whoosh_search(keywords).all()
            course2 = []
            for tag in tags:
                tc=tag.courses.all()
                course2 += tc
            courses = course1 + course2
        courses = courses[0:5]
        return json.dumps(
            [course.to_json2() for course in courses],
            ensure_ascii=False,
            indent=1
        ), 200

