# coding:utf-8

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from flask import current_app, url_for, g
from xueer.exceptions import ValidationError


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
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

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

# a secondary table
CourseTag = db.Table(
    'CourseTag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)


class User(UserMixin, db.Model):
    """
    id, username, password, like(Courses), comment(Comment),
    UserLike: m to m
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(164), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(164), index=True)
    qq = db.Column(db.String(164), index=True)
    phone = db.Column(db.String(164), index=True)
    major = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship("Comments", backref='users', lazy="dynamic")
    like = db.relationship(
        'Comments',
        secondary=UCMLike,
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )
    like_2 = db.relationship(
        'Courses',
        secondary=UCLike,
        backref=db.backref('user', lazy='dynamic'),
        lazy='dynamic'
    )
    qq = db.Column(db.Integer, default=None)
    phone = db.Column(db.Integer, default=None)
    school = db.Column(db.String(200), index=True, default=None)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.username == 'neo1218':
                self.role = Role.query.filter_by(permissions=0x04).first()

    @staticmethod
    def generate_fake(count=100):
        """
        生成虚拟数据
        :param count: count 生成数据量
        :return: None 提交到数据库的对象
        """
        from sqlalchemy.exc import IntegrityError
        # IntegrityError: Wraps a DB-API IntegrityError.
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(
                username=forgery_py.name.full_name(),
                email=forgery_py.internet.email_address(),
                password=forgery_py.lorem_ipsum.word(),
                qq='834597629',
                phone='13007149711',
                major=u'软件工程',
                school=u'计算机'
            )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration):
        s = Serializer(
            current_app.config['SECRET_KEY'],
            expiration
        )
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get_or_404(data['id'])

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user_id', id=self.id, _external=True),
            'username': self.username,
            'like': self.like.all(),
            'qq': self.qq,
            'phone': self.phone,
            'school': self.school,
        }
        return json_user


class AnonymousUser(AnonymousUserMixin):
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
    __tablename__ = 'courses'
    # __table_args__ = {'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(280))
    # 按专必公必分类 category_id(外键)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # 按文理艺体分类
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    # credit记录学分
    credit = db.Column(db.Integer)
    # teacher_id(外键)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    # introduction(课程介绍)
    introduction = db.Column(db.Text)

    # likecount决定用redis数据库
    # like(对点赞的计数，只有登录用户可以点赞课程)
    # likecount = db.Column(db.Integer)

    # comment(定义和Comments表的一对多关系)
    comment = db.relationship('Comments', backref="courses", lazy='dynamic')
    # 定义与标签的多对多关系
    tags = db.relationship(
        "Tags",
        secondary=CourseTag,
        backref=db.backref('courses', lazy="dynamic"),
        lazy="dynamic"
    )

    @staticmethod
    def generate_fake(count=100):
        """
        生成课程虚拟数据
        :param count:  生成虚拟数据的个数
        :return:  None 向数据库的一系列的添加
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()  # 初始化
        for i in range(count):
            c = Courses(
                name=forgery_py.name.full_name(),
                credit=10,
                introduction=forgery_py.lorem_ipsum.sentence()
            )
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def liked(self):
        if self in g.current_user.like.all():
            return True
        return False

    def __repr__(self):
        return '<Courses %r>' % self.name

    def to_json(self):
        json_courses = {
            'id': self.id,
            'url': url_for('api.get_course_id', id=self.id, _external=True),
            'title': self.name,
            'teacher': self.teacher.name,
            'introduction': self.introduction,
            'comments': url_for('api.get_comments_id', id=self.id, _external=True),
            'category': self.category.first().name,
            'credit': self.credit,
            'likes': len(self.user.all()),
            'like_url': url_for('api.like_add', id=self.id, _external=True),
            'liked': self.liked,
            'Tags': self.tags.all(),
            'cat': self.type.first().name,
            'comment_url': url_for('api.get_comments_id', id=self.id, _external=True)
        }
        return json_courses


# CourseCategories
#	1     公必
#	2     公选
#	3     专必
#	4     专选
class CourseCategories(db.Model):
    # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="category", lazy="dynamic")

    def __repr__(self):
        return '<CourseCategory %r>' % self.name


# CourseTypes
#	id    name
#	1     理科
#	2     文科
#	3     艺体
class CourseTypes(db.Model):
    # __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="type", lazy="dynamic")

    def __repr__(self):
        return '<CourseType %r>' % self.name


class Comments(db.Model):
    # __table_args__ = {'mysql_charset':'utf8'}
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # user外键关联到user表的username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    count = db.Column(db.Integer)  # 客户端能否+1
    # is_useful计数
    is_useful = db.Column(db.Integer)

    def __repr__(self):
        return '<Comments %r>' % self.course_id

    def to_json(self):
        json_comments = {
            'id': self.id,
            'url': url_for('api.get_comments_id', id=self.course_id, _external=True),
            'user_name': url_for('api.get_user_id', id=self.user_id, _external=True),
            'course': url_for('api.get_course_id', id=self.course_id, _external=True),
            'date': self.time,
            'body': self.body,
            'is_useful': self.useful,
            'likes': len(self.user.all()),
            'like_url': url_for('api.comment_like_add', id=self.id, _external=True)
        }
        return json_comments

    @staticmethod
    def from_json(json_comments):
        body = json_comments.get('body')
        if body is None or body == '':
            raise ValidationError('评论不能为空哦！')
        return Comments(body=body)


class Teachers(db.Model):
    # __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    department = db.Column(db.String(150))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(20))
    weibo = db.Column(db.String(150))
    courses = db.relationship("Courses", backref="teacher", lazy="dynamic")

    def __repr__(self):
        return '<Teachers %r>' % self.name

    def to_json(self):
        json_teacher = {
            'url': url_for('api.get_teacher_id', id=self.id, _external=True),
            'name': self.name,
            'department': self.department,
            'introduction': self.introduction,
            'phone': self.phone,
            'weibo': self.weibo,
            'courses': self.courses.all()
        }


class Tags(db.Model):
    __tablename__ = 'tags'
    # __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return '<Tags %r>' % self.name

    def to_json(self):
        json_tag = {
            'id': self.id,
            'tag_url': url_for('api.get_tags', _external=True),
            'title': self.name
        }
