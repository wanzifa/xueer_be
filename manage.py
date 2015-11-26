# coding: utf-8

import sys
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
# from flask.ext.admin import Admin
# from flask.ext.admin.contrib.sqla import ModelView
from xueer import app, db
from xueer.models import Permission, Role, User, AnonymousUser, Courses, CourseCategories, \
		 CourseTypes, Comments,	Teachers, Tags


# 编码设置
reload(sys)
sys.setdefaultencoding('utf-8')


manager = Manager(app)
migrate = Migrate(app, db)
# admin = Admin(app, name="")


def make_shell_context():
    """自动加载环境"""
    return dict(
        app = app,
        db = db,
        Permission = Permission,
        Role = Role,
        User = User,
        AnonymousUser = AnonymousUser,
        Courses = Courses,
        CourseCategories = CourseCategories,
        CourseTypes = CourseTypes,
        Comments = Comments,
        Teachers = Teachers,
        Tags = Tags
        )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# 后台数据库管理界面
# admin.add_view(ModelView([models], db.session))


@manager.command
def test():
    """运行测试"""
    import unittest
    tests = unittest.TestLoader().discover('test')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    app.debug = True
    manager.run()
