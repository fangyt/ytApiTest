#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiData.py

import os, yaml, operator, jsonpath, requests, json, warnings, copy, time
from urllib.parse import urlparse
from  ytApiTest import apiRequest

class YAML_CONFIG_KEY():
    OBJECT_HOST = 'OBJECT_HOST'
    INTERFACE_URL = 'url'
    INTERFACE_REQUEST_DATA = 'req_data'
    INTERFACE_ASSERT_DATA = 'ast_data'
    INTERFACE_CASE_DES = 'des'
    DING_TALK_URL = 'DING_TALK_URL'
    INTERFACE_JSON_PATH = 'json_expr'
    INTERFACE_ASSERT_DATA_SETUP = 'setup'
    INTERFACE_REQUEST_DATA_TEARDOWN = 'tearDown'
    INTERFACE_REQUEST_HEADERS = 'headers'
    INTERFACE_CACHE_UPDATE_DATA = 'CACHE_UPDATE_DATA'
    INTERFACE_CACHE_METHOD = 'method'

class FindFile():

    def get_yaml_path(self):
        '''
        查找数据文件
        :return:
        '''
        for dirpath, dirnames, filenames in os.walk('./'):

            if len(filenames):

                for index, file_name in enumerate(filenames):

                    if bool(os.path.splitext(file_name).count('.yaml')):
                        return os.path.join(dirpath, file_name)

class YamlSingleton():
    _obj = None
    _init_flag = True
    yaml_data = None
    res_data = dict()

    def __new__(cls, *args, **kwargs):

        if YamlSingleton._obj == None:
            YamlSingleton._obj = object.__new__(cls)

        return cls._obj

    def __init__(self):

        if YamlSingleton._init_flag:
            YamlSingleton._init_flag = False
            YamlSingleton.yaml_data = self.get_yaml_data()
            YamlSingleton.res_data = self.res_data

    def get_yaml_data(self):
        '''
        获取yaml测试数据
        :return:
        '''

        yaml_file_path = FindFile().get_yaml_path()

        assert yaml_file_path, AssertionError('未找到yaml数据文件')
        temp_dic = {}
        with open(yaml_file_path, encoding='UTF-8') as f:
            all_dic = yaml.load_all(f, Loader=yaml.FullLoader)

            for dic in all_dic:
                temp_dic.update(dic)

        return temp_dic

    def update_response_data(self, response: dict):
        '''
		更新接口返回数据
		'''
        self.res_data.update(response)

class ParsingData():

    def __init__(self):

        self.yaml_data = YamlSingleton().yaml_data
        self.response_data = YamlSingleton().res_data
        self.yaml_key = YAML_CONFIG_KEY
        self.req = apiRequest.InterFaceReq()

    def get_interface_data(self, interface_name, assert_name, yaml_config_key=None):

        '''
        获取接口数据
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :param yaml_config_key: yaml配置key
        :return:
        '''

        if self.yaml_data.__contains__(interface_name) and \
                self.yaml_data[interface_name].__contains__(assert_name):

            if self.yaml_data[interface_name][assert_name].__contains__(yaml_config_key):
                return self.yaml_data[interface_name][assert_name][yaml_config_key]
            elif operator.eq(yaml_config_key,None):return self.yaml_data[interface_name][assert_name]


    def get_object_host(self):
        '''
        获取项目host ，默认返回第一个HOST
        :param host_key:
        :return:
        '''
        return self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST]

    def get_interface_url(self, interface_name: str, host_key: str = None):
        '''
        获取接口URL路径
        :param interface_name: 接口名称
        :param host_key: 项目host_key
        :return:
        '''
        if self.yaml_data.__contains__(interface_name):

            url = self.yaml_data[interface_name][YAML_CONFIG_KEY.INTERFACE_URL]

            if url.find('http') != -1: return url

        return self.get_headers_key(host_key) + url

    def get_headers_key(self,host_key):

        return host_key if operator.ne(host_key,None) else iter(self.get_object_host().values()).__next__()

    def get_interface_request_data(self, interface_name, assert_name):
        '''
        获取接口请求数据
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :return:
        '''

        old_data = copy.deepcopy(self.yaml_data)

        request_data = old_data[interface_name][assert_name][YAML_CONFIG_KEY.INTERFACE_REQUEST_DATA]

        if request_data == None:
            return request_data

        self.recursive_replace_json_expr(replace_value=request_data)

        if operator.ne(self.get_interface_case_req_method(interface_name,assert_name),'post') :

            request_data = json.dumps(request_data)

        return request_data

    def get_interface_assert_value(self, interface_name, assert_name):

        '''
        获取接口断言数据
        :param interface_name: 接口名称
        :param assert_name:  接口对应断言名称
        :return:
        '''
        assert_value = self.get_interface_data(interface_name=interface_name,
                                               assert_name=assert_name,
                                               yaml_config_key=YAML_CONFIG_KEY.INTERFACE_ASSERT_DATA)
        if isinstance(assert_value, str):
            if assert_value.find('$') != -1:
                assert_value = self.find_json_expr_value(assert_value)
        else:
            self.recursive_replace_json_expr(assert_value)

        return assert_value

    def get_interface_setup_list(self, interface_name, assert_name):
        '''
		获取前置操作接口数据
		:param interface_name: 接口名称
		:param assert_name: 接口关联断言名称
		:return:
		'''

        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=self.yaml_key.INTERFACE_ASSERT_DATA_SETUP)

    def get_interface_tear_down_list(self, interface_name, assert_name):
        '''
		获取用例后置操作
		:param interface_name: 接口名称
		:param assert_name: 接口关联断言名称
		:return:
		'''
        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=self.yaml_key.INTERFACE_REQUEST_DATA_TEARDOWN)

    def get_interface_des(self, interface_name, assert_name):

        '''
        获取用例说明
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :return:
        '''

        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=YAML_CONFIG_KEY.INTERFACE_CASE_DES)

    def get_interface_json_path(self, interface_name, assert_name):

        '''
        获取用例jsonpath
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名
        :return:
        '''

        json_expr = self.get_interface_data(interface_name=interface_name,
                                            assert_name=assert_name,
                                            yaml_config_key=YAML_CONFIG_KEY.INTERFACE_JSON_PATH)
        return json_expr

    def get_interface_case_req_method(self,interface_name, assert_name):

        default_method = self.yaml_data[interface_name][assert_name][YAML_CONFIG_KEY.INTERFACE_CACHE_METHOD]
        return default_method if operator.ne(default_method,None) else 'post'

    def get_interface_url_interface_name(self, assert_name: str):
        '''
		通过hostkey获取接口名称
		:param host_key:
		:return:
		'''
        for interface_name, value in self.yaml_data.items():
            if value == None: continue
            if value.__contains__(assert_name) and operator.ne(interface_name, YAML_CONFIG_KEY.OBJECT_HOST):
                return interface_name

    def get_interface_response_data(self):
        '''
		获取接口返回值
		:return:
		'''
        return YamlSingleton().res_data

    def get_send_error_info_url(self):
        '''
        获取项目配置钉钉机器人URL
        :return:
        '''
        return self.yaml_data[YAML_CONFIG_KEY.DING_TALK_URL]

    def get_interface_request_header(self, interface_name, assert_name):
        '''
		获取接口自定义请求头
		:return:
		'''
        headers = self.get_interface_data(interface_name=interface_name,
                                         assert_name=assert_name,
                                         yaml_config_key=YAML_CONFIG_KEY.INTERFACE_REQUEST_HEADERS)

        return headers

    def get_interface_req_headers(self,interface_name,assert_name,**kwargs):

        headers_key = self.get_headers_key(kwargs.get('host_key'))
        if self.response_data.__contains__(headers_key): return self.response_data.get(headers_key)

        setup_list = self.get_interface_setup_list(interface_name=interface_name, assert_name=assert_name)
        default_headers = {'Content-Type': 'application/json'}
        if operator.ne(setup_list,None):

            for dic in setup_list:
                interface_name_ = dic.get('interface_name')
                assert_name_ = dict.get('assert_name')
                url = self.get_interface_url(interface_name_)
                data = self.get_interface_request_data(interface_name_,assert_name_)
                method = kwargs.get('method') if operator.ne(kwargs.get('method'),None) else self.get_interface_case_req_method(interface_name=interface_name, assert_name=assert_name_)
                params = json.loads(data) if operator.ne(method,'get') else None
                headers = self.get_interface_request_header(interface_name_,assert_name_)
                headers = headers if operator.ne(headers,None) else default_headers
                self.req.req(method=method,url=url,data=data,params=params,headers=headers)


        headers_ = self.get_interface_request_header(interface_name=interface_name,assert_name=assert_name)
        headers = headers_ if operator.ne(headers_, None) else default_headers
        interface_name = self.get_interface_url_interface_name(interface_name)
        url = self.get_interface_url(interface_name=interface_name,host_key=assert_name)
        data = self.get_interface_request_data(interface_name=interface_name,assert_name=assert_name)
        method = kwargs.get('method') if operator.ne(kwargs.get('method'),None) else self.get_interface_case_req_method(interface_name=interface_name,assert_name=assert_name)

        respons = self.req.req(method=method,headers=headers,data=data,url=url)

        error_info = "登录信息缓存失败url={url}\n\nreq_data={req_data}\n\nrespons{respons}".format(url=respons.url,
                                                                                           req_data=respons.request.body,
                                                                                           respons=respons.text)
        assert respons.json()['rtn'] == 0,error_info
        if respons.request._cookies:
            headers.update(respons.request.headers)
            return headers
        rep_json = respons.json()['data']

        if rep_json.__contains__('userinfo'):

            headers.update({'Content-Type': 'application/json',
                                          'Cookie': 'userId={userId}; '
                                                    'sessionId={sessionId};weId=supermonkey-weapp'.format(
                                              userId=rep_json['userinfo']['userId'],
                                              sessionId=rep_json['sessionId']),
                                          })

        elif rep_json.__contains__('token'):

            headers.update({'authorization': rep_json['token']})

        self.save_response_data({assert_name:headers})
        return headers

    def get_interface_assert_name(self, assert_value: dict):
        '''
        获取接口断言key
        :param assert_value: 断言值
        :return:
        '''

    def update_interface_json_path(self, interface_name, assert_name, new_value: dict):
        '''
        修改json_path 路径
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :param new_value: 修改值，以字典传入
        :return:
        '''

        old_json_path = self.get_interface_json_path(interface_name=interface_name,
                                                     assert_name=assert_name)
        if old_json_path == None: return
        self.yaml_data[interface_name][assert_name][YAML_CONFIG_KEY.INTERFACE_JSON_PATH] = old_json_path.format(
            **new_value)

    def update_interface_request_data(self, interface_name, assert_name, new_request_data: dict):
        '''
        修改接口请求参数
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :param new_request_data: 新接口请求值
        '''
        req_data = json.loads(self.get_interface_request_data(interface_name=interface_name, assert_name=assert_name))
        req_data.update(new_request_data)
        self.yaml_data[interface_name][assert_name][YAML_CONFIG_KEY.INTERFACE_REQUEST_DATA].update(req_data)

    def updata_interface_assert_data(self, interface_name, assert_name, assert_data: dict):
        '''
		更新断言数据
		:param interface_name: 接口名称
		:param assert_name: 用例名称
		:param assert_data: 数据
		:return:
		'''
        data = self.get_interface_assert_value(interface_name=interface_name,
                                               assert_name=assert_name)
        data.update(assert_data)

        self.yaml_data[interface_name][assert_name][YAML_CONFIG_KEY.INTERFACE_ASSERT_DATA] = data

    def save_response_data(self, response: requests.Response):
        '''
        保存接口返回值
        :param dic:
        :return:
        '''

        if isinstance(response, dict):

            json_value = response

        else:

            name_list = urlparse(response.request.url).path.split('/')
            name_list = name_list[len(name_list) - 2:]
            name_list[-1] = name_list[-1].replace('.', '-')
            json_key = '-'.join(name_list)
            json_value = {json_key: self.parse_response_data(response_data=response)}
        YamlSingleton().update_response_data(response=json_value)

    def parse_response_data(self, response_data: requests.Response):
        '''
        解析接口返回对象为json
        :param response_data:
        :return:
        '''
        if isinstance(response_data, requests.Response):
            return response_data.json()

        elif isinstance(response_data, dict):

            return response_data
        else:
            return False

    def find_json_expr_value(self, json_expr):
        '''
        查找json_expr 返回值
        :param json_expr:
        :return:
        '''
        index = None
        temp_json_expr = json_expr
        if json_expr.find('/') != -1:
            index = int(json_expr.split('/')[-1])
            json_expr = json_expr.split('/')[0]

        if jsonpath.jsonpath(self.get_interface_response_data(), json_expr):

            json_value = jsonpath.jsonpath(self.response_data, json_expr)

        elif jsonpath.jsonpath(self.yaml_data, json_expr):
            json_value = jsonpath.jsonpath(self.yaml_data, json_expr)

        else:
            warnings.warn('未查找到json_expr值{json_expr}'.format(json_expr=temp_json_expr))
            return temp_json_expr
        if temp_json_expr.find('/') != -1:
            return json_value[index]

        return json_value

    def recursive_replace_json_expr(self, replace_value, interface_name=None, assert_name=None):
        '''
        递归替换请求数据内json_expr
        :param replace_value:
        :return:
        '''
        if isinstance(replace_value, dict):

            for key, value in replace_value.items():
                if type(value) != dict or type(value) != list:

                    if isinstance(value, str) and value.find('$') != -1:
                        replace_value[key] = self.find_json_expr_value(value)

                self.recursive_replace_json_expr(value, interface_name=interface_name, assert_name=assert_name)

        elif isinstance(replace_value, list):

            for index, list_value in enumerate(replace_value):
                if type(list_value) != dict or type(list_value) != list:
                    if isinstance(list_value, str) and list_value.find('$') != -1:
                        replace_value[index] = self.find_json_expr_value(list_value)

                self.recursive_replace_json_expr(list_value, interface_name=interface_name, assert_name=assert_name)

    def combination_req_data(self, interface_name=None, assert_name=None, host_key=None,method=None):

        url = self.get_interface_url(interface_name=interface_name,
                                     host_key=host_key)

        data = self.get_interface_request_data(interface_name=interface_name,
                                               assert_name=assert_name)
        headers = self.get_interface_req_headers(interface_name=interface_name,
                                                 assert_name=assert_name,
                                                 host_key=host_key)
        des = self.get_interface_des(interface_name=interface_name,assert_name=assert_name)
        setup = self.get_interface_setup_list(interface_name=interface_name,assert_name=assert_name)
        req_method = self.get_interface_case_req_method(interface_name,assert_name)
        req_method = req_method if operator.ne(method,None) else method
        json_expr = self.get_interface_json_path(interface_name,assert_name)
        return {YAML_CONFIG_KEY.INTERFACE_URL: url,
                YAML_CONFIG_KEY.INTERFACE_ASSERT_DATA: data,
                YAML_CONFIG_KEY.INTERFACE_REQUEST_HEADERS: headers,
                YAML_CONFIG_KEY.INTERFACE_CASE_DES:des,
                YAML_CONFIG_KEY.INTERFACE_ASSERT_DATA_SETUP:setup,
                YAML_CONFIG_KEY.INTERFACE_CACHE_METHOD:req_method,
                YAML_CONFIG_KEY.INTERFACE_JSON_PATH:json_expr}


if __name__ == '__main__':
    print({"2":None})
