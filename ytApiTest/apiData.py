#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiData.py

import os, yaml, operator, jsonpath, requests, json, warnings, copy, time
from urllib.parse import urlparse


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

    def get_interface_data(self, interface_name, assert_name, yaml_config_key):

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

    def get_object_host(self, host_key: str = None):
        '''
        获取项目host ，默认返回第一个HOST
        :param host_key:
        :return:
        '''
        if operator.eq(host_key, None):

            return iter(self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST].values()).__next__()

        else:

            if self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST].__contains__(host_key):
                return self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST][host_key]

    def get_interface_url(self, interface_name: str, host_key: str = None):
        '''
        获取接口URL路径
        :param interface_name: 接口名称
        :param host_key: 项目host_key
        :return:
        '''
        if self.yaml_data.__contains__(interface_name):

            url = self.yaml_data[interface_name][YAML_CONFIG_KEY.INTERFACE_URL]

            if url.find('http') != -1:

                return url

            else:

                return self.get_object_host(host_key=host_key) + url

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

    def get_interface_url_host_key(self, url: str):

        '''
		获取URL对应HOST key值
		:param url: url
		:return:
		'''
        object_host_dict = self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST]
        url_netloc = urlparse(url).netloc
        for key, value in object_host_dict.items():
            if operator.eq(urlparse(value).netloc, url_netloc):
                return key

    def get_interface_url_interface_name(self, host_key: str):
        '''
		通过hostkey获取接口名称
		:param host_key:
		:return:
		'''
        for interface_name, value in self.yaml_data.items():
            if value == None: continue
            if value.__contains__(host_key) and operator.ne(interface_name, YAML_CONFIG_KEY.OBJECT_HOST):
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
        header = self.get_interface_data(interface_name=interface_name,
                                         assert_name=assert_name,
                                         yaml_config_key=YAML_CONFIG_KEY.INTERFACE_REQUEST_HEADERS)

        if operator.eq(header, None):
            header = {'Content-Type': 'application/json'}

        return header

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
            warnings.warn('未查找到json_expr值{json_expr}'.format(json_expr=json_expr))
            return json_expr
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
                        replace_value[key] = self.multilayer_json_expr(value)

                self.recursive_replace_json_expr(value, interface_name=interface_name, assert_name=assert_name)

        elif isinstance(replace_value, list):

            for index, list_value in enumerate(replace_value):
                if type(list_value) != dict or type(list_value) != list:
                    if isinstance(list_value, str) and list_value.find('$') != -1:
                        replace_value[index] = self.multilayer_json_expr(list_value)

                self.recursive_replace_json_expr(list_value, interface_name=interface_name, assert_name=assert_name)

    def multilayer_json_expr(self, json_expr):
        '''
		多层json_expr
		:param json_expr: 多层表达式
		:return:
		'''
        if json_expr.find('{') == -1:
            return self.find_json_expr_value(json_expr)

        return self.find_json_expr_value(self.parse_multilayer_json_expr(json_expr))

    def parse_multilayer_json_expr(self, json_expr):
        '''
		解析多层为一层并返回
		:param json_expr:
		:return:
		'''
        if json_expr == None or json_expr.find('{') == -1:
            return json_expr
        start_index = json_expr.find('{')
        end_index = json_expr.find('}') + 1
        new_json_expr = self.find_json_expr_value(json_expr[start_index:end_index])
        return new_json_expr

    def save_interface_update_cache_data(self, interface_name, assert_name, update_value):

        cache_data = self.yaml_data[YAML_CONFIG_KEY.INTERFACE_CACHE_UPDATE_DATA]

        if cache_data == None:
            cache_data = {}

        cache_data.update({interface_name: {assert_name: update_value}})

    def get_interface_update_cache_data(self, interface_name, assert_name):
        '''
        获取接口更新缓存数据
        '''

        return self.yaml_data[YAML_CONFIG_KEY.INTERFACE_CACHE_UPDATE_DATA]

    def joine_timestamp(self, value, interface_name=None, assert_name=None):

        if type(value) != str:
            return value
        if value.find == -1:
            return value

        timestamp = int(time.time()) * 1000
        new_value = value.format(timestamp=timestamp)
        self.save_interface_update_cache_data(interface_name=interface_name,
                                              assert_name=assert_name,
                                              update_value=new_value)
        return new_value

    def replace_assert_json_expr(self, replace_value, replace_dic: dict):
        '''
        替换断言数据json_path
        :param replace_dic:
        :return:
        '''

        if isinstance(replace_value, dict):
            for key, dic_value in replace_value.items():

                if (type(dic_value) != dict and type(dic_value) != list) and isinstance(dic_value, str):

                    if dic_value.find('{') != -1:
                        try:
                            replace_value[key] = dic_value.format_map(replace_dic)
                        except KeyError:
                            warnings.warn('json_expr替换失败', dic_value)

                self.replace_assert_json_expr(replace_value=dic_value, replace_dic=replace_dic)

        elif isinstance(replace_value, list):

            for index, list_value in enumerate(replace_value):

                if (type(list_value) != dict and type(list_value) != list) and isinstance(list_value, str):
                    if list_value.find('{') != -1:
                        try:
                            list_value[index] = list_value.format_map(replace_dic)
                        except KeyError:
                            warnings.warn('json_expr替换失败', list_value)

                self.replace_assert_json_expr(replace_value=list_value, replace_dic=replace_dic)

if __name__ == '__main__':
    pass
