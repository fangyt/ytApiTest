#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:22
# Author : fyt
# File   : apiReq.py

import requests, os, pysnooper
from urllib import parse
from dingtalkchatbot.chatbot import DingtalkChatbot

from ytApiTest import configKey
from ytApiTest import parsingData


def get_url_key(url):
    '''
    获取URL key
    :param url: URL
    :return: URL最后一个路径
    '''
    return os.path.split(parse.urlparse(url).path)[-1]


def get_account_cookies(url):
    url_key = parsingData.get_host_key(url=url)
    json_data = parsingData.parsing_json_data()
    if json_data.__contains__(url_key):

        return json_data[url_key]

    else:
        url = parsingData.get_interface_url(interface_key=parsingData.get_cookie_key(host_key=url_key),
                                            host_key=url_key)
        data = parsingData.get_interface_request_data(parsingData.get_cookie_key(url_key),
                                                                             case_key=url_key)
        response = requests.post(url=url,
                                 data=data)

        if response.status_code == 200:

            if response.request._cookies:

                headers = response.request.headers

            if response.headers['Content-Type'] != 'text/html; charset=UTF-8':

                headers = {'User-Agent': 'python-requests/2.22.0',
                           'Accept-Encoding': 'gzip, deflate',
                           'Accept': '*/*',
                           'Connection': 'keep-alive',
                           'Cookie': 'userId={userId}; sessionId={sessionId}; SMclient=MicroMessenger; SMmodel=Xiaomi_MI_8; SMsystem=Android_8.1.0; SMver=7.0.3; SMdisplay=393x818; SDKVersion=2.6.1; weId=supermonkey-weapp-gear; version=1.2.0;'.format(
                               userId=response.json()['data']['userinfo']['userId'],
                               sessionId=response.json()['data']['sessionId']),
                           'Content-Length': '0'
                           }

            parsingData.save_response_data(response={url_key: headers})

            return headers

        else:

            exit(0), print('headers保存失败', response.text)


def save_account_cookies():

    url = parsingData.parsing_case_yaml_data(configKey.ACCOUNT_URL)
    data = parsingData.parsing_case_yaml_data(configKey.ACCOUNT_DATA)

    return parsingData.save_response_data(requests.post(url=url, data=data))



def get(interface_key, case_key, host_key=None):

    url = parsingData.get_interface_url(interface_key, host_key=host_key)
    params = parsingData.get_interface_request_data(interface_key, case_key)

    response = requests.get(url=url,
                            params=params,
                            headers=get_account_cookies(url=url))


    parsingData.save_response_data(response)

    return response



def post(interface_key, case_key, host_key=None):

    url = parsingData.get_interface_url(interface_key, host_key=host_key)

    data = parsingData.get_interface_request_data(interface_key, case_key)

    response = requests.post(url=url,
                             data=data,
                             headers=get_account_cookies(url))


    parsingData.save_response_data(response)

    return response


def send_ding_talk_info(title, text):
    '''
    markdown类型
    :param title: 首屏会话透出的展示内容
    :param text: markdown格式的消息内容
    :return:
    '''

    if parsingData.parsing_case_yaml_data(configKey.DING_TALK_URL):

        url = parsingData.parsing_case_yaml_data(configKey.DING_TALK_URL)
        DingtalkChatbot(url).send_markdown(title=title,
                                           text=text)

    else:
        print('没有找到发送钉钉群URL')


if __name__ == '__main__':
   pass

