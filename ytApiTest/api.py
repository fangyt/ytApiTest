#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-03-20 15:27
# @Author  : SuperMonkey
# @Site    : 
# @File    : api.py
# @Software: PyCharm

from ytApiTest.apiRequest import InterFaceReq
from ytApiTest.apiAssert import InterFaceAssert
from ytApiTest.apiData import ParsingData

def get(interface_name,assert_name,host_key=None):
	
	return InterFaceReq().get(interface_name=interface_name,
	                        assert_name=assert_name,
	                          host_key=host_key)

def post(interface_name,assert_name,host_key=None):
	
	return InterFaceReq().post(interface_name=interface_name,
	                         assert_name=assert_name,
	                           host_key=host_key)

def get_interface_url(interface_name:str,host_key:str = None):
	'''
	获取接口URL路径
	:param interface_name: 接口名称
	:param host_key: 项目host_key
	:return:
	'''
	return ParsingData().get_interface_url(interface_name=interface_name,
	                                     host_key=host_key)


def get_interface_request_data(interface_name, assert_name):
	'''
	获取接口请求数据
	:param interface_name: 接口名称
	:param assert_name: 断言名称
	:return:
	'''
	return ParsingData().get_interface_request_data(interface_name=interface_name,
	                                              assert_name=assert_name)


def get_interface_case_assert_data(interface_name, assert_name):
	'''
	获取接口断言数据
	:param interface_name: 接口名称
	:param assert_name:  接口对应断言名称
	:return:
	'''
	return ParsingData().get_interface_assert_value(interface_name=interface_name,
	                                              assert_name=assert_name)


def get_interface_json_path(interface_name, assert_name):
	'''
	获取用例jsonpath
	:param interface_name: 接口名称
	:param assert_name: 接口对应断言名
	:return:
	'''
	
	return ParsingData().get_interface_json_path(interface_name=interface_name,
	                                           assert_name=assert_name)


def update_interface_json_path(interface_name, assert_name, new_value: dict):
	'''
	修改json_path 路径
	:param interface_name: 接口名称
	:param assert_name: 断言名称
	:param new_value: 修改值，以字典传入
	:return:
	'''
	return ParsingData().update_interface_json_path(interface_name=interface_name,
	                                              assert_name=assert_name,
	                                              new_value=new_value)


def update_interface_request_data(interface_name, assert_name, new_request_data: dict):
	'''
	修改接口请求参数
	:param interface_name: 接口名称
	:param assert_name: 断言名称
	:param new_request_data: 新接口请求值
	'''
	
	return ParsingData().update_interface_request_data(interface_name=interface_name,
	                                                 assert_name=assert_name,
	                                                 new_request_data=new_request_data)


def assert_body_eq_assert_value(response_data, assert_value, json_expr):
	'''
	断言
	:param response_data: 接口返回值
	:param assert_value: 请求数据
	:param json_expr: jsonpath表达式
	'''
	InterFaceAssert().assert_body_eq_assert_value(response_data=response_data,
	                                              assert_value=assert_value,
	                                              json_expr=json_expr)
	
def assert_body_include_value(response_data, assert_value, json_expr):
	'''
	判断是否包含
	:param response_data: 接口返回数据
	:param assert_value: 断言数据
	:param json_expr: jsonpath路径
	:return:
	'''
	
	InterFaceAssert().assert_body_include_value(response_data=response_data,
	                                            assert_value=assert_value,
	                                            json_expr=json_expr)

def assert_response_url_status(response):
    '''
	断言返回值中所有URL是否可以正常访问
	:param response: 后台返回值
	:return:
	'''
    InterFaceAssert().assert_response_url_status(response=response)