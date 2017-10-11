# coding: utf-8

################################
# Date:    2017/9/29
# Author:  govind
################################

from exception.ZbxException import E3CZbxException
import json
import subprocess
import urllib
from urllib import request


class ZabbixAPI(object):
    __zbx_objects = ['Action', 'Alert', 'APIInfo', 'Application', 'DCheck', 'DHost', 'DRule',
                'DService', 'Event', 'Graph', 'Graphitem', 'History', 'Host', 'Hostgroup', 'Image', 'Item',
                'Maintenance', 'Map', 'Mediatype', 'Proxy', 'Screen', 'Script', 'Template', 'Trigger', 'User',
                'Usergroup', 'Usermacro', 'Usermedia']
    __auth = ''
    __id = 0
    _state = {}

    def __new__(cls, *args, **kwargs):
        """
        如果__new__创建的是当前类的实例，会自动调用__init__函数，通过return语句里面调用的__new__函数的第一个参数是cls来保证是
         当前类实例，如果是其他类的类名，那么实际创建返回的就是其他类的实例，其实就不会调用当前类的__init__函数，
         也不会调用其他类的__init__函数。
        :param args:
        :param kwargs:
        :return:
        """
        if cls not in cls._state:
            cls._state[cls] = object.__new__(cls)
        return cls._state[cls]

    def __init__(self, url, user, password):
        self.__url = url.rstrip('/') + '/zabbix/api_jsonrpc.php'
        self.__user = user
        self.__password = password
        self._zabbix_api_object_list = (item.lower() for item in self.__zbx_objects)

    def __getattr__(self, name):
        if name not in self._zabbix_api_object_list:
            raise E3CZbxException('No Such API object: %s' % name)
        if name not in self.__dict__:
            self.__dict__[name] = ZabbixAPIObjectFactory(self, name)
        return self.__dict__[name]

    ####
    # zabbix POST 请求参数封装
    ####
    def json_obj(self, method, params):
        obj = {
               'jsonrpc': '2.0',
               'method': method,
               'params': params,
               'id': self.__id
               }
        if method not in ['user.login', 'apiinfo.version']:
            obj['auth'] = self.__auth
        return json.dumps(obj)

    ####
    #  POST request
    ####
    def post_request(self, json_obj):
        data = bytes(json_obj, 'utf-8')
        headers = {
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'python/zabbix_api'
        }

        req = request.Request(self.__url, data=data, headers=headers)
        opener = request.urlopen(req, timeout=3)
        content = json.loads(opener.read().decode('utf-8'))
        self.__id += 1
        return content

    ####
    # Login related functions
    ####
    def login(self):
        user_info = {'user': self.__user, 'password': self.__password}
        obj = self.json_obj('user.login', user_info)
        try:
            content = self.post_request(obj)
        except urllib.request.HTTPError:
            raise E3CZbxException('Zabbix URL Error')

        try:
            self.__auth = content['result']
        except KeyError as e:
            e = content['error']['data']
            raise E3CZbxException(e)

    def is_login(self):
        return self.__auth != ''

    def __checkAuth__(self):
        if not self.is_login():
            raise E3CZbxException('NOT Logged In')

    ###################
    #  Exposed Zbx API
    ###################
    def get_host_by_hostid(self, hostids):
        if not isinstance(hostids, list):
           hostids = [hostids]
        return []


    ###################
    #  Decorate Method
    ###################
    @staticmethod
    def check_auth(func):
        # print('Check Auth')

        def ret(self, *args):
            self.__checkAuth__()
            return func(self, *args)
        return ret

    @staticmethod
    def post_json(method_name):
        def decorator(func):
            def wrapper(self, params):
                try:
                    content = self.post_request(self.json_obj(method_name, params))
                    return content['result']
                except KeyError as e:
                    e = content['error']['data']
                    raise E3CZbxException(e)
            return wrapper
        return decorator

    @staticmethod
    def zabbix_api_object_method(func):
        # print('Zbx Api Method Invoked')

        def wrapper(self, method_name, params):
            try:
                content = self.post_request(self.json_obj(method_name, params))
                return content['result']
            except KeyError as e:
                e = content['error']['data']
                raise E3CZbxException(e)
        return wrapper


###############
#
##############


class ZabbixAPIObjectFactory(object):
    def __init__(self, zapi, object_name=''):
        self.__zapi = zapi
        self.__object_name = object_name

    def __checkAuth__(self):
        self.__zapi.__checkAuth__()

    def post_request(self, json_obj):
        return self.__zapi.post_request(json_obj)

    def json_obj(self, method, params):
        return self.__zapi.json_obj(method, params)

    def __getattr__(self, method_name):
        """
        在访问对象的method_name属性的时候，如果对象并没有这个相应的属性、方法，那么将会调用这个方法来处理。
        __getattribute__：对于对象的所有特性的访问，都将会调用这个方法来处理（在新式类中才有）
        :param method_name:
        :return:
        """
        def method(params):
            return self.proxy_method('%s.%s' % (self.__object_name, method_name), params)
        return method

    ###############
    #  find method is a wrapper of get
    #  find will create object you want while get doesn't exist
    ################
    def find(self, params, attr_name=None, to_create=False):
        filtered_list = []
        result = self.proxy_method('%s.get' % self.__object_name, {'output': 'extend', 'filter': params})

        if to_create and len(result) == 0:
            result = self.proxy_method('%s.create' % self.__object_name, params)
            return result.values()[0]
        if attr_name is not None:
            for elem in result:
                filtered_list.append(elem[attr_name])
            return filtered_list
        else:
            return result

    @ZabbixAPI.check_auth
    @ZabbixAPI.zabbix_api_object_method
    def proxy_method(self, method, params):
        """
        装饰器自上而下执行，首先检查用户是否登录，然后在执行下面的zbx api 操作。
        装饰器的调用顺序与使用 @ 语法糖声明的顺序相反。
        :param method:
        :param params:
        :return:
        """
        pass

if __name__ == '__main__':
    zpi = ZabbixAPI('http://10.233.87.241', 'admin', 'zabbix')
    zpi.login()
    #NOTE: zapi.(user、host...)等方法必须在用户登录后才能访问
    # print(zpi.apiinfo.version({}))
    # print(zpi.zabbix.status({'nocache': 'true'}))

    var = zpi.host.get({
        "output": [
            "hostid",
            "host"
        ],
        "selectInterfaces": [
            "interfaceid",
            "ip"
        ]
    })

    print(var)