#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiAssert.py

import requests, jsonpath, operator, json

from ytApiTest import apiData, apiRequest


class AssertException(AssertionError):
	
	def __init__(self, errorInfo):

		self.errorInfo = str(errorInfo)
	
	def __str__(self):
		return self.errorInfo




class InterFaceAssert():
	
	def __init__(self):
		
		self.parsing_data = apiData.ParsingData()
	
	def find_interface_assert_value(self, response_data: requests.Response, json_expr: str):
		'''
		根据json_path表达式查找接口发返回值对应对比数据
		:param response_data: 接口返回response对象
		:param expr: json_path表达式
		:return:
		'''
		if operator.eq(json_expr, None):
			return self.parsing_data.parse_response_data(response_data=response_data)
		
		response_json = self.parsing_data.parse_response_data(response_data)
		assert response_json, AssertionError('无法解析返回值{response_data}'.format(response_data=response_data))
		
		find_value = jsonpath.jsonpath(response_json, json_expr)
		
		assert find_value, AssertionError('未从返回值中查找到对比数据{find_value}'.format(response_data=find_value))
		
		return find_value[0]
	
	def assert_body_include_value(self, response_data, assert_value, json_expr):
		'''
		判断是否包含
		:param response_data: 接口返回数据
		:param assert_value: 断言数据
		:param json_expr: jsonpath路径
		:return:
		'''
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr)
		
		if isinstance(assert_value, dict) and isinstance(find_value, dict):
			
			for key, value in assert_value.items():
				assert operator.eq(find_value[key], value), apiRequest.InterFaceReq().send_case_error_info(
																											'response={response} \n\n assert={assert}'.format_map
																												(
																													{'response': {key: find_value[key]},
																													 'assert': {key: value}
																													 }
																												)
																										)
		
		elif isinstance(assert_value,list) and isinstance(find_value,list):
			
			for index,value in enumerate(assert_value):
				error_info = 'response={response} \n\n assert={assert}'.format_map(
					{'response': find_value,
					 'assert': value})
				assert operator.ne(find_value.count(value),0),apiRequest.InterFaceReq().send_case_error_info(error_info)
				
	
	def assert_body_eq_assert_value(self, response_data, assert_value, json_expr):
		'''
		断言
		:param response_data: 接口返回值
		:param assert_value: 请求数据
		:param json_expr: jsonpath表达式
		:return:
		'''
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr)
		
		if isinstance(find_value, dict) and isinstance(assert_value, dict):
			self.assert_dict_eq(response_dic=find_value,
			                    assert_dic=assert_value)
		
		if isinstance(find_value, list) and isinstance(assert_value, list):
			self.assert_list_eq(response_list=response_data,
			                    assert_list=assert_value)
	
	def assert_length_ep(self, response_value, assert_value):
		'''
		判断对比数据长度
		:param response_value:
		:param assert_value:
		:return:
		'''
		error_info = 'response_length: {response_length} \n\n assert_length: {assert_length}'.format_map(
			{'response_length': len(response_value),
			 'assert_length': len(assert_value)})
		
		assert operator.eq(len(response_value), len(assert_value)), apiRequest.InterFaceReq().send_case_error_info(error_info)
	def assert_dict_eq(self, response_dic: dict, assert_dic: dict):
		'''
		判断字典是否相等
		:param response_dic: 返回值
		:param assert_dic: 断言字典
		:return:
		'''
		self.assert_length_ep(response_value=response_dic,
		                      assert_value=assert_dic)
		for key, value in assert_dic.items():
			assert operator.eq(response_dic[key], value), 'response={response} \n\n assert={assert}'.format_map(
					{'response': {key: response_dic[key]},
					 'assert': {key: value}})
	
	def assert_list_eq(self, response_list: list, assert_list: list):
		'''
		判断列表数据是否相等
		:param response_list:
		:param assert_list:
		:return:
		'''
		self.assert_length_ep(response_value=response_list,
		                      assert_value=assert_list)
		
		for index, value in enumerate(assert_list):
			assert operator.eq(response_list[index], value), apiRequest.InterFaceReq().send_case_error_info(
				'response={response} \n\n assert={assert}'.format_map(
					{'response': response_list[index],
					 'assert': value}))
	
	def assert_response_url_status(self, response):
		'''
		断言返回值中所有URL是否可以正常访问
		:param response: 后台返回值
		:return:
		'''
		
		response_str = json.dumps(self.parsing_data.parse_response_data(response))
		for rep_value in response_str.split(','):
			
			if rep_value.rfind('https') != -1:
				url = str(rep_value[rep_value.rfind('https'):]).replace("\"", '').replace(',', '')
				requests.packages.urllib3.disable_warnings()
				body = requests.get(self.rem_special_chars(url), verify=False)
				error_info = {url: body.status_code}
				assert operator.eq(body.status_code, 200), apiRequest.InterFaceReq().send_case_error_info('状态码错误{error_info}'.format_map(error_info))
	
	def rem_special_chars(self, string: str):
		'''
		删除特殊大括号中括号空格特殊字符
		:param string:
		:return:
		'''
		
		remap = {
			ord("{"): None,
			ord("["): None,
			ord("}"): None,
			ord(']'): None,
			ord(' '): None,
			ord('\"'): None,
			ord("\'"): None
			
		}
		
		return string.translate(remap)


if __name__ == '__main__':
	apiRequest.InterFaceReq().send_case_error_info('00000')
