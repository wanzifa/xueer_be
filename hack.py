# coding: utf-8
"""
  hack.py
  ~~~~~~~

    hack for website info

"""

from xueer import app
from flask import request, render_template


@app.route('/info/')
def hack_info():
  IP = request.remote
