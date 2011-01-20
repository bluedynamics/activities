from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility
import activities.tokens # registers multiadapter

from node.ext.uml.interfaces import IAction
from node.ext.uml.interfaces import IActivity
from node.ext.uml.interfaces import IActivityEdge
from node.ext.uml.interfaces import IActivityFinalNode
from node.ext.uml.interfaces import IDecisionNode
from node.ext.uml.interfaces import IFinalNode
from node.ext.uml.interfaces import IForkNode
from node.ext.uml.interfaces import IInitialNode
from node.ext.uml.interfaces import IMergeNode
from node.ext.uml.interfaces import IStereotype
from node.ext.uml.interfaces import ITaggedValue

from activities.interfaces import IActionInfo
from activities.interfaces import IActivityRuntime
from activities.interfaces import IExecution
from activities.interfaces import ITaggedValueDict
from activities.interfaces import IToken
from activities.interfaces import ITokenFilter

from activities.interfaces import ActivityRuntimeError
from activities.tokens import Token
from activities.tokens import TokenPool

import logging
log = logging.getLogger('activities')

class ActivityRuntime(object):
    implements(IActivityRuntime)

    def __init__(self, activity):
        try:
            assert(IActivity.providedBy(activity))
        except AssertionError:
            raise ActivityRuntimeError,\
                  " ActivityRuntime must be initialized with an Activity instance"

        self.activity = activity
        self.token_pool = TokenPool()

    def start(self, data=None):
        try:
            assert(len(self.token_pool) == 0)
        except AssertionError:
            raise ActivityRuntimeError,\
                  "A active activity cannot be re-started."

        self._eval_constraints(self.activity.preconditions, data)

        for profile in self.activity.package.profiles:
            # Importing executions associated with model
            # Imported modules are not available because they are not bound
            # to a variable. but we just want to execute modules and register
            # utilities here.
            __import__(profile.__name__)

        # TODO: check guard conditions for outgoing_nodes here?
        for node in self.activity.filtereditems(IInitialNode):
            for edge in node.outgoing_edges:
                self._create_token(edge, data)
        self._unlock_token()

    def stop(self):
        log.info('stopping activity')
        del self.token_pool[:]

    def next(self):
        data_output = {}
        do_stop = False
        for node in self.activity.nodes:
            # TODO: if node is still executing (and may not be a reentrant or
            # so), don't let it execute again. only needed for asyn behavior

            # InitialNode only considered at runtime-start
            if IInitialNode.providedBy(node):
                continue

            ### Is node executable?
            is_merge_node = IMergeNode.providedBy(node)
            can_execute = not is_merge_node # TODO: i don't like this construct
            for edge in node.incoming_edges:
                tokens = getMultiAdapter((self.token_pool, edge), ITokenFilter)
                tok = [tk for tk in tokens if not tk.lock]
                if is_merge_node:
                    # merge behavior: any token on any edge fires node
                    can_execute = can_execute or tok
                else:
                    # implicit and explicit synchronisation (join, et. al):
                    # only when all tokens are present, node is fired.
                    can_execute = can_execute and tok
            if not can_execute:
                continue

            ### Getting and destroying tokens and merging data
            data = {}
            for edge in node.incoming_edges:
                tokens = getMultiAdapter((self.token_pool, edge), ITokenFilter)
                for token in tokens:
                    if token.lock:
                        # don't manipulate locked tokens (in case of IMergeNode)
                        continue

                    # merge the token's data
                    data = self._merge_data(data, token.data)

                    # when nodes execute, tokens are deleted
                    self.token_pool.remove(token)

            ### Executing actions
            do_set_tokens = True
            if IAction.providedBy(node):
                self._eval_constraints(node.preconditions, data)
                data = self._execute(node, data)
                self._eval_constraints(node.postconditions, data)
                # contract: if data is none, there is async behavior and action
                # is still executing.
                # if data is not none, processing on node can continue
                # TODO: check this contract, formalise and document it.
                do_set_tokens = data is not None
            if not do_set_tokens:
                continue

            # TODO: UML2's MergeNode behavior does not reduce concurrency
            # here the concurrency is reduced if 2 tokens come into the node
            # at a time. THIS SHOULD BE CHANGED...
            ### Setting tokens
            else_branch = None
            for edge in node.outgoing_edges:
                if edge.guard \
                   and not edge.guard == "else" \
                   and not eval(edge.guard, None, data):
                    continue
                elif edge.guard == "else" and else_branch is None:
                    else_branch = edge
                else:
                    else_branch = False
                    # create tokens for outgoing edges
                    self._create_token(edge, data)
                    if IDecisionNode.providedBy(node):
                        # XOR semantic for DecisionNode: only one outgoing edge
                        # can traverse.
                        break

            if IActivityEdge.providedBy(else_branch):
                self._create_token(else_branch, data)

            ### Prepare for FinalNode if so
            # Collecting data from tokens running into IFinalNode
            # TODO: only when reaching IFinalNode data is returned?
            if IFinalNode.providedBy(node):
                data_output = self._merge_data(data_output, data)

            # The activity must be stopped when ActivityFinalNode is reached
            # But let other tokens be processed before. The order in which a
            # Token reaches ActivityFinalNode is not deterministic anyways.
            if IActivityFinalNode.providedBy(node):
                do_stop = True

        # after all nodes processed, unlock the tokens created in this run
        self._unlock_token()

        if do_stop:
            self.stop()

        # TODO: does this really mean that activity is reached it's end or is
        # it just an implicit stop? len(self.token_pool) == 0
        # maybe do_stop should apply here
        # TODO: should token be erased before postconstraints are evaluated?
        # maybe better before, so that tokens are preserved and activity is
        # hindered to stop
        if len(self.token_pool) == 0:
            self._eval_constraints(self.activity.postconditions, data_output)

        if data_output:
            return data_output

    def print_token_state(self):
        for token in self.token_pool:
            print(self.activity.node(token.edge_uuid).__name__
                  + ': '
                  + str(token)
                  + ', data: ' + str(token.data)
            )
    # convinience
    ts = print_token_state

    def _eval_constraints(self, constraints, data=None):
        for constr in constraints:
            try:
                assert(eval(constr.specification, None, data))
            except (NameError, AssertionError):
                raise ActivityRuntimeError,\
                      constr.__class__.__name__ + ' not fulfilled: "' +\
                      constr.specification + '"'

    def _merge_data(self, data_dict, new_data_dict):
        for key in data_dict.keys():
            if key in new_data_dict.keys():
                if data_dict[key] is not new_data_dict[key]:
                    raise ActivityRuntimeError,\
                          """Failed to merge token data:
                          Same key, different values"""
        data_dict.update(new_data_dict)
        return data_dict

    def _unlock_token(self):
        # TOKEN LOCK:
        # locked token's should not be considered for node execution in current
        # step. wait for next step.
        # token lock exist because we want tokens only be passed by one node
        # per step.
        # TOKEN MUST BE UNLOCKED HERE
        for token in self.token_pool:
            token.lock = False

    def _create_token(self, edge, data=None):
        """Helper method to ease token creation.
        """
        # token should not be modified more than once per iteration
        # therefore lock=True
        self.token_pool.append(
            Token(edge_uuid=edge.uuid, data=data, lock=True)
        )

    def _execute(self, action, data):
        action_info = IActionInfo(action)
        for stereotype in action.stereotypes:
            tgv_dict = ITaggedValueDict(stereotype)
            execution = getUtility(IExecution, name=stereotype.__name__)
            data = execution(action_info, tgv_dict, data)

        log.info('executing: "' + action.__name__ + '"')
        return data

    def _receive(self, action_uuid, data=None):
        # create tokens with data for action with uuid
        pass
