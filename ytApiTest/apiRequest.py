#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:39
# Author : fyt
# File   : apiRequest.py

import requests

from ytApiTest.apiData import ParsingData
from dingtalkchatbot.chatbot import DingtalkChatbot

class InterFaceReq():
	
	def __init__(self):
		
		self.parsing_data = ParsingData()
	
	def get_interface_cookie(self,url:str):
		'''
		获取并保存接口cookis
		:param url: 完整接口url
		:return:
		'''
		cookie_key = self.parsing_data.get_interface_url_host_key(url=url)
		response_data = self.parsing_data.get_interface_response_data()
		if response_data.__contains__(cookie_key):
			
			return response_data[cookie_key]
		
		interface_name = self.parsing_data.get_interface_url_interface_name(host_key=cookie_key)
		login_url = self.parsing_data.get_interface_url(interface_name=interface_name)
		requests_data = self.parsing_data.get_interface_request_data(interface_name=interface_name,
		                                                             assert_name=cookie_key)
				
		response = requests.post(url=login_url,
		                              data=requests_data)
		
		if response.status_code == 200:
			
			if response.request._cookies:
				headers = response.request.headers
			
			elif response.headers['Content-Type'] != 'text/html; charset=UTF-8':
				headers = {'User-Agent': 'python-requests/2.22.0',
				           'Accept-Encoding': 'gzip, deflate',
				           'Accept': '*/*',
				           'Connection': 'keep-alive',
				           'Cookie': 'userId={userId}; sessionId={sessionId}; SMclient=MicroMessenger; SMmodel=Xiaomi_MI_8; SMsystem=Android_8.1.0; SMver=7.0.3; SMdisplay=393x818; SDKVersion=2.6.1; weId=supermonkey-weapp-gear; version=1.2.0;'.format(
					           userId=response.json()['data']['userinfo']['userId'],
					           sessionId=response.json()['data']['sessionId']),
				           'Content-Length': '0'
				           }
						
			self.parsing_data.save_response_data(response={cookie_key: headers})
			
			return headers
		
	def get(self,interface_name,assert_name,host_key=None):
		'''
		get 请求
		:param interface_name: 接口名称
		:param assert_name: 接口断言名称
		:param host_key: 拼接URL host名称
		:return:
		'''
		url = self.parsing_data.get_interface_url(interface_name=interface_name, host_key=host_key)
		params = self.parsing_data.get_interface_request_data(interface_name=interface_name, assert_name=assert_name)
		
		response = requests.get(url=url,
		                        params=params,
		                        headers=self.get_interface_cookie(url=url))
		
		self.parsing_data.save_response_data(response)
		
		return response
	
	def post(self, interface_name, assert_name, host_key=None):
		'''
		post 请求
		:param interface_name: 接口名称
		:param assert_name: 接口断言名称
		:param host_key: 拼接URL host名称
		:return:
		'''
		url = self.parsing_data.get_interface_url(interface_name=interface_name, host_key=host_key)
		params = self.parsing_data.get_interface_request_data(interface_name=interface_name, assert_name=assert_name)
		
		response = requests.post(url=url,
		                        params=params,
		                        headers=self.get_interface_cookie(url=url))
		
		self.parsing_data.save_response_data(response)
		
		return response
	
	def send_case_error_info(self,error_info):
		'''
		发送错误消息到钉钉群
		:param error_info:
		:return:
		'''
		DingtalkChatbot(self.parsing_data.get_send_error_info_url()).send_markdown(error_info)
		
		
		
if __name__ == '__main__':
    v = InterFaceReq().post(interface_name='getInitInfo',
                              assert_name='assert_user_info').text
    print(v)
    