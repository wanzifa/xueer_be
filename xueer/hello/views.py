# coding: utf-8

from . import hello


@hello.route('/hello')
def hello():
    return "<h1>hello for neo1218!</h1>"
