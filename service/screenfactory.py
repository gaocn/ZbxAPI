# coding: utf-8

################################
# Date:    2017/10/18
# Author:  govind
################################

from zbxapi import ZabbixAPI
from exception.e3cexceptions import E3CZbxException


class ScreenFactory(object):
    """
    used to create  screen for  a group of 'existed hosts' in  Zabbix
    eg:
        for existing hosts: ["10.235.237.1", "10.235.237.2", "10.235.237.3", ...]
        host group: es_servers

        we create a screen named "es_servers_statistics" with dimension "2*4", each of them has following graphs:
               es_servers CPU Stats               es_servers CPU Utilization Stats
               es_servers Memory Stats            es_servers FileSystem Stats
               es_servers Income Net IO Stats     es_servers Outcome Net IO Stats
               es_servers Read Disk IO Stats      es_servers Write Disk IO Stats

        1. check if there exists hosts and  host group
    """
    __items = {
        'CPU_Load': ['system.cpu.load[percpu,avg1]'],
        'CPU_Utilization': ['system.cpu.util[,iowait]', 'system.cpu.util[,user]', 'system.cpu.util[,system]'],
        'Memory': ['vm.memory.size[used]'],
        'Filesystem': ['custom.ulog.fs.stats.used_percent'],
        'Income_Net_IO': ['net.if.in[eth0]', 'custom.if.net.income.bandwidth.util'],
        'Outcome_Net_IO': ['net.if.out[eth0]', 'custom.if.net.outcome.bandwidth.util'],
        'Read_Disk_IO': ['custom.vfs.dev.iostats.rkb'],
        'Write_Disk_IO': ['custom.vfs.dev.iostats.wkb']
    }
    __colors = [
        '1A7C11', 'F63100', '2774A4', 'A54F10', 'FC6EA3', '6C59DC', 'AC8C14', '611F27', 'F230E0', '5CCD18',
        'BB2A02', '5A2B57', '89ABF8', '7EC25C', '274482', '2B5429', '8048B4', 'FD5434', '790E1F', '87AC4D',
        'E89DF4'
    ]
    __color_indicator = 0

    def __get_color(self):
        color = self.__colors[self.__color_indicator]
        self.__color_indicator = (self.__color_indicator + 1) % len(self.__colors)
        return color

    def __init__(self, url, username, password, hosts, hostgroup):
        self.__url = url
        self.__username = username
        self.__password = password
        self.__hosts = hosts
        self.__hostgroup = hostgroup
        if url and username and password:
            self.__zapi = ZabbixAPI(url, username, password)
            self.__zapi.login()
            print('user is login')
            # check if self.__hostgroup exists, if not create it
            self.get_group_id(self.__hostgroup)

    def get_group_id(self, group_name):
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
            print('[Warning]There is no group named: %s, We Create it for you!!!' % group_name)
            self.create_group(self.__hostgroup)

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

    def get_hosts_ids(self):
        hostids = list()
        for host in self.__hosts:
            params = {"output": ["hostid"], "filter": {"host": host}}
            result = self.__zapi.host.get(params)
            try:
                hostids.append(result[0]['hostid'])
            except IndexError:
                raise E3CZbxException('there is no host %s' % host)
        print("[SUCCESS] host ids: %s" % hostids)
        return hostids

    def get_itemid_by_key(self, hostid, key):
        """
        :param hostid:
        :param key:
        :return:
        """
        params = {"output": ["itemid"],  "hostids": hostid, "search": {"key_": key}}
        result = self.__zapi.item.get(params)
        try:
            if len(result) == 1:
                itemid = result[0]['itemid']
                return itemid
            else:
                raise E3CZbxException('There are no item or more than one items(%s) in host(hostid=%s)' % (key, hostid))
        except IndexError:
            raise E3CZbxException('There is no key(%s) in host(hostid=%s)' % (key, hostid))

    def create_graph(self, name, itemids, width=900,  height=400):
        params = {"name": name, "width": width, "height": height, "gitems": []}

        for itemid in itemids:
            conf = {'itemid': itemid, 'color': self.__get_color()}
            params['gitems'].append(conf)
        # print(params)

        result = self.__zapi.graph.create(params)
        print("[SUCCESS] create graph: %s(graphid=%s)" % (name, result['graphids'][0]))
        return result['graphids'][0]

    def create_statistic_graphs(self):
        hostids = self.get_hosts_ids()
        resourceids = []

        for key in self.__items:
            itemids = []
            for item in self.__items[key]:
                for hostid in hostids:
                    itemids.append(self.get_itemid_by_key(hostid, item))
            # print('create_statistic_graphs: ', 'itemids  %s  for hostid=%s' % (itemids, hostid))
            graph_name = '%s %s Stats' % (self.__hostgroup, key)
            resourceids.append(self.create_graph(graph_name, itemids))
        return resourceids

    def create_screen(self, hsize=2, vsize=4):
        screen_name = " %s Statistics" % self.__hostgroup
        params = {
            "name": screen_name,
            "hsize": hsize,
            "vsize": vsize,
            "screenitems": []
        }

        #1. create graphs
        resourceids = self.create_statistic_graphs()

        for y in range(vsize):
            for x in range(hsize):
                screenitem = {
                    "resourcetype": 0,
                    "resourceid": resourceids[2 * y + x],
                    "rowspan": 1,
                    "colspan": 1,
                    "width": 900,
                    "height": 400,
                    "x": x,
                    "y": y
                }
                params['screenitems'].append(screenitem)
        # print(params)

        result = self.__zapi.screen.create(params)
        print("[SUCCESS] create screen: %s(screenid=%s)" % (screen_name, result['screenids'][0]))
        return result['screenids'][0]

    def create_screen_with_params(self, hosts, group_name):
        self.__hosts = hosts
        self.__hostgroup = group_name
        # check if self.__hostgroup exists, if not create it
        self.get_group_id(self.__hostgroup)

        self.create_screen()

if __name__ == '__main__':

    NginxServers = ['10.233.87.54']
    group_name = 'Nginx Servers'
    proxy = ScreenFactory('http://10.233.87.241', 'admin', 'zabbix',
                           NginxServers,
                           group_name)
    # proxy.create_screen()

    EsServers = ['10.230.135.126', '10.230.135.127', '10.230.135.128']
    # collectors '10.230.146.162', '10.230.146.163'的网口不是 eth0，导致错误
    CollectorServers = ['10.233.86.204', '10.233.86.205']
    IndexerServers = ['10.233.81.118', '10.233.81.208', '10.230.136.177']
    KafkaServers = ['10.230.135.124', '10.230.135.125', '10.230.134.225', '10.230.134.226']

    # proxy.create_screen_with_params(EsServers, "Elasticsearch Servers")
    # proxy.create_screen_with_params(CollectorServers, "Collector Servers")
    # proxy.create_screen_with_params(IndexerServers, "Indexer Servers")
    # proxy.create_screen_with_params(KafkaServers, "Kafka Servers")
