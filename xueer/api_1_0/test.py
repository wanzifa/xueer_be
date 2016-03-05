# coding: utf-8
# test.py: api for test

from . import api
from xueer.models import Comments
from flask import jsonify


@api.route('/test/token/')
def get_test_token():
    """ get token for test """
    return jsonify(
        Comments.test_json()
    ), 200
