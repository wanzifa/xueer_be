# -*- coding:utf-8 -*-  
from flask import Blueprint

hello = Blueprint('hello', __name__)

from app.hello import views, errors
from ..models import Permission

@hello.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
