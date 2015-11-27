# xueer_be

  the backend of xueer::学而后台
  
## 0. build
### virtual environment

    $ virtual venv
    $ source venv/bin/activate
    $ pip install -r requirement.text (--no-cache-dir)
    
### test database

    $ chmod 777 data.sh
    $ ./data.sh
    >> Role.insert_roles()
    >> quit()
    
### add user

    $ python manage.py adduser username email
    password: (输入密码,不显示) 
    confirm: （确认密码,不显示）

## 1. 参与人员

  朱承浩、王怡凡、黄刘胤

## 2. 提交流程

	fork这个仓库, 每一个新功能checkout一个新分支，向这个仓库的主分支提交
	朱承浩(@neo1218)负责合并和维护这个仓库

	ps: 请每次工作前务必git pull一下

## 3. 进度

	151102: 任务安排1+提交流程
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	151106: 任务安排2
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	151109: 任务安排3 + 提交数据库修正
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	151125: 任务安排4
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	151126: 本地可以运行(无语法错误)
	~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	151126: 完成清理工作(删除不必要的模版, 导航栏及其他)
	
	
## 4. ToDo
~~0. clean~~

    1. API 测试
        1. token可以请求(@王怡凡)
    2. 部署测试数据库(from sqlite to mysql)

