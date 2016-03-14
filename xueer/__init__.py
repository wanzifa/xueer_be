# coding: utf-8
"""
xueer
~~~~~

    华中师范大学评课系统

"""
import os

from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from xueer_config import config


app = Flask(__name__)
app.config.from_object(config['product'])
# app.config.from_object(config['develop'])
# app.config.from_envvar("XUEER_SERVER_SETTING")


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
moment = Moment(app)


from hello import hello
app.register_blueprint(hello)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

