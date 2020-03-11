#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:22
# Author : fyt
# File   : apiAssert.py

from urllib import parse
import operator, json, requests,warnings

from ytApiTest import apiReq
from ytApiTest import parsingData


class assert_error_info(Exception):
    '''
    自定义错误类，输出断言错误信息
    '''

    def __init__(self, errorInfo):
        self.errorInfo = str(errorInfo)

    def __str__(self):
        return self.errorInfo

def fmt_assert_info(body, differenceValue):
    '''
    格式化错误信息
    :param body: 接口返回值
    :param assertValue: 断言值
    :param differenceValue: 断言失败值
    :return: 组合错误信息
    '''

    if isinstance(body, requests.Response):
        data = ''
        url = body.request.url
        if body.request.body != None:
            data = parse.unquote(body.request.body)
        interface_info = url + data

        info = 'ErrorInfo: {errorInfo}\n\n' \
               'InterfaceInfo: {interfaceInfo}\n\n'.format(errorInfo=differenceValue,
                                                   interfaceInfo=interface_info,
                                                   )

        apiReq.send_ding_talk_info(title='接口断言失败',
                                   text=info)
        return info
    else:
        return None

#----------------断言方法------------------

def assert_url_code(body, assertValue):
    '''
    断言请求状态
    :return:
    '''

    assert operator.eq(body.status_code, assertValue), fmt_assert_info(body, '状态码不等于200')

def assert_body_include_value(body=None, assertValue=None):
    '''
    断言body 是否包含 value
    :return:
    '''

    body_str = json.dumps(parsingData.parser_response(body), ensure_ascii=False)
    assert_str = json.dumps(assertValue, ensure_ascii=False)

    response_str_set = set(interception_response_value(body_str, assert_str))
    assert_str_set = set(split_string(assert_str))

    if len(response_str_set) == 0:

        error = '未查找到断言值{response}'.format(response=body_str)

        return warnings.warn(error)

    assert_difference_info = list(assert_str_set.difference(response_str_set))
    response_difference_info = list(response_str_set.difference(assert_str_set))

    response_difference_info.sort()
    assert_difference_info.sort()

    error_info = {'ASSERT': '{assert_difference_info}'.format(assert_difference_info=assert_difference_info),
                  '************': '***********', 'RESPONSE': '{response_difference_info}'.format(
            response_difference_info=response_difference_info)}

    assert operator.eq(len(assert_difference_info), 0), assert_error_info(
        fmt_assert_info(body, assertValue, error_info))

def assert_body_ep_value(body=None, assertValue=None):
    '''
    断言body 是否与value完全相等
    :return:
    '''
    if body == None and assertValue == None:
        return

    body_str = rem_special_chars(json.dumps(parsingData.parser_response(body), ensure_ascii=False))
    assert_str = rem_special_chars(json.dumps(assertValue, ensure_ascii=False))

    response_str_set = set(body_str.split(','))
    assert_str_set = set(assert_str.split(','))

    assert_difference_info = list(assert_str_set.difference(response_str_set))
    response_difference_info = list(response_str_set.difference(assert_str_set))

    response_difference_info.sort()
    assert_difference_info.sort()

    error_info = {'ASSERT': '{assert_difference_info}'.format(assert_difference_info=response_difference_info),
                  '************': '***********', 'RESPONSE': '{response_difference_info}'.format(
            response_difference_info=assert_difference_info)}

    assert operator.eq(len(assert_difference_info), 0), assert_error_info(
        fmt_assert_info(body, assertValue, error_info))

def assert_response_url_status(response):
    '''
    断言返回值中所有URL是否可以正常访问
    :param response: 后台返回值
    :return:
    '''

    response_str = json.dumps(parsingData.parser_response(response))
    for rep_value in response_str.split(','):

        if rep_value.rfind('https') != -1:
            url = str(rep_value[rep_value.rfind('https'):]).replace("\"", '').replace(',', '')
            requests.packages.urllib3.disable_warnings()
            body = requests.get(rem_special_chars(url), verify=False)
            error_info = {url: body.status_code}
            assert operator.eq(body.status_code, 200), fmt_assert_info(differenceValue=error_info,
                                                                       body=response,
                                                                       assertValue=200)

def assert_skip_singletion_vlaue(body,assertValue,ignore_key):
    '''
    断言返回值，并忽略个别值不断言
    :param body:
    :param assertValue:
    :param ignore:
    :return:
    '''
    body_str = json.dumps(parsingData.parser_response(body), ensure_ascii=False)
    assert_str = json.dumps(assertValue, ensure_ascii=False)

    interception_list = rem_skip_assert_value(interception_response_value(body_str,assert_str),ignore_key=ignore_key)
    assert_list = rem_skip_assert_value(split_string(assert_str),ignore_key=ignore_key)


    response_str_set = set(interception_list)
    assert_str_set = set(assert_list)

    if len(response_str_set) == 0:

        error = '未查找到断言值{response}'.format(response=body_str)

        return warnings.warn(error)

    assert_difference_info = list(assert_str_set.difference(response_str_set))
    response_difference_info = list(response_str_set.difference(assert_str_set))

    response_difference_info.sort()
    assert_difference_info.sort()

    error_info = {'ASSERT': '{assert_difference_info}'.format(assert_difference_info=assert_difference_info),
                  '************': '***********', 'RESPONSE': '{response_difference_info}'.format(
            response_difference_info=response_difference_info)}

    assert operator.eq(len(assert_difference_info), 0), assert_error_info(
        fmt_assert_info(body, assertValue, error_info))

# ------------优化方法---------------
def interception_response_value(response_str: str, assert_str: str):
    '''
    截取返回值中的断言值
    :param response_str:
    :param assert_str:
    :return:
    '''
    if operator.not_(get_interception_index(response_str,assert_str)):
        '''
        未找到断言值
        '''
        return []


    if len(assert_str.split(',')) == 1:
        '''
        处理只有一个值需要查找
        '''
        return singleton_assert_value(response_str, assert_str)

    if get_interception_index(response_str, assert_str).__contains__('first_index') and \
       get_interception_index(response_str, assert_str).__contains__('last_index'):
        '''
        处理第一个值和最后一个都匹配，返回匹配列表
        '''
        star_index = get_interception_index(response_str, assert_str)['first_index']
        end_index = get_interception_index(response_str, assert_str)['last_index'] + 1

        new_response_value = split_string(response_str)[star_index:end_index]
        new_assert_value = split_string(assert_str)

        return (replace_list_chars_structure(new_response_value,new_assert_value))

    elif get_interception_index(response_str, assert_str).__contains__('first_index'):
        '''
        处理只有第一个值匹配，返回匹配列表
        '''
        return replace_list_chars_structure(
            response_list=split_string(response_str)[get_interception_index(response_str, assert_str)['first_index']:][
                          :len(assert_str.split(','))],
            assert_value=split_string(assert_str))

    elif get_interception_index(response_str, assert_str).__contains__('last_index'):

        '''
        处理只有最后一个值匹配，返回匹配列表
        '''

        return replace_list_chars_structure(response_list=split_string(response_str)[
                                                          :get_interception_index(response_str, assert_str)[
                                                               'last_index'] + 1][-len(assert_str.split(',')):],
                                            assert_value=split_string(assert_str))

def split_string(string: str):
    '''
    删除空格
    :param string:
    :return:
    '''
    return string.replace(' ', '').split(',')

def rem_special_chars(string: str):
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

def get_interception_index(response_str: str, find_value: str):
    '''
    获取返回值列表截取下标
    :return:
    '''

    rep_li = rem_special_chars(response_str).split(',')
    find_value_li = rem_special_chars(find_value).split(',')

    find_value_first = find_value_li[0]
    find_value_last = find_value_li[-1]

    first_index = -1
    last_index = -1

    if len(rep_li) == 0:

        print('后台返回值为空',rep_li)

        return {}

    if rep_li.count(find_value_first) and rep_li.count(find_value_last):

        first_index = rep_li.index(find_value_first)
        last_index = rep_li.index(find_value_last)

    elif rep_li.count(find_value_first):
    
        first_index = rep_li.index(find_value_first)
        
    elif rep_li.count(find_value_last):
    
        last_index = rep_li.index(find_value_last)

    if first_index != -1 and last_index != -1:

        return {'first_index':first_index,
                'last_index':last_index}
    
    elif first_index != -1:
        
        return {'first_index': first_index}
    
    elif last_index != -1:
        
        return {'last_index': last_index}

def replace_list_chars_structure(response_list: list, assert_value: list):
    '''
    替换最外围数据结构，以断言值为准
    :param response_list: 接口返回值截取列表
    :param assert_value: 断言数据列表
    :return:
    '''
    # 长度为1的时候下标取值-1和0其实是一个值，

    assert_first_value = iter(get_first_chars_index(assert_value[0]).keys()).__next__()[
                         :iter(get_first_chars_index(assert_value[0]).values()).__next__()]

    assert_last_value = iter(get_last_chars_index(assert_value[-1]).keys()).__next__()[
                        iter(get_last_chars_index(assert_value[-1]).values()).__next__():]

    rep_first_value = assert_first_value + iter(get_first_chars_index(response_list[0]).keys()).__next__()[
                                           iter(get_first_chars_index(response_list[0]).values()).__next__():]
    
    if iter(get_last_chars_index(response_list[-1]).values()).__next__() == -1:

        rep_last_value = iter(get_last_chars_index(response_list[-1]).keys()).__next__() + assert_last_value

    else:

        rep_last_value = iter(get_last_chars_index(response_list[-1]).keys()).__next__()[
                         :iter(get_last_chars_index(response_list[-1]).values()).__next__()] + assert_last_value

    t = response_list[0].split(':')
    t[0] = rep_first_value
    v = ':'.join(t)
    response_list[0] = v
    s = response_list[-1].split(':')
    s[-1] = rep_last_value
    q = ':'.join(s)

    response_list[-1] = q

    return response_list

def get_first_chars_index(first_chars: str):
    '''
    从右边开始查找中括号大括号下标
    :param first_chars:
    :return:
    '''

    key = first_chars.split(':')[0]
    brace_index = key.rfind('{')
    brackets_index = key.rfind('[')

    return {key: max(brace_index, brackets_index) + 1}

def get_last_chars_index(last_chars: str):
    '''
    从左边开始查找查找中括号大括号下标
    :param last_chars:
    :return:
    '''

    key = last_chars.split(':')[-1]

    brace_index = key.find('}')
    brackets_index = key.find(']')

    if brace_index != -1 and brackets_index != -1:

        index = min(brace_index, brackets_index)

    elif brackets_index == -1:

        index = brace_index

    elif brace_index == -1:

        index = brackets_index

    return {key: index}

def singleton_assert_value(response_str: str, assert_str: str):
    '''
    截取返回值单个值*****好像过度封装了
    :param response_str:
    :param assert_str:
    :return:
    '''
    temp_list = []
    response_list = rem_special_chars(response_str).split(':')
    assert_list = rem_special_chars(assert_str).split(':')

    for value in response_list:

       for v in str(value).split(','):

           temp_list.append(v)

    if temp_list.count(assert_list[0]) and temp_list.count(assert_list[-1]):

        return temp_list[temp_list.index(assert_list[0]):temp_list.index(assert_list[-1]) + 1]

    elif temp_list.count(assert_list[0]):

        return temp_list[temp_list.index(assert_list[0]):temp_list.index(assert_list[0]) + 2]


def rem_skip_assert_value(rm_list:list,ignore_key:str):
    '''
    删除列表忽略key
    :param rm_list: 忽略list
    :param ignore_key: 忽略key
    :return:
    '''
    for index,value in enumerate(rm_list):

        if str(value).count(ignore_key):

            rm_list[index] = value[:str(value).index(ignore_key)-1]

    return rm_list


if __name__ == '__main__':

    response_data = json.dumps({
        "rtn": 0,
        "data": {
            "list": [
                {
                    "sk": "c2105c81",
                    "scheduleId": 1440242384,
                    "boxName": "\u4fa8\u9999\u5e97",
                    "month": "2019-12",
                    "className": "BODYJAM\u683c\u83b1\u7f8e\u821e\u8e48",
                    "boxId": 1006,
                    "scheduleDate": "2019-12-24",
                    "startTime": "2019-12-24 15:10:00",
                    "endTime": "2019-12-24 15:15:00",
                    "workoutMins": 6.0,
                    "background": "https://img.supermonkey.com.cn/class/5065/200.jpg/first.jpg",
                    "trainerStageName": "\u6de1\u6de1",
                    "maxHR": 84,
                    "calories": 16,
                    "isBestKcal": 0,
                    "averageHR": 77,
                    "classImage": "https://img.supermonkey.com.cn/class/5065/200.jpg/first.jpg",
                    "trainerHead": "https://img.supermonkey.com.cn/trainer/1890241/1553655799992.jpeg",
                    "trainerUserId": 0
                },
                {
                    "sk": "55c5d4b7",
                    "scheduleId": 1440242383,
                    "boxName": "\u4fa8\u9999\u5e97",
                    "month": "2019-12",
                    "className": "TRX\u6d77\u8c79\u7a81\u51fb\u961f(For Running) ",
                    "boxId": 1006,
                    "scheduleDate": "2019-12-24",
                    "startTime": "2019-12-24 14:25:00",
                    "endTime": "2019-12-24 14:30:00",
                    "workoutMins": 5.0,
                    "background": "https://img.supermonkey.com.cn/class/5065/200.jpg/first.jpg",
                    "trainerStageName": "\u6de1\u6de1",
                    "maxHR": 84,
                    "calories": 16,
                    "isBestKcal": 0,
                    "averageHR": 77,
                    "classImage": "https://img.supermonkey.com.cn/class/5000/200.jpg/first.jpg",
                    "trainerHead": "https://img.supermonkey.com.cn/trainer/2581349/1574065125525.jpeg",
                    "trainerUserId": 0
                }
            ]
        }
    },ensure_ascii=False)
    assert_data = json.dumps({"data":
                                       {
                                            "list": [
                                                        {
                                                            "sk": "c2105c81",
                                                            "scheduleId": 1440242384,
                                                            "boxName": "\u4fa8\u9999\u5e97",
                                                            "month": "2019-12"
                                                        }
                                                     ]
                                       }
                            },ensure_ascii=False)
   


