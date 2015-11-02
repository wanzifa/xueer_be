# -*- coding:utf-8 -*-

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from _basedir import basedir
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flasky:1234@localhost/flaskynew?charset=utf8'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://neo1218:test@115.28.152.113/xueer_test.myd?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'xueer_test.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
login_manager.init_app(app)


# regist blueprint
from hello import hello
app.register_blueprint(hello)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')
