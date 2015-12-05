# coding: utf-8

"""
    获取首页的选课贴士, 每次5条. 按时间倒序排序。
    {
        'id':1,
        'title':"评价最高的课程合集，最热门的课程评价",
        'url':'/tips/?page=1',
        'img_url': "http://foo.com/a.png",
        'views':30,
        'likes':20,
        'date':'2015-11-25'
    }
"""
# 挖坑
# 填坑
from xueer.api_1_0 import api


@api.route('/tips/', methods=["GET"])
def get_tips():
    """
    获取首页的每日tip
    :return:
    """
    pass
