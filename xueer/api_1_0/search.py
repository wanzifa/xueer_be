# coding: utf-8

from flask import jsonify, url_for, request, current_app
from flask_login import current_user
from .authentication import auth
from ..models import Courses, User, Tags, CourseCategories, Search,  Teachers, KeyWords
from . import api
from xueer import db
import json
from sqlalchemy import desc



@api.route('/search/', methods=['GET'])
def get_search():
    """
    获取搜索结果
    :param keywords:
    :return: search results
    """
    courses = []; course1 = []; course2 = [] ;course3 = []
    keywords = request.args.get('keywords')
    if keywords:
        k = KeyWords.query.filter_by(name=keywords).first()
        if k is None:
            k = KeyWords(name=keywords)
            db.session.add(k)
            db.session.commit()
        k.counts += 1
        db.session.add(k)
        db.session.commit()
        searches = Search.query.whoosh_search(keywords).all()
        if request.args.get('sort') == 'view':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            for ct in tag.courses:
                                course2 += ct.courses.filter_by(
                                        type_id=request.args.get('ts_cat'),
                                        category_id=request.args.get('main_cat')
                                    ).all()
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)
                else:
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            for ct in tag.courses:
                                course2 += ct.courses.filter_by(
                                        category_id=request.args.get('main_cat')
                                    ).all()
                                ).all()
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.count, reverse=True)
            else:
                #对教师进行搜索
                course3 = Courses.query.whoosh_search(keywords).all()
                #对标签进行搜索
                tags = Tags.query.whoosh_search(keywords).all()
                for tag in tags:
                    if tag.courses is not None:
                        for ct in tag.courses:
                            course2 += ct.courses.all()
                #根据课程名搜索
                for search in searches:
                    if search.courses is not None:
                        course1 += search.courses.all()
                course0 = list(set(course1 + course2 + course3))
                courses = sorted(course0,  key=lambda course : course.count, reverse=True)

        elif request.args.get('sort') == 'like':
            if request.args.get('main_cat'):
                if request.args.get('ts_cat'):
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            for ct in tag.courses:
                                course2 += ct.courses.filter_by(
                                        type_id=request.args.get('ts_cat'),
                                        category_id=request.args.get('main_cat')
                                    ).all()
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                type_id=request.args.get('ts_cat'),
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)
                else:
                    #对教师进行搜索
                    course3 = Courses.query.whoosh_search(keywords).filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    #对标签进行搜索
                    tags = Tags.query.whoosh_search(keywords).all()
                    for tag in tags:
                        if tag.courses is not None:
                            for ct in tag.courses:
                                course2 += ct.courses.filter_by(
                                        category_id=request.args.get('main_cat')
                                    ).all()
                    #根据课程名搜索
                    for search in searches:
                        if search.courses is not None:
                            course1 += search.courses.filter_by(
                                category_id=request.args.get('main_cat')
                            ).all()
                    course0 = list(set(course1 + course2 + course3))
                    courses = sorted(course0,  key=lambda course : course.likes, reverse=True)
            else:
                #对教师进行搜索
                course3 = Courses.query.whoosh_search(keywords).all()
                #对标签进行搜索
                tags = Tags.query.whoosh_search(keywords).all()
                for tag in tags:
                    if tag.courses is not None:
                        for ct in tag.courses:
                                course2 += ct.courses.all()
                #根据课程名搜索
                for search in searches:
                    if search.courses is not None:
                        course1 += search.courses.all()
                course0 = list(set(course1 + course2 + course3))
                courses = sorted(course0,  key=lambda course : course.likes, reverse=True)

        else:
            #对教师进行搜索
            course3 = Courses.query.whoosh_search(keywords).all()
            #对标签进行搜索
            tags = Tags.query.whoosh_search(keywords).all()
            for tag in tags:
                if tag.courses is not None:
                    for ct in tag.courses:
                            course2 += ct.courses.all()
            #根据课程名搜索
            for search in searches:
                if search.courses is not None:
                    course1 += search.courses.all()
            courses = course1+course2+course3

    """
    if not courses:
        #这个字典用来存储课程名以及它对应的关键字元素匹配个数
        course_name_count = {}
        for course in Courses.query.all():
            #关键字元素匹配个数初始值都是0
            course_name_count[course.name] = 0
            #item就是关键字中取出来做匹配的元素
            for item in keywords:
                if item in course.name:
                    courses_name_count[course.name] += 1
                    # 如果课程名对应的关键字元素匹配数和关键字内的元素个数相等
                    # 比如"马基"有两个汉字 如果courses_name_count也等于2 也就是匹配了这个名字中拆开的所有字
                    # 说明这个课程和马基关联很大 我们返回搜索结果
                    if courses_name_count[course.name] == len(keywords)/3:
                        courses.append(course)
        courses = list(set(courses))
        if request.args.get('sort') == 'view':
            courses =sorted(courses,  key=lambda course : course.count, reverse=True)
        elif request.args.get('sort') == 'like':
            courses =sorted(courses,  key=lambda course : course.likes, reverse=True)
    """

    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
    ), 200



@api.route('/search/prefetch/', methods=['GET', 'POST'])
def get_research2():
    if request.method == 'POST':
        save()
        courses = []
        course1 = []
        course2 = []
        course3 = []
        if request.args.get('keywords'):
            keywords = request.args.get('keywords')
            if KeyWords.query.filter_by(name=keywords).all():
                k = KeyWords.query.filter_by(name=keywords).first()
            else:
                k = KeyWords(name=keywords)
                db.session.add(k)
                db.session.commit()
            k.counts += 1
            db.session.add(k)
            db.session.commit()
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


@api.route('/search/hot/', methods=['GET'])
def hot_search():
    list = KeyWords.query.all()
    hots = sorted(list, key=lambda item: item.counts, reverse=True)[:10]
    return json.dumps(
        [keyword.to_json() for keyword in hots],
        ensure_ascii=False,
        indent=1
    ), 200

