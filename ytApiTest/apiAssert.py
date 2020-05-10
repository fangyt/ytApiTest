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
		self.request = apiRequest.InterFaceReq()
	
	def error_info(self, response_data: requests.Response):
		
		return '未从返回值中查找到对比数据\n\n' \
		       'URL = {URL}\n\n' \
		       'param = {param}\n\n' \
		       'response = {response}'.format(URL=response_data.url,
		                                      param=response_data.request.body,
		                                      response=response_data.text)
	
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
		assert response_json, self.request.send_case_error_info(
			'无法解析返回值{response_data}'.format(response_data=response_data))
		find_value = jsonpath.jsonpath(response_json, json_expr)
		assert find_value, self.request.send_case_error_info(error_info=self.error_info(response_data))
		
		return find_value[0]
	
	def assert_include(self, response_data, assert_value, json_expr, **kwargs):
		'''
		判断是否包含
		:param response_data: 接口返回数据
		:param assert_value: 断言数据
		:param json_expr: jsonpath路径
		:return:
		'''
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr)
		default_bool = False
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		
		try:
			if isinstance(assert_value, dict) and isinstance(find_value, dict):
				error_info = '\ndes:{des}' \
				             '\n\nresponse: {response}' \
				             '\n\n assert: {assert}' \
				             '\n\n url: {url}' \
				             '\n\n params: {params}' \
				             '\n\nheaders: {headers}'
				
				for key, value in assert_value.items():
					if find_value.__contains__(key):
						default_bool = True
					assert operator.eq(find_value[key], value), self.request.send_case_error_info(
						error_info.format_map
							(
							{'des': des,
							 'response': {key: find_value[key]},
							 'assert': {key: value},
							 'url': response_data.url,
							 'params': response_data.request.body,
							 'headers': response_data.request.headers
								
							 }
						)
					)
				assert default_bool, self.request.send_case_error_info(
					error_info='find_value = {find_value}'
					           '\n\nassert_value = {assert_value}'.format(
						assert_value=assert_value, find_value=find_value))
			
			elif isinstance(assert_value, list) and isinstance(find_value, list):
				for index, value in enumerate(assert_value):
					error_info = '\ndes:{des}' \
					             '\n\nresponse: {response} ' \
					             '\n\n assert: {assert}' \
					             '\n\n url: {url}' \
					             '\n\n params: {params}' \
					             '\n\nheaders: {headers}'.format_map(
						{'des': des,
						 'response': find_value,
						 'assert': assert_value,
						 'url': response_data.url,
						 'params': response_data.request.body,
						 'headers': response_data.request.headers
						 }
					)
					assert operator.ne(find_value.count(value), 0), self.request.send_case_error_info(
						error_info)
		finally:
			
			self.run_case_request(
				self.parsing_data.get_interface_tear_down_list(interface_name=kwargs.get('interface_name'),
				                                               assert_name=kwargs.get('assert_name')))
	
	def assert_eq(self, response_data, assert_value, json_expr, **kwargs):
		'''
		断言
		:param response_data: 接口返回值
		:param assert_value: 请求数据
		:param json_expr: jsonpath表达式
		:return:
		'''
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr)
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		error_info = '\ndes{des}\n\n断言值为空{assert_value}'
		assert operator.ne(assert_value, None), self.request.send_case_error_info(
			error_info.format(assert_value=assert_value,
			                  des=des))
		
		try:
			if isinstance(find_value, dict) and isinstance(assert_value, dict):
				print(find_value, '\n\n', assert_value)
				self.assert_dict_eq(response_dic=find_value,
				                    assert_dic=assert_value,
				                    response_data=response_data,
				                    interface_name=kwargs.get('interface_name'),
				                    assert_name=kwargs.get('assert_name'))
			
			elif isinstance(find_value, list) and isinstance(assert_value, list):
				self.assert_list_eq(response_list=find_value,
				                    assert_list=assert_value,
				                    response_data=response_data,
				                    interface_name=kwargs.get('interface_name'),
				                    assert_name=kwargs.get('assert_name'))
		
		finally:
			self.run_case_request(
				self.parsing_data.get_interface_tear_down_list(interface_name=kwargs.get('interface_name'),
				                                               assert_name=kwargs.get('assert_name')))
	
	def assert_length_eq(self, response_value, assert_value, **kwargs):
		'''
		判断对比数据长度
		:param response_value:
		:param assert_value:
		:return:
		'''
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		error_info = '\ndes:{des}\n\nresponse_length: {response_length} \n\n assert_length: {assert_length}'.format_map(
			{'response_length': len(response_value),
			 'assert_length': len(assert_value),
			 'des': des})
		
		assert operator.eq(len(response_value), len(assert_value)), self.request.send_case_error_info(
			error_info)
	
	def assert_dict_eq(self, response_dic: dict, assert_dic: dict, **kwargs):
		'''
		判断字典是否相等
		:param response_dic: 返回值
		:param assert_dic: 断言字典
		:return:
		'''
		self.assert_length_eq(response_value=response_dic,
		                      assert_value=assert_dic)
		error_info = '\ndes={des}' \
		             '\n\nurl= {url}' \
		             '\n\nparam= {param}' \
		             '\n\nresponse={response} ' \
		             '\n\n assert={assert}'
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		for key, value in assert_dic.items():
			assert operator.eq(response_dic[key], value), self.request.send_case_error_info(
				error_info.format_map(
					{'response': {key: response_dic[key]},
					 'assert': {key: value},
					 'des': des,
					 'url': kwargs.get('response_data').url,
					 'param': kwargs.get('response_data').request.body}))
	
	def assert_list_eq(self, response_list: list, assert_list: list, **kwargs):
		'''
		判断列表数据是否相等
		:param response_list:
		:param assert_list:
		:return:
		'''
		self.assert_length_eq(response_value=response_list,
		                      assert_value=assert_list)
		
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		
		error_info = '\ndes={des}' \
		             '\n\nurl= {url}' \
		             '\n\nparam= {param}' \
		             '\n\nresponse={response} ' \
		             '\n\n assert={assert}'
		#:列表要排序在对比
		assert_list.sort()
		response_list.sort()
		for index, value in enumerate(assert_list):
			assert operator.eq(response_list[index], value), self.request.send_case_error_info(
				error_info.format_map(
					{'response': response_list[index],
					 'assert': value,
					 'des': des,
					 'url': kwargs.get('response_data').url,
					 'param': kwargs.get('response_data').request.body
					 }))
	
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
				assert operator.eq(body.status_code, 200), self.request.send_case_error_info(
					'\n状态码错误{error_info}'.format(error_info=error_info))
	
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
	
	def assert_url_status_code(self, response_data, **kwargs):
		'''
		断言url状态是否200
		:param response_data:
		:param kwargs:
		:return:
		'''
		des = self.parsing_data.get_interface_des(interface_name=kwargs.get('interface_name'),
		                                          assert_name=kwargs.get('assert_name'))
		error_info = '\ndes: {des}' \
		             '\n\n{info}'.format_map({'des': des,
		                                      'info': {response_data.url: response_data.status_code}})
		assert operator.eq(response_data.status_code, 200), self.request.send_case_error_info(error_info=error_info)
	
	def run_case_request(self, request_list: list):
		'''
		用例前置和后置操作
		:param request_list:
		:return:
		'''
		if request_list != None and len(request_list) != 0:
			
			for dic in request_list:
				response_data = self.request.post(interface_name=dic['interface_name'],
				                                  assert_name=dic['assert_name'],
				                                  host_key=dic.get('host_key'))
				
				self.assert_url_status_code(response_data=response_data,
				                            interface_name=dic['interface_name'],
				                            assert_name=dic['assert_name'])


if __name__ == '__main__':
	pass
