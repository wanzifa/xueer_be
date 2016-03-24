# coding: utf-8

"""basedir: 系统根路径"""

import os
# 也就是说: flask-whooshalchemy自己包含一个分词, 这个分词不知道有没有使用,
# 或者和jieba一起使用, 其实分词这块已经不需要 flask-whooshalchemy了,
# 问题就是分词表创建完后的搜索问题, 不知道whooshalchemy有没有搜索优化,
# 然后如果建立关系的话, 其实就不需要搜索优化的问题, 关系可以直接定向导入


basedir = os.path.abspath(os.path.dirname(__file__))
