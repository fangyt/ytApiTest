项目介绍
==========================
此扩展包通过读取yaml文件配置接口请求参数
通过GET、POST方法获取接口返回值并断言

安装和使用
============

| 安装命令如下：

::

    pip install ytApiTest

| 支持功能如下：

-  支持 GET 请求
-  支持 POST 请求
-  支持 yaml文件内请求参数或断言数据使用JOSNPATH 语法获取接口返回值
-  支持 断言接口返回值，字段某部分或某个键值对是否存在返回值中
-  支持 断言接口返回值所有字段是否与断言值相等
-  支持 断言失败发送对应错误接口信息到钉钉群

| 使用：

- 使用扩展包项目根目录下必须新建.yaml文件管理测试用例数据
- .yaml文件必须遵循以下格式并包含以下关键字

.. code:: python

    配置钉钉机器人URL
    DING_TALK_URL: https://钉钉机器人URL

    项目host
    OBJECT_HOST: https://object/host


    interface_name(你接口名称,可自己命名):
                                url(接口路径,此关键字必须包含): 值可为空
                                assert_key(断言key,可自己命名):
                                                    des(此关键字必须包含): 用例说明，值可为空,用于断言错误时展示
                                                    req_data(此关键字必须包含): 接口请求参数,值可为空
                                                    ast_data(此关键字必须包含): 接口断言值,值可为空
                                                    json_expr(此关键值必须包含): 返回查找路径,值可为空

- .yaml文件内使用JSONPATH语法示例

.. code:: python


    interface_name:
                    url:
                    assert_key:
                                des:
                                req_data:
                                            key: $.interface_name.data.XXX
                                ast_data:
                                            key: $.interface_name.data.XXX

方法说明及使用示例
======================


.. code:: python

    #POST 请求
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    response = ytApiTest.post(interface_name,assert_key)
    #参数说明：interface_name(.yaml你接口名称),assert_key(.yaml文件内与接口对应的assert_key值)


.. code:: python

    #GET 请求
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送get请求到后台,返回response对象
    response = ytApiTest.get(interface_name,assert_key)
    #参数说明：interface_name(.yaml你接口名称),assert_key(.yaml文件内与接口对应的assert_key值)


.. code:: python

    #获取接口断言数据
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    response = ytApiTest.get_interface_case_assert_data(interface_name,assert_key)
    #参数说明：interface_name(.yaml你接口名称),assert_key(.yaml文件内与接口对应的assert_key值)


.. code:: python

    #获取接口请求数据
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    response = ytApiTest.get_interface_request_data(interface_name,assert_key)
    #参数说明：interface_name(.yaml你接口名称),assert_key(.yaml文件内与接口对应的assert_key值)

.. code:: python

    #获取接口完整URL
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    response = ytApiTest.get_interface_url(interface_name,assert_key)
    #参数说明：interface_name(.yaml你接口名称),assert_key(.yaml文件内与接口对应的assert_key值)

.. code:: python

    #执行相等断言方法
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    ytApiTest.assert_body_eq_assert_value(response,assert_value,json_expr)
    #参数说明：response(接口返回response对象),assert_value(.yaml文件内断言值),json_expr(.yaml文件内json_expr值)


.. code:: python

    #断言返回值中URL状态是否为200方法
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    ytApiTest.assert_response_url_status(response）
    #参数说明：response(接口返回response对象)


.. code:: python

    #修改请求参数
    import ytApiTest
    #读取.yaml文件内对应的接口值并发送post请求到后台,返回response对象
    ytApiTest.update_case_req_data(interface_key=None, assert_key=None,new_request_data=None）
    参数：interface_key=接口名称, assert_key=断言值,req_data=请求字典