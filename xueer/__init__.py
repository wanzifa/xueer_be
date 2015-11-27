# -*- coding:utf-8 -*-

from flask import Flask
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
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
    app.register_blueprint(hello)

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
