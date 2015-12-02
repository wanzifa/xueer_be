from flask import request, jsonify, url_for
from .. import db
from ..models import User
from . import api


@api.route('/api/register', methods=['GET', 'POST'])
def register():
    """
    用户注册页面
    """
    user = User.from_json(request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json()), 201, {'Location': url_for('api.get_user_id', id=user.id, _external=True)}
