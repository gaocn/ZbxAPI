# coding: utf-8

################################
# Date:    2017/10/30
# Author:  govind
################################

from service.hostsfactory import HostsFactory
from service.screenfactory import ScreenFactory


if __name__ == '__main__':
    url = 'http://10.233.87.54:9090'
    user = 'admin'
    passwd = 'zabbix'
    template_name = 'ulog_system_stats_template_zbx20'

    NginxServers = ['10.233.87.54']
    EsServers = ['10.230.135.126', '10.230.135.127', '10.230.135.128']
    # collectors '10.230.146.162', '10.230.146.163'的网口不是 eth0，导致错误
    CollectorServers = ['10.233.86.204', '10.233.86.205']
    IndexerServers = ['10.233.81.118', '10.233.81.208', '10.230.136.177']
    KafkaServers = ['10.230.135.124', '10.230.135.125', '10.230.134.225', '10.230.134.226']

    group_name = 'NginxServers'

    screen_proxy = ScreenFactory(url, user, passwd)
    host_proxy = HostsFactory(url, user, passwd, template_name=template_name)

    host_proxy .create_host_link_template(hosts=NginxServers, group_name=group_name)
    screen_proxy.create_screen(hosts=NginxServers, group_name=group_name)

