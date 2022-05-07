from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from requests import request
from Myapp.models import *
import json
import requests
import re

# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Q

@login_required
def welcome(request):
    return render(request,'welcome.html')

#控制不同的页面返回不同的数据：数据分发器
def child_json(request,eid,oid='',ooid=''):
    res = {}
    if eid == 'home.html':
        date = DB_home_href.objects.all()
        home_log = DB_apis_log.objects.filter(user_id=oid)[::-1]
        hosts = DB_host.objects.all()
        if ooid == '':
            res = {"hrefs": date, "home_log": home_log,"hosts":hosts}
        else:
            log = DB_apis_log.objects.filter(id=ooid)[0]
            res = {"hrefs": date, "home_log": home_log, "log": log,"hosts":hosts}

    if eid == 'project_list.html':
        if request.user.username=='admin':
            date = DB_project.objects.all().filter()
        else:
            date = DB_project.objects.all().filter(Q(other_user__contains=request.user.username) | Q(user=request.user.username))
        res = {"projects":date}
    if eid == 'P_apis.html':
        project = DB_project.objects.filter(id= oid)[0]
        project_folder = DB_project_folder.objects.filter(Q(project_id= oid) & Q(project_folder_id=''))
        project_host_folders = DB_project_host_folder.objects.filter(project_id=oid).order_by('-id').values()[::-1]
        project_host = DB_project_host_folder.objects.filter(project_id=oid).order_by('-id').values()[::-1]
        apis = DB_api.objects.filter(Q(project_id=oid) & Q(project_folder_id=''))

        res = {"project":project,"project_folder":project_folder,"apis":apis,"project_host_folders":project_host_folders,"project_host":project_host}
        # res = {"project":project,"apis":apis,'project_header':project_header,"hosts":hosts,"project_host":project_host}
    if eid == 'P_cases.html':
        project = DB_project.objects.filter(id= oid)[0]
        res = {"project":project}
    if eid == 'P_project_set.html':
        project = DB_project.objects.filter(id= oid)[0]
        res = {"project":project}
    if eid == 'P_cases.html':
        #这里应该是去数据库拿到这个项目的所有大用例了
        project = DB_project.objects.filter(id=oid)[0]
        Cases = DB_case.objects.filter(project_id=oid).order_by('index')
        apis = DB_api.objects.filter(project_id=oid)
        project_header = DB_project_header.objects.filter(project_id=oid)
        hosts = DB_host.objects.all()
        # project_host = DB_project_host.objects.filter(project_id = oid)
        # res = {"project":project,"Cases":Cases,"apis":apis,'project_header':project_header,"hosts":hosts,"project_host":project_host}
        res = {"project": project, "Cases": Cases, "apis": apis, 'project_header': project_header, "hosts": hosts}
    return res

#返回子页面
def child(request, eid, oid,ooid):
    # print("oid:%s" % oid)
    res = child_json(request,eid,oid,ooid)
    return render(request, eid,res)

# 获取公共参数
def glodict(request):
    userimg = str(request.user.id)+'.png'
    res = {"username":request.user.username,"userimg":userimg}
    return res

#进入主页
@login_required
def home(request,log_id=''):
    return render(request,'welcome.html',{"whichHTML": "home.html","oid":request.user.id,"ooid":log_id,**glodict(request)})

#进入登录页
def login(request):
    return render(request,'login.html')

#开始登录
def login_action(request):
    u_name = request.GET['username']
    p_word = request.GET['password']

    from django.contrib import auth
    user = auth.authenticate(username=u_name,password=p_word)

    if user is not None:
        auth.login(request,user)
        request.session['user'] = u_name
        #返回前端告诉前端成功
        return HttpResponse('成功')
    else:
        #返回前端告诉前端失败
        return HttpResponse('失败')
#注册
def register_action(request):
    u_name = request.GET['username']
    p_word = request.GET['password']
    if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",u_name):
        from django.contrib.auth.models import User
        try:
            user = User.objects.create_user(username=u_name,password=p_word)
            user.save()
            return HttpResponse('注册成功！')
        except:
            return HttpResponse('注册失败，用户名已存在')
    else:
        return HttpResponse('注册失败，用户名为邮箱格式')

#退出
def logout(request):
    from django.contrib import auth
    auth.logout(request)
    return HttpResponseRedirect('/login/')

#吐槽
def pei(request):
    tucao_text = request.GET['tucao_text']
    DB_tucao.objects.create(user=request.user.username,text=tucao_text)
    return HttpResponse('')

#帮助文档
def api_help(request):
    return render(request,'welcome.html',{"whichHTML":"help.html","oid":"",**glodict(request)})


#展示项目列表
def project_list(request):
    return render(request,'welcome.html',context={"whichHTML":"project_list.html","oid":"",**glodict(request)})

#删除项目
def delete_project(request):
    id = request.GET['id']
    DB_project.objects.filter(id=id).delete()
    DB_api.objects.filter(project_id=id).delete() #删除旗下接口
    all_Case = DB_case.objects.filter(project_id=id)
    for i in all_Case:
        DB_step.objects.filter(Case_id=i.id).delete() #删除步骤
        i.delete() #删除用例
    return HttpResponse('')

#删除
def delete(request):
    type = request.GET['type']
    id = request.GET['id']
    if type == 'folder':
        # DB_api.objects.filter(project_folder_id=id).delete()
        digui(id)
    elif type == 'project':
        project_folders= DB_project_folder.objects.filter(Q(project_id=id) & Q(project_folder_id=''))
        project_apis = DB_api.objects.filter(Q(project_id=id) & Q(project_folder_id='')).delete() #删除项目下第一级api
        for i in project_folders:
            digui(i.id)
        DB_project.objects.filter(id=id).delete() #删除项目
    else:
        DB_api.objects.filter(id=id).delete()

    # DB_project.objects.filter(id=id).delete()
    # DB_api.objects.filter(project_id=id).delete() #删除旗下接口
    # all_Case = DB_case.objects.filter(project_id=id)
    # for i in all_Case:
    #     DB_step.objects.filter(Case_id=i.id).delete() #删除步骤
    #     i.delete() #删除用例
    return HttpResponse('')

def digui(id):
    folders = DB_project_folder.objects.filter(project_folder_id=id)
    if folders:
        for i in folders:
            digui(i.id)
    DB_project_folder.objects.filter(id=id).delete()
    DB_api.objects.filter(project_folder_id=id).delete()


#添加项目
def add_project(request):
    project_name = request.GET['project_name']
    DB_project.objects.create(name=project_name,remark='',user=request.user.username,other_user='',local_variable_id=0)
    return HttpResponse('')

def edit_project(request):
    project_id = request.GET['project_id']
    local_variable_id = request.GET['local_variable_id']
    DB_project.objects.filter(id=project_id).update(local_variable_id=local_variable_id)
    return HttpResponse('')

#进入接口库
def open_apis(request,id):
    project_id = id
    return render(request,'welcome.html',{"whichHTML":"P_apis.html","oid":project_id,**glodict(request)})

#进入用例库
def open_cases(request,id):
    project_id = id
    return render(request,'welcome.html',{"whichHTML":"P_cases.html","oid":project_id,**glodict(request)})

#进入项目设置
def open_project_set(request,id):
    project_id = id
    return render(request,'welcome.html',{"whichHTML":"P_project_set.html","oid":project_id,**glodict(request)})

#保存项目设置
def save_project_set(request,id):
    project_id = id
    name = request.GET['name']
    remark = request.GET['remark']
    other_user = request.GET['other_user']
    project_mysql = request.GET['project_mysql']
    DB_project.objects.filter(id=project_id).update(name=name,remark=remark,other_user=other_user,project_mysql=project_mysql)
    return HttpResponse('')

#新增目录接口
def project_fodler_add(request):
    project_id = request.GET['project_id']
    project_folder_id = request.GET['id']
    project_name = request.GET['project_name']
    result = DB_project_folder.objects.create(project_id=project_id,project_folder_id=project_folder_id,name=project_name)
    folder_list = DB_project_folder.objects.filter(id=result.id)
    ret = {"folder_list":list(folder_list.values("id","project_id","project_folder_id","name"))[::-1]}
    return HttpResponse(json.dumps(ret), content_type='application/json')

#修改目录名
def project_fodler_edit(request):
    project_id = request.GET['project_id']
    id = request.GET['id']
    project_folder_name = request.GET['project_folder_name']
    DB_project_folder.objects.filter(id=id).update(name=project_folder_name)
    return HttpResponse('')
    # return HttpResponseRedirect('/apis/%s/' % project_id)

#修改接口名
def project_api_edit(request):
    project_id = request.GET['project_id']
    id = request.GET['id']
    project_api_name = request.GET['project_api_name']
    DB_api.objects.filter(id=id).update(name=project_api_name)
    return HttpResponse('')

#获取目录、接口列表
def folder_api_list(request):
    project_id = request.GET['project_id']
    id = request.GET['id']
    #获取目录下目录
    folder_list = DB_project_folder.objects.filter(Q(project_folder_id=id) & Q(project_id=project_id)).order_by('-id')
    api_list = DB_api.objects.filter(Q(project_folder_id=id) & Q(project_id=project_id)).order_by('-id')
    ret = {"folder_list":list(folder_list.values("id","project_id","project_folder_id","name"))[::-1],"api_list":list(api_list.values("id","project_id","name","api_method","api_host","api_url"))[::-1]}
    return HttpResponse(json.dumps(ret),content_type='application/json')

#新增接口
def project_api_add(request):
    project_id = request.GET['project_id']
    project_folder_id = request.GET['project_folder_id']
    api_name = request.GET['api_name']
    api_des = request.GET['api_des']
    result = DB_api.objects.create(project_id=project_id,project_folder_id=project_folder_id,name=api_name,des=api_des,api_method='post',api_url='')
    api_list = DB_api.objects.filter(id=result.id)
    ret = {"api_list": list(api_list.values("id","name","api_method","api_host","api_url"))[::-1]}
    return HttpResponse(json.dumps(ret), content_type='application/json')

#删除接口
def project_api_delete(request,id):
    project_id = DB_api.objects.filter(id=id)[0].project_id
    DB_api.objects.filter(id=id).delete()
    return HttpResponseRedirect('/apis/%s/'%project_id)

#保存接口备注
def save_bz(request):
    api_id = request.GET['api_id']
    bz_value = request.GET['bz_value']
    DB_api.objects.filter(id=api_id).update(des=bz_value)
    return HttpResponse('')

#获取接口备注
def get_bz(request):
    api_id = request.GET['api_id']
    bz_value = DB_api.objects.filter(id=api_id)[0].des
    return HttpResponse(bz_value)

#保存接口
def Api_save(request):
    #提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    api_body = request.GET['ts_api_body']
    api_name = request.GET['api_name']
    # ts_login = request.GET['ts_login']
    # ts_project_headers = request.GET['ts_project_headers']
    # if ts_body_method == '返回体':
    #     api = DB_api.objects.filter(id=api_id)[0]
    #     ts_body_method = api.last_body_method
    #     ts_api_body = api.last_api_body
    # else:
    #     ts_api_body = request.GET['ts_api_body']
    #保存数据
    DB_api.objects.filter(id=api_id).update(
        api_method=ts_method,
        api_url = ts_url,
        # api_login = ts_login,
        api_header = ts_header,
        body_method = ts_body_method,
        api_body = api_body,
        name = api_name,
        last_body_method=ts_body_method,
        last_api_body=api_body,
        # public_header = ts_project_headers
    )
    #返回
    return HttpResponse('success')

#获取接口数据
def get_api_data(request):
    api_id = request.GET['api_id']
    api = DB_api.objects.filter(id=api_id).values()[0]
    new_api = time_change(api)
    return HttpResponse(json.dumps(new_api),content_type='application/json')

def time_change(data):
    if 'datetime.datetime' in str(data):
        new_dict = {}
        for i in data:
            if data[i] != None:
                new_dict[i] = str(data[i])
            else:
                new_dict[i] = data[i]
        # data = new_dict
    return new_dict

#发送请求
def Api_send(request):
    # 提取所有数据
    api_id = request.GET['api_id']
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']
    api_name = request.GET['api_name']
    # ts_project_headers = request.GET['ts_project_headers'].split(',')
    # ts_login = request.GET['ts_login']
    ts_login = ''
    if ts_login == 'yes': #说明要调用登录态
        login_res = project_login_send_for_other(project_id=DB_api.objects.filter(id=api_id)[0].project_id)
    else:
        login_res = {}

    # 发送请求获取返回值
    if ts_header == '':
        ts_header = '{}'
    try:
        header = json.loads(ts_header)
    except:
        return HttpResponse('请求体不符合json格式！')

    if ts_body_method == '0':
        # form-data插入登录态
        if type(login_res) == dict:
            response = requests.request(ts_method.upper(),ts_url,headers=header,data={})
        else:
            response = login_res.request(ts_method.upper(),ts_url,headers=header,data={})
    elif ts_body_method == 'form-data':
        files = []
        payload = {}
        for i in eval(ts_api_body):
            payload[i[0]] = i[1]
        # print(payload)
        # form-data插入登录态
        if type(login_res) == dict:
            for i in login_res.keys():
                payload[i] = login_res[i]
            response = requests.request(ts_method.upper(),ts_url,headers=header,data=payload,files=files)
        else:
            response = login_res.request(ts_method.upper(), ts_url, headers=header, data=payload, files=files)
    elif ts_body_method == 'x-www-form-urlencoded':
        header['Content-Type'] = 'application/x-www-form-urlencoded'
        payload = {}
        for i in eval(ts_api_body):
            payload[i[0]] = i[1]

        response = requests.request(ts_method.upper(), ts_url, headers=header, data=payload)
    else: #这时肯定是raw的五个子选项
        response = requests.request(ts_method.upper(),ts_url,headers=header,json=json.loads(ts_api_body))
        # print(header)
        # print(ts_url)
        # print(ts_api_body)
        # print(ts_method)
        # print(response.text)

    #把返回值传给前端页面
    response.encoding="utf-8"
    DB_host.objects.update_or_create(host=ts_url)
    return HttpResponse(response.text)

#复制接口
def copy_api(request):
    api_id = request.GET['api_id']
    old_api = DB_api.objects.filter(id=api_id)[0]
    DB_api.objects.create(
        project_id=old_api.project_id,
        name=old_api.name,
        api_method=old_api.api_method,
        api_url=old_api.api_url,
        api_header=old_api.api_header,
        api_login=old_api.api_login,
        api_host=old_api.api_host,
        des=old_api.des,
        body_method=old_api.body_method,
        api_body=old_api.api_body,
        result=old_api.result,
        sign=old_api.sign,
        file_key=old_api.file_key,
        file_name=old_api.file_name,
        public_header=old_api.public_header,
        last_body_method=old_api.last_body_method,
        last_api_body=old_api.last_api_body
    )
    return HttpResponse('')

#异常值发送请求
def error_request(request):
    api_id = request.GET['api_id']
    new_body = request.GET['new_body']
    span_text = request.GET['span_text']
    api = DB_api.objects.filter(id=api_id)[0]
    method = api.api_method
    url = api.api_url
    host = api.api_host
    header = api.api_header
    body_method = api.body_method
    if header != '':
        header = json.loads(header)
    else:
        header = {}
    if host[-1] == '/' and url[0] == '/':  # 都有/
        url = host[:-1] + url
    elif host[-1] != '/' and url[0] != '/':  # 都没有/
        url = host + '/' + url
    else:  # 肯定有一个有/
        url = host + url
    try:
        if body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload, files=files)
        elif body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(new_body):
                payload[i[0]] = i[1]
            response = requests.request(method.upper(), url, headers=header, data=payload)
        elif body_method == 'Json':
            header['Content-Type'] = 'application/json'
            response = requests.request(method.upper(), url, headers=header, data=new_body.encode('utf-8'))
        else:
            return HttpResponse('非法的请求体类型')
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        res_json = {"response":response.text,"span_text":span_text}
        return HttpResponse(json.dumps(res_json),content_type='application/json')
    except:
        res_json = {"response": '对不起，接口未通！', "span_text": span_text}
        return HttpResponse(json.dumps(res_json), content_type='application/json')

# 首页发送请求
def Api_send_home(request):
    # 提取所有数据
    ts_method = request.GET['ts_method']
    ts_url = request.GET['ts_url']
    ts_host = request.GET['ts_host']
    ts_header = request.GET['ts_header']
    ts_body_method = request.GET['ts_body_method']
    ts_api_body = request.GET['ts_api_body']
    # 发送请求获取返回值
    try:
        if ts_header != '':
            header = json.loads(ts_header)#处理header
        else:
            header  = {}
    except:
        return HttpResponse('请求头不符合json格式！')
    # 写入到数据库请求记录表中
    DB_apis_log.objects.create(user_id=request.user.id,
                               api_method=ts_method,
                               api_url=ts_url,
                               api_header=ts_header,
                               api_host=ts_host,
                               body_method=ts_body_method,
                               api_body=ts_api_body,)
    # 拼接完整url
    if ts_host[-1] == '/' and ts_url[0] =='/': #都有/
        url = ts_host[:-1] + ts_url
    elif ts_host[-1] != '/' and ts_url[0] !='/': #都没有/
        url = ts_host+ '/' + ts_url
    else: #肯定有一个有/
        url = ts_host + ts_url
    try:
        if ts_body_method == 'none':
            response = requests.request(ts_method.upper(), url, headers=header, data={} )

        elif ts_body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload, files=files )

        elif ts_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(ts_api_body):
                payload[i[0]] = i[1]
            response = requests.request(ts_method.upper(), url, headers=header, data=payload )

        else: #这时肯定是raw的五个子选项：
            if ts_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Json':
                header['Content-Type'] = 'application/json'

            if ts_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if ts_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(ts_method.upper(), url, headers=header, data=ts_api_body.encode('utf-8'))

        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=ts_host)
        return HttpResponse(response.text)
    except Exception as e:
        return HttpResponse(str(e))

# 首页获取请求记录
def get_home_log(request):
    user_id = request.user.id
    all_logs = DB_apis_log.objects.filter(user_id=user_id)
    ret = {"all_logs":list(all_logs.values("id","api_method","api_host","api_url"))[::-1]}
    return HttpResponse(json.dumps(ret), content_type='application/json')

#获取完整的单一的请求记录数据
def get_api_log_home(request):
    log_id = request.GET['log_id']
    log = DB_apis_log.objects.filter(id=log_id)
    ret = {"log":list(log.values())[0]}
    return HttpResponse(json.dumps(ret),content_type='application/json')

#增加用例
def add_case(request,eid):
    all_len = len(DB_case.objects.filter(project_id=eid))
    DB_case.objects.create(project_id=eid,name='用例',index=all_len+1)
    return HttpResponseRedirect('/cases/%s/'%eid)

#删除用例
def del_case(request,eid,oid):
    DB_case.objects.filter(id=oid).delete()
    DB_step.objects.filter(Case_id=oid).delete()
    return HttpResponseRedirect('/cases/%s/'%eid)

#复制用例
def copy_case(request,eid,oid):
    old_case = DB_case.objects.filter(id=oid)[0]
    DB_case.objects.create(project_id=old_case.project_id,name=old_case.name+'_副本')
    return HttpResponseRedirect('/cases/%s/'%eid)

# 获取小用例步骤的数据
def get_small(request):
    case_id = request.GET['case_id']
    steps = DB_step.objects.filter(Case_id= case_id).order_by('index')
    ret = {"all_steps":list(steps.values("index","id","name")) }
    return HttpResponse(json.dumps(ret),content_type='application/json')

#上传头像
def user_upload(request):
    file = request.FILES.get("fileUpload",None) # 靠name获取上传的文件，如果没有，避免报错，设置成None

    if not file:
        return HttpResponseRedirect('/home/') #如果没有则返回到首页

    new_name = str(request.user.id) + '.png' #设置好这个新图片的名字
    print(new_name)
    destination = open("MyApp/static/user_img/"+new_name, 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in file.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()

    return HttpResponseRedirect('/home/') #返回到首页

#新增小步骤接口
def add_new_step(request):
    Case_id = request.GET['Case_id']
    project_id = request.GET['project_id']
    all_len = len(DB_step.objects.filter(Case_id=Case_id))
    DB_step.objects.create(project_id=project_id,Case_id=Case_id,name='我是新步骤',index=all_len+1)
    return HttpResponse('')

#删除小步骤接口
def delete_step(request,eid):

    step = DB_step.objects.filter(id=eid)[0] #获取待删除的step
    index = step.index #获取目标index
    Case_id = step.Case_id #获取目标所属的大用例id
    step.delete() #删除目标steps
    for i in DB_step.objects.filter(Case_id=Case_id).filter(index__gt=index): #遍历所有该大用例下的步骤中，序号大于目标index的步骤
        i.index -= 1 #执行顺序自减1
        i.save()
    return HttpResponse('')

# 获取小步骤
def get_step(request):
    step_id = request.GET['step_id']
    step = DB_step.objects.filter(id=step_id)
    steplist = list(step.values())[0]
    return HttpResponse(json.dumps(steplist),content_type='application/json')

# 保存小步骤
def save_step(request):
    step_id = request.GET['step_id']
    name = request.GET['name']
    index = request.GET['index']
    step_method = request.GET['step_method']
    step_url = request.GET['step_url']
    step_host = request.GET['step_host']
    step_header = request.GET['step_header']
    ts_project_headers = request.GET['ts_project_headers']
    mock_res = request.GET['mock_res']
    step_body_method = request.GET['step_body_method']
    step_api_body = request.GET['step_api_body']

    get_path = request.GET['get_path']
    get_zz = request.GET['get_zz']
    assert_zz= request.GET['assert_zz']
    assert_qz = request.GET['assert_qz']
    assert_path = request.GET['assert_path']
    step_login = request.GET['step_login']

    DB_step.objects.filter(id=step_id).update(name=name,
                                              index=index,
                                              api_method=step_method,
                                              api_url=step_url,
                                              api_host=step_host,
                                              api_header=step_header,
                                              public_header=ts_project_headers,
                                              mock_res=mock_res,
                                              api_body_method=step_body_method,
                                              api_body=step_api_body,
                                              get_path=get_path,
                                              get_zz=get_zz,
                                              assert_zz=assert_zz,
                                              assert_qz=assert_qz,
                                              assert_path=assert_path,
                                              api_login=step_login,
                                              )
    return HttpResponse('')

# 步骤详情页获取接口数据：
def step_get_api(request):
    api_id = request.GET['api_id']
    api = DB_api.objects.filter(id=api_id).values()[0]
    return HttpResponse(json.dumps(api),content_type='application/json')

# 运行大用例
def Run_Case(request):
    Case_id = request.GET['Case_id']
    Case = DB_case.objects.filter(id = Case_id)[0]
    steps = DB_step.objects.filter(Case_id=Case_id)
    from Myapp.run_case import run
    run(Case_id,Case.name,steps)
    return HttpResponse('')

# 运行所有用例
def run_all(request):
    project_id = request.GET['project_id']
    project = DB_project.objects.filter(id = project_id)[0]
    steps = DB_step.objects.filter(project_id = project_id)
    from Myapp.run_case import runall
    runall(project_id, project.name, steps)
    #return HttpResponse('')
    # Cases = DB_case.objects.filter(project_id=project_id).values()
    # Case_ids = [item['id'] for item in Cases]
    # for i in range(len(Case_ids)):
    #     Case_id = Case_ids[i]
    #     Case = DB_case.objects.filter(id=Case_id)[0]
    #     steps = DB_step.objects.filter(Case_id=Case_id)
    #     from MyApp.run_case import run
    #     run(Case_id, Case.name, steps)
    return HttpResponse('成功')
    #return HttpResponse(Case_ids)

# 查看报告
def look_report(request,eid):
    Case_id = eid
    return render(request,'Reports/%s.html'%Case_id)

# 保存项目公共请求头
def save_project_header(request):
    project_id = request.GET['project_id']
    req_names = request.GET['req_names']
    req_keys = request.GET['req_keys']
    req_values = request.GET['req_values']
    req_ids = request.GET['req_ids']

    names = req_names.split(',')
    keys = req_keys.split(',')
    values =req_values.split(',')
    ids = req_ids.split(',')

    for i in range(len(ids)):
        if names[i] != '':
            if ids[i] == 'new':
                DB_project_header.objects.create(project_id=project_id,name=names[i],key=keys[i],value=values[i])
            else:
                DB_project_header.objects.filter(id=ids[i]).update(name=names[i],key=keys[i],value=values[i])
        else:
            try:
                DB_project_header.objects.filter(id=ids[i]).delete()
            except:
                pass

    return HttpResponse('')

#保存用例名字
def save_case_name(request):
    id = request.GET['id']
    name = request.GET['name']
    DB_case.objects.filter(id=id).update(name=name)
    return HttpResponse('')

#保存用例排序
def save_case_index(request):
    id = request.GET['id']
    index = request.GET['index']
    DB_case.objects.filter(id=id).update(index=index)
    return HttpResponse('')

# 保存项目公共域名
def save_project_host(request):
    host_folder_id = request.GET['host_folder_id']
    req_names = request.GET['req_names']
    req_hosts = request.GET['req_hosts']
    req_ids = request.GET['req_ids']
    names = req_names.split(',')
    hosts = req_hosts.split(',')
    ids = req_ids.split(',')
    ids1 = req_ids.split(',')
    if req_ids:
        for i in range(len(ids)):
            if ids[i] == 'new':
                res = DB_project_host.objects.create(host_folder_id=host_folder_id,name=names[i],host=hosts[i])
                ids1.append(res.id)
                ids1.remove(ids[i])
            else:
                DB_project_host.objects.filter(id=ids[i]).update(name=names[i],host=hosts[i])
        DB_project_host.objects.filter(~Q(id__in=ids1) & Q(host_folder_id=host_folder_id)).delete() #删除项目下不在ids内的host
    else:
        res = DB_project_host.objects.filter(Q(host_folder_id=host_folder_id)).delete()  # 删除项目下所有的host
    return HttpResponse('')
#
# def get_project_host(request):
#     host_folder_id = request.GET['host_folder_id']
#     project_host = DB_project_host.objects.filter(host_folder_id=host_folder_id)

# 获取项目登录态
def project_get_login(request):
    project_id = request.GET['project_id']
    try:
        login = DB_login.objects.filter(project_id=project_id).values()[0]
    except:
        login = {}
    return HttpResponse(json.dumps(login),content_type='application/json')

#保存项目登录态接口
def project_login_save(request):
    # 提取所有数据
    project_id = request.GET['project_id']
    login_method = request.GET['login_method']
    login_url = request.GET['login_url']
    login_host = request.GET['login_host']
    login_header = request.GET['login_header']
    login_body_method = request.GET['login_body_method']
    login_api_body = request.GET['login_api_body']
    login_response_set = request.GET['login_response_set']
    code = request.GET['code']
    code_url = request.GET['code_url']
    # 保存数据
    project_login = DB_login.objects.filter(project_id=project_id)
    if project_login.exists():
        DB_login.objects.filter(project_id=project_id).update(
            api_method=login_method,
            api_url=login_url,
            api_header=login_header,
            api_host=login_host,
            body_method=login_body_method,
            api_body=login_api_body,
            set=login_response_set,
            code=code,
            code_url=code_url
        )
    else:
        DB_login.objects.filter(project_id=project_id).create(
            project_id=project_id,
            api_method=login_method,
            api_url=login_url,
            api_header=login_header,
            api_host=login_host,
            body_method=login_body_method,
            api_body=login_api_body,
            set=login_response_set,
            code=code,
            code_url=code_url
        )

    # 返回
    return HttpResponse('success')

def get_project_host(request):
    id = request.GET['host_folder_id']
    project_host = DB_project_host.objects.filter(host_folder_id=id).order_by('-id').values()[::-1]
    # print("project_host:%s" % project_host)
    return HttpResponse(json.dumps(project_host), content_type='application/json')

def add_host_folder(request):
    project_id = request.GET['project_id']
    name = request.GET['name']
    id = request.GET['id']
    if id:
        DB_project_host_folder.objects.filter(Q(project_id=project_id)&Q(id=id)).update(name=name)
    else:
        id = DB_project_host_folder.objects.create(name=name,project_id=project_id).id
    host_folder = DB_project_host_folder.objects.filter(project_id=project_id).order_by('-id').values()[::-1]
    ret = {"host_folder":host_folder,"id":id,"name":name}
    return HttpResponse(json.dumps(ret), content_type='application/json')

def del_host_folder(request):
    project_id = request.GET['project_id']
    id = request.GET['id']

    DB_project_host_folder.objects.filter(Q(project_id=project_id) & Q(id=id)).delete()
    DB_project_host.objects.filter(host_folder_id=id).delete()
    # host_folder = DB_project_host_folder.objects.filter(project_id=project_id).order_by('-id').values()[::-1]
    return HttpResponse('')

# 调试登录态接口
def project_login_send(request):
    # 第一步，获取前端数据
    login_method = request.GET['login_method']
    login_url = request.GET['login_url']
    login_host = request.GET['login_host']
    login_header = request.GET['login_header']
    login_body_method = request.GET['login_body_method']
    login_api_body = request.GET['login_api_body']
    login_response_set = request.GET['login_response_set']
    code = request.GET['code']
    code_url = request.GET['code_url']

    if login_header == '':
        login_header = '{}'

    # 第二步，发送请求
    try:
        header = json.loads(login_header) #处理header
    except:
        return HttpResponse('请求头不符合json格式！')

    # 拼接完整url
    if login_host[-1] == '/' and login_url[0] =='/': #都有/
        url = login_host[:-1] + login_url
    elif login_host[-1] != '/' and login_url[0] !='/': #都没有/
        url = login_host+ '/' + login_url
    else: #肯定有一个有/
        url = login_host + login_url


    try:
        if login_body_method == 'none':
            response = requests.request(login_method.upper(), url, headers=header, data={} )
        elif login_body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(login_api_body):
                payload[i[0]] = i[1]
            response = requests.request(login_method.upper(), url, headers=header, data=payload, files=files )

        elif login_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(login_api_body):
                payload[i[0]] = i[1]
            response = requests.request(login_method.upper(), url, headers=header, data=payload )

        # elif login_body_method == 'GraphQL':
        #     header['Content-Type'] = 'application/json'
        #     query = login_api_body.split('*WQRF*')[0]
        #     graphql = login_api_body.split('*WQRF*')[1]
        #     try:
        #         eval(graphql)
        #     except:
        #         graphql = '{}'
        #     payload = '{"query":"%s","variables":%s}' % (query, graphql)
        #     response = requests.request(login_method.upper(), url, headers=header, data=payload )


        else: #这时肯定是raw的五个子选项：
            if login_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Json':
                # 验证码插入
                if code == 'yes':
                    res = requests.get(code_url)
                    login_code = {"code":res.json()['data']}
                    login_api_body = json.loads(login_api_body)
                    for i in login_code.keys():
                        login_api_body[i] = login_code[i]
                    login_api_body = json.dumps(login_api_body)
                    print(login_api_body)
                else:
                    pass
                header['Content-Type'] = 'application/json'

            if login_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            response = requests.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))

        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=login_host)
        res = response.json()

        # 第三步，对返回值进行提取
        # 先判断是否是cookie持久化，若是，则不处理
        if login_response_set == 'cookie':
            end_res = {"response": response.text, "get_res": 'cookie保持会话无需提取返回值'}
        else:
            get_res = '' #声明提取结果存放
            for i in login_response_set.split('\n'):
                if i == "":
                    continue
                else:
                    i = i.replace(' ','')
                    key = i.split('=')[0] #拿出key
                    path = i.split('=')[1]  #拿出路径
                    value = res
                    for j in path.split('/')[1:]:
                        value = value[j]
                    get_res += key + '="' + value +'"\n'
            # 第四步，返回前端
            end_res = {"response":response.text,"get_res":get_res}
        return HttpResponse(json.dumps(end_res),content_type='application/json')
    except Exception as e:
        end_res = {"response":str(e),"get_res":''}
        return HttpResponse(json.dumps(end_res),content_type='application/json')

# 调用登陆态接口
def project_login_send_for_other(project_id):
    # 第一步，获取数据
    login_api= DB_login.objects.filter(project_id=project_id)[0]
    # print('login_api:%s'% login_api)
    login_method = login_api.api_method
    login_url = login_api.api_url
    login_host = login_api.api_host
    login_header = login_api.api_header
    login_body_method = login_api.body_method
    login_api_body = login_api.api_body
    login_response_set = login_api.set
    code = login_api.code
    code_url = login_api.code_url
    if login_header == '':
        login_header = '{}'
    # 第二步，发送请求
    try:
        header = json.loads(login_header) #处理header
    except:
        return HttpResponse('请求头不符合json格式！')
    # 拼接完整url
    if login_host[-1] == '/' and login_url[0] =='/': #都有/
        url = login_host[:-1] + login_url
    elif login_host[-1] != '/' and login_url[0] !='/': #都没有/
        url = login_host+ '/' + login_url
    else: #肯定有一个有/
        url = login_host + login_url

    try:
        if login_body_method == 'none':
            # 先判断是否是cookie持久化，若是，则不处理
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data={} )
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data={} )
        elif login_body_method == 'form-data':
            files = []
            payload = {}
            for i in eval(login_api_body):
                payload[i[0]] = i[1]
            # 先判断是否是cookie持久化，若是，则不处理
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=payload, files=files)
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=payload, files=files)

        elif login_body_method == 'x-www-form-urlencoded':
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            payload = {}
            for i in eval(login_api_body):
                payload[i[0]] = i[1]
                # 先判断是否是cookie持久化，若是，则不处理
                if login_response_set == 'cookie':
                    a = requests.session()
                    a.request(login_method.upper(), url, headers=header, data=payload)
                    return a
                else:
                    response = requests.request(login_method.upper(), url, headers=header, data=payload )

        # elif login_body_method == 'GraphQL':
        #     header['Content-Type'] = 'application/json'
        #     query = login_api_body.split('*WQRF*')[0]
        #     graphql = login_api_body.split('*WQRF*')[1]
        #     try:
        #         eval(graphql)
        #     except:
        #         graphql = '{}'
        #     payload = '{"query":"%s","variables":%s}' % (query, graphql)
        #     response = requests.request(login_method.upper(), url, headers=header, data=payload )

        else:  # 这时肯定是raw的五个子选项：
            if login_body_method == 'Text':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'JavaScript':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Json':
                # 验证码插入
                if code == 'yes':
                    res = requests.get(code_url)
                    login_code = {"code": res.json()['data']}
                    login_api_body = json.loads(login_api_body)
                    for i in login_code.keys():
                        login_api_body[i] = login_code[i]
                    login_api_body = json.dumps(login_api_body)
                    print(login_api_body)
                else:
                    pass
                header['Content-Type'] = 'application/json'

            if login_body_method == 'Html':
                header['Content-Type'] = 'text/plain'

            if login_body_method == 'Xml':
                header['Content-Type'] = 'text/plain'
            # 先判断是否是cookie持久化，若是，则不处理
            if login_response_set == 'cookie':
                a = requests.session()
                a.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))
                return a
            else:
                response = requests.request(login_method.upper(), url, headers=header, data=login_api_body.encode('utf-8'))
        # 把返回值传递给前端页面
        response.encoding = "utf-8"
        DB_host.objects.update_or_create(host=login_host)
        res = response.json()
        # 第三步，对返回值进行提取
        get_res = {}  # 声明提取结果存放
        for i in login_response_set.split('\n'):
            if i == "":
                continue
            else:
                i = i.replace(' ', '')
                key = i.split('=')[0]  # 拿出key
                path = i.split('=')[1]  # 拿出路径
                value = res
                for j in path.split('/')[1:]:
                    value = value[j]
                get_res[key] = value
        return get_res
    except Exception as e:
        return {}
