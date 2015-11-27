# -*- coding:utf-8 -*-

from flask import Flask
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from _basedir import basedir
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = "I hate flask hahahahhahahahhahahha"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flasky:1234@localhost/flaskynew?charset=utf8'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://neo1218:test@115.28.152.113/xueer_test.myd?charset=utf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'xueer_test.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['FLASK_COMMENTS_PER_PAGE'] = 10
app.config['FLASK_COURSES_PER_PAGE'] = 10
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


moment = Moment(app)
db = SQLAlchemy(app)
login_manager.init_app(app)


# regist blueprint
from hello import hello
app.register_blueprint(hello)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
