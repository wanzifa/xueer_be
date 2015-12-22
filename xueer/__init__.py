# -*- coding:utf-8 -*-
import os

from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import config


app = Flask(__name__)
app.config.from_object(config['default'])
config['default'].init_app(app)
# app.config.from_object(config['testing'])
# config['testing'].init_app(app)


db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
moment = Moment(app)

<<<<<<< HEAD
    # regist blueprint
    from hello import hello
    app.register_blueprint(hello, url_prefix='/hello')

    from auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    from api_1_0 import api
    app.register_blueprint(api, url_prefix='/api')
=======

from hello import hello
app.register_blueprint(hello)

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')
>>>>>>> a73d146f808268e47822f03b8727d286dd637d4d

from api_1_0 import api as api_1_0_blueprint
app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
