# coding: utf-8

from getpass import getpass
import sys
import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
# from flask.ext.admin import Admin
# from flask.ext.admin.contrib.sqla import ModelView
from flask import g
from xueer import db, app
from xueer.models import Permission, Role, User, AnonymousUser, Courses, CourseCategories, \
    CourseTypes, Comments, Teachers, Tags, Tips, Search, save


# 编码设置
reload(sys)
sys.setdefaultencoding('utf-8')


# use create_app to create flask app
# app = create_app(os.environ.get('XUEER_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)


# admin = Admin(app, name="")


def make_shell_context():
    """自动加载环境"""
    return dict(
        g=g,
        app=app,
        db=db,
        Permission=Permission,
        Role=Role,
        User=User,
        AnonymousUser=AnonymousUser,
        Courses=Courses,
        CourseCategories=CourseCategories,
        CourseTypes=CourseTypes,
        Comments=Comments,
        Teachers=Teachers,
        Tags=Tags,
        Tips=Tips,
        Search=Search
    )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def config():
    """项目配置"""
    pass



# 后台数据库管理界面
# admin.add_view(ModelView([models], db.session))
@manager.command
def adduser(username, email):
    """添加用户"""
    password = getpass('password ')
    confirm = getpass('confirm ')
    if password == confirm:
        u = User(
            email=email,
            username=username,
            password=password
        )
        db.session.add(u)
        db.session.commit()
        print "user %s add in database! " % username
    else:
        print "password not confirmed!"
        exit(0)


@manager.command
def test():
    """运行测试"""
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def freeze():
    """首页静态化"""
    from xueer.hello import hello
    from flask_frozen import Freezer

    freezer = Freezer(hello)

    if __name__ == '__main__':
        freezer.freeze()


if __name__ == '__main__':
    app.debug = True
    manager.run()
