# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories, Search, save, Teachers
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
    save()
    courses = []
    course1 = []
    course2 = []
    course3 = []
    if request.args.get('keywords'):
        keywords = request.args.get('keywords')
        searches = Search.query.whoosh_search(keywords)
        course3 = Courses.query.whoosh_search(keywords).all()
        if request.args.get('sort') == 'view':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    for search in searches:
                        course1 = search.courses.filter_by(
                            type_id=request.args.get('ts_cat'),
                            category_id=request.args.get('main_cat')
                        ).all()
                        for tag in search.tags:
                            course = tag.courses.filter_by(
                            type_id=request.args.get('ts_cat'),
                            category_id=request.args.get('main_cat')
                        ).all()
                            course2 += course
                    course0 = course1 + course2 + course3
                    courses =sorted(course0,  key=lambda course : course.count, reverse=True)
                else:
                    for search in searches:
                        course1 += search.courses.filter_by(category_id=request.args.get('main_cat')).all()
                        tags = search.tags
                        for tag in tags:
                            course2 += tag.courses.fiter_by(category_id=request.args.get('main_cat')).all()
                    course0 = course1 + course2 + course3
                    courses =sorted(course0,  key=lambda course : course.count, reverse=True)

            else:
                for search in searches:
                    course1 += search.courses.all()
                    tags = search.tags
                    for tag in tags:
                        course2 += tag.courses.all()
                    course0 = course1 + course2 + course3
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)

        elif request.args.get('sort') == 'like':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    for search in searches:
                        course1 = search.courses.filter_by(
                            type_id=request.args.get('ts_cat'),
                            category_id=request.args.get('main_cat')
                        ).all()
                        for tag in search.tags:
                            course = tag.courses.filter_by(
                            type_id=request.args.get('ts_cat'),
                            category_id=request.args.get('main_cat')
                        ).all()
                            course2 += course
                    course0 = course1 + course2 + course3
                    courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
                else:
                    for search in searches:
                        course1 += search.courses.filter_by(category_id=request.args.get('main_cat')).all()
                        tags = search.tags
                        for tag in tags:
                            course2 += tag.courses.fiter_by(category_id=request.args.get('main_cat')).all()
                    course0 = course1 + course2 + course3
                    courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
            else:
                for search in searches:
                    course1 += search.courses.all()
                    tags = search.tags
                    for tag in tags:
                        course2 += tag.courses.all()
                course0 = course1 + course2 + course3
                courses =sorted(course0,  key=lambda course : course.likes, reverse=True)
        else:
            for search in searches:
               course1 += search.courses.all()
               tags = search.tags
               for tag in tags:
                   course2 += tag.courses.all()
            courses = course1+course2+course3

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

