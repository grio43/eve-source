#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\controllers\namedrefs.py
import trinity
from eveaudio.controllers import GetEmittersFromOwner
from evegraphics.controllers import expressiontree

class ResourceType(object):
    VARIABLE = 0
    MESH_ANIMATION = 1
    CURVE_SET = 2
    CURVE_SET_RANGE = 3


class ResourceReference(object):

    def __str__(self):
        return '%s: %s' % (self.GetCategoryLabel(), self.GetLabel())

    def __hash__(self):
        return hash(str(self))

    def GetCategoryLabel(self):
        raise NotImplementedError()

    def GetLabel(self):
        raise NotImplementedError()

    def Resolve(self, controller):
        raise NotImplementedError()

    def Rename(self, newRef, references):
        raise NotImplementedError()


class VariableReference(ResourceReference):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, VariableReference) and self.name == other.name

    def GetCategoryLabel(self):
        return 'Variable'

    def GetLabel(self):
        return self.name

    def Resolve(self, controller):
        var = controller.variables.FindByName(self.name)
        if var:
            return [var]
        else:
            return []

    def Rename(self, newRef, references):
        if not isinstance(newRef, VariableReference):
            raise ValueError()
        for each in references:
            _RenameOwnedExpressionReferences(each, self, newRef)
            if isinstance(each, (trinity.Tr2ActionSetValue, trinity.Tr2ActionAnimateValue)):
                if each.path.strip() == self.name:
                    each.animation = newRef.name


class MeshAnimationReference(ResourceReference):

    def __init__(self, name, animationOwner = None):
        self.name = name
        self.animationOwner = animationOwner

    def __eq__(self, other):
        return isinstance(other, MeshAnimationReference) and self.name == other.name and self.animationOwner == other.animationOwner

    def GetCategoryLabel(self):
        return 'Mesh Animation'

    def GetLabel(self):
        return self.name

    def Resolve(self, controller):
        if self.animationOwner:
            owner = self.animationOwner
        else:
            owner = controller.GetOwner()
        animationUpdater = getattr(owner, 'animationUpdater', None)
        if animationUpdater and self.name in animationUpdater.GetAnimationNames():
            return [animationUpdater]
        else:
            return []

    def Rename(self, newRef, references):
        if not isinstance(newRef, MeshAnimationReference):
            raise ValueError()
        for each in references:
            _RenameOwnedExpressionReferences(each, self, newRef)
            if isinstance(each, trinity.Tr2ActionPlayMeshAnimation) and each.animation == self.name:
                each.animation = newRef.name


class CurveSetReference(ResourceReference):

    def __init__(self, name):
        parts = name.split('/')
        self.name = parts[0]
        self.rangeName = '/'.join(parts[1:])

    def __eq__(self, other):
        return isinstance(other, CurveSetReference) and self.name == other.name and self.rangeName == other.rangeName

    def GetCategoryLabel(self):
        return 'Curve Set'

    def GetLabel(self):
        if self.rangeName:
            return '/'.join((self.name, self.rangeName))
        else:
            return self.name

    def Resolve(self, controller):
        result = []
        for each in controller.GetOwner().Find('trinity.TriCurveSet'):
            if each.name == self.name and (not self.rangeName or each.ranges.FindByName(self.rangeName)):
                result.append(each)

        return result

    def Rename(self, newRef, references):
        if not isinstance(newRef, CurveSetReference):
            raise ValueError()
        for each in references:
            _RenameOwnedExpressionReferences(each, self, newRef)
            if isinstance(each, trinity.Tr2ActionPlayCurveSet):
                each.curveSetName = newRef.name
                each.rangeName = newRef.rangeName


class EmitterReference(ResourceReference):

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, EmitterReference) and self.name == other.name

    def GetCategoryLabel(self):
        return 'Audio Emitter'

    def GetLabel(self):
        return self.name

    def Resolve(self, controller):
        owner = controller.GetOwner()
        emitters = GetEmittersFromOwner(owner)
        for emitter in emitters:
            if emitter.name == self.name:
                return [emitter]

        return []

    def Rename(self, newRef, references):
        if not isinstance(newRef, EmitterReference):
            raise ValueError()
        for each in references:
            _RenameOwnedExpressionReferences(each, self, newRef)
            if isinstance(each, trinity.Tr2ActionPlaySound):
                each.emitter = newRef.name


def _Walk(node, visitor):
    visitor(node)
    for each in node.GetInputs():
        _Walk(each, visitor)


def _RenameExpressionReference(expression, oldReference, newReference):
    try:
        expr = expressiontree.Parse(expression)
    except ValueError:
        return expression

    replacements = {}

    def findReferences(node):
        if isinstance(node, expressiontree.Variable) and isinstance(oldReference, VariableReference) and node.name == oldReference.name:
            replacements[node.startPosition] = (len(node.name), newReference.name)
        elif isinstance(node, expressiontree.StringFunctionCall):
            param = node.param[1:-1]
            if node.name == 'AnimationTime' and isinstance(oldReference, MeshAnimationReference) and param == oldReference.name:
                replacements[node.paramStartPosition] = (len(node.param), '"%s"' % newReference.name)
            elif node.name == 'CurveSetTime' and isinstance(oldReference, CurveSetReference) and param == oldReference.GetLabel():
                replacements[node.paramStartPosition] = (len(node.param), '"%s"' % newReference.GetLabel())

    _Walk(expr, findReferences)
    for pos in sorted(replacements, reverse=True):
        length, insert = replacements[pos]
        expression = expression[:pos] + insert + expression[pos + length:]

    return expression


def _RenameOwnedExpressionReferences(expressionOwner, oldReference, newReference):
    if isinstance(expressionOwner, (trinity.Tr2ActionSetValue, trinity.Tr2ActionAnimateValue, trinity.Tr2ActionAnimateCurveSet)):
        expressionOwner.value = _RenameExpressionReference(expressionOwner.value, oldReference, newReference)
    elif isinstance(expressionOwner, trinity.Tr2StateMachineTransition):
        expressionOwner.condition = _RenameExpressionReference(expressionOwner.condition, oldReference, newReference)


def _FindExpressionReferences(expression):
    try:
        expr = expressiontree.Parse(expression)
    except ValueError:
        return []

    references = set()

    def findReferences(node):
        if isinstance(node, expressiontree.Variable):
            references.add(VariableReference(node.name))
        elif isinstance(node, expressiontree.StringFunctionCall):
            param = node.param[1:-1]
            if node.name == 'AnimationTime':
                references.add(MeshAnimationReference(param))
            elif node.name == 'CurveSetTime':
                references.add(CurveSetReference(param))

    _Walk(expr, findReferences)
    return references


ACTIONS_WITH_REFERENCES = ['trinity.Tr2ActionAnimateValue',
 'trinity.Tr2ActionSetValue',
 'trinity.Tr2ActionAnimateCurveSet',
 'trinity.Tr2ActionPlayCurveSet',
 'trinity.Tr2ActionPlayMeshAnimation',
 'trinity.Tr2ActionPlaySound',
 'trinity.Tr2ActionSetAttenuationScaling']

def ActionHasReference(action):
    try:
        return action.__bluetype__ in ACTIONS_WITH_REFERENCES
    except AttributeError:
        return False


def ActionIsValid(action, controller):
    if not ActionHasReference(action):
        return True
    if controller is None:
        return False
    references = {}
    _UpdateReferenceDictForAction(action, references)
    resolved = ResolveReferences(references, controller)
    hasUnresolvedReferences = any((not resolved.get(k, None) for k in references))
    return not hasUnresolvedReferences


def TransitionIsValid(transition, controller):
    if controller is None:
        return False
    references = {}
    _UpdateReferenceDictForTransition(transition, references)
    resolved = ResolveReferences(references, controller)
    hasUnresolvedReferences = any((not resolved.get(k, None) for k in references))
    return not hasUnresolvedReferences


def GetResourceReferences(controller):
    references = {}
    for each in controller.Find(ACTIONS_WITH_REFERENCES, 7):
        _UpdateReferenceDictForAction(each, references)

    for each in controller.Find('trinity.Tr2StateMachineTransition', 7):
        _UpdateReferenceDictForTransition(each, references)

    return references


def _UpdateReferenceDictForTransition(transition, references):
    for r in _FindExpressionReferences(transition.condition):
        references.setdefault(r, set()).add(transition)


def _UpdateReferenceDictForAction(action, referenceDict):
    if isinstance(action, (trinity.Tr2ActionSetValue, trinity.Tr2ActionAnimateValue)):
        for r in _FindExpressionReferences(action.value):
            referenceDict.setdefault(r, set()).add(action)

        if action.path or not action.destination:
            dest = action.path.split('.')[0].strip()
            if dest != 'Owner':
                referenceDict.setdefault(VariableReference(dest), set()).add(action)
    elif isinstance(action, trinity.Tr2ActionAnimateCurveSet):
        for r in _FindExpressionReferences(action.value):
            referenceDict.setdefault(r, set()).add(action)

    elif isinstance(action, trinity.Tr2ActionPlayCurveSet):
        referenceDict.setdefault(CurveSetReference('/'.join((action.curveSetName, action.rangeName))), set()).add(action)
    elif isinstance(action, trinity.Tr2ActionPlayMeshAnimation):
        referenceDict.setdefault(MeshAnimationReference(action.animation, action.GetDestination()), set()).add(action)
    elif isinstance(action, trinity.Tr2ActionPlaySound):
        referenceDict.setdefault(EmitterReference(action.emitter), set()).add(action)
    elif isinstance(action, trinity.Tr2ActionSetAttenuationScaling):
        referenceDict.setdefault(VariableReference(action.controllerVariable), set()).add(action)


def ResolveReferences(references, controller, resolverOverrides = None):
    resolverOverrides = resolverOverrides or {}
    result = {}
    for k in references:
        if type(k) in resolverOverrides:
            result[k] = resolverOverrides[type(k)](k, controller)
        else:
            result[k] = k.Resolve(controller)

    return result
