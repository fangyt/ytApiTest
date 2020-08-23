#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:39
# Author : fyt
# File   : apiRequest.py

import requests

from ytApiTest.apiData import ParsingData
from  ytApiTest.yamlKey import YAML_CONFIG_KEY
from dingtalkchatbot.chatbot import DingtalkChatbot


class InterFaceReq():

    def __init__(self):

        self.parsing_data = ParsingData()
        self.data_key = YAML_CONFIG_KEY



    def req(self, **kwargs):

        requests.packages.urllib3.disable_warnings()
        response = requests.request( method=kwargs.get(self.data_key.INTERFACE_CACHE_METHOD), url=kwargs.get(self.data_key.INTERFACE_URL),params=kwargs.get(self.data_key.INTERFACE_REQUEST_DATA),data=kwargs.get(self.data_key.INTERFACE_ASSERT_DATA),headers=kwargs.get(self.data_key.INTERFACE_REQUEST_HEADERS),verify=False, **kwargs)
        response.raise_for_status()
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

