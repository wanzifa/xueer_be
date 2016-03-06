# coding: utf-8

import json
from flask import Flask
from flask import render_template,request
from jinja2 import Environment
from . import hello


def is_mobie():
    platform = request.user_agent.platform
    if platform in ["android", "iphone", "ipad"]:
        return True
    else:
        return False


@hello.route('/')
def index():
    flag = is_mobie()
    if flag:
        return render_template("hello/mobile/index.html")
    else:
        return render_template("hello/desktop/index.html")
