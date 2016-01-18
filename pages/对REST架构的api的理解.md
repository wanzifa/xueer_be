title: "对REST架构的api的理解"
date: 2015-11-30 10:54:43

# 对REST架构的api 的理解


---
这篇文章是《flask web开发》这本书第十四章的学习总结，主要是对书中所介绍的restful架构的api的认识，结合一些网络资源的辅助，把自己对这一块的理解记录一下。
## 为什么会有api？ ##
在之前的学习过程中，都是写完代码后直接让客户端去访问服务器端的程序，逻辑方面的东西基本上都在服务器端实现，不需要考虑api。所以，刚接触api的时候，我比较关心的是它出现的原因和它的作用。
api的出现，与web程序的发展趋势分不开。随着**业务逻辑越来越多地移到了客户端这一侧**，比起逻辑实现，服务器需要着重体现的是它的**数据存取功能**。“服务器变成了web服务或api”————这是书中api部分的第一段话，一开始很让我不解，因为api的全称是应用编程接口，而服务器上面有那么多内容，怎么会只充当一个接口呢。后来读了这部分的代码之后，觉得这句话应该是说“服务器可以提供web服务，api是服务器端的一部分“，而api的作用，正是负责服务器端与客户端之间的**资源流通**。如何实现资源流通，在第三部分会用代码来辅助理解，现在先有个宏观的把握。

## api的版本问题 ##
在本书的代码中，api部分的文件名其实是“api1.0”。为什么后面还要跟一个版本号？因为服务器虽然可是随时更新web浏览器的客户端（毕竟服务器是完全掌控程序的），但是无法强制更新手机中的应用呀（因为手机应用和服务器程序是独立开发的）。万一用户拒绝更新，还想使用旧版本，我们就必须保证旧版本也可用，新版本也可用，而且既然更新就很可能会更新多次，所以需要保留的api版本也会比较多。


----------


## 关于REST架构 ##
 基于Web的架构，实际上就是各种规范的集合，这些规范共同组成了Web架构。比如Http协议，比如客户端服务器模式，这些都是规范。每当我们在原有规 范的基础上增加新的规范，就会形成新的架构。而REST正是这样一种架构，他结合了一系列的规范，而形成了一种新的基于Web的架构风格。
REST的全称是“Representational State Transfer”，即表现层状态转移。本书介绍的api就是使用的这种架构。
**资源是REST架构的核心概念**，每个资源都要用唯一的url表示，某一类资源的集合也要用一个url，举个例子：
表示**某一个资源**：api／posts／12345 可以表示id为12345的一篇文章。
表示**某一类资源**：api／posts／ 就可以啦，只需要省去具体的id～～
既然有url，就有相应的请求方法啦：
get：获取目标资源（常用）
post：提交新资源（常用）
put：修改现有资源或者创建新资源
delete：删除目标集合的所有资源


----------

## REST架构的api的代码体现 ##
其实就是**资源交互**的代码体现。
我们之前说服务器着重体现的就是数据存取功能，那么如何提供这个数据，也就是JSON：

    json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
上面这段代码，**打开了资源流通的大门**，用字典的形式存储了一篇博客文章的对应资源，客户端可以通过这个字典访问服务器的信息。
我们在实现某一个功能的时候，不一定要用到JSON文件里的所有资源，比如当我们需要创建新文章的时候：

    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)
这段代码实现了资源的调用（从JSON里调用目的资源非常方便）。整个只用了一个body属性，因为其它属性在这里并没有什么意义嘛～

说完了如何提供信息，我们还需要关注如何修改信息。
新朋友出场啦！让我们来看看这个函数——jsonify（）




    @main.app_errorhandler(404)
    def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response


这个函数的作用就是修改JSON里面的资源内容，比如上面这个操作，往JSON里编辑了一个error属性和message属性，一旦在客户端的某一个操作触发这个函数，就可以生成一个错误响应啦～～

思路就是这样啦，正在撰写我的第一个api，如果在写的过程中有觉得重要的遗漏了的，再更新过来。
