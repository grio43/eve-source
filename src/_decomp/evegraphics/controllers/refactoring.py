#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\controllers\refactoring.py
import re
import trinity
from . import expressiontree
CAN_REFACTOR = ('CurveSetTime', 'ShipMaxSpeed')

def _FindCalls(node, calls):
    if isinstance(node, (expressiontree.FunctionCall, expressiontree.StringFunctionCall)) and node.name in CAN_REFACTOR:
        calls.add(node)
    else:
        for each in node.GetInputs():
            _FindCalls(each, calls)


class CallInstance(object):
    transition = None
    state = None
    machine = None
    node = None
    ast = None
    label = ''


class RefactorAction(object):
    LEAVE = 0
    SET_AT_START = 1
    SET_AT_SOURCE = 2


class CallGroup(object):
    action = RefactorAction.LEAVE
    variable = ''

    def __init__(self):
        self.calls = []


def CollectFunctionCalls(controller):
    calls = []
    for sm in controller.stateMachines:
        for state in sm.states:
            for transition in state.transitions:
                try:
                    ast = expressiontree.Parse(transition.condition.strip())
                except ValueError:
                    continue

                nodes = set()
                _FindCalls(ast, nodes)
                for each in nodes:
                    call = CallInstance()
                    call.transition = transition
                    call.state = state
                    call.machine = sm
                    call.node = each
                    call.ast = ast
                    call.label = each.BuildExpression()
                    calls.append(call)

    return calls


def _MakeValidID(name):
    return '_' + re.sub('_+', '_', name.strip('_'))


def _ChooseUniqueName(template, names):
    prefix = re.sub('[^a-zA-Z0-9_]', '_', template)
    prefix = '_' + re.sub('_+', '_', prefix.strip('_'))
    if prefix not in names:
        name = prefix
    else:
        idx = 0
        name = '%s%s' % (prefix, idx)
        while name in names:
            idx += 1
            name = '%s%s' % (prefix, idx)

    return name


def GroupFunctionCalls(calls, controller):
    grouped = {}
    for each in calls:
        grouped.setdefault(each.label, CallGroup()).calls.append(each)

    names = set((x.name for x in controller.variables))
    for each, call in grouped.items():
        call.variable = _ChooseUniqueName(each, names)
        names.add(call.variable)

    return grouped


def _ReplaceNode(ast, old, new):
    if ast == old:
        return new
    for i, each in enumerate(ast.GetInputs()[:]):
        if each == old:
            ast.GetInputs()[i] = new
        else:
            _ReplaceNode(each, old, new)

    return ast


class Changes(object):

    def SetValue(self, obj, attr, value):
        setattr(obj, attr, value)

    def Append(self, obj, value):
        obj.append(value)


def IntroduceVariables(groupedCalls, controller, changes):
    for lbl, group in groupedCalls.items():
        if group.action == RefactorAction.LEAVE:
            continue
        variable = trinity.Tr2ControllerFloatVariable()
        variable.name = group.variable
        changes.Append(controller.variables, variable)
        states = set()
        for each in group.calls:
            varRef = expressiontree.Variable(group.variable)
            ast = _ReplaceNode(each.ast, each.node, varRef)
            changes.SetValue(each.transition, 'condition', ast.BuildExpression())
            if group.action == RefactorAction.SET_AT_SOURCE:
                states.add(each.state)
            else:
                states.add(each.machine.startState)

        for each in states:
            action = trinity.Tr2ActionSetValue()
            action.path = group.variable
            action.attribute = 'value'
            action.value = lbl
            changes.Append(each.actions, action)
