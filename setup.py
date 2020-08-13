#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
# Time   : 2020-01-07 19:57
# Author : fyt
# File   : setup.py


from setuptools import setup


def readme_data():
    with open('./README.rst', encoding='utf-8') as f:
        data = f.read()

        return data


setup(
    name='ytApiTest',
    version='1.0.46',
    author='fyt',
    author_email='fangyt@163.com',
    packages=["ytApiTest"],
    install_requires=[
        'PyYAML',
        'requests',
        'jsonpath',
        'DingtalkChatbot',
        'pytest',
        'pytest-parallel',
        'deepdiff',
        'allure-pytest'
    ],
    long_description=readme_data(),
    url='https://github.com/fangyt/ytApiTest.git'
)
