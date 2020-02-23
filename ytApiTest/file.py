#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 22:21
# Author : fyt
# File   : file.py

import os

def create_data_file():

    response_path = './dataFile'

    if not os.path.isdir(response_path):

       os.makedirs(response_path)

       with open(response_path + os.sep + 'response.json','w+') as json_file:

           json_file.write('{}')

    return response_path + os.sep + 'response.json'


def find_obj_yaml_file():

    for dirpath, dirnames, filenames in os.walk('./'):
        if len(filenames):
           for index ,file_name in enumerate(filenames):
               if bool(os.path.splitext(file_name).count('.yaml')):
                   return os.path.join(dirpath,file_name)

    return None


if __name__ == '__main__':
    import pytest

    def data():
        return {"key":"value"}

    @pytest.mark.parametrize('dic',data())



    def test_dic(dic):
        print(dic)

