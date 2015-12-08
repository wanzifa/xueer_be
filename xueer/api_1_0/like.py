# coding: utf-8

"""
    点赞API

"""
from . import api
from flask import g
from xueer import db
from xueer.api_1_0.authentication import auth
from xueer.models import Courses


@auth.login_required
@api.route('/courses/<int:id>/like/', methods=["GET"])
def new_courses_id_like(id):
    """
    点赞特定id的课程
    :param id:
    :return:
    """
    course = Courses.query.get_or_404(id)
    course.users.append(g.current_user)
    db.session.add(course)
    db.session.commit()


@auth.login_required
@api.route('/course/<int:id>/like/', method=["GET", "POST"])
def delete_courses_id_like(id):
    """
    删除特定id的评论
    :param id:
    :return:
    """

