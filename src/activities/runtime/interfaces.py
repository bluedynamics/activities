# -*- coding: utf-8 -*-
#
# Copyright 2009: Johannes Raggam, BlueDynamics Alliance
#                 http://bluedynamics.com
# GNU Lesser General Public License Version 2 or later

__author__ = """Johannes Raggam <johannes@raggam.co.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import Attribute

"""Literature:
[1] OMG Unified Modeling LanguageTM (OMG UML), Superstructure. Version 2.2.
[2] The Unified Modeling Language Reference Manual Second Edition.
    James Rumbaugh, Ivar Jacobson, Grady Booch. Addison-Wesley, 2005
"""


class IToken(Interface):
    """The presence of a locus of control, including possible data values, during
    the execution of an activity. ([2], pg. 644)

    There is no specification of a token-concept in [1].
    """
    data = Attribute(
        u'Optional data payload of token.'
    )
    lock = Attribute(
        u'Boolean flag for temporary lock.'
        u"""Indicates if Token was just created and cannot be manipulated in
        current step. We don't want the machine to run too fast."""
    )
    edge_uuid = Attribute(
        u'The uuid of the edge where token sits on.'
    )


class ITokenPool(Interface):
    """A list holding all Tokens the runtime.
    """

class ITokenFilter(Interface):
    """Returns all tokens to a given edge
    """

class IActivityRuntime(Interface):
    """Activity Model Runtime Engine for Python, AMREP.
    """
    activity = Attribute(u'The activity model to operate on.')
    token_pool = Attribute(u'A list, holding the tokens which are produced.')

    def start(data=None):
        """Begins model traversing.
        Finds all IInitialNodes and create tokens for them.
        If tokens are present, the activity is active and cannot be started.
        """
        data = Attribite(
            u"""Data to initialize tokens.
            Compare to ActivityInputParameter"""
        )

    def next():
        """Next iteration.
        Returns possible output parameters.
        """

    def stop():
        """Stops an activity, deleting all tokens from token_pool.
        """

    def print_token_state():
        """Prints the token state to the console for debugging purposes.
        """

# TODO: check if dict / IFullMapping makes sense here
#from zope.interface.common.mapping import IFullMapping
#class IActionInfo(IFullMapping):
class IActionInfo(Interface):
    action_uuid = Attribute(
        u"""uuid of acton"""
    )
    context = Attribute(
        u"""The acton's context respectively the activity's context"""
    )

class ITaggedValueDict(Interface):
    u"""Dictionary of taggedvalues.
    Key = TaggedValue.__name__, value = TaggedValue.value
    """


class IExecution(Interface):

    name = Attribute(
        u"""Name under which execution will be registered as utility"""
    )
    def __call__(action_info, tgv_dict, data):
        """
        @return: None -> asynchronous, data-> synchronous
        """
