# coding:utf-8

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin, current_user
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
    __table_args__ = {'mysql_charset': 'utf8'}
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
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(164), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(164), index=True)
    qq = db.Column(db.String(164), index=True)
    major = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship("Comments", backref='users', lazy="dynamic")
    phone = db.Column(db.String(200), default=None)
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
                # major=u'软件工程',
                major = 'CS',
                # school=u'计算机'
                school = 'CCNUCS'
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
        """generate a token"""
        s = Serializer(
            current_app.config['SECRET_KEY'],
            expiration
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
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user_id', id=self.id, _external=True),
            'username': self.username,
            'like_courses': url_for('api.get_user_like_courses', id=self.id, _external=True),
            # 'like_comments': self.comment.all(),
            'email': self.email,
            'qq': self.qq,
            'major': self.major,
            'phone': self.phone,
            'school': self.school,
        }
        return json_user

    @staticmethod
    def from_json(json_user):
        username = json_user.get('username')
        password = json_user.get('password')
        email = json_user.get('email')
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
        return User(username=username, password=password, email=email)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    __table_args__ = {'mysql_charset': 'utf8'}

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
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'courses'
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

    # comment(定义和Comments表的一对多关系)
    comment = db.relationship('Comments', backref="courses", lazy='dynamic')
    # count: 课程对应的评论数
    count = db.Column(db.Integer)
    # likes: 课程对应的点赞数
    likes = db.Column(db.Integer)
    # 定义与标签的多对多关系
    tags = db.relationship(
        "Tags",
        secondary=CourseTag,
        backref=db.backref('courses', lazy="dynamic"),
        lazy="dynamic"
    )

    users = db.relationship(
        "User",
        secondary=UCLike,
        backref=db.backref('courses', lazy="dynamic"),
        lazy='dynamic'
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
        """
        查询当前用户是否点赞了这门课
        :return:
        """
        if hasattr(g, 'current_user'):
            # 如果当前用户登录
            # 查看用户是否点赞
            # 匿名用户和未点赞用户返回False
            if self in g.current_user.courses.all():
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
        :return:
        """
        tags = self.tags
        hot_tag = []
        for tag in tags:
            # 筛选排序
            hot_tag.append(tag.name)
        return hot_tag

    def to_json(self):
        json_courses = {
            'id': self.id,
            #'url': url_for('api.get_course_id', id=self.id, _external=True),
            'title': self.name,
            # 'teacher': url_for('api.get_teacher_id', id=self.teacher_id, _external=True),
            # 老师只返回姓名
            'teacher': Teachers.query.filter_by(id=self.teacher_id).first().name,
            #'introduction': self.introduction,
            'comment_url': url_for('api.get_courses_id_comments', id=self.id, _external=True),
            'hot_tags': self.hot_tags,
            # 'category': self.category.name,
            #'credit': self.credit,
            'likes': self.likes,  # 点赞的总数
            'like_url': url_for('api.new_courses_id_like', id=self.id, _external=True),  # 给一门课点赞
            # 喜欢这门课的所有用户
            #'like_users': url_for('api.get_like_courses_id_users', id=self.id, _external=True),
            'liked': self.liked,  # 查询的用户是否点赞了
            # 'tags': url_for('api.get_courses_id_tags', id=self.id, _external=True),
            'cat': CourseTypes.query.filter_by(id=self.type_id).first().name,
            'views': self.count  # 浏览量其实是评论数
        }
        return json_courses

    def to_json2(self):
        json_courses2 = {
            'id': self.id,
            'title': self.name,
            'teacher': Teachers.query.filter_by(id=self.teacher_id).first().name,
            'views': self.count, # 浏览量其实是评论数
            'likes': self.likes,  # 点赞的总数
            'main_cat': self.category.name,
            'ts_cat': CourseTypes.query.filter_by(id=self.type_id).first().name
        }
        return json_courses2

    @staticmethod
    def from_json(request_json):
        name = request_json.get('name')
        teacher_id = request_json.get('teacher_id')
        introduction = request_json.get('introduction')
        category_id = request_json.get('category_id')
        comment = request_json.get('comment')
        credit = request_json.get('credit')
        tags = request_json.get('tags')
        type_id = request_json.get('type_id')
        return Courses(
            # 原来创建是从后往前创建的
            name = name,
            teacher_id = teacher_id,
            introduction = introduction,
            category_id = category_id,
            comment = comment,
            credit = credit,
            tags = tags,
            type_id = type_id
        )

    def __repr__(self):
        return '<Courses %r>' % self.name


# CourseCategories
#   1     公共课
#   2     通识课
#   3     专业课
#   4     素质课
class CourseCategories(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="category", lazy="dynamic")

    def __repr__(self):
        return '<CourseCategory %r>' % self.name


# CourseTypes
#   id    name
#   1     理科
#   2     文科
#   3     艺体
#   4     工科
class CourseTypes(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="type", lazy="dynamic")

    def __repr__(self):
        return '<CourseType %r>' % self.name


class Comments(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # user外键关联到user表的username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    time = db.Column(db.String(164), index=True)
    body = db.Column(db.Text)
    count = db.Column(db.Integer)  # 客户端能否+1
    likes = db.Column(db.Integer)  # 评论被点赞的数目
    # is_useful计数
    is_useful = db.Column(db.Integer)
    user = db.relationship(
        "User",
        secondary=UCMLike,
        backref=db.backref('comment', lazy="dynamic"),
        lazy='dynamic'
    )

    @property
    def liked(self):
        """
        查询当前用户是否点赞了这门课
        :return:
        """
        if hasattr(g, 'current_user'):
            # 如果当前用户登录
            # 查看用户是否点赞
            # 匿名用户和未点赞用户返回False
            if self in g.current_user.comment.all():
                return True
            else:
                return False
        else:
            return False

    def to_json(self):
        json_comments = {
            'id': self.id,
            # 'url': url_for('api.get_courses_id_comments', id=self.course_id, _external=True),
            # 'user': url_for('api.get_comments_id_users', id=self.id, _external=True),
            'user_name': User.query.filter_by(id=self.user_id).first().username,
            'avatar' : 'http://7xj431.com1.z0.glb.clouddn.com/1-140G2160520962.jpg', # 占位
            # 'course': url_for('api.get_course_id', id=self.course_id, _external=True),
            'date': '2015-12-05',  # 占位
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
    __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    department = db.Column(db.String(150))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(20))
    weibo = db.Column(db.String(150))
    courses = db.relationship("Courses", backref="teacher", lazy="dynamic")

    @staticmethod
    def generate_fake(count=100):
        """
         生成教师虚拟数据
        :param count:  100
        :return: None
        """
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            t = Teachers(
                name=forgery_py.name.full_name(),
                department=u'文学院',
                introduction=forgery_py.lorem_ipsum.sentence(),
                phone='13007145519',
                weibo='neo1218'
            )
            db.session.add(t)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

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
    __table_args__ = {'mysql_charset':'utf8'}
    __tablename__ = 'tags'
    # __table_args__ = {'mysql_charset':'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    count = db.Column(db.Integer)

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
