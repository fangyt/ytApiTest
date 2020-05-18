#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiAssert.py

import requests, jsonpath, operator, json

from ytApiTest import apiData, apiRequest


class InterFaceAssert():
	
	def __init__(self):
		
		self.parsing_data = apiData.ParsingData()
		self.request = apiRequest.InterFaceReq()
	
	def format_interface_send_info(self, response: requests.Response, **kwargs):
		'''
		格式化提示信息
		:param response:
		:param kwargs:
		:return:
		'''
		interface_name = kwargs.get('interface_name')
		assert_name = kwargs.get('assert_name')
		
		title = kwargs.get('title')
		des = self.parsing_data.get_interface_des(interface_name=interface_name,
		                                          assert_name=assert_name)
		response_json = response.json()
		interface_url = response.url
		params = response.request.body
		assert_value = kwargs.get('assert_value')
		if operator.ne(assert_value , None):
			assert_value = self.parsing_data.get_interface_assert_value(interface_name=interface_name,
			                                                            assert_name=assert_name)
		
		json_expr = self.parsing_data.get_interface_json_path(interface_name=interface_name,
		                                                      assert_name=assert_name)
		
		headers = response.request.headers
		find_value = kwargs.get('find_value')
		info_dic = {'title': title,
		            'case_des': des,
		            'url': interface_url,
		            'json_expr': json_expr,
		            'response': response_json,
		            'assert': assert_value,
		            'find_value': find_value,
		            'params': params,
		            'headers': headers}
		
		info = '\n TITLE      =   {title}' \
		       '\n\n DES        =   {case_des}' \
		       '\n\n URL        =   {url}' \
		       '\n\n PARAMS     =   {params}' \
		       '\n\n JONS_EXPR  =   {json_expr}' \
		       '\n\n HEADERS    =   {headers}' \
		       '\n\n RESPONSE   =   {response}' \
		       '\n\n FIND_VALUE  =   {find_value}' \
		       '\n\n ASSERT_VALUE     =   {assert}'.format_map(info_dic)
		
		self.request.send_case_error_info(error_info=info)
		
		return info
	
	def error_info(self, response_data: requests.Response):
		
		return '未从返回值中查找到对比数据\n\n' \
		       'URL = {URL}\n\n' \
		       'param = {param}\n\n' \
		       'response = {response}'.format(URL=response_data.url,
		                                      param=response_data.request.body,
		                                      response=response_data.text)
	
	def find_interface_assert_value(self, response_data: requests.Response, json_expr: str, **kwargs):
		'''
		根据json_path表达式查找接口发返回值对应对比数据
		:param response_data: 接口返回response对象
		:param expr: json_path表达式
		:return:
		'''
		interface_name = kwargs.get('interface_name')
		assert_name = kwargs.get('assert_name')
		if operator.eq(json_expr, None):
			return self.parsing_data.parse_response_data(response_data=response_data)
		
		response_json = self.parsing_data.parse_response_data(response_data)
		
		assert response_json, \
			self.format_interface_send_info(response=response_data,
			                                title='后台数据解析错误',
			                                interface_name=interface_name,
			                                assert_name=assert_name)
		
		find_value = jsonpath.jsonpath(response_json, json_expr)
		
		assert find_value, \
			self.format_interface_send_info(response=response_data,
			                                title='json_expr表达式查找错误',
			                                interface_name=kwargs.get('interface_name'),
			                                assert_name=kwargs.get('assert_name'))
		
		return find_value[0]
	
	def assert_include(self, response_data, assert_value, json_expr, **kwargs):
		'''
		判断是否包含
		:param response_data: 接口返回数据
		:param assert_value: 断言数据
		:param json_expr: jsonpath路径
		:return:
		'''
		interface_name = kwargs.get('interface_name')
		assert_name = kwargs.get('assert_name')
		
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr,
		                                              interface_name=interface_name,
		                                              assert_name=assert_name)
		default_bool = False
		
		try:
			if isinstance(assert_value, dict) and isinstance(find_value, dict):
				
				for key, value in assert_value.items():
					
					if find_value.__contains__(key):
						default_bool = True
					
					assert operator.eq(find_value[key], value), \
						self.format_interface_send_info(response=response_data,
						                                title='包含断言失败',
						                                interface_name=interface_name,
						                                assert_name=assert_name,
						                                find_value=find_value)
				
				assert default_bool, \
					self.format_interface_send_info(response=response_data,
					                                title='包含断言失败',
					                                interface_name=interface_name,
					                                assert_name=assert_name,
					                                find_value=find_value)
			
			
			
			elif isinstance(assert_value, list) and isinstance(find_value, list):
				
				for index, value in enumerate(assert_value):
					assert operator.ne(find_value.count(value), 0), \
						self.format_interface_send_info(
							response=response_data,
							title='包含断言失败',
							interface_name=interface_name,
							assert_name=assert_name,
							find_value=find_value)
		
		
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
		interface_name = kwargs.get('interface_name')
		assert_name = kwargs.get('assert_name')
		
		find_value = self.find_interface_assert_value(response_data=response_data,
		                                              json_expr=json_expr,
		                                              interface_name=interface_name,
		                                              assert_name=assert_name)
		
		
		
		try:
			if isinstance(find_value, dict) and isinstance(assert_value, dict):
				
				self.assert_dict_eq(response_dic=find_value,
				                    assert_dic=assert_value,
				                    response=response_data,
				                    interface_name=interface_name,
				                    assert_name=assert_name)
			
			elif isinstance(find_value, list) and isinstance(assert_value, list):
				
				self.assert_list_eq(response_list=find_value,
				                    assert_list=assert_value,
				                    response=response_data,
				                    interface_name=interface_name,
				                    assert_name=assert_name)
			else:
				
				assert operator.eq(find_value, assert_value), \
					self.format_interface_send_info(response=response_data,
					                                title='相等断言失败',
					                                interface_name=interface_name,
					                                assert_name=assert_name,
					                                find_value=find_value)
		
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
		interface_name = kwargs.get('interface_name'),
		assert_name = kwargs.get('assert_name')
		response = kwargs.get('response')
		
		assert operator.eq(len(response_value), len(assert_value)), \
			self.format_interface_send_info(title='相等断言失败，断言数据与返回数据长度不一致',
			                                interface_name=interface_name,
			                                assert_name=assert_name,
			                                find_value=response_value,
			                                response=response)
	
	def assert_dict_eq(self, response_dic: dict, assert_dic: dict, **kwargs):
		'''
		判断字典是否相等
		:param response_dic: 返回值
		:param assert_dic: 断言字典
		:return:
		'''
		
		interface_name = kwargs.get('interface_name'),
		assert_name = kwargs.get('assert_name')
		response = kwargs.get('response')
		
		self.assert_length_eq(response_value=response_dic,
		                      assert_value=assert_dic,
		                      interface_name=interface_name,
		                      assert_name=assert_name,
		                      response=response)
		
		for key, value in assert_dic.items():
			assert operator.eq(response_dic[key], value), \
				self.format_interface_send_info(title='相等字典方法断言失败',
				                                response=response,
				                                interface_name=interface_name,
				                                assert_name=assert_name,
				                                find_value={key: response_dic[key]},
				                                assert_value={key: value})
	
	def assert_list_eq(self, response_list: list, assert_list: list, **kwargs):
		'''
		判断列表数据是否相等
		:param response_list:
		:param assert_list:
		:return:
		'''
		interface_name = kwargs.get('interface_name'),
		assert_name = kwargs.get('assert_name')
		response = kwargs.get('response')
		
		self.assert_length_eq(response_value=response_list,
		                      assert_value=assert_list,
		                      interface_name=interface_name,
		                      assert_name=assert_name,
		                      response=response)
		#:列表要排序在对比
		assert_list.sort()
		response_list.sort()
		for index, value in enumerate(assert_list):
			assert operator.eq(response_list[index], value), \
				self.format_interface_send_info(response=response,
				                                title='相等列表断言失败',
				                                interface_name=interface_name,
				                                assert_name=assert_name,
				                                find_value=response_list[index],
				                                assert_value=value)
	
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
				assert operator.eq(body.status_code, 200), \
					self.format_interface_send_info(title='接口返回值链接请求错误',
					                                response=response,
					                                find_value=error_info)
				requests.delete(url=url)
	
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
	
	def run_case_request(self, request_list: list):
		'''
		用例前置和后置操作
		:param request_list:
		:return:
		'''
		if request_list != None and len(request_list) != 0:
			
			for dic in request_list:
				self.request.post(interface_name=dic['interface_name'],
				                  assert_name=dic['assert_name'],
				                  host_key=dic.get('host_key'))


if __name__ == '__main__':
	pass
