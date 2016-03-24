from ..models import Courses, Tags, Search
import jieba
from .. import db

def save():
   for course in Courses.query.all():
       seg_list = jieba.cut_for_search(course.name)
       str = '/'.join(seg_list)
       results = str.split('/')
       results.append(course.name)
       for result in results:
           if(Search.query.filter_by(name=result).first() == None):
               s = Search(name=result)
               s.courses.append(course)
               db.session.add(s)
               db.session.commit()
           elif(course not in Search.query.filter_by(name=result).first().courses.all()):
               s = Search.query.filter_by(name=result).first()
               s.courses.append(course)
               db.session.add(s)
               db.session.commit()

   for tag in Tags.query.all():
       seg_list = jieba.cut_for_search(tag.name)
       str = '/'.join(seg_list)
       results = str.split('/')
       results.append(tag.name)
       for result in results:
           if(Search.query.filter_by(name=result).first() == None):
               s = Search(name=result)
               s.tags.append(tag)
               db.session.add(s)
               db.session.commit()
           elif(tag not in Search.query.filter_by(name=result).first().tags.all()):
               s = Search.query.filter_by(name=result).first()
               s.tags.append(tag)
               db.session.add(s)
               db.session.commit()