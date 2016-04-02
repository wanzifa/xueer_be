import requests
from xueer.models import __package__import Courses, CourseCategories
import base64

token=base64.b64encode('eyJpZCI6MX0.32BFm_OeqXXn558zOr2t9queYDc:')
print token

Headers = {
            'host': 'xueer.ccnuer.cn',
            'connection': 'keep-alive',
            'authorization':"Basic %s" % token,
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0; WOW64)'
         }
                                                                }

for course in Courses.query.all():
        id=course.id
            data={
                    'name':course.name,
                    'teacher':course.teacher,
                    'category_id':course.category_id,
                    'sub_category_id':course.subcategory_id,
                    'type_id':course.type_id
                                                 }
        r=requests.put('http://xueer.ccnuer.cn/api/v1.0/courses/%s/' % str(id),data=str(data),headers=Headers)
                    # r=requests.put('http://127.0.0.1:8000/api/v1.0/courses/14/data',
                    # headers=Headers)
        print r.status_code

