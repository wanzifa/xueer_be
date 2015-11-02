# -*- coding:utf-8 -*-

from flask import render_template, redirect, url_for, abort, flash, request
from . import hello
from ..decorators import admin_required, permission_required
from ..models import Permission, User, Role, Post, Courses, Comments, CourseTag, Tags
from flask.ext.login import login_user, logout_user, login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db



@hello.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)


@hello.route('/admin')
@login_required
@admin_required
def admin_only():
    return "for admin!!"


@hello.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)

@hello.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@hello.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

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
