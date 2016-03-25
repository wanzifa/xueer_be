# coding:utf-8

from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin, current_user
from . import login_manager, app, db
from flask import current_app, url_for, g, request
from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import URLSafeSerializer as Serializer
from .exceptions import ValidationError
from . import app
import flask.ext.whooshalchemy as whooshalchemy
import base64
import jieba


class Permission:
    """
    1. COMMENT: 0x01
    2. MODERATE_COMMENTS: 0x02
    3. ADMINISTER: 0x04
    """
    COMMENT = 0x01
    MODERATE_COMMENTS = 0x02
    ADMINISTER = 0x04


class Role(db.Model):
    """
    1. User: COMMENT
    2. Moderator: MODERATE_COMMENTS
    3. Administrator: ADMINISTER
    """
    #__table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic', cascade='all')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT, True),
            'Moderator': (Permission.COMMENT |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (
                Permission.COMMENT |
                Permission.MODERATE_COMMENTS |
                Permission.ADMINISTER,
                False
            )
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


# a secondary table
# 多对多关系的中间表
UCLike = db.Table(
    'user_like',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

UCMLike = db.Table(
    'user_comment_like',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comments.id'))
)

UTLike = db.Table(
    'user_tips_like',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('tips_id', db.Integer, db.ForeignKey('tips.id'))
)


class CourseTag(db.Model):
    #__table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'courses_tags'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    count = db.Column(db.Integer)
    counts = db.Column(db.Integer)

CourseSearch =  db.Table(
    'courses_search',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('search_id', db.Integer, db.ForeignKey('search.id'))
)

TagSearch = db.Table(
    'tags_search',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('search_id', db.Integer, db.ForeignKey('search.id'))
)


class User(UserMixin, db.Model):
    """
    id, username, password, like(Courses), comment(Comment),
    UserLike: m to m
    """
    # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(164), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(164), index=True, unique=True)
    qq = db.Column(db.String(164), index=True)
    major = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship("Comments", backref='users', lazy="dynamic", cascade='all')
    phone = db.Column(db.String(200), default=None)
    school = db.Column(db.String(200), index=True, default=None)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username == 'neo1218':
                self.role = Role.query.filter_by(permissions=0x04).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        password_decode = base64.b64decode(password)
        self.password_hash = generate_password_hash(password_decode)

    def verify_password(self, password):
        # password = base64.b64decode(password)
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        """generate a token"""
        s = Serializer(
            current_app.config['SECRET_KEY']
            # expiration
        )
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """verify the user with token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        # get id
        return User.query.get_or_404(data['id'])

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        # is administrator
        return (self.role_id == 2)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'id': self.id,
            'url': url_for('api.get_user_id', id=self.id, _external=True),
            'username': self.username,
            'email': self.email,
            'qq': self.qq,
            'major': self.major,
            'phone': self.phone,
            'school': self.school,
        }
        return json_user

    def to_json2(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
        return json_user

    @staticmethod
    def from_json(json_user):
        username = json_user.get('username')
        password = json_user.get('password')
        email = json_user.get('email')
        role_id = json_user.get('roleid')
        qq = json_user.get('qq')
        major = json_user.get('major')
        phone = json_user.get('phone')
        school = json_user.get('school')
        if username is None or username == '':
            raise ValidationError('用户名不能为空哦！')
        if password is None or password == '':
            raise ValidationError('请输入密码！')
        if email is None or email == '':
            raise ValidationError('请输入邮箱地址！')
        return User(username=username, password=password, email=email, role_id=role_id)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
  # __table_args__ = {'mysql_charset': 'utf8'}

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def generate_auth_token(self, expiration):
        return None


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Courses(db.Model):
    """Courses model"""
    __searchable__ = ['teacher']
    # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(280))
    # 按专必公必分类 category_id(外键)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    # 按文理艺体分类
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    # credit记录学分
    credit = db.Column(db.Integer)
    # just teacher's name
    teacher = db.Column(db.String(164))
    # introduction(课程介绍)
    introduction = db.Column(db.Text)

    # comment(定义和Comments表的一对多关系)
    comment = db.relationship('Comments', backref="courses", lazy='dynamic', cascade='all')
    # count: 课程对应的评论数
    count = db.Column(db.Integer)
    # likes: 课程对应的点赞数
    likes = db.Column(db.Integer)
    # 定义与标签的多对多关系
    tags = db.relationship("CourseTag", backref="courses", lazy="dynamic", cascade='all')
    users = db.relationship(
        "User",
        secondary=UCLike,
        backref=db.backref('courses', lazy="dynamic"),
        lazy='dynamic',
        cascade='all'
    )
    #search定义和search表的多对多关系

    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.users.all():
                return True
            else:
                return False
        else:
            return False

    @property
    def hot_tags(self):
        """
        返回热门的4个标签
        用空格隔开、组成4个字符串
        """
        # 查询记录

        s = ""
        ct = CourseTag.query.filter_by(course_id=self.id).all()
        sct = sorted(ct, lambda x, y: cmp(y.count, x.count))
        for link in sct[:4]:
            s = s + link.tags.name + " "
        return s[:-1]

    def to_json(self):
        if CourseTypes.query.filter_by(id=self.type_id).first() is None:
            credit_category = "无分类"
        else:
            credit_category = CourseTypes.query.filter_by(id=self.type_id).first().name
        if CoursesSubCategories.query.filter_by(id=self.subcategory_id).first() is None:
            sub_category = "无分类"
        else:
            sub_category = CoursesSubCategories.query.filter_by(id=self.subcategory_id).first().name
        json_courses = {
            'id': self.id,
            'title': self.name,
            'teacher': self.teacher,
            'comment_url': url_for('api.get_courses_id_comments', id=self.id, _external=True),
            'hot_tags': self.hot_tags,
            'likes': self.likes,  # 点赞的总数
            'like_url': url_for('api.new_courses_id_like', id=self.id, _external=True),  # 给一门课点赞
            'liked': self.liked,  # 查询的用户是否点赞了
            'main_category': CourseCategories.query.filter_by(id=self.category_id).first().name,
            'sub_category': sub_category,
            'credit_category': credit_category,
            'views': self.count  # 浏览量其实是评论数
        }
        return json_courses

    def to_json2(self):
        if CourseTypes.query.filter_by(id=self.type_id).first() is None:
            credit_category = "无分类"
        else:
            credit_category = CourseTypes.query.filter_by(id=self.type_id).first().name
        if CoursesSubCategories.query.filter_by(id=self.subcategory_id).first() is None:
            sub_category = "无分类"
        else:
            sub_category = CoursesSubCategories.query.filter_by(id=self.subcategory_id).first().name
        json_courses2 = {
            'id': self.id,
            'title': self.name,
            'teacher': self.teacher,
            'views': self.count, # 浏览量其实是评论数
            'likes': self.likes,  # 点赞的总数
            'main_category': CourseCategories.query.filter_by(id=self.category_id).first().name,
            'sub_category': sub_category,
            'credit_category': credit_category
        }
        return json_courses2

    @staticmethod
    def from_json(json_courses):
        name = json_courses.get('name')
        teacher = json_courses.get('teacher')
        introduction = json_courses.get('introduction')
        category_id = json_courses.get('category_id')
        credit = json_courses.get('credit')
        # 二级课程分类和学分分类可选
        type_id = json_courses.get('type_id')
        subcategory_id = json_courses.get('sub_category_id')
        return Courses(
            name=name,
            teacher=teacher,
            category_id=category_id,
            type_id=type_id,
            subcategory_id=subcategory_id
        )

    def __repr__(self):
        return '<Courses %r>' % self.name

whooshalchemy.whoosh_index(app, Courses)


# CourseCategories
#   1     公共课
#   2     通识课
#   3     专业课
#   4     素质课
class CourseCategories(db.Model):
  # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="category", lazy="dynamic", cascade='all')
    subcategories = db.relationship("CoursesSubCategories", backref="category", lazy="dynamic", cascade='all')


    def __repr__(self):
        return '<CourseCategory %r>' % self.name


# CoursesSubCategories
# 1     通识核心课
# 2     通识选修课
class CoursesSubCategories(db.Model):
  # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'subcategory'
    id = db.Column(db.Integer, primary_key=True)
    main_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(640))
    courses = db.relationship('Courses', backref='subcategory', lazy='dynamic', cascade='all')

    def __repr__(self):
        return "<SubCategory %r> % self.name"


# CourseTypes
#   id    name
#   1     理科
#   2     文科
#   3     艺体
#   4     工科
class CourseTypes(db.Model):
  # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="type", lazy="dynamic", cascade='all')

    def __repr__(self):
        return '<CourseType %r>' % self.name


class Comments(db.Model):
  # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # user外键关联到user表的username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    count = db.Column(db.Integer)  # 客户端能否+1
    likes = db.Column(db.Integer, default=0)  # 评论被点赞的数目
    # is_useful计数
    is_useful = db.Column(db.Integer)
    tip_id = db.Column(db.Integer, db.ForeignKey('tips.id'))
    user = db.relationship(
        "User",
        secondary=UCMLike,
        backref=db.backref('comment', lazy="dynamic"),
        lazy='dynamic',
        cascade='all'
    )

    @property
    def time(self):
        time_str = str(self.timestamp)
        time = time_str[0:10]
        return time

    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.user.all():
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def test_json():
        json_test = {
            'token_headers': request.headers.get('authorization', None)
        }
        return json_test

    def to_json(self):
        json_comments = {
            'id': self.id,
            'user_name': User.query.filter_by(id=self.user_id).first().username,
            'avatar' : 'http://7xj431.com1.z0.glb.clouddn.com/1-140G2160520962.jpg', # 占位
            'date': self.time,
            'body': self.body,
            'is_useful': self.is_useful,
            'likes': self.likes,
            'liked': self.liked,
            'like_url': url_for('api.new_comments_id_like', id=self.id, _external=True)
        }
        return json_comments

    @staticmethod
    def from_json(json_comments):
        body = json_comments.get('body')
        if body is None or body == '':
            raise ValidationError('评论不能为空哦！')
        return Comments(body=body)

    def __repr__(self):
        return '<Comments %r>' % self.id


class Teachers(db.Model):
    __tablename__ = 'teachers'
    # __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    department = db.Column(db.String(150))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(20))
    weibo = db.Column(db.String(150))

    def to_json(self):
        json_teacher = {
            'id': self.id,
            'url': url_for('api.get_teacher_id', id=self.id, _external=True),
            'name': self.name,
            'department': self.department,
            'introduction': self.introduction,
            'phone': self.phone,
            'weibo': self.weibo,
            'courses': url_for('api.get_courses', teacher=self.id, _external=True)
        }
        return json_teacher

    @staticmethod
    def from_json(request_json):
        name = request_json.get('name')
        department = request_json.get('department')
        introduction = request_json.get('introduction')
        phone = request_json.get('phone')
        weibo = request_json.get('weibo')
        return Teachers(
            name=name,
            department=department,
            introduction=introduction,
            phone=phone,
            weibo=weibo
        )

    def __repr__(self):
        return '<Teachers %r>' % self.name


class Tags(db.Model):
  # __table_args__ = {'mysql_charset':'utf8'}
    __tablename__ = 'tags'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    count = db.Column(db.Integer)
    courses = db.relationship("CourseTag", backref="tags", lazy="dynamic", cascade='all')

    def to_json(self):
        json_tag = {
            'id': self.id,
            'tag_url': url_for('api.get_tags_id', id=self.id, _external=True),
            'title': self.name
        }
        return json_tag

    @staticmethod
    def from_json(json_tag):
        name=json_tag.get('name')
        return Tags(name=name)

    def __repr__(self):
        return '<Tags %r>' % self.name

whooshalchemy.whoosh_index(app, Tags)



class Tips(db.Model):
  # __table_args__ = {'mysql_charset':'utf8'}
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    img_url = db.Column(db.String(164))
    author = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # likes number
    likes = db.Column(db.Integer, default=0)
    # views counts
    views = db.Column(db.Integer, default=0)
    users = db.relationship(
        "User",
        secondary=UTLike,
        backref=db.backref('tips', lazy="dynamic"),
        lazy='dynamic', cascade='all'
    )

    @property
    def time(self):
        time_str = str(self.timestamp)
        time = time_str[0:10]
        return time

    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.users.all():
                return True
            else:
                return False
        else:
            return False

    def to_json(self):
        json_tips = {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'url': url_for('api.get_tip_id', id=self.id, _external=True),
            'views': self.views,
            'likes': self.likes,
            'date': self.time,
            'img_url': self.img_url
        }
        return json_tips

    def to_json2(self):
        json_tips2 = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'body': self.body,
            'likes': self.likes,
            'date': self.time
        }
        return json_tips2

    @staticmethod
    def from_json(json_tips):
        title = json_tips.get('title')
        img_url = json_tips.get('img_url')
        body = json_tips.get('body')
        author = json_tips.get('author')
        return Tips(
            title=title,
            body=body,
            img_url=img_url,
            author=author
        )

    def __repr__(self):
        return '<Tips %r>' % self.title


class Search(db.Model):
    """
    分词表: jieba分词
    courses: 课程多对多关系
    tags: 标签多对多关系
    """
    __tablename__ = 'search'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(280))
    courses = db.relationship(
        'Courses',
        secondary = CourseSearch,
        backref = db.backref('search', lazy='dynamic'),
        lazy='dynamic', cascade='all'
    )
    # tags = db.relationship(
    #   'Tags',
    #    secondary = TagSearch,
    #    backref = db.backref('search', lazy='dynamic'),
    #    lazy='dynamic', cascade='all'
    # )

    def __repr__(self):
        return '<Search %r>' % self.name


whooshalchemy.whoosh_index(app, Search)


class KeyWords(db.Model):
    """Key Words"""
    __tablename__ = 'keywords'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(164))
    counts = db.Column(db.Integer, default=0)

    def to_json(self):
        json_keywords = {
            'id': self.id,
            'key_word': self.name
        }
        return json_keywords

    def __repr__(self):
        return '<KeyWords %r>' % self.name

