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
from flask import jsonify, url_for, request, current_app
from sqlalchemy import desc
from ..models import Tips
from . import api
from xueer import db
import json
from xueer.api_1_0.authentication import auth


@api.route('/tips', methods=["GET"])
def get_tips():
    """
    获取首页的每日tip
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = Tips.query.order_by(Tips.timestamp.desc()).paginate(
        page, per_page=current_app.config['XUEER_TIPS_PER_PAGE'],
        error_out=False
    )
    tips = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_tips', page=page - 1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_tips', page=page + 1, _external=True)
    tips_count = len(Tips.query.all())
    if tips_count%current_app.config['XUEER_TIPS_PER_PAGE'] == 0:
        page_count = tips_count//current_app.config['XUEER_TIPS_PER_PAGE']
    else:
        page_count = tips_count//current_app.config['XUEER_TIPS_PER_PAGE']+1
    last = url_for('api.get_tips', page=page_count, _external=True)
    return json.dumps(
        [tip.to_json() for tip in tips],
        ensure_ascii=False,
        indent=1
    ), 200, {'link': '<%s>; rel="next", <%s>; rel="last"' % (next, last)}


@api.route('/tip/<int:id>', methods=['GET'])
def get_tip_id(id):
    """
    获取已知id对应的tip
    :return:
    """
    tip = Tips.query.get_or_404(id)
    return jsonify(
        tip.to_json()
    )


@api.route('/tip/<int:id>', methods=['GET', 'POST'])
@auth.login_required
def new_tip(id):
    """
    发布一条新贴士
    :param id: 贴士id
    :return:
    """
    tip = Tips.from_json(request.json)
    db.session.add(tip)
    db.session.commit()
    return jsonify(
        tip.to_json()), 201, {
               'Location': url_for(
                    'api.get_tip_id',
                    id=tip.id, _external=True
               )
           }


@api.route('/tip/<int:id>', methods=['GET', 'DELETE'])
@auth.login_required
def delete_tip(id):
    """
    删除一个贴士
    :param id: 贴士id
    :return:
    """
    tip = Tips.query.get_or_404(id)
    db.session.delete(tip)
    db.session.commit()
    return jsonify({
        'message': '该贴士已被删除'
    })




