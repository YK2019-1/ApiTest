"""ApiTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from Myapp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^welcome/$',welcome),#进入首页
    url(r'^home/$',home),
    url(r"^child/(?P<eid>.+)/(?P<oid>.*)/(?P<ooid>.*)/$", child),  # 返回子页面
    url(r'^login/$',login), #进入登录页面
    url(r'^login_action/$',login_action), #登录
    url(r'^register_action/$',register_action), #注册
    url(r'^accounts/login/$',login),#非登录状态进入自动跳到登录界面
    url(r'^logout/$',logout),#退出登录
    url(r'^pei/$',pei),#吐槽
    url(r'^help/$',api_help),#进入帮助文档
    url(r'^project_list/$',project_list),#进入项目列表
    url(r'^delete_project/$',delete_project),#删除项目
    url(r'^delete/$',delete),#删除目录、接口、项目
    url(r'^add_project/$',add_project),#添加项目
    url(r'^edit_project/$',edit_project),

    url(r'^apis/(?P<id>.*)/$',open_apis),#进入接口库
    url(r'^cases/(?P<id>.*)/$',open_cases),#进入用例库
    url(r'^project_set/(?P<id>.*)/$',open_project_set),#进入项目设置
    url(r'^save_project_set/(?P<id>.*)/$',save_project_set),#保存项目设置
    url(r'^save_case_name/$',save_case_name),#保存用例名字
    url(r'^save_case_index/$',save_case_index),#保存用例排序
    url(r'^project_fodler_add/$',project_fodler_add),#新增目录
    url(r'^project_fodler_edit/$',project_fodler_edit),#编辑目录名
    url(r'^project_api_edit/$',project_api_edit),#编辑接口名
    url(r'^folder_api_list/$',folder_api_list), #获取目录、接口列表
    url(r'^project_api_add/$',project_api_add),#新增接口
    url(r'^project_api_delete/(?P<id>.*)/$',project_api_delete),#删除接口
    url(r'^save_bz/$',save_bz),#保存接口备注
    url(r'^get_bz/$',get_bz),#获取接口备注
    url(r'^Api_save/$',Api_save),#保存接口
    url(r'^get_api_data/$',get_api_data),#获取接口数据
    url(r'^Api_send/$',Api_send),#发送请求
    url(r'^copy_api/$',copy_api),#复制接口
    url(r'^error_request/$',error_request), #调用异常测试接口

    url(r'^Api_send_home/$',Api_send_home),#首页发送请求
    url(r'^get_home_log/$',get_home_log),#获取最新请求记录
    url(r'^get_api_log_home/$',get_api_log_home),#获取完整的单一的请求记录数据
    url(r'^home_log/(?P<log_id>.*)/$',home),# 再次进入首页，这次要带着请求记录

    url(r'^add_case/(?P<eid>.*)/$', add_case),  #增加用例
    url(r'^del_case/(?P<eid>.*)/(?P<oid>.*)/$', del_case),  # 删除用例
    url(r'^copy_case/(?P<eid>.*)/(?P<oid>.*)/$', copy_case),  # 复制用例

    url(r'^get_small/$',get_small), # 获取小用例步骤的列表数据
    url(r'^user_upload/$',user_upload), # 上传头像

    url(r'^add_new_step/$',add_new_step), #新增小步骤接口
    url(r'delete_step/(?P<eid>.*)/$',delete_step), #删除小步骤接口
    url(r'get_step/$',get_step), #获取小步骤
    url(r'save_step/$',save_step), #保存小步骤
    url(r'step_get_api/$',step_get_api), #步骤详情页获取接口数据
    url(r'Run_Case/$',Run_Case), #运行大用例
    url(r'look_report/(?P<eid>.*)/$',look_report), # 查看报告

    url(r'save_project_header/$',save_project_header), #保存项目公共请求头
    url(r'save_project_host/$',save_project_host), #保存项目公共域名
    url(r'get_project_host/$',get_project_host),#获取项目公共域名
    url(r'add_host_folder/$',add_host_folder),#新增环境变量目录
    url(r'del_host_folder/$',del_host_folder),

    url(r'project_get_login/$',project_get_login), #获取项目登录态接口
    url(r'project_login_save/$',project_login_save), #保存项目登录态接口
    url(r'project_login_send/$',project_login_send), # 调试登录态接口

    url(r'run_all/$',run_all),#运行所有用例
]
