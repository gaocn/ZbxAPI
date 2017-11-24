# coding: utf-8

################################
# Date:    2017/10/30
# Author:  govind
################################

from service.hostsfactory import HostsFactory
from service.screenfactory import ScreenFactory
from service.actionsfactory import ActionsFactory
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

        self.screen_proxy = ScreenFactory(url, user, password)
        self.host_proxy = HostsFactory(url, user, password, template_name)
        self.action_proxy = ActionsFactory(url, user, password)

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
    # hsc.auto_creator()
    hsc.auto_create_action()
    # hsc.auto_creator(file='data/conf_product_monitores.json')
    # hsc.auto_creator(file='data/conf_product_ulog.json')
    # hsc.auto_creator(file='data/conf_product_ulog2.json')
    # hsc.auto_creator(file='data/conf_product_others.json')
    # hsc.auto_creator(file='data/conf_product_win.json')

