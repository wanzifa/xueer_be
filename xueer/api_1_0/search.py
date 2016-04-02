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
    page = request.args.get('page', 1, type=int)
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
                            course2 = [c.courses for c in tag.courses.all()
                                       if c.courses.category_id=='main_cat' and c.courses.type_id=='ts_cat']
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
                            for ct in tag.courses.all():
                                course2 = [c.courses for c in tag.courses.all() if c.courses.category_id=='main_cat']
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
                        course2 = [c.courses for c in tag.courses.all()]
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
                            course2 = [c.courses for c in tag.courses.all()
                                       if c.courses.category_id=='main_cat' and c.courses.type_id=='ts_cat']
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
                            course2 = [c.courses for c in tag.courses.all() if c.courses.category_id=='main_cat']
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
                        course2 = [c.courses for c in tag.courses.all()]
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
                 course2 = [c.courses for c in tag.courses.all()]
            #根据课程名搜索
            for search in searches:
                if search.courses is not None:
                    course1 += search.courses.all()
            courses = list(set(course1+course2+course3))
       pagination = courses.paginate(
               page, per_page=current_app.config['XUEER_COURSES_PER_PAGE'],
               error_out=False
       ) 
       prev = ""
       if pagination.has_prev:
           prev = url_for('api.get_search', page=page-1)
       next = ""
       if pagination.has_next:
           next = url_for('api.get_search', page=page+1)
       courses_count = len(courses)
       if courses_count%current_app.config['XUEER_COURSES_PER_PAGE'] == 0:
           page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']
       else:
           page_count = courses_count//current_app.config['XUEER_COURSES_PER_PAGE']+1
       last = url_for('api.get_search', page=page_count, _external=True) 


    return json.dumps(
        [course.to_json2() for course in courses],
        ensure_ascii=False,
        indent=1
        ), 200,{"link":"<%s>;rel='next',<%s>;rel='last'" % (next, last)}



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

