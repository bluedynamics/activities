# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

from activities.runtime.interfaces import IExecution
from zope.interface import implements
from zope.component import getGlobalSiteManager

class Execution1(object):
    implements(IExecution)
    name = "execution1"

    def __call__(self, action_info, stereotype_info, data):
        # value of key test is changed
        # rest of data is passed through
        data['test'] = not data['test']
        print "data['test'] = " + str(data['test'])
        return data

class Execution2(object):
    implements(IExecution)
    name = "execution2"

    def __call__(self, action_info, stereotype_info, data):
        # data is replaced
        return {'info': "execution2 has completed"}

gsm = getGlobalSiteManager()
gsm.registerUtility(component=Execution1(), name=Execution1.name)
gsm.registerUtility(component=Execution2(), name=Execution2.name)
