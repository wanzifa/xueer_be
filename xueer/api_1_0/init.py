from flask import Blueprint


api = Blueprint('api', __name__)


from . import authentication, comments, courses, decorators, errors, teachers, users
