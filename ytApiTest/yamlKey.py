class YAML_CONFIG_KEY():
    OBJECT_HOST = 'OBJECT_HOST' #项目host ，<dictionary>
    INTERFACE_URL = 'url' # 用例接口路径<string>
    INTERFACE_REQUEST_DATA = 'req_data' #接请求参数 <dictionary>
    INTERFACE_ASSERT_DATA = 'ast_data' #断言参数<dictionary>
    INTERFACE_CASE_DES = 'des' #接口说明
    DING_TALK_URL = 'DING_TALK_URL' #钉钉URL<string>
    INTERFACE_JSON_PATH = 'json_expr' #JSON_PATH表达式<string>
    INTERFACE_ASSERT_DATA_SETUP = 'setup' #用例前置操作
    INTERFACE_REQUEST_DATA_TEARDOWN = 'tearDown' #用例后置操作
    INTERFACE_REQUEST_HEADERS = 'headers' #用例请求头
    INTERFACE_CACHE_UPDATE_DATA = 'CACHE_UPDATE_DATA'
    INTERFACE_CACHE_METHOD = 'method' # 用例请求方法<string>
    INTERFACE_CASE_SLEEP = 'sleep' #用例睡眠时长，单位秒<int>
