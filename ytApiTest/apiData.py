#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiData.py

import ytApiTest
import os,yaml,operator,jsonpath,requests
from urllib.parse import urlparse
class YAML_CONFIG_KEY():

    OBJECT_HOST = 'OBJECT_HOST'
    INTERFACE_URL = 'url'
    INTERFACE_REQUEST_DATA = 'req_data'
    INTERFACE_ASSERT_DATA = 'ast_data'
    INTERFACE_CASE_DES = 'des'
    DING_TALK_URL = 'DING_TALK_URL'
    INTERFACE_JSON_PATH = 'json_expr'

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

        assert yaml_file_path ,AssertionError('未找到yaml数据文件')

        with open(yaml_file_path, encoding='UTF-8') as f:
            dic = yaml.load(f, Loader=yaml.FullLoader)
            return dic

    def update_response_data(self,response:dict):
        '''
        更新接口返回数据
        '''
        self.res_data.update(response)

class ParsingData():

    def __init__(self):

        self.yaml_data = YamlSingleton().yaml_data
        self.response_data = YamlSingleton().res_data

    def get_interface_data(self,interface_name,assert_name,yaml_config_key):
        
        '''
        获取接口数据
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :param yaml_config_key: yaml配置key
        :return:
        '''
        
        if self.yaml_data.__contains__(interface_name) and self.yaml_data[interface_name].__contains__(assert_name):
            
            if self.yaml_data[interface_name][assert_name].__contains__(yaml_config_key):

                return self.yaml_data[interface_name][assert_name][yaml_config_key]
            
    def get_object_host(self,host_key:str = None):
        '''
        获取项目host ，默认返回第一个HOST
        :param host_key:
        :return:
        '''
        if operator.eq(host_key,None):

            return iter(self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST].values()).__next__()

        else:

            if self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST].__contains__(host_key):

                return self.yaml_data[YAML_CONFIG_KEY.OBJECT_HOST][host_key]

    def get_interface_url(self,interface_name:str,host_key:str = None):
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

    def get_interface_request_data(self,interface_name,assert_name):
        '''
        获取接口请求数据
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :return:
        '''
        
        request_data = self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=YAML_CONFIG_KEY.INTERFACE_REQUEST_DATA)
        
        if request_data != None:
            
            return self.find_interface_request_data_json_path(request_data=request_data)
        
        return request_data

    def get_interface_assert_value(self,interface_name,assert_name):
        
        '''
        获取接口断言数据
        :param interface_name: 接口名称
        :param assert_name:  接口对应断言名称
        :return:
        '''
        
        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=YAML_CONFIG_KEY.INTERFACE_ASSERT_DATA)
    
    def get_interface_des(self,interface_name,assert_name):
    
        '''
        获取用例说明
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名称
        :return:
        '''

        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=YAML_CONFIG_KEY.INTERFACE_CASE_DES)
        
    def get_interface_json_path(self,interface_name,assert_name):
        
        '''
        获取用例jsonpath
        :param interface_name: 接口名称
        :param assert_name: 接口对应断言名
        :return:
        '''
        
        return self.get_interface_data(interface_name=interface_name,
                                       assert_name=assert_name,
                                       yaml_config_key=YAML_CONFIG_KEY.INTERFACE_JSON_PATH)

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

    def get_interface_url_interface_name(self, host_key:str):
        '''
		通过hostkey获取接口名称
		:param host_key:
		:return:
		'''
    
        for interface_name, value in self.yaml_data.items():
            if value.__contains__(host_key) and operator.ne(interface_name,YAML_CONFIG_KEY.OBJECT_HOST):
                return interface_name

    def get_interface_response_data(self):
        '''
		获取接口返回值
		:return:
		'''
        return self.response_data
    
    def get_send_error_info_url(self):
        '''
        获取项目配置钉钉机器人URL
        :return:
        '''
        return self.yaml_data[YAML_CONFIG_KEY.DING_TALK_URL]
    
    def get_interface_assert_name(self,assert_value:dict):
        '''
        获取接口断言key
        :param assert_value: 断言值
        :return:
        '''
        
    def update_interface_json_path(self,interface_name,assert_name,new_value:dict):
        '''
        修改json_path 路径
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :param new_value: 修改值，以字典传入
        :return:
        '''
        old_json_path = self.get_interface_json_path(interface_name=interface_name,
                                                     assert_name=assert_name)
        
        old_json_path.format(**new_value)
    
    def update_interface_request_data(self,interface_name,assert_name,new_request_data:dict):
        '''
        修改接口请求参数
        :param interface_name: 接口名称
        :param assert_name: 断言名称
        :param new_request_data: 新接口请求值
        '''
        
        old_interface_request_data = self.get_interface_request_data(interface_name=interface_name,
                                           assert_name=assert_name)
        
        if old_interface_request_data != None:
            
            old_interface_request_data.update(new_request_data)
        
    def find_interface_request_data_json_path(self,request_data:dict):
        '''
        替换请求参数里通过jonspath查找到的值
        :param request_data: 请求字典
        :return:
        '''
        for key,value in request_data.items():
            
            if isinstance(value,str) and value.find('$') != -1:
                
                find_value = jsonpath.jsonpath(self.response_data,value)
                
                if find_value:
                    
                    request_data[key] = find_value[0]
        
        
        return request_data
        
    def save_response_data(self,response:requests.Response):
        '''
        保存接口返回值
        :param dic:
        :return:
        '''
        if isinstance(response, dict):
    
            json_value = response

        else:
    
            if response.status_code == 200:
                json_key = os.path.split(urlparse(response.request.url).path)[-1]
                json_key = json_key.replace('.', '/')
                json_value = {json_key: self.parse_response_data(response_data=response)}

        YamlSingleton().update_response_data(response=json_value)
    
    def parse_response_data(self,response_data:requests.Response):
        '''
        解析接口返回对象为json
        :param response_data:
        :return:
        '''
        
        if isinstance(response_data, requests.Response) and operator.eq(response_data.headers['Content-Type'], 'application/json; charset=UTF-8'):
            return response_data.json()
       
        elif isinstance(response_data,dict):
            return response_data
        
    

if __name__ == '__main__':
    print(ParsingData().get_interface_request_data(interface_name='res_login',
                                                   assert_name='DEV_HOST'))
