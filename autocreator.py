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

    def __init__(self, file='data/conf.json'):
        with open(file, 'rb') as fd:
            self.conf = json.load(fd)
            self.__init_config()

    def __init_config(self):
        url = self.conf['url']
        user = self.conf['user']
        password = self.conf['password']
        template_name = self.conf['template']

        self.screen_proxy = ScreenFactory(url, user, password)
        self.host_proxy = HostsFactory(url, user, password, template_name)
        self.action_proxy = ActionsFactory(url, user, password)

    def auto_creator(self):
        for key in self.conf['ServerMap']:
            self.host_proxy.create_host_link_template(hosts=self.conf['ServerMap'][key], group_name=key)
            self.screen_proxy.create_screen(hosts=self.conf['ServerMap'][key], group_name=key)
        # create action config
        for item in self.conf['ActionMap']:
            try:
                action = self.conf['ActionMap'][item]
                hosts = self.conf['ServerMap'][item]
                action_name = action['actionName']
                command = action['command']
                trigger_name_pattern = action['triggerNamePattern']
                print(action_name)
                self.action_proxy.create_action(action_name, command, hosts, trigger_name_pattern)
            except KeyError as e:
                print('[ERROR] configuration error for "ActionMap ==>%s"' % item)


if __name__ == '__main__':
    hsc = HostsScreenCreator(file='data/conf.json')
    hsc.auto_creator()

