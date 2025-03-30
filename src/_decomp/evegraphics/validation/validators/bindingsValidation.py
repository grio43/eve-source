#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\bindingsValidation.py
import blue
import trinity
from trinutils.bindings import FindBrokenBindingReferences
from evegraphics.validation.commonUtilities import Validate

def GetUnboundCurves(context, obj):
    curveSets = blue.FindInterface(obj, 'TriCurveSet')
    for curveSet in curveSets:
        for curve in curveSet.curves:
            if type(curve).__module__ == 'trinity' and not context.IsBoundAsSource(curve):
                yield curve


def _IsEveStretch2LoopCurveSet(root, curveSet):
    for route in blue.FindRoute(root, curveSet):
        if isinstance(route[-1][0], trinity.EveStretch2) and route[-1][2] == 'loop':
            return True

    return False


def GetEmptryCurveSets(obj):
    return [ x for x in blue.FindInterface(obj, 'TriCurveSet') if not x.bindings and not x.curves and not _IsEveStretch2LoopCurveSet(obj, x) ]


def _HasRoutes(parents, obj, isSource):
    for each in parents.get(obj, ()):
        if isinstance(each[0], trinity.TriValueBinding):
            if isSource and each[2] == 'destinationObject':
                return True
            if not isSource and each[2] == 'sourceObject':
                return True
        else:
            return True

    return False


def FindBrokenBindings(obj):
    bindings = set(FindBrokenBindingReferences(obj))
    allBindings = blue.FindInterface(obj, 'TriValueBinding')
    for binding in allBindings:
        if not binding.isValid and not binding.name.startswith('self_') and not binding.name.startswith('new_') and not binding.name.startswith('old_'):
            bindings.add(binding)

    parents = blue.FindAllReferences(obj)
    src = {}
    dst = {}
    for binding in allBindings:
        if binding in bindings:
            continue
        if binding.sourceObject:
            if binding.sourceObject not in src:
                src[binding.sourceObject] = _HasRoutes(parents, binding.sourceObject, True)
            if not src[binding.sourceObject]:
                bindings.add(binding)
        if binding.destinationObject:
            if binding.destinationObject not in dst:
                dst[binding.destinationObject] = _HasRoutes(parents, binding.destinationObject, False)
            if not dst[binding.destinationObject]:
                bindings.add(binding)

    return bindings


def _DeleteObject(root, obj):

    def inner():
        for route in blue.FindRoute(root, obj):
            last = route[-1]
            if last[1] == 0:
                setattr(last[0], last[2], None)
            else:
                last[0].remove(obj)

        return True

    return ('Delete %s' % (getattr(obj, 'name', '') or type(obj).__name__), inner, True)


@Validate('/*')
def ValidateBindings(context, root):
    bindings = set(FindBrokenBindings(root))
    for each in bindings:
        label = ''
        if not each.sourceObject:
            label += ' has no source object'
        if not each.destinationObject:
            if label:
                label += '\n\tand'
            label += ' has no destination object'
        if each.sourceObject and each.destinationObject:
            if label:
                label += '\n\tand'
            if each.isValid:
                label += ' binding source or destination object does not appear to be referenced anywhere else'
            else:
                label += ' is invalid'
        context.Error(each, label, actions=[_DeleteObject(context.GetStack()[0], each)])


@Validate('/*')
def ValidateUnusedCurves(context, root):
    curves = set(GetUnboundCurves(context, root))
    for each in curves:
        if isinstance(each, trinity.TriEventCurve):
            continue
        context.Error(each, 'is not used anywhere', actions=[_DeleteObject(context.GetStack()[0], each)])


@Validate('/*')
def ValidateUnusedCurveSets(context, root):
    curveSets = set(GetEmptryCurveSets(root))
    for each in curveSets:
        context.Error(each, 'is empty', actions=[_DeleteObject(context.GetStack()[0], each)])


@Validate('TriCurveSet')
def NoDuplicateBindingsInCurveSet(context, curveSet):
    destinations = set()
    for each in curveSet.bindings:
        if not isinstance(each, trinity.TriValueBinding):
            continue
        key = (each.destinationObject, each.destinationAttribute)
        if key in destinations:
            context.Error(each, 'duplicate binding', actions=[_DeleteObject(curveSet.bindings, each)])
        destinations.add(key)
