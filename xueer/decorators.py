# coding:utf-8

from functools import wraps
from flask import abort, request, g
from flask_login import current_user
from xueer.models import User


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_header = request.headers['authorization']
        token = token_header[6:]
        if token:
            g.current_user = User.verify_auth_token(token)
            if not g.current_user.is_administrator():
                abort(403)
            return f(*args, **kwargs)
    return decorated

