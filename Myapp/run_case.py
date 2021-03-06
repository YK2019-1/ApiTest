"""
=============================
@author:WYP
@email:1295920589@qq.com
@time:2020-12-23 20:23
=============================
"""
import unittest,time,re,json,requests
from Myapp.A_WQRFhtmlRunner import HTMLTestRunner

import sys,os,django
path = "../ApiTest"
sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE","ApiTest.settings")
django.setup()
from Myapp.models import *

class Test(unittest.TestCase):
    '_测试类_'
    @classmethod
    def setUpClass(cls):
        #print('收尾功能')
        try:
            for i in login_res_list:
                if i['project_id'] == cls.project_id:
                    login_res_list.remove(i)
                    break
        except:
            pass
        #print(cls.project_id)

    def demo(self, step):
        #print(step.api_url)
        # 提取所有请求数据
        api_method = step.api_method
        api_url = step.api_url
        api_host = step.api_host
        api_header = step.api_header
        api_body_method = step.api_body_method
        api_body = step.api_body
        get_path = step.get_path
        get_zz = step.get_zz
        assert_zz = step.assert_zz
        assert_qz = step.assert_qz
        assert_path = step.assert_path
        mock_res = step.mock_res
        if step.public_header != '':
            ts_project_headers = step.public_header.split(',')  # 获取公共请求头



        if mock_res not in ['',None,'None']:
            res = mock_res
        else:
            #检查是否需要进行替换占位符的
            rlist_url = re.findall(r"##(.+?)##",api_url)
            for i in rlist_url:
                api_url = api_url.replace("##"+i+"##",str(eval(i)))

            rlist_header = re.findall(r"##(.*?)##", api_header)
            for i in rlist_header:
                api_header = api_header.replace("##"+i+"##", repr(str(eval(i))))

            if api_body_method == 'none':
                pass
            elif api_body_method == 'form-data' or api_body_method == 'x-www-form-urlencoded':
                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", str(eval(i)))
            elif api_body_method == 'Json':
                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", repr(eval(i)))
            else:
                rlist_body = re.findall(r"##(.*?)##", api_body)
                for i in rlist_body:
                    api_body = api_body.replace("##" + i + "##", str(eval(i)))

            # 实际发送请求
            # 处理域名host
            if api_host[:4] == '全局域名':
                project_host_id = api_host.split('-')[1]
                api_host = DB_project_host.objects.filter(id=project_host_id)[0].host

            #处理header
            if api_header == "":
                api_header = "{}"
            try:
                header = json.loads(api_header)  # 处理header
            except:
                header = eval(api_header)
            #在这里遍历公共请求头，并把其加入到header的字典中
            if step.public_header != '':
                for i in ts_project_headers:
                    project_header = DB_project_header.objects.filter(id=i)[0]
                    header[project_header.key] = project_header.value

            #print(header)

            ## 输出请求数据
            print('【host】：', api_host)
            print('【url】：', api_url)
            print('【header】：', header)
            print('【method】：', api_method)
            print('【body_method】：', api_body_method)
            print('【body】：', api_body)

            # 拼接完整的url
            if api_host[-1] == '/' and api_url[0] == '/':   # 都有/
                url = api_host[:-1] + api_url
            elif api_host[-1] != '/' and api_url[0] != '/':  # 都没有/
                url = api_host + '/' + api_url
            else:  # 肯定有一个有/
                url = api_host + api_url

            #登录态代码
            api_login = step.api_login #获取登录开关
            if api_login == 'yes':
                project_id = DB_step.objects.filter(id=step.id)[0].project_id #先求出当前执行step所属的project_id
                global login_res_list #新建一个登录态列表
                try:
                    eval("login_res_list")
                except:
                    login_res_list = [] #判断是否存在，若不存在，则创建空的，一般只有平台重启后才会触发一次
                # 去login_res_list中查找是否已经存在
                for i in login_res_list:
                    if i['project_id'] == project_id:
                        #print('找到了')
                        login_res = i
                        break
                else:
                    #print('没有找到要创建')
                    from Myapp.views import project_login_send_for_other
                    #project_id = DB_case.objects.filter(id=DB_step.objects.filter(id=step.id)[0].Case_id)[0].project_id
                    login_res = project_login_send_for_other(project_id)
                    if type(login_res) == dict:
                        login_res['project_id'] = project_id
                        login_res_list.append(login_res)
                ## header插入
                print('【登录态】：',login_res)
                if type(login_res) == dict:
                    header.update(login_res)
            else:
                pass


            if api_body_method == 'none' or api_body_method == 'null':
                if type(login_res) == dict:
                    response = requests.request(api_method.upper(),url,headers=header,data={})
                else:
                    response = login_res.request(api_method.upper(),url,headers=header,data={})
            elif api_body_method == 'form-data':
                files = []
                payload = {}
                for i in eval(api_body):
                    payload[i[0]] = i[1]
                if type(login_res) == dict:
                    for i in eval(api_body):
                        payload[i[0]] = i[1]
                    response = requests.request(api_method.upper(), url, headers=header, data=payload, files=files)
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=payload, files=files)
            elif api_body_method == 'x-www-form-urlencoded':
                header['Content-Type'] = 'application/x-www-form-urlencoded'
                payload = {}
                if type(login_res) == dict:
                    for i in eval(api_body):
                        payload[i[0]] = i[1]
                    response = requests.request(api_method.upper(), url, headers=header, data=payload)
                else:
                    response = login_res.request(api_method.upper(), url, headers=header, data=payload)
            else: #这时肯定是raw的五个子选项
                if api_body_method == 'Text':
                    header['Content-Type'] = 'text/plain'
                if api_body_method == 'JavaScript':
                    header['Content-Type'] = 'text/plain'
                if api_body_method == 'Json':
                    header['Content-Type'] = 'application/json'
                if api_body_method == 'Html':
                    header['Content-Type'] = 'text/plain'
                if api_body_method == 'Xml':
                    header['Content-Type'] = 'text/plain'
                response = requests.request(api_method.upper(), url, headers=header, data=api_body.encode('utf-8'))
            response.encoding = "utf-8"
            res = response.text
            DB_host.objects.update_or_create(host=api_host)
        print('【返回体】：',res)

        # 对返回值res进行提取：
        ##路径法提取：
        if get_path != '': #说明有设置
            for i in get_path.split('\n'):
                key = i.split('=')[0].rstrip()
                path = i.split('=')[1].rstrip()

                py_path = ""
                for j in path.split('/'):
                    if j !='':
                        if j[0] != '[':
                            py_path += '["%s"]'%j
                        else:
                            py_path +=j
                value = eval("%s%s" % (json.loads(res),py_path))
                print("提取值", key, value)
                exec('global %s\n%s = value ' % (key, key))
        ## 正则法提取：
        if get_zz != '': #说明有设置
            for i in get_zz.split('\n'):
                key = i.split('=')[0].rstrip()
                zz = i.split('=')[1].rstrip()
                value = re.findall(zz,res)[0]
                exec('global %s\n%s = %s '%(key,key,value))

        #对返回值res进行断言：
        ## 断言-路径法：
        if assert_path != '': #说明有设置
            for i in assert_path.split('\n'):
                path = i.split('=')[0].rstrip()
                want = eval(i.split('=')[1].lstrip())
                py_path = ""
                for j in path.split('/'):
                    if j != '':
                        if j[0] != '[':
                            py_path += '["%s"]' % j
                        else:
                            py_path += j
                value = eval("%s%s" % (json.loads(res),py_path))
                self.assertEqual(want,value,'值不等')
        ## 断言-正则
        if assert_zz != '': #说明有设置
            for i in assert_zz.split('/n'):
                zz = i.split('=')[0].rstrip()
                want = i.split('=')[1].lstrip()
                value = re.findall(zz,res)[0]
                self.assertEqual(want,value,'值不等')
        ## 断言-全值
        if assert_qz != '':
            for i in assert_qz.split('\n'):
                if i not in res:
                    raise AssertionError('字符串不存在：%s'%i)


def make_defself(step):
    def tool(self):
        Test.demo(self,step)
    setattr(tool,"__doc__",u"%s"%step.name)
    return tool


def make_def(steps,project_id):
    Test.project_id = project_id
    for fun in dir(Test):
        if 'test_' in fun:
            delattr(Test,fun)

    for i in range(len(steps)):
        setattr(Test,'test_'+str(str(steps[i].Case_id)+str(steps[i].index).zfill(3)).zfill(5),make_defself(steps[i]))

def run(Case_id,Case_name,steps):
    project_id=DB_case.objects.filter(id = Case_id)[0].project_id
    make_def(steps,project_id)
    suit = unittest.makeSuite(Test)
    filename = 'Myapp/templates/Reports/%s.html'%Case_id
    fp = open(filename,'wb')
    runner = HTMLTestRunner(fp,title='接口测试平台测试报告:%s'%Case_name,description='%s的测试报告'%Case_name)
    runner.run(suit)

def runall(project_id,project_name,steps):
    make_def(steps,project_id)
    suit = unittest.makeSuite(Test)
    project_report_name = project_id+'all'
    filename = 'Myapp/templates/Reports/%s.html' % project_report_name
    fp = open(filename, 'wb')
    runner = HTMLTestRunner(fp, title='接口测试平台测试报告:%s' % project_name, description='%s项目的接口测试报告' % project_name)
    runner.run(suit)


if __name__ == '__main__':
    unittest.main()