#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-03-18 23:40
# Author : fyt
# File   : apiAssert.py

import requests, jsonpath, operator, json
from deepdiff import DeepDiff

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
        error_info = kwargs.get('error_info')

        title = kwargs.get('title')
        des = self.parsing_data.get_interface_des(interface_name=interface_name,
                                                  assert_name=assert_name)
        response_json = self.parsing_data.parse_response_data(response)
        interface_url = response.url
        if response.request.method == "POST" and response.request.body != None:
            params = json.loads(response.request.body)
        else:
            params = None
        assert_value = kwargs.get('assert_value')
        if operator.eq(assert_value, None):
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
                    'params': params,
                    'headers': headers,
                    'assert_value': assert_value,
                    "error_info": error_info}

        info = '\n TITLE      =   {title}' \
               '\n\n DES        =   {case_des}' \
               '\n\n URL        =   {url}' \
               '\n\n PARAMS     =   {params}' \
               '\n\n JONS_EXPR  =   {json_expr}' \
               '\n\n HEADERS    =   {headers}' \
               '\n\n RESPONSE   =   {response}' \
               '\n\n ASSERTVALUE   =   {assert_value}' \
               '\n\n ERRORINFO  =   {error_info}'.format_map(info_dic)

        self.request.send_case_error_info(error_info=info)

        return info

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
        temp_json_expr = json_expr
        if json_expr.find('/') != -1:
            json_expr = json_expr.split('/')[0]

        find_value = jsonpath.jsonpath(response_json, json_expr)

        if find_value == False:
            return find_value

        if temp_json_expr.find('/') != -1:
            index = int(temp_json_expr.split('/')[-1])
            return find_value[index]
        return find_value

    def assert_include(self, response_data: requests.Response, assert_value, json_expr, **kwargs):
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

                temp_intersection = find_value.intersection(assert_value)

                assert operator.ne(temp_intersection, assert_value), \
                    self.format_interface_send_info(
                        response=response_data,
                        title='包含断言失败',
                        interface_name=interface_name,
                        assert_name=assert_name,
                        find_value=temp_intersection)



        finally:

            self.run_case_request(
                self.parsing_data.get_interface_tear_down_list(interface_name=kwargs.get('interface_name'),
                                                               assert_name=kwargs.get('assert_name')))

    def assert_eq(self, response_data: requests.Response, assert_value, json_expr, **kwargs):
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

            deff = DeepDiff(assert_value, find_value)
            assert not deff, self.format_interface_send_info(response=response_data,
                                                             assert_value=assert_value,
                                                             interface_name=interface_name,
                                                             assert_name=assert_name,
                                                             error_info=deff,
                                                             title='接口返回数据与断言数据不一致')

        finally:
            self.run_case_request(
                self.parsing_data.get_interface_tear_down_list(interface_name=kwargs.get('interface_name'),
                                                               assert_name=kwargs.get('assert_name')))

    def assert_no_in(self, response_data: requests.Response, assert_value, json_expr, **kwargs):
        '''
        不包含
        :param response_data:
        :param assert_value:
        :param json_expr:
        :param kwargs:
        :return:
        '''
        interface_name = kwargs.get('interface_name')
        assert_name = kwargs.get('assert_name')
        find_value = self.find_interface_assert_value(response_data=response_data,
                                                      json_expr=json_expr,
                                                      interface_name=interface_name,
                                                      assert_name=assert_name)
        assert operator.eq(assert_value, find_value), self.format_interface_send_info(response=response_data,
                                                                                      interface_name=interface_name,
                                                                                      assert_name=assert_name)

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
        if response_value is False or assert_value is None:
            assert response_value, self.format_interface_send_info(title='相等断言失败，断言数据与返回数据长度不一致',
                                                                   interface_name=interface_name,
                                                                   assert_name=assert_name,
                                                                   find_value=response_value,
                                                                   response=response,
                                                                   assert_value=assert_value)
        assert operator.eq(len(response_value), len(assert_value)), \
            self.format_interface_send_info(title='相等断言失败，断言数据与返回数据长度不一致',
                                            interface_name=interface_name,
                                            assert_name=assert_name,
                                            find_value=response_value,
                                            response=response,
                                            assert_value=assert_value)

    def compare_json_value(self, find_json, assert_json, **kwargs):
        '''
        递归比较json值
        :param find_json: json_expr 表达式返回值
        :param assert_json: 断言json_value
        :param kwargs:
        :return:
        '''

        if isinstance(assert_json, dict):

            for key, assert_json_dic_value in assert_json.items():
                if type(assert_json_dic_value) != dict and type(assert_json_dic_value) != list:
                    assert operator.eq(assert_json_dic_value, find_json.get(key)), self.format_interface_send_info(
                        response=kwargs.get('response'),
                        interface_name=kwargs.get('interface_name'),
                        assert_name=kwargs.get('assert_name'),
                        title='相等断言失败',
                        assert_value={key: assert_json_dic_value},
                        find_value={key: find_json.get(key)})

                self.compare_json_value(find_json=find_json.get(key),
                                        assert_json=assert_json_dic_value,
                                        interface_name=kwargs.get('interface_name'),
                                        assert_name=kwargs.get('assert_name'),
                                        response=kwargs.get('response'))
        elif isinstance(assert_json, list):

            for index, assert_json_list_value in enumerate(assert_json):

                if type(assert_json_list_value) != dict and type(assert_json_list_value) != list:
                    assert operator.eq(assert_json_list_value, find_json[index]), self.format_interface_send_info(
                        response=kwargs.get('response'),
                        interface_name=kwargs.get('interface_name'),
                        assert_name=kwargs.get('assert_name'),
                        title='相等断言失败',
                        assert_value=assert_json_list_value,
                        find_value=find_json[index])
                self.compare_json_value(find_json=find_json[index],
                                        assert_json=assert_json_list_value,
                                        interface_name=kwargs.get('interface_name'),
                                        assert_name=kwargs.get('assert_name'),
                                        response=kwargs.get('response'))

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
        if request_list == None or len(request_list) == 0:
            return

        for dic in request_list:
            if dic.get('method') == 'get':

                self.request.get(interface_name=dic['interface_name'],
                                  assert_name=dic['assert_name'],
                                  host_key=dic.get('host_key'))

            self.request.post(interface_name=dic['interface_name'],
                                             assert_name=dic['assert_name'],
                                             host_key=dic.get('host_key'))


if __name__ == '__main__':
    pass
