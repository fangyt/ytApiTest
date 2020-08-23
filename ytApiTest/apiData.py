#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiData.py

import os, yaml, operator, jsonpath, requests, json, warnings, copy, time,types
from urllib.parse import urlparse
from ytApiTest import apiRequest, yamlKey


class FindFile():

    def __init__(self):

        self.file_name = '.yaml'

    def get_yaml_path(self, dirname=None, filename=None):
        '''
        查找数据文件
        :return:
        '''
        path_list = []
        for dirpath, dirnames, filenames in os.walk('./'):

            if operator.ne(dirname, None):
                if len([name for name in filenames if os.path.splitext(name)[-1] == self.file_name]) and dirpath.find(
                        dirname) != -1:
                    path_list.extend(
                        [os.path.join(dirpath, name) for name in filenames if
                         os.path.splitext(name)[-1] == self.file_name])

            elif operator.ne(filename, None):
                if len([file_name for file_name in filenames if os.path.splitext(file_name)[0] == filename]):
                    return [os.path.join(dirpath, file_name) for file_name in filenames if
                            os.path.splitext(file_name)[0] == filename]
            else:
                path_list.extend([os.path.join(dirpath, file_name_) for file_name_ in filenames if
                                  os.path.splitext(file_name_)[-1] == self.file_name])

        return path_list


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
        yaml_data = {}
        yaml_file_path = FindFile().get_yaml_path()

        assert yaml_file_path, AssertionError('未找到yaml数据文件')

        for path in yaml_file_path:
            with open(path, encoding='UTF-8') as f:
                [yaml_data.update({'-'.join(
                    path.split('/')[-2:] if len(path.split('/')) > 2 else path.split('/')[-1:]).replace(
                    FindFile().file_name, ''): dic}) for dic in yaml.load_all(f, Loader=yaml.FullLoader)]
                [yaml_data.update({yaml_dic_key.split('-')[-1]: yaml_data[yaml_dic_key]}) for yaml_dic_key in
                 yaml_data.copy().keys()]
        return yaml_data

    def update_response_data(self, response: dict):
        '''
		更新接口返回数据
		'''
        self.res_data.update(response)


class YamlData():

    def __init__(self):
        self.yaml_data = YamlSingleton().yaml_data

    def yaml_file_data(self, file_name=None):
        '''
        param file_name: yaml文件名，存在多个yaml文件时，如果该值不传入以ASCII排序 第一个文件数据
        :return:
        '''
        if file_name != None:
            return self.yaml_data.get(file_name)
        yaml_keys = list(self.yaml_data.keys())
        yaml_keys.sort()
        yaml_key = yaml_keys[0]
        return self.yaml_data.get(yaml_key)

    def get_case_data(self, interface_name, assert_name, file_name=None):
        '''
        获取用例数据
        :param interface_name: 接口名称
        :param assert_name:  用例名
        :param file_name: yaml文件名，存在多个yaml文件时，如果该值不传入以ASCII排序 第一个文件数据
        :return:
        '''
        json_expr = '$.' + file_name + '.' + interface_name + '.' + assert_name + '/0'

        if file_name == None:
            json_expr = '$.' + interface_name + '.' + assert_name + '/0'

        return self.find_json_expr_value(file_name, json_expr)
    def replace_case_data(self,interface_name, assert_name, file_name=None):
        '''
        查找json_expr 并将查找到的值替换表达式
        :param interface_name: 接口名
        :param assert_name: 用例名
        :param file_name: yaml文件名，存在多个yaml文件时，如果该值不传入以ASCII排序 第一个文件数据
        :return:
        '''

        old_case_data = self.get_case_data(interface_name=interface_name,assert_name=assert_name,file_name=file_name)
        new_case_data = copy.deepcopy(old_case_data)

        for case_value in dict.items():
            pass

    def recursive_replace_json_expr(self,replace_obj,file_name=None):

        if isinstance(replace_obj,dict):

            for key,vlaue in replace_obj.items():

                if type(vlaue) != dict and type(vlaue) and list and isinstance(vlaue,str) and vlaue.find('$') != -1:
                    replace_obj[key] = self.find_json_expr_value(self.yaml_file_data(file_name=file_name), vlaue)

                self.recursive_replace_json_expr(replace_obj=vlaue,file_name=file_name)
        elif isinstance(replace_obj,list):

            for index ,list_value in enumerate(replace_obj):
                if type(list_value) != dict and type(list_value) and list and isinstance(list_value, str) and list_value.find('$') != -1:

                    replace_obj[index] = self.find_json_expr_value(self.yaml_file_data(file_name=file_name), list_value)

    def find_json_expr_value(self, file_name, expr):
        json_path_value = jsonpath.jsonpath(self.yaml_file_data(file_name), expr.split('/')[0])
        if json_path_value:
            if self.interception_json_expr_index(expr):
                return json_path_value[self.interception_json_expr_index(expr)]
            return json_path_value

        info = '无法查找到该接口数据' + json_path_value
        assert json_path_value, info

    def interception_json_expr_index(self, json_expr):

        '''
        截取json_expr 下标
        :param json_expr:
        :return:
        '''
        if json_expr.find('/') == -1: return False
        return int(json_expr.split('/')[-1])


class ParsingData():

    def __init__(self):

        self.yaml_data = YamlSingleton().yaml_data
        self.response_data = YamlSingleton().res_data
        self.yaml_key = yamlKey.self.YAML_CONFIG_KEY
        self.req = apiRequest.InterFaceReq()

    def get_case_data(self, interface_name, assert_name, file_name=None):

        self.yaml_key.sort()

        if file_name == None:

            if iter(self.yaml_key).__next__().values().get(interface_name) != None:
                return iter(self.yaml_key).__next__().values().get(interface_name).get(assert_name)

        if len([yaml_data for yaml_data in self.yaml_key if yaml_data.__contains__(file_name)]):
            return iter([yaml_data for yaml_data in self.yaml_key if
                         yaml_data.__contains__(file_name)]).__next__().values().get(interface_name).get(assert_name)

    def get_interface_data(self, interface_name, assert_name, yaml_key=None):

        '''
        获取接口数据
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :param self.yaml_key: yaml配置key
        :return:
        '''

        if self.yaml_data.__contains__(interface_name) and \
                self.yaml_data[interface_name].__contains__(assert_name):

            if self.yaml_data[interface_name][assert_name].__contains__(yaml_key):
                return self.yaml_data[interface_name][assert_name][yaml_key]
            elif operator.eq(yaml_key, None):
                return self.yaml_data[interface_name][assert_name]

    def get_object_host(self):
        '''
        获取项目host ，默认返回第一个HOST
        :param host_key:
        :return:
        '''
        return self.yaml_data[self.yaml_key.OBJECT_HOST]

    def get_interface_url(self, interface_name: str, host_key: str = None):
        '''
        获取接口URL路径
        :param interface_name: 接口名称
        :param host_key: 项目host_key
        :return:
        '''
        if self.yaml_data.__contains__(interface_name):

            url = self.yaml_data[interface_name][self.yaml_key.INTERFACE_URL]

            if url.find('http') != -1: return url

        return self.get_headers_key(host_key) + url

    def get_headers_key(self, host_key):

        return host_key if operator.ne(host_key, None) else iter(self.get_object_host().values()).__next__()

    def get_interface_request_data(self, interface_name, assert_name):
        '''
        获取接口请求数据
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :return:
        '''

        old_data = copy.deepcopy(self.yaml_data)

        request_data = old_data[interface_name][assert_name][self.yaml_key.INTERFACE_REQUEST_DATA]

        if request_data == None:
            return request_data

        self.recursive_replace_json_expr(replace_value=request_data)

        if operator.ne(self.get_interface_case_req_method(interface_name, assert_name), 'post'):
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
                                               yaml_key=self.yaml_key.INTERFACE_ASSERT_DATA)
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
                                       yaml_key=self.yaml_key.INTERFACE_ASSERT_DATA_SETUP)

    def get_interface_tear_down_list(self, interface_name, assert_name):
        '''
		获取用例后置操作
		:param interface_name: 接口名称
		:param assert_name: 接口关联断言名称
		:return:
		'''
        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_key=self.yaml_key.INTERFACE_REQUEST_DATA_TEARDOWN)

    def get_interface_des(self, interface_name, assert_name):

        '''
        获取用例说明
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :return:
        '''

        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_key=self.yaml_key.INTERFACE_CASE_DES)

    def get_interface_json_path(self, interface_name, assert_name):

        '''
        获取用例jsonpath
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名
        :return:
        '''

        json_expr = self.get_interface_data(interface_name=interface_name,
                                            assert_name=assert_name,
                                            yaml_key=self.yaml_key.INTERFACE_JSON_PATH)
        return json_expr

    def get_interface_case_req_method(self, interface_name, assert_name):

        default_method = self.yaml_data[interface_name][assert_name][self.yaml_key.INTERFACE_CACHE_METHOD]
        return default_method if operator.ne(default_method, None) else 'post'

    def get_interface_url_interface_name(self, assert_name: str):
        '''
		通过hostkey获取接口名称
		:param host_key:
		:return:
		'''
        for interface_name, value in self.yaml_data.items():
            if value == None: continue
            if value.__contains__(assert_name) and operator.ne(interface_name, self.yaml_key.OBJECT_HOST):
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
        return self.yaml_data[self.yaml_key.DING_TALK_URL]

    def get_interface_request_header(self, interface_name, assert_name):
        '''
		获取接口自定义请求头
		:return:
		'''
        headers = self.get_interface_data(interface_name=interface_name,
                                          assert_name=assert_name,
                                          yaml_key=self.yaml_key.INTERFACE_REQUEST_HEADERS)

        return headers

    def get_interface_req_headers(self, interface_name, assert_name, **kwargs):

        headers_key = self.get_headers_key(kwargs.get('host_key'))
        if self.response_data.__contains__(headers_key): return self.response_data.get(headers_key)

        setup_list = self.get_interface_setup_list(interface_name=interface_name, assert_name=assert_name)
        default_headers = {'Content-Type': 'application/json'}
        if operator.ne(setup_list, None):

            for dic in setup_list:
                interface_name_ = dic.get('interface_name')
                assert_name_ = dict.get('assert_name')
                url = self.get_interface_url(interface_name_)
                data = self.get_interface_request_data(interface_name_, assert_name_)
                method = kwargs.get('method') if operator.ne(kwargs.get('method'),
                                                             None) else self.get_interface_case_req_method(
                    interface_name=interface_name, assert_name=assert_name_)
                params = json.loads(data) if operator.ne(method, 'get') else None
                headers = self.get_interface_request_header(interface_name_, assert_name_)
                headers = headers if operator.ne(headers, None) else default_headers
                self.req.req(method=method, url=url, data=data, params=params, headers=headers)

        headers_ = self.get_interface_request_header(interface_name=interface_name, assert_name=assert_name)
        headers = headers_ if operator.ne(headers_, None) else default_headers
        interface_name = self.get_interface_url_interface_name(interface_name)
        url = self.get_interface_url(interface_name=interface_name, host_key=assert_name)
        data = self.get_interface_request_data(interface_name=interface_name, assert_name=assert_name)
        method = kwargs.get('method') if operator.ne(kwargs.get('method'),
                                                     None) else self.get_interface_case_req_method(
            interface_name=interface_name, assert_name=assert_name)

        respons = self.req.req(method=method, headers=headers, data=data, url=url)

        error_info = "登录信息缓存失败url={url}\n\nreq_data={req_data}\n\nrespons{respons}".format(url=respons.url,
                                                                                           req_data=respons.request.body,
                                                                                           respons=respons.text)
        assert respons.json()['rtn'] == 0, error_info
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

        self.save_response_data({assert_name: headers})
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
        self.yaml_data[interface_name][assert_name][self.yaml_key.INTERFACE_JSON_PATH] = old_json_path.format(
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
        self.yaml_data[interface_name][assert_name][self.yaml_key.INTERFACE_REQUEST_DATA].update(req_data)

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

        self.yaml_data[interface_name][assert_name][self.yaml_key.INTERFACE_ASSERT_DATA] = data

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

    def combination_req_data(self, interface_name=None, assert_name=None, host_key=None, method=None):

        setup = self.get_interface_setup_list(interface_name=interface_name, assert_name=assert_name)

        temp_case_list = []

        for case_dic in setup:
            case_data = self.combination_req_data(interface_name=case_dic.get('interface_name'),
                                                  assert_name=case_dic.get('assert_name'),
                                                  host_key=case_dic.get('host_key'),
                                                  method=case_dic.get('method'))

            temp_case_list.append(case_data)

        return {self.yaml_key.INTERFACE_ASSERT_DATA_SETUP: temp_case_list}.update(
            self.get_interface_case_req_method(interface_name=interface_name,
                                               assert_name=assert_name,
                                               host_key=host_key,
                                               method=method))

    def combination_case_data(self, interface_name=None, assert_name=None, host_key=None, method=None):

        url = self.get_interface_url(interface_name=interface_name,
                                     host_key=host_key)

        data = self.get_interface_request_data(interface_name=interface_name,
                                               assert_name=assert_name)
        headers = self.get_interface_req_headers(interface_name=interface_name,
                                                 assert_name=assert_name,
                                                 host_key=host_key)
        des = self.get_interface_des(interface_name=interface_name, assert_name=assert_name)
        req_method = self.get_interface_case_req_method(interface_name, assert_name)
        req_method = req_method if operator.ne(method, None) else method
        json_expr = self.get_interface_json_path(interface_name, assert_name)

        return {self.yaml_key.INTERFACE_URL: url,
                self.yaml_key.INTERFACE_ASSERT_DATA: data,
                self.yaml_key.INTERFACE_REQUEST_HEADERS: headers,
                self.yaml_key.INTERFACE_CASE_DES: des,
                self.yaml_key.INTERFACE_CACHE_METHOD: req_method,
                self.yaml_key.INTERFACE_JSON_PATH: json_expr}

    def req_case_data(self, case_dic: dict):

        if len(case_dic.get(self.yaml_key.INTERFACE_ASSERT_DATA_SETUP)) != 0:
            for case_dic_data in case_dic.get(self.yaml_key.INTERFACE_ASSERT_DATA_SETUP):
                self.req.req(case_dic_data)

        return self.req.req(case_dic)


if __name__ == '__main__':
    t = ['$12345']

    if isinstance(t,str) and t.find('$') != -1 and type(t) != dict and type(t) != list:
        print('----')
