from django.contrib import admin

# Register your models here.
from Myapp.models import *

admin.site.register(DB_tucao) #注册吐槽表
admin.site.register(DB_home_href)#注册超链接表
admin.site.register(DB_project)#注册项目表
admin.site.register(DB_project_folder)#注册项目目录表
admin.site.register(DB_api)#注册接口表
admin.site.register(DB_apis_log)#注册接口日志表
admin.site.register(DB_case)#注册用例表
admin.site.register(DB_step)#注册测试步骤表
admin.site.register(DB_project_header)#注册全局请求头表
admin.site.register(DB_host) #注册域名表
admin.site.register(DB_project_host)#环境变量
admin.site.register(DB_project_host_folder) #项目环境变量目录
admin.site.register(DB_login) #注册登录态表
