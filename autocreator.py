# coding: utf-8

################################
# Date:    2017/10/30
# Author:  govind
################################

from service.hostsfactory import HostsFactory
from service.screenfactory import ScreenFactory
from service.actionsfactory import ActionsFactory
from exception.e3cexceptions import E3CZbxException
import json


class HostsScreenCreator(object):

    def __init__(self, file):
        with open(file, 'rb') as fd:
            self.conf = json.load(fd)
            self.__init_config()

    def __reconfig(self, file):
        with open(file, 'rb') as fd:
            self.conf = json.load(fd)

    def __init_config(self):
        url = self.conf['url']
        user = self.conf['user']
        password = self.conf['password']
        template_name = self.conf['template']

        self.host_proxy = HostsFactory(url, user, password, template_name)
        self.screen_proxy = ScreenFactory(url, user, password, items=self.__template_to_config(template_name))
        self.action_proxy = ActionsFactory(url, user, password)

    def __template_to_config(self, temlpate_name):
        """
        NOTE: 因为不同机器中的网口可能不同（eth0, eth1, eth2,....),并且不同机器上ES存放数据的挂载点也不相同，因此ScreenFactory.__items
              参数就不能是固定值。为了适应不同主机配置需求，通过对模板名称进行设置来区分不同的主机配置。
              例如：
                    ulog_system_stats_template_zbx20_eth1_sda_home => 解析出：eth1、sda、home三个参数作为ScreenFactory的对应参数
                    ulog_system_stats_template_zbx20_eth2_sdb_nas  => 解析出：eth2、sdb、nas三个参数作为ScreenFactory的对应参数
                    ulog_system_stats_template_zbx20_eth3_sda_san  => 解析出：eth3、sda、san三个参数作为ScreenFactory的对应参数
              将解析出来的三个参数作为ScreenFactory构造函数的参数，用于动态生成ScreenFactoyr.__item的对应监控项的key，进而动态创建Screen。
        :param temlpate_name:
        :return:
        """
        items = temlpate_name.split('_')
        if len(items) < 3:
            raise E3CZbxException('Illegal Template Name!')
        return items[len(items) - 3:]

    def auto_creator(self, file=''):
        if file != '':
            self.__reconfig(file)

        self.auto_create_host()
        self.auto_create_screen()
        self.auto_create_action()

    def auto_create_host(self, file=''):
        if file != '':
            self.__reconfig(file)

        for key in self.conf['ServerMap']:
            self.host_proxy.create_host_link_template(hosts=self.conf['ServerMap'][key], group_name=key)

    def auto_create_screen(self, file=''):
        if file != '':
            self.__reconfig(file)

        for key in self.conf['ServerMap']:
            self.screen_proxy.create_screen(hosts=self.conf['ServerMap'][key], group_name=key)

    def auto_create_action(self, file=''):
        if file != '':
            self.__reconfig(file)

        # create action config
        for item in self.conf['ActionMap']:
            for action in self.conf['ActionMap'][item]:
                try:
                    hosts = self.conf['ServerMap'][item]
                    action_name = action['actionName']
                    command = action['command']
                    trigger_name_pattern = action['triggerNamePattern']
                    # print(action_name)
                    self.action_proxy.create_action(action_name, command, hosts, trigger_name_pattern)
                except KeyError as e:
                    print('[ERROR] configuration error for "ActionMap ==>%s"' % item)

if __name__ == '__main__':
    hsc = HostsScreenCreator(file='data/conf_product_nginx.json')
    hsc.auto_creator()

    # hsc.auto_creator(file='data/conf_product_monitores_es.json')
    # hsc.auto_creator(file='data/conf_product_monitores.json')

    # hsc.auto_creator(file='data/conf_product_ulog_es.json')
    # hsc.auto_creator(file='data/conf_product_ulog.json')

    # hsc.auto_creator(file='data/conf_product_ulog2_es.json')
    # hsc.auto_creator(file='data/conf_product_ulog2.json')

    # hsc.auto_creator(file='data/conf_product_mbank_es.json')
    # hsc.auto_creator(file='data/conf_product_apm_es.json')

