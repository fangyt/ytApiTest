#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:22
# Author : fyt
# File   : apiReq.py

import requests,os,pysnooper
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

@pysnooper.snoop()
def get_account_cookies(url):

    url_key = parsingData.get_host_key(url=url)

    json_data = parsingData.parsing_json_data()

    if json_data.__contains__(url_key):

        return json_data[url_key]

    else:

        response = requests.post(url=parsingData.get_interface_url(interface_key=parsingData.get_cookie_key(url_key)),
                                 data=parsingData.get_interface_request_data(parsingData.get_cookie_key(url_key),case_key=url_key))

        if response.status_code == 200:

            parsingData.save_response_data(response={parsingData.get_host_key(response.url): response.request._cookies})

        else:

            exit(0), print('cookie保存失败', response.text)


def save_account_cookies():


    url = parsingData.parsing_case_yaml_data(configKey.ACCOUNT_URL)
    data = parsingData.parsing_case_yaml_data(configKey.ACCOUNT_DATA)

    return parsingData.save_response_data(requests.post(url=url, data=data))

def get(interface_key,case_key,host_key = None):

    url = parsingData.get_interface_url(interface_key,host_key=host_key)
    params = parsingData.get_interface_request_data(interface_key, case_key)

    response = requests.get(url=url,
                 params=params,
                 headers=get_account_cookies())

    if response.json()['rtn'] == 25 or response.json()['rtn'] == 11:

        save_account_cookies()
        get(interface_key,case_key) #会不会死循环~~
    parsingData.save_response_data(response)
    return response

def post(interface_key,case_key,host_key = None):

    url  = parsingData.get_interface_url(interface_key,host_key=host_key)
    data = parsingData.get_interface_request_data(interface_key, case_key)
    response = requests.post(url=url,
                             data=data,
                             cookies=get_account_cookies(url))
    parsingData.save_response_data(response)
    return response

def send_ding_talk_info(title,text):
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
    post('classScheduleJson','search')
    post('classScheduleJson','search')
    post('classScheduleJson','search')
    print(post('classScheduleJson','search').text)



