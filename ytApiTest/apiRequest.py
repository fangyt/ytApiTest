#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:39
# Author : fyt
# File   : apiRequest.py

import requests,json

from ytApiTest.apiData import ParsingData
from dingtalkchatbot.chatbot import DingtalkChatbot


class InterFaceReq():

    def __init__(self):

        self.parsing_data = ParsingData()

    def run_interface_setup_req(self, interface_name, assert_name):
        '''
		运行接口setup 关键字接口
		:param interface_name: 接口名称
		:param assert_name: 接口内关联用例
		:return:
		'''
        setup_list = self.parsing_data.get_interface_setup_list(interface_name=interface_name,
                                                                assert_name=assert_name)
        if setup_list != None:

            for index, interface_dic_info in enumerate(setup_list):
                list_interface_name = interface_dic_info.get('interface_name')
                list_assert_name = interface_dic_info.get('assert_name')
                list_host_key = interface_dic_info.get('host_key')
                url = self.parsing_data.get_interface_url(interface_name=list_interface_name,
                                                          host_key=list_host_key)
                data = self.parsing_data.get_interface_request_data(interface_name=list_interface_name,
                                                                    assert_name=list_assert_name)
                headers = self.parsing_data.get_interface_request_header(interface_name=list_interface_name,
                                                                         assert_name=list_assert_name)
                setup_response = requests.post(url=url,
                                               data=data,
                                               headers=headers)
                setup_response.raise_for_status()
                self.parsing_data.save_response_data(response=setup_response)
                requests.delete(url=url,
                                data=data,
                                headers=headers)

    def save_interface_headers_info(self, interface_name, assert_name):
        '''
		保存接口请求头信息
		:param interface_name:
		:param assert_name:
		:param host_key:
		:return:
		'''

        self.run_interface_setup_req(interface_name=interface_name,
                                     assert_name=assert_name)

        interface_url = self.parsing_data.get_interface_url(interface_name=interface_name,
                                                            host_key=assert_name)

        interface_req_data = self.parsing_data.get_interface_request_data(interface_name=interface_name,
                                                                          assert_name=assert_name)

        interface_headers = self.parsing_data.get_interface_request_header(interface_name=interface_name,

                                                                           assert_name=assert_name)

        response = requests.post(url=interface_url,
                                 data=interface_req_data,
                                 headers=interface_headers)
        response.raise_for_status()

        if interface_headers == None:
            interface_headers = {'Content-Type': 'application/json'}

        if response.request._cookies:
            interface_headers.update(response.request.headers)
            return interface_headers
        response_json = self.parsing_data.parse_response_data(response)

        if response_json.__contains__('data') and response_json.get('rtn') == 0:
            if response_json.get('data').__contains__('userinfo'):
                interface_headers.update({'Content-Type': 'application/json',
                                          'Cookie': 'userId={userId}; '
                                                    'sessionId={sessionId};weId=supermonkey-weapp'.format(
                                              userId=response.json()['data']['userinfo']['userId'],
                                              sessionId=response.json()['data']['sessionId']),
                                          })
            elif response_json.get('data').__contains__('token'):

                interface_headers.update({'authorization': response.json()['data']['token']})

        self.parsing_data.save_response_data(response={assert_name: interface_headers})

        return interface_headers

    def get_interface_cookie(self, url: str, host_key=None):
        '''
		获取并保存接口cookis
		:param url: 完整接口url
		:return:
		'''
        if host_key != None:

            assert_name = host_key

        else:

            assert_name = self.parsing_data.get_interface_url_host_key(url=url)
        response_data = self.parsing_data.get_interface_response_data()

        if response_data.__contains__(assert_name):
            return response_data[assert_name]

        interface_name = self.parsing_data.get_interface_url_interface_name(host_key=assert_name)
        return self.save_interface_headers_info(interface_name=interface_name,
                                                assert_name=assert_name)

    def get(self, interface_name, assert_name, host_key=None):
        '''
		get 请求
		:param interface_name: 接口名称
		:param assert_name: 接口断言名称
		:param host_key: 拼接URL host名称
		:return:
		'''
        url = self.parsing_data.get_interface_url(interface_name=interface_name,
                                                  host_key=host_key)
        params = self.parsing_data.get_interface_request_data(interface_name=interface_name,
                                                              assert_name=assert_name)
        interface_headers = self.parsing_data.get_interface_request_header(interface_name=interface_name,
                                                                           assert_name=assert_name)

        headers = self.get_interface_cookie(url=url,
                                            host_key=host_key)

        if interface_name != None:

            headers.update(interface_headers)

        response = requests.get(url=url,
                                params=json.loads(params),
                                headers=headers,
                                verify=False)

        response.raise_for_status()
        requests.delete(url=url, params=params)

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
        url = self.parsing_data.get_interface_url(interface_name=interface_name,
                                                  host_key=host_key)
        params = self.parsing_data.get_interface_request_data(interface_name=interface_name,
                                                              assert_name=assert_name)
        interface_headers = self.parsing_data.get_interface_request_header(interface_name=interface_name,
                                                                           assert_name=assert_name)

        headers = self.get_interface_cookie(url=url,
                                            host_key=host_key)

        requests.packages.urllib3.disable_warnings()
        if interface_name != None:
            headers.update(interface_headers)
        response = requests.post(url=url,
                                 data=params,
                                 headers=headers,
                                 verify=False)
        response.raise_for_status()
        requests.delete(url=url, data=params)

        self.parsing_data.save_response_data(response)

        return response

    def send_case_error_info(self, error_info):
        '''
		发送错误消息到钉钉群
		:param error_info:
		:return:
		'''
        DingtalkChatbot(self.parsing_data.get_send_error_info_url()).send_text(error_info)

        return error_info


if __name__ == '__main__':
    pass

