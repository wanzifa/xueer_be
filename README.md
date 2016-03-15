# 学而后端代码库
![xueer](https://avatars2.githubusercontent.com/u/10476331?v=3&s=200)

## 1. 介绍
学而后端代码主要使用[python flask](https://github.com/mitsuhiko/flas://github.com/mitsuhiko/flask)框架开发,
提供后端数据存储[PostgreSql](http://www.postgresql.org),
并向[学而移动版](https://github.com/Muxi-Studio/Xueer_Moblie),
和学而桌面版(待开发)提供数据接口.

## 2. 本地构建开发环境

### 1. clone 这个仓库到本地

    $ git clone https://github.com/Muxi-Studio/xueer_be.git

### 2. 创建虚拟环境并安装扩展

    $ virtualenv venv && source venv/bin/activate
    $ pip install -r requirements/dev.txt

如果pip安装较慢推荐使用[豆瓣pypi源](https://www.douban.com/note/302711300/)

### 3. 构建本地数据库
本地数据库使用轻量的[sqlite](https://www.sqlite.org)

    $ python manage.py db init  # 创建迁移目录
    $ python manage.py db migrate  # 初始迁移
    $ python manage.py db upgrade  # 更新数据库

### 4. 创建用户角色
学而设有三种用户角色(普通用户, 协管员, 管理员)

    $ python manage.py shell
    >> Role.insert_roles()

### 5. 添加用户

    $ python manage.py adduser username useremail
    password: 
    comfirmd: 

完成以上步骤, 你就可以在本地运行学而桌面版(目前就一个placeholder页面),
以及在浏览器手机调试器中运行学而web app, 并使用学而的API服务.

    $ python manage.py runserver -d

Tips: 推荐使用[Navicat](http://www.navicat.com)管理数据库.

## 3. 学而后端主要部分和实现原理

### 1. 同步开发模式
由于学而后端主要通过API提供数据, 所以采用前后端分离的同步开发模式, 前后端约定好API文档后
前端使用[mock虚拟数据](http://mockjs.com)占位, 后端则使用[httpie](https://github.zohttps://github.com/jkbrzt/httpieem/)在终端
测试API.

### 2. 开发环境设置
学而后端配置文件采用python 类的形式将配置环境分割为4个部分:
<code>公有配置,开发配置,测试配置,生产配置</code>, 分别对应相应的扩展txt文件. <br/>
并且采用系统环境变量配置密钥和数据库连接路径, 既保护了敏感信息,
又有效解决了不同环境下配置的冲突问题. <br/>
linux设置环境变量的方法

    $ vim ~/.bashrc
    ==== file .bashrc ====

    set ENVVAR
    export ENVVAR="xxxxxxxxx"
    export PATH=$PATH:$ENVVAR

    ======================
    $ source ~/.bashrc

### 3. 桌面版和移动版路由
桌面版和移动版路由使用flask的路由、视图函数实现, 本身没有太多逻辑功能,
只是作为一个路由占位,
并使用<code>request.user_agent.platform</code>判断用户访问平台(代码如下)

    def is_mobie():
        platform = request.user_agent.platform
        if platform in ["android", "iphone", "ipad"]:
            return True
        else:
            return False

### 4. API
采用flask编写API, 具体可以参见这篇博客

1. [flask编写API的核心思想](http://neo1218.github.io/api/)

### 5. 数据存储
学而后台在开发过程中使用过3个数据库(sqlite, mysql, postgresql),
最终决定使用两个数据库(sqlite和postgresql)分别用于本地环境和生产环境.需要注意sqlite不支持行更新和删除.

+ postgresql资源
    + [centos源码编译安装初始化postgresql数据库](http://www.centoscn.com/image-text/install/2015/0524/5518.html)
    + [postgresql设置允许远程访问的方法](http://blog.csdn.net/ll136078/article/details/12747403)
    + [postgresql新手入门](http://www.ruanyifeng.com/blog/2013/12/getting_started_with_postgresql.html)

### 6. 全文搜索
基本思路: 主要是一个save函数和一个search类, save函数实现对存入的每一个课程／教师／标签名进行排查, 对没有分的进行分词
search类用于存储这些分词 并且建立每个分词于原课程／教师／标签的关系.

+ [flask-whooshalchemy](https://github.com/gyllstromk/Flask-WhooshAlchemy)
+ [jieba分词](https://github.com/fxsjy/jieba)

### 7. 后端功能测试

+ 测试工具: [httpie](https://github.com/jkbrzt/httpie/)
    + 需要注意 httpie 会自动将 --auth 字段的值进行base64加密, 以及将token进行 "Basic Basic64(token:)" 编码
+ 抓包工具: [mitmproxy](http://mitmproxy.org)
    + [教程](http://liuxiang.logdown.com/posts/192057-use-mitmproxy-to-monitor-http-requests)

### 7. 项目部署

[nginx](http://nginx.org) + [supervisord](http://supervisord.org) + [gunicorn](http://gunicorn.org) + wsgi <br/>
**nginx 反向代理gunicorn启动flask应用,使用supervisord管理进程**

1. [supervisord使用教程](http://www.restran.net/2015/10/04/supervisord-tutorial/)
2. [nginx常用命令](http://www.cnblogs.com/derekchen/archive/2011/02/17/1957209.html)
3. [gunicorn与uwsgi](http://lenciel.cn/2013/08/why-you-need-something-like-gunicorn/)

### 8. 其他

1. 压力测试工具: [siege](https://github.com/JoeDog/siege)
2. 统计工具: 百度统计...

