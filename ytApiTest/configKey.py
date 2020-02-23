#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-09 21:27
# Author : fyt
# File   : configKey.py

DING_TALK_URL = 'DING_TALK_URL' #钉钉URL
OBJECT_HOST = 'OBJECT_HOST' #项目host
ACCOUNT_URL = 'ACCOUNT_URL' #账号host
ACCOUNT_DATA = 'ACCOUNT_DATA'

class YAML_KEY():
    URL = 'url'
    DES = 'des'
    REQ_DATA = 'req_data'
    ASSERT_DATA = 'ast_data'

if __name__ == '__main__':
    s = '123'
    print(s[s.index('3')+1:])