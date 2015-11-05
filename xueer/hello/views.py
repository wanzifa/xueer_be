# -*- coding:utf-8 -*-

from flask import render_template, redirect, url_for, abort, flash, request
from . import hello
from ..decorators import admin_required, permission_required
from ..models import Permission, User, Role, Courses, Comments, CourseTag, Tags
from flask.ext.login import login_user, logout_user, login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db


@hello.route("/course/<id>", methods=['GET', 'POST'])
def course_page(id):
    course = Courses.query.filter_by(id=id).first()
    form = CommentForm()
    #save the comments and tags data into db
    if form.validate_on_submit():
        course = Courses.query.filter_by(id=id).first()
        all_tags = Tags.query.all()
        c = Comments(body=form.body.data)
        t_data = form.tags.data
        tl = t_data.split()
        taglist_all = []
        taglist_this = []
        for t_1 in all_tags:
            taglist_all.append(t_1.name)
        for t_2 in course.tags:
            taglist_this.append(t_2.tags.name)
        for l in tl:
            if l in taglist_all:
                if l in taglist_this:
                    t_id = Tags.query.filter_by(name=l).first().id
                    row = CourseTag.query.filter_by(course_id=id).filter_by(tag_id=t_id).first()
                    row.count = row.count + 1
                    db.session.add(row)
                else:
                    link = CourseTag(count=1)
                    nt = Tags.query.filter_by(name=l).first()
                    link.tags = nt
                    link.course_id = course.id
                    course.tags.append(link)
                    db.session.add(link)
            else:
                link = CourseTag(count=1)
                nt = Tags(name=l)
                link.tags = nt
                course.tags.append(link)
                db.session.add(nt)
        db.session.add(c)
        course.comment.append(c)
        form.tags.data = ''
        form.body.data = ''
        flash('评论发表成功！')
        return redirect(url_for('.course_page', id = id))
    tags = course.tags
    page = request.args.get('page', 1, type = int)
    pagination = Comments.query.filter_by(course_id = id).paginate(page, per_page = 5, error_out = False)
    comments = pagination.items
    return render_template('course.html', course = course, form = form, comments = comments, tags = tags, pagination = pagination)
