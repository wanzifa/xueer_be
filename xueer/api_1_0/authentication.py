from flask import jsonify
from flask.ext.httpauth import HTTPBasicAuth
from flask import g, jsonify
from . import api
from ..models import User, AnonymousUser


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user == AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_password(email_or_token)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return false
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.before_request
def before_request():
    pass


@auth.login_required
@api.route('/token', method = ['POST', 'GET'])
def get_token():
    if g.token_used:
         return unauthorized('Invalid credentials')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration = 3600),
        'expiration': 3600
    })
