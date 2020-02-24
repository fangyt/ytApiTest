#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:22
# Author : fyt
# File   : parsingData.py

import yaml, json, os, jsonpath, operator, requests
from ytApiTest.file import create_data_file
from ytApiTest import configKey, file
from urllib import parse


class YamlSingleton():
    _obj = None
    _init_flag = True
    yaml_data = None

    def __new__(cls, *args, **kwargs):

        if YamlSingleton._obj == None:
            YamlSingleton._obj = object.__new__(cls)

        return cls._obj

    def __init__(self):
        if YamlSingleton._init_flag:
            YamlSingleton._init_flag = False
            YamlSingleton.yaml_data = self.get_yaml_data()

    def get_yaml_data(self):
        '''
        获取yaml测试数据
        :return:
        '''

        yaml_file_path = file.find_obj_yaml_file()

        if not yaml_file_path:
            return '找不到yaml数据文件'

        try:
            with open(yaml_file_path, encoding='UTF-8') as f:
                dic = yaml.load(f, Loader=yaml.FullLoader)
                return dic
        except RuntimeError as e:
            exit(1)
            print('解析用例数据文件错误，或者找不到', e)

    def get_json_data(self):
        pass

__CONFIG__ = YamlSingleton().yaml_data

def parser_response(response):
    '''
    解析body 为json数据
    :param body:
    :return:
    '''
    if isinstance(response, requests.Response) and \
            operator.eq(response.headers['Content-Type'], 'application/json; charset=UTF-8'):
        return response.json()

    else:
        return response


def parsing_json_data():
    '''
    解析后台接口返回值
    :return:
    '''
    with open(create_data_file(), encoding='utf-8')as json_file:
        data = json.load(json_file)

        return data


def parsing_case_yaml_data(interface_key=None, assert_key=None, assert_value_key=None):
    '''
    解析用例数据文件
    :param interface_key: 接口key
    :param case_key: 断言key
    :param get_case_key:
    :return:
    '''
    try:

        dic = __CONFIG__

        if interface_key and \
                assert_key and \
                assert_value_key:

            if dic.__contains__(interface_key) and \
                    dic[interface_key].__contains__(assert_key) and \
                    dic[interface_key][assert_key].__contains__(assert_value_key):
                return dic[interface_key][assert_key][assert_value_key]
        elif interface_key and \
                assert_key and \
                not assert_value_key:

            if dic.__contains__(interface_key) and \
                    dic[interface_key].__contains__(assert_key):
                return dic[interface_key][assert_key]
        elif interface_key and \
                not assert_key and \
                not assert_value_key:

            if dic.__contains__(interface_key):
                return dic[interface_key]


    except RuntimeError as e:
        exit(1)
        print('解析用例数据文件错误，或者找不到', e)


def save_response_data(response):
    '''
    保持接口返回数据
    :param response: 后台返回值
    :return:
    '''
    if response.status_code == 200:
        json_key = os.path.split(parse.urlparse(response.request.url).path)[-1]
        json_value = {json_key: parser_response(response)}
    else:
        return '无法解析后台返回值', response

    old_json_data = parsing_json_data()

    old_json_data.update(json_value)

    json_data = json.dumps(old_json_data, indent=4)

    try:

        with open(create_data_file(), 'w', encoding='utf-8') as f:

            f.write(json_data)

    except RuntimeError as error:

        print('json数据写入失败', error)


def get_interface_request_data(interface_key, case_key):
    '''
    获取接口请求数据
    :param interface_key: 接口
    :param case_key: 断言key
    :return:
    '''

    return replace_json_path_value(parsing_case_yaml_data(interface_key, case_key, configKey.YAML_KEY().REQ_DATA))


def get_interface_url(interface_key):
    '''
    获取接口URL
    :param interface_key: 接口key
    :return:
    '''
    return parsing_case_yaml_data(configKey.OBJECT_HOST) + parsing_case_yaml_data(interface_key,
                                                                                  configKey.YAML_KEY().URL)


def get_interface_case_assert_data(interface_key, case_key):
    '''
    获取 接口断言参数
    :param interface_key: 接口
    :param case_key: 用例key
    :return:
    '''
    return replace_json_path_value(parsing_case_yaml_data(interface_key, case_key, configKey.YAML_KEY().ASSERT_DATA))


def get_interface_case_des(interface_key, case_key):
    '''
    获取用例说明
    :param interface_key: 接口key
    :param case_key: 用例key
    :return:
    '''
    return parsing_case_yaml_data(interface_key, case_key, configKey.YAML_KEY().DES)


def replace_json_path_value(dic):
    '''
    替换字典内jsonpath值为接口返回值
    :param dic: 替换字典
    :return:
    '''
    response_data = parsing_json_data()

    if isinstance(dic, dict):

        for key, value in dic.items():

            if operator.ne(value, str):
                value = str(value)

            if operator.ne(value.find('$'), -1):
                dic[key] = jsonpath.jsonpath(response_data, value)[0]

    return dic


if __name__ == '__main__':
    s = YamlSingleton()
    print(s.yaml_data)
    print(s.yaml_data)
    print(s.yaml_data)
