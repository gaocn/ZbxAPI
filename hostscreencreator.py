# coding: utf-8

################################
# Date:    2017/10/30
# Author:  govind
################################

from service.hostsfactory import HostsFactory
from service.screenfactory import ScreenFactory
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

    def auto_creator(self):
        for key in self.conf['ServerMap']:
            self.host_proxy.create_host_link_template(hosts=self.conf['ServerMap'][key], group_name=key)
            self.screen_proxy.create_screen(hosts=self.conf['ServerMap'][key], group_name=key)

if __name__ == '__main__':
    hsc = HostsScreenCreator()
    hsc.auto_creator()

