#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\nodes\atom.py
from nodegraph.common.nodes.action import ActionNode
from nodegraph.common.nodes.event import EventNode
from nodegraph.common.nodes.getter import GetterNode
from nodegraph.common.nodes.validation import ValidationNode
from nodegraph.client.actions import get_atom_action_class
from nodegraph.client.events import get_atom_event_class
from nodegraph.client.getters import get_atom_getter_class
from nodegraph.client.conditions import get_atom_condition_class

class ClientActionNode(ActionNode):

    @classmethod
    def get_atom_class(cls, atom_id):
        return get_atom_action_class(atom_id)


class ClientEventNode(EventNode):

    @classmethod
    def get_atom_class(cls, atom_id):
        return get_atom_event_class(atom_id)


class ClientGetterNode(GetterNode):

    @classmethod
    def get_atom_class(cls, atom_id):
        return get_atom_getter_class(atom_id)


class ClientValidationNode(ValidationNode):

    @classmethod
    def get_atom_class(cls, atom_id):
        return get_atom_condition_class(atom_id)
