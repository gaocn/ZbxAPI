# coding: utf-8

################################
# Date:    2017/10/19
# Author:  govind
################################

from exception.e3cexceptions import E3CZbxException
from zbx.zbxapi import ZabbixAPI


class ActionsFactory(object):
    """
    给哪一个IP主机添加Action的流程：
       1. 若zbx中IP对应监控主机不存在，则添加失败
       2. 若zbx中存在监控主机，指定Action的触发器名
          1). 若指定触发器不存在，则添加失败；
          2). 若触发器存在，则指定operation操作（默认是添加Remote Command，因为发送邮件生产环境不支持）
    """
    __SMS_TYPE = ['ESProcess', 'KafkaProcess', 'CollectorProcess', 'IndexerProcess', 'GatewayProcess', 'DiskAlert']

    def valid_check(func):
        def wrapper(*args, **kwargs):
            for key in args:
                if isinstance(key, ActionsFactory):
                    continue
                if key == '':
                    raise E3CZbxException('[ERROR] Positional Argument Can not be null')
            # for key in kwargs:
            #     print(key)
            return func(*args, **kwargs)
        return wrapper

    @valid_check
    def __init__(self, url, username, password, hosts=[], trigger_names=[]):

        self.__url = url
        self.__username = username
        self.__password = password

        self.__zapi = ZabbixAPI(url, username, password)
        self.__zapi.login()
        print('[ActionsFactory] user is login')

        if len(hosts) != 0:
            self.__hosts_ids = self.get_hostids_by_IP(hosts)
        if len(trigger_names) != 0:
            self.__triggers_names = trigger_names

    def __get_hostids_by_IP(self, hosts):
        host_ids = []
        params = {"filter": {"name": "10.230.135.128"}}

        for IP in hosts:
            params['filter']['name'] = IP
            try:
                result = self.__zapi.host.get(params)
                host_ids.append(result[0]['hostid'])
            except IndexError as e:
                print('[WARN] There exists no host(%s) in zabbix' % IP)
        return host_ids

    def __create_action_helper(self, action_name, hostid, trigger_name_like, command, period=3600, step_from=1, step_to=4):
        params = {
            "name": action_name,                # Action名称
            "eventsource": 0,
            "evaltype": 0,
            "status": 0,                        # enable
            "esc_period": period,               # Action执行周期，默认为3600s
            "def_shortdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}",
            "def_longdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}",
            "conditions": [
                {                               # Maintenance status not in "maintenance"
                    "conditiontype": 16,
                    "operator": 7
                },
                {                               # Trigger value = "PROBLEM"
                    "conditiontype": 5,
                    "operator": 0,
                    "value": 1
                },
                {                               # Host = "{hostid}"
                    "conditiontype": 1,
                    "operator": 0,
                    "value": hostid
                },
                {                               # Trigger name like "{trigger_name_like}"
                    "conditiontype": 3,
                    "operator": 2,
                    "value": trigger_name_like
                }
            ],
            "operations": [
                {
                    "operationtype": 1,
                    "esc_step_from": step_from,
                    "esc_step_to": step_to,
                    "evaltype": 0,
                    "opconditions": [
                        {                        # Not Ack
                            "conditiontype": 14,
                            "operator": 0,
                            "value": "0"
                        }
                    ],
                    "opcommand_hst": [          # execute command on current host
                        {
                            "hostid": "0"
                        }
                    ],
                    "opcommand": {
                        "type": 0,
                        "execute_on": 0,
                        "command": command
                    }
                }
            ]
        }
        try:
            result = self.__zapi.trigger.create(params)
            print('[SUCCESS] %s' % result)
        except E3CZbxException as e:
            print(e)

    def create_action(self, action_name, command, hosts=[], trigger_names=[]):
        if len(hosts) != 0:
            self.__hosts_ids = self.get_hostids_by_IP(hosts)
        if len(trigger_names) != 0:
            self.__triggers_names = trigger_names

        for hostid in self.__hosts_ids:
            for trigger_name in self.__triggers_names:
                self.create_action_helper(action_name, hostid, trigger_name, command)


if __name__ == '__main__':
    af = ActionsFactory('http://10.233.87.54:9090', 'admin', 'zabbix', hosts=['10.230.135.12', '10.233.87.54'], trigger_names=['nginx'])
    af.create_action('from zbx api', 'cd ~; ./test.sh')