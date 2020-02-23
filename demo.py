#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-02-23 15:15
# Author : fyt
# File   : demo.py

import ytApiTest


def demo():

    r = ytApiTest.post('getInitInfo','assert_user_info')
    print(r.text)

    r2 = ytApiTest.post('getInitInfo','assert_user_hr_settings')

    print(r2.text)


if __name__ == '__main__':
    demo()