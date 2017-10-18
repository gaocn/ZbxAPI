# coding: utf-8

################################
# Date:    2017/10/18
# Author:  govind
################################

from zbxapi import ZabbixAPI
from exception.ZbxException import E3CZbxException


class HostsFactory(object):
    """
      used to create  host and  link  host  object to a  specific template
    """

    def __init__(self, url, username, password, template_name, group, hosts):
        self.__url = url
        self.__username = username
        self.__password = password
        self.__template = template_name
        self.__hosts = hosts
        self.__group = group
        if url and username and password:
            self.__zapi = ZabbixAPI(url, username, password)
            self.__zapi.login()
            print('user is login')

    def get_hostgroup_id(self, group_name):
        params = {
            "filter": {
                "name": group_name
            }
        }
        result = self.__zapi.hostgroup.get(params)
        # print(result)
        if result:
            return result[0]['groupid']
        else:
            raise E3CZbxException('There is no group named: %s' % group_name)

    def create_group(self, group_name):
        """
          create host group and return groupid
        :param group_name:
        :return:
        """
        params = {
            "name": group_name
        }
        result = self.__zapi.hostgroup.create(params)
        if len(result['groupids']) == 1:
            print("[SUCCESS] create hostgroup: %s(groupid=%s)" % (group_name, result['groupids'][0]))
            return result['groupids'][0]
        else:
            raise E3CZbxException('there are more than one groups')

    def get_template_id(self):
        var = self.__zapi.template.get({
            "output": [
                "hostid",
                "name"
            ],
            "filter": {
                "name": [
                    self.__template
                ]
            }

        })
        if var:
            return var[0]['templateid']
        else:
            raise ZbxException('there is no template named "%s"' % self.__template)

    def __create_host_helper(self, host, templateid, groupid):
        params = {
            "host": host,
            "name": host,
            "interfaces": [
                {
                    "type": 1,
                    "main": 1,
                    "useip": 1,
                    "ip": host,
                    "dns": "",
                    "port": "10050"
                }
            ],
            "groups": [
                {
                    "groupid": groupid
                }
            ],
            "templates": [
                {
                    "templateid": templateid
                }
            ]
        }
        # print(params)
        try:
            result = self.__zapi.host.create(params)
            print('[SUCCESS] create host: %s (hostid=%s) and link to template: %s' % (host, result['hostids'], self.__template))
        except E3CZbxException as e:
            print(e)

    def create_host_link_template(self):
        """
        create hosts according to @self.hosts and link host to @self.__template
        :return:
        """
        templateid = self.get_template_id()
        try:
            groupid = self.create_group(self.__group)
        except E3CZbxException:
            groupid = self.get_hostgroup_id(self.__group)

        for host in self.__hosts:
            self.__create_host_helper(host, templateid, groupid)


if __name__ == "__main__":
    host = HostsFactory('http://10.233.87.241', 'admin', 'zabbix', 'ulog_system_stats_template',
                        'zbx_zpi', ['10.230.235.184'])
    host.create_host_link_template()