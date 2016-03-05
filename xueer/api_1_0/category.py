# coding: utf-8
from . import api
from xueer import db
from xueer.decorators import admin_required
from xueer.models import CourseCategories, CourseTypes, CoursesSubCategories
from flask import jsonify, request


@api.route('/main_category/', methods=['GET'])
def category():
    """
    获取主课程分类信息
    :return:
    """
    categories = CourseCategories.query.all()
    return jsonify({
        category.name: category.id for category in categories
    })


@api.route('/main_category/', methods=['GET', 'POST'])
@admin_required
def new_category():
    """
    添加一个课程分类
    :return:
    """
    category = CourseCategories(
        name=request.get_json().get('category_name'),
        id=request.get_json().get('id')
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({
        category.name: category.id
    }), 201


@api.route('/main_category/<int:id>/', methods=['GET', 'PUT'])
@admin_required
def update_category(id):
    """
    更新相应id的类别名
    :return:
    """
    category = CourseCategories.query.get_or_404(id)
    category.name = request.get_json().get('name')
    db.session.add(category)
    db.session.commit()
    return jsonify({
        category.name: category.id
    })


@api.route('/sub_category/', methods=["GET"])
def sub_category():
    main_category_id = request.args.get('main_category_id')
    sub_categories = CoursesSubCategories.query.filter_by(main_category_id=main_category_id).all()
    return jsonify({
        sub_category.name: sub_category.id for sub_category in sub_categories
    })


@api.route('/sub_category/', methods=['GET', 'POST'])
@admin_required
def new_sub_category():
    sub_category = CoursesSubCategories(
        name=request.get_json().get('name'),
        main_category_id=request.get_json().get('main_category_id')
    )
    db.session.add(sub_category)
    db.session.commit()
    return jsonify({
        sub_category.name: sub_category.id
    }), 201


@api.route('/sub_category/<int:id>/', methods=["GET", "PUT"])
@admin_required
def update_sub_category(id):
    sub_category = CoursesSubCategories.query.get_or_404(id)
    sub_category.name = request.get_json().get('name')
    sub_category.main_category_id = request.get_json().get('main_category_id')
    db.session.add(sub_category)
    db.session.commit()
    return jsonify({
        sub_category.name: sub_category.id
    })


@api.route('/credit_category/', methods=['GET'])
def credit_categories():
    """
    返回学分类别信息
    :return:
    """
    credit_categories = CourseTypes.query.all()
    return jsonify({
        credit_category.name: credit_category.id for credit_category in credit_categories
    })

