#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:22
# Author : fyt
# File   : apiAssert.py

from urllib import parse
import operator, json, re, requests

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


def fmt_assert_info(body, assertValue, differenceValue):
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
               'InterfaceInfo: {interfaceInfo}\n\n' \
               'assertValue: {assertValue}'.format(errorInfo=differenceValue,
                                                   interfaceInfo=interface_info,
                                                   assertValue='')

        apiReq.send_ding_talk_info(title='接口断言失败',
                                   text=info)
        return info
    else:
        return None


def assert_url_code(body, assertValue):
    '''
    断言请求状态
    :return:
    '''

    assert operator.eq(body.status_code, assertValue), fmt_assert_info(body, assertValue, '状态码不等于200')


def assert_body_include_value(body=None, assertValue=None):
    '''
    断言body 是否包含 value
    :return:
    '''
    if body == None and assertValue == None:
        return

    body_str = json.dumps(parsingData.parser_response(body), ensure_ascii=False)
    assert_str = json.dumps(assertValue, ensure_ascii=False)
    if len(assert_str.split(',')) == 1:
        assert remove_special_characters(body_str).split(',').count(
            remove_special_characters(assert_str).split(',')[0]), fmt_assert_info(body, assertValue, assert_str)

        return

    matching_value = find_response_assert_value(assert_value=assert_str,
                                                response_value=body_str)
    if operator.eq(None, matching_value):
        assert_error_info(fmt_assert_info(body, assertValue, '返回值不包含断言数据'))
        print('找不到断言数据', matching_value)
        return assert_error_info('返回值不包含断言数据')
    response_str_set = set(matching_value)
    assert_str_set = set(assert_str.replace(' ', '').split(','))
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

    body_str = remove_special_characters(json.dumps(parsingData.parser_response(body), ensure_ascii=False))
    assert_str = remove_special_characters(json.dumps(assertValue, ensure_ascii=False))

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
            body = requests.get(remove_special_characters(url), verify=False)
            error_info = {url: body.status_code}
            assert operator.eq(body.status_code, 200), fmt_assert_info(differenceValue=error_info,
                                                                       body=response,
                                                                       assertValue=200)


def splice_regula_expression(dic):
    '''
    生成匹配断言正则表达式
    :param dic: 断言数据
    :return:
    '''

    if isinstance(dic, dict):
        assert_data_str = remove_special_characters(json.dumps(dic, ensure_ascii=False))
        ex_star_str = assert_data_str[:assert_data_str.find(':')]
        ex_end_str = assert_data_str[assert_data_str.rfind(':'):]
        pattern = ex_star_str + '.*' + ex_end_str

        return pattern


def remove_special_characters(string):
    '''
    删除特殊字符{,[,],}
    :param string:
    :return:
    '''
    if isinstance(string, str):
        return string.replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace(' ', '')


def interception_json_assert_value(assert_value_str: str, response_str: str):
    response_str = response_str[1:-1]

    if assert_value_str.endswith("]}"):

        sta_str = assert_value_str[:assert_value_str.index(':')].replace('{', '')
        end_str = str(assert_value_str[assert_value_str.rfind(',') + 1:]).replace('}', '')

        if operator.ne(response_str.find(sta_str), -1) and operator.ne(response_str.find(end_str), -1):
            value = response_str[response_str.index(sta_str):response_str.index(end_str) + len(end_str)]

            return value

    else:

        sta_str = assert_value_str[:assert_value_str.index(':')].replace('{', '')
        end_str = str(assert_value_str[:assert_value_str.rfind(':') + 1]).replace('}', '')
        end_str = end_str[end_str.rfind(',') + 1:]

        if operator.ne(response_str.find(sta_str), -1) and operator.ne(response_str.find(end_str), -1):
            end_str_index = response_str.index(',', response_str.index(end_str))
            sta_str_index = response_str.index(sta_str)

            return response_str[sta_str_index:end_str_index]


def find_response_assert_value(assert_value: str, response_value: str):

    response_value_list = response_value.translate(response_value.maketrans('{}[]', '    ')).replace(' ', '').split(',')

    assert_value_list = assert_value.translate(response_value.maketrans('{}[]', '    ')).replace(' ', '').split(',')

    start_str = assert_value_list[0]
    end_str = assert_value_list[-1]

    try:

        if response_value_list.count(start_str) and response_value_list.count(end_str):
            # 处理头尾都存在情况
            start_str_index = response_value_list.index(start_str)
            end_str_index = response_value_list.index(end_str)

            interception_list_response_value = response_value.split(',')[start_str_index:end_str_index + 1]
            cutting_value = assert_value.split(',')
            replace_first_value = interception_colon_before_value(cutting_value[0])
            new_interception_list_response_first_value = interception_list_response_value[0].replace(
                interception_colon_before_value(interception_list_response_value[0]), replace_first_value)
            new_interception_list_response_last_value = interception_list_response_value[-1].replace(
                interception_colon_before_value(interception_list_response_value[-1], True),
                interception_colon_before_value(cutting_value[-1], True))

            interception_list_response_value[0] = new_interception_list_response_first_value
            interception_list_response_value[-1] = new_interception_list_response_last_value
            interception_list_response_value = [v.replace(' ', '') for v in interception_list_response_value]
            return interception_list_response_value

        elif response_value_list.count(start_str) and not response_value_list.count(end_str):
            # 处理只有头部匹配情况

            interception_list_response_value = ','.join(
                response_value.replace(' ', '').split(',')[response_value_list.index(start_str) + 1:])[
                                               :len(','.join(assert_value.replace(' ', '').split(',')[1:]))].split(',')
            interception_list_response_value.insert(0, assert_value.split(',')[0])

            if assert_value.split(',')[-1].find(':') != -1:
                interception_list_response_value[-1] = interception_list_last_special_chars(
                    assert_value.split(',')[-1].split(':')[-1], interception_list_response_value[-1])
            else:
                interception_list_response_value[-1] = interception_list_last_special_chars(assert_value.split(',')[-1],
                                                                                            interception_list_response_value[
                                                                                                -1])

            return interception_list_response_value

        elif not response_value_list.count(start_str) and response_value_list.count(end_str):
            # 处理只有头部匹配情况

            interception_response_value = ','.join(
                response_value.replace(' ', '').split(',')[:response_value_list.index(end_str)])

            interception_list_response_value = ('{' + interception_response_value[(len(
                interception_response_value) - len(','.join(assert_value.replace(' ', '').split(',')[:-1]))):]).split(
                ',')

            interception_list_response_value.insert(len(interception_list_response_value),
                                                    assert_value.replace(' ', '').split(',')[-1])

            interception_list_response_value[0] = interception_list_first_special_chars(
                assert_first_value=assert_value.split(',')[0],
                response_first_value=interception_list_response_value[0])
            interception_list_response_value = [v.replace(' ', '') for v in interception_list_response_value]
            return interception_list_response_value

    except ValueError as e:
        print(e)


def interception_list_last_special_chars(assert_last_value: str, response_lase_value: str):
    one_index = assert_last_value.find('}')
    two_index = assert_last_value.find(']')

    if one_index != -1 and two_index != -1:

        value = assert_last_value[one_index if one_index < two_index else two_index:]
        response_lase_value = response_lase_value.translate(response_lase_value.maketrans('{}[]', '    ')).replace(' ',
                                                                                                                   '')

        return response_lase_value.translate(response_lase_value.maketrans('{}[]', '    ')).replace(' ', '') + value

    elif one_index == -1:

        value = assert_last_value[two_index:]

        return response_lase_value.translate(response_lase_value.maketrans('{}[]', '    ')).replace(' ', '') + value

    elif two_index == -1:

        value = assert_last_value[one_index:]

        return response_lase_value.translate(response_lase_value.maketrans('{}[]', '    ')).replace(' ', '') + value


def special_last_chars_index(chars: str):

    split_value = chars.split(':')[1]
    one_index = split_value.find('}')
    two_index = split_value.find(']')
    index = one_index if one_index > two_index else two_index

    return index - 1


def interception_list_first_special_chars(assert_first_value: str, response_first_value: str):
    return assert_first_value[:special_chars_index(assert_first_value)] + response_first_value[
                                                                          special_chars_index(response_first_value):]


def special_chars_index(chars: str):
    split_value = chars.split(':')[0]
    one_index = split_value.rfind('{')
    two_index = split_value.rfind('[')
    index = one_index if one_index > two_index else two_index

    return index + 1


def interception_colon_before_value(interception_value: str, is_last=False):
    if is_last:
        return interception_value[interception_value.rfind(':'):]

    return interception_value[:interception_value.rfind(':')]


if __name__ == '__main__':
    s = '{{"userExtInfo":{"userId":2661076'
    a = '{"userExtInfo":{"userId":2661076'
    print(interception_list_first_special_chars(s, a))
