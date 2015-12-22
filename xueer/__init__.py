# -*- coding:utf-8 -*-

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    """create function"""
    # create flask app
    app = Flask(__name__)

    # import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # init flask ext with app
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # regist blueprint
    from hello import hello
    app.register_blueprint(hello, url_prefix='/hello')

    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api')

    return app
