# -*- coding:utf-8 -*-  
from datetime import datetime
import hashlib
from flask import current_app, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80
	
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'dtk1994@21cn.com':
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
				
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
		
	

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
		
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
		
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)		
			
    def __repr__(self):
        return '<User %r>' % self.username
		
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
	

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    
    
#new stuff
UserLike = db.Table('UserLike',
    db.Column('userb_id', db.Integer, db.ForeignKey('userb.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

class CourseTag(db.Model):
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    count = db.Column(db.Integer)
    tags = db.relationship("Tags", backref='coursetag')



class UserB(db.Model):
    __tablename__ = 'userb'
    __table_args__ = {'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(50))
    #like设置到Courses表的关系
    like = db.relationship('Courses',
    	secondary = UserLike,
        backref=db.backref('userb', lazy = 'dynamic'),lazy = 'dynamic')
    #comment(定义和Comments表的一对多关系)
    comment = db.relationship('Comments',lazy = 'dynamic')
    def __repr__(self):
        return '<UserB %r>' % self.username



class Courses(db.Model):
    __tablename__ = 'courses'
    __table_args__ = {'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
	#按专必公必分类 category_id(外键)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
	#category(定义和CourseCategories的多对一关系)
    category = db.relationship('CourseCategories', backref=db.backref('courses', lazy='dynamic'))

	#按文理艺体分类 
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
	#type(定义和CourseCategories的多对一关系)
    type = db.relationship('CourseTypes', backref=db.backref('courses', lazy='dynamic'))

	#credit记录学分
    credit = db.Column(db.Integer)

	#teacher_id(外键)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
	#teacher(定义和Teachers表的多对一关系)
    teacher = db.relationship('Teachers', backref=db.backref('courses', lazy='dynamic'))

	#introduction(课程)
    introduction = db.Column(db.Text)

	#like(只是对点赞的计数，匿名和登录用户都可以)????定义likecount计数
    likecount = db.Column(db.Integer)

	#comment(定义和Comments表的一对多关系)???
    comment = db.relationship('Comments',backref = 'course')
    
    tags = db.relationship('CourseTag', backref='courses')

    def __repr__(self):
		return '<Courses %r>' % self.name



#CourseCategories
#	1     公必
#	2     公选
#	3     专必
#	4     专选
class CourseCategories(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))

    def __repr__(self):
		return '<CourseCategory %r>' % self.name

#CourseTypes
#	id    name    
#	1     理科
#	2     文科
#	3     艺体
class CourseTypes(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30))

    def __repr__(self):
		return '<CourseType %r>' % self.name



class Comments(db.Model):
    __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key = True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
	#user外键关联到user表的username
    user = db.Column(db.Integer, db.ForeignKey('userb.username'))
    time = db.Column(db.DateTime, index=True, default = datetime.utcnow)
    body = db.Column(db.Text)
    #is_useful计数
    is_useful = db.Column(db.Integer)
    
    def __repr__(self):
		return '<Comments %r>' % self.course_id



class Teachers(db.Model):
    __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    department = db.Column(db.String(150))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(20))
    weibo = db.Column(db.String(150))

    def __repr__(self):
		return '<Teachers %r>' % self.name




class Tags(db.Model):
    __tablename__ = 'tags'
    __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))

    def __repr__(self):
		return '<Tags %r>' % self.name
