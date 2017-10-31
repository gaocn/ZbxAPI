# coding: utf-8

################################
# Date:    2017/10/18
# Author:  govind
################################

from exception.e3cexceptions import E3CZbxException
from zbx.zbxapi import ZabbixAPI


class HostsFactory(object):
    """
      used to create  host and  link  host  object to a  specific template
    """

    def __init__(self, url, username, password, template_name='', group='', hosts=[]):
        self.__url = url
        self.__username = username
        self.__password = password
        if template_name != '':
            self.__template = template_name
        if group != '':
            self.__group = group
        if len(hosts) != 0:
            self.__hosts = hosts
        if url and username and password:
            self.__zapi = ZabbixAPI(url, username, password)
            self.__zapi.login()
            print('[HostsFactory] user is login')

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
            raise E3CZbxException('there is no template named "%s"' % self.__template)

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
            if 'exists' in e.__str__():
                print('[SUCCESS] existed host: %s' % (host))
            else:
                raise E3CZbxException(e)

    def create_host_link_template(self, hosts=[], template_name='', group_name=''):
        """
        create hosts according to @self.hosts and link host to @self.__template
        :return:
        """
        # initialize parameters
        if template_name != '':
            self.__template = template_name
        if group_name != '':
            self.__group = group_name
        if len(hosts) != 0:
            self.__hosts = hosts

        templateid = self.get_template_id()
        try:
            groupid = self.create_group(self.__group)
        except E3CZbxException:
            groupid = self.get_hostgroup_id(self.__group)

        for host in self.__hosts:
            self.__create_host_helper(host, templateid, groupid)

if __name__ == "__main__":
    pass
    # NginxServer = ['10.233.87.54']
    # template_name = 'ulog_system_stats_template_zbx20'
    #
    # host = HostsFactory('http://10.233.87.54:9090', 'admin', 'zabbix', template_name,
    #                     'Nginx Servers', ['10.233.87.54'])
    # host.create_host_link_template()
    #
    # EsServers = ['10.230.135.126', '10.230.135.127', '10.230.135.128']
    # CollectorServers = ['10.233.86.204', '10.233.86.205', '10.230.146.162', '10.230.146.163']
    # IndexerServers = ['10.233.81.118', '10.230.141.118', '10.233.81.208', '10.230.136.177']
    # KafkaServers = ['10.230.135.124', '10.230.135.125', '10.230.134.225', '10.230.134.226']

    # host.create_host_link_template(hosts=EsServers, group_name="Elasticsearch Servers")
    # host.create_host_link_template(hosts=CollectorServers, group_name="Collector Servers")
    # host.create_host_link_template(hosts=IndexerServers, group_name="Indexer Servers")
    # host.create_host_link_template(hosts=KafkaServers, group_name="Kafka Servers")