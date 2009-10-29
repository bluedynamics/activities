# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

from zope.component import getGlobalSiteManager
from zope.component import adapter, adapts
from zope.interface import implementer, implements

from activities.metamodel.interfaces import IAction
from activities.metamodel.interfaces import IActivityEdge
from activities.metamodel.interfaces import IStereotype

from activities.runtime.interfaces import IActionInfo
from activities.runtime.interfaces import ITaggedValueDict
from activities.runtime.interfaces import IToken
from activities.runtime.interfaces import ITokenFilter
from activities.runtime.interfaces import ITokenPool

import uuid

class Token(object):
    implements(IToken)
    _data = None
    def __init__(self, edge_uuid, data=None, lock=False):
        self.edge_uuid = edge_uuid
        self.data = data
        self.lock = lock # Boolean flag for temporary lock

    def get_data(self):
        return self._data
    def set_data(self, data):
        self._data = {}
        if isinstance(data, dict):
            self._data = data
        elif data is not None:
            if not isinstance(data, list):
                data = [data,]
            for item in data:
                self._data[str(uuid.uuid4())] = item

    data = property(get_data, set_data)


class TokenPool(list):
    """Pool of tokens.
    """
    implements(ITokenPool)


@implementer(ITokenFilter)
@adapter(ITokenPool, IActivityEdge)
def tokenfilter(token_pool, edge):
    """Get ITokens for an given IActivityEdge.
    """
    token_list = [tk for tk in token_pool if tk.edge_uuid == edge.uuid]
    return token_list

class ActionInfo(object):
    implements(IActionInfo)
    adapts(IAction)

    def __init__(self, action):
        self.uuid = action.uuid
        self.context = action.context

class TaggedValueDict(dict):
    implements(ITaggedValueDict)
    adapts(IStereotype)

    def __init__(self, stereotype):
        for tgv in stereotype.taggedvalues:
            self[tgv.__name__] = tgv.value

gsm = getGlobalSiteManager()
gsm.registerAdapter(tokenfilter)
gsm.registerAdapter(ActionInfo)
gsm.registerAdapter(TaggedValueDict)
