# coding: utf-8

from xueer.exceptions import ValidationError
from flask import jsonify
from . import api


def not_found(message):
    response = jsonify({'error': 'not_found', 'message': message})
    response.status_code = 404
    return response


def bad_request(message):
    response = jsonify({'error': 'bad_request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unathorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def server_error(message):
    response = jsonify({'error': 'server_error', 'message': message})
    response.status_code = 500
    return response


"""
@api.error_handler(ValidationError)
def ValidationError(e):
     return bad_request(e.args[0])


@api.error_handler(ValidationError)
def ValidationError(e):
     return not_found(e.args[0])


@api.error_handler(ValidationError)
def ValidationError(e):
     return unauthorized(e.args[0])


@api.error_handler(ValidationError)
def ValidationError(e):
    return forbidden(e.args[0])


@api.error_handler(ValidationError)
def ValidationError(e):
    return server_error(e.args[0])
"""
