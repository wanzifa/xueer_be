# coding: utf-8
"""
    manage.py
    ~~~~~~~~~

    xueer backend management

"""

from getpass import getpass
import sys
import os
import base64
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask import g
from xueer import db, app
from xueer.models import Permission, Role, User, AnonymousUser, Courses, CourseCategories, \
    CourseTypes, Comments, Teachers, Tags, Tips, Search


# set encoding utf-8
reload(sys)
sys.setdefaultencoding('utf-8')


manager = Manager(app)
migrate = Migrate(app, db)


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
            password=base64.b64encode(password)
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
