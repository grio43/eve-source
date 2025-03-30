#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\controllerValidation.py
import os
import blue
import trinity
from evegraphics.controllers import namedrefs
from evegraphics.validation.commonUtilities import Validate
from evegraphics.validation import validationFunctions, resources

def _GetControllerReferences(context, controller):
    key = (controller, 'references')
    if key in context.cache:
        return context.cache[key]
    refs = namedrefs.GetResourceReferences(controller)
    context.cache[key] = refs
    return refs


def _GetMeshAnimationResolver(context):

    def inner(reference, controller):
        if reference.animationOwner:
            owner = reference.animationOwner
        else:
            owner = controller.GetOwner()
        mesh = getattr(owner, 'mesh', None)
        if not mesh:
            return []
        geom = getattr(mesh, 'geometry', None)
        if geom:
            granny = resources.GetResource(context, geom.path, resources.ResourceType.GRANNY)
            if granny:
                names = [ x.name for x in granny.animations ]
                if reference.name in names:
                    return [getattr(owner, 'animationUpdater', None) or mesh]
        return []

    return inner


def _ResolveControllerReferences(context, controller):
    refs = _GetControllerReferences(context, controller)
    key = (controller, 'resolved')
    if key in context.cache:
        return (refs, context.cache[key])
    resolved = namedrefs.ResolveReferences(refs, controller, {namedrefs.MeshAnimationReference: _GetMeshAnimationResolver(context)})
    context.cache[key] = resolved
    return (refs, resolved)


@Validate('/Tr2Controller')
def SeparateControllerIsShared(context, controller):
    if not controller.isShared:
        context.Error(controller, 'shared controller needs isShared flag to be set')


@Validate('Tr2Controller')
def ControllerNeedsAName(context, controller):
    if not controller.name:
        context.Error(controller, 'controller needs a name')


@Validate('Tr2ControllerFloatVariable')
def ControllerVariableNeedsAName(context, variable):
    if not variable.name:
        context.Error(variable, 'controller variable needs a name')


@Validate('Tr2ControllerFloatVariable')
def ControllerVariableHasValidType(context, variable):
    if variable.variableType not in (0, 1, 2, 3):
        context.Error(variable, 'variable type is invalid')


@Validate('Tr2ControllerFloatVariable')
def EnumControllerVariableHasValidEnumDescription(context, variable):
    if variable.variableType != 3:
        return
    if not variable.enumValues:
        context.Error(variable, 'enum variable needs a valid enumValues description')
        return
    elements = variable.enumValues.split(',')
    seen = set()
    for each in elements:
        if '=' not in each:
            context.Error(variable, "enum element '%s' is not of key=value format" % each)
            continue
        k, v = each.rsplit('=', 1)
        try:
            float(v)
        except ValueError:
            context.Error(variable, "enum element '%s' value is not a number" % each)

        if k in seen:
            context.Error(variable, "duplicate enum element key '%s'" % k)
        seen.add(k)


@Validate('Tr2Controller(controller)/.../Tr2ControllerFloatVariable(variable)')
def ControllerVariableNeedsToBeReferenced(context, controller, variable):
    refs = _GetControllerReferences(context, controller)
    if namedrefs.VariableReference(variable.name) not in refs:
        context.Error(variable, 'variable is not used')


@Validate('List[Tr2ControllerFloatVariable]')
def ControllerVariablesHaveUniqueNames(context, variables):
    names = set()
    for each in variables:
        if each.name in names:
            context.Error(each, 'duplicate variable name')
        names.add(each.name)


@Validate('Tr2Controller')
def ControllerReferencesNeedToBeResolved(context, controller):
    if controller.isShared:
        return
    refs, resolved = _ResolveControllerReferences(context, controller)
    for each in refs:
        if not resolved.get(each, None):
            for refFrom in refs[each]:
                context.Error(refFrom, "unresolved reference to '%s'" % each)


@Validate('Tr2StateMachine')
def StateMachineNeedsAName(context, stateMachine):
    if not stateMachine.name:
        context.Error(stateMachine, 'state machine needs a name')


@Validate('Tr2StateMachine')
def StateMachineNeedsStates(context, stateMachine):
    if not stateMachine.states:
        context.Error(stateMachine, 'state machine needs at least one state')


@Validate('Tr2StateMachine')
def StateMachineNeedsAStartState(context, stateMachine):
    if not stateMachine.startState:
        context.Error(stateMachine, 'state machine needs a start state')


@Validate('Tr2StateMachine')
def StateMachineNeedsToOwnStartState(context, stateMachine):
    if stateMachine.startState not in stateMachine.states:
        context.Error(stateMachine, 'state machine start state is not one of its states')


@Validate('Tr2StateMachine')
def StateMachineStatesAreReachable(context, stateMachine):
    if not stateMachine.startState:
        return
    reachable = {stateMachine.startState}
    modified = True
    while modified:
        modified = False
        for each in reachable:
            for transition in each.transitions:
                dest = stateMachine.states.FindByName(transition.name)
                if not dest:
                    continue
                if dest not in reachable:
                    reachable.add(dest)
                    modified = True

            if modified:
                break

    for each in stateMachine.states:
        if each not in reachable:
            context.Error(each, 'state is not reachable from start state')


@Validate('List[Tr2StateMachineState]')
def StateMachineStateNamesNeedToBeUnique(context, states):
    names = set()
    for each in states:
        if each.name in names:
            context.Error(each, 'duplicate state name')
        names.add(each.name)


@Validate('Tr2StateMachine(stateMachine)/.../Tr2StateMachineTransition(transition)')
def StateMachineTransitionDestinationIsValid(context, stateMachine, transition):
    if not stateMachine.states.FindByName(transition.name):
        context.Error(transition, 'transition destination is invalid')


@Validate('*/Tr2Controller/.../Tr2StateMachineTransition')
def StateMachineTransitionConditionIsValid(context, transition):
    if not transition.isConditionValid:
        context.Error(transition, 'transition condition is invalid')


@Validate('*/Tr2Controller/.../Tr2ActionSetValue')
def SetValueActionExpressionIsValid(context, action):
    if not action.isExpressionValid:
        context.Error(action, 'expression is invalid')


@Validate('*/Tr2Controller/.../Tr2ActionSetValue')
def SetValueActionBindingIsValid(context, action):
    if not action.isBindingValid and not action.delayBinding:
        context.Error(action, 'binding is invalid')


@Validate('Tr2ActionSetValue')
def SetValueActionBindingIsValid(context, action):
    if not action.path and action.delayBinding:
        context.Error(action, 'delayed binding only work with implicit destinations (i.e. set through a path)')


@Validate('Tr2ActionPlayMeshAnimation')
def PlayMeshAnimationBindingIsValid(context, action):
    if not action.path and action.delayBinding:
        context.Error(action, 'delayed binding only work with implicit destinations (i.e. set through a path)')


@Validate('Tr2Controller(controller)/.../Tr2ActionSetValue(action)')
def SetValueActionBindingNeedsToBeImplicitForSharedController(context, controller, action):
    if controller.isShared and action.destination:
        context.Error(action, 'binding needs to be implicit (using path) for shared controller')


@Validate('*/Tr2Controller/.../Tr2ActionAnimateValue')
def AnimateValueActionExpressionIsValid(context, action):
    if not action.isExpressionValid:
        context.Error(action, 'expression is invalid')


@Validate('*/Tr2Controller/.../Tr2ActionAnimateValue')
def AnimateValueActionBindingIsValid(context, action):
    if not action.isBindingValid and not action.delayBinding:
        context.Error(action, 'binding is invalid')


@Validate('Tr2ActionSetValue')
def AnimateValueActionBindingIsValid(context, action):
    if not action.path and action.delayBinding:
        context.Error(action, 'delayed binding only work with implicit destinations (i.e. set through a path)')


@Validate('Tr2Controller(controller)/.../Tr2ActionAnimateValue(action)')
def AnimateValueActionBindingNeedsToBeImplicitForSharedController(context, controller, action):
    if controller.isShared and action.destination:
        context.Error(action, 'binding needs to be implicit (using path) for shared controller')


@Validate('Tr2Controller(controller)/.../Tr2ActionPlayMeshAnimation(action)')
def PlayMeshAnimationActionBindingNeedsToBeImplicitForSharedController(context, controller, action):
    if controller.isShared and action.destination:
        context.Error(action, 'binding needs to be implicit (using path) for shared controller')


@Validate('Tr2ActionAnimateValue')
def AnimateValueActionNeedsACurveIfItIsReferenced(context, action):
    if not action.curve and 'Curve' in action.value:
        context.Error(action, 'curve is missing')


@Validate('Tr2ActionOverlay')
def OvelayActionPathIsValid(context, action):
    validationFunctions.ValidateResPath(context, action, 'path', ('.red',))


@Validate('Tr2ActionOverlay')
def OvelayActionSkinnedVariantIsValid(context, action):
    SKINNED_SUFFIX = '_skinned'
    root, ext = os.path.splitext(action.path)
    variantPath = root + SKINNED_SUFFIX + ext
    if os.path.exists(blue.paths.ResolvePath(variantPath)):
        validationFunctions.ValidateResPath(context, action, 'path', ('.red',), pathOverride=variantPath)
    else:
        context.Error(action, "A '_skinned' variant of {} cannot be found.\nExpected path: {}".format(action.path, blue.paths.ResolvePath(variantPath)))


@Validate('Tr2ActionPlayCurveSet')
def PlayCurveSetActionCurveSetNameIsValid(context, action):
    if not action.curveSetName:
        context.Error(action, 'curve set name is invalid')


@Validate('Tr2ActionCallback')
def CallbackNameIsValid(context, action):
    if not action.callbackName:
        context.Error(action, 'callback name must not be empty')
    if ' ' in action.callbackName:
        context.Error(action, 'callback name must not contain spaces')


@Validate('*(owner)/*/Tr2Controller(controller)/.../Tr2ActionPlayCurveSet(action)')
def PlayCurveSetActionCurveSetExists(context, owner, controller, action):
    if controller.isShared or not action.curveSetName:
        return
    if not any((x.name == action.curveSetName for x in blue.FindInterface(owner, 'TriCurveSet'))):
        context.Error(action, 'curve set does not exist')


@Validate('*(owner)/*/Tr2Controller(controller)/.../Tr2ActionPlayCurveSet(action)')
def PlayCurveSetActionPlayRangeExists(context, owner, controller, action):
    if controller.isShared or not action.curveSetName or not action.rangeName:
        return
    cs = [ x for x in blue.FindInterface(owner, 'TriCurveSet') if x.name == action.curveSetName ]
    for each in cs:
        if each.ranges.FindByName(action.rangeName):
            return

    context.Error(action, 'no curve set with name "%s" contains time range "%s"' % (action.curveSetName, action.rangeName))


@Validate('Tr2ActionPlayMeshAnimation')
def PlayCurveSetActionAnimationNameIsValid(context, action):
    if not action.animation:
        context.Error(action, 'animation name is invalid')


@Validate('Tr2ControllerReference')
def ControllerReferencePathIsValid(context, controllerRef):
    validationFunctions.ValidateResPath(context, controllerRef, 'path', ('.red',))


@Validate('Tr2ActionChildEffect')
def ActionChildEffectPathIsValid(context, childEffect):
    validationFunctions.ValidateResPath(context, childEffect, 'path', ('.red',))


@Validate('Tr2ActionPlaySound')
def ActionPlaySoundHasEmitter(context, action):
    if not action.emitter:
        context.Error(action, 'play sound action must have an emitter name')


@Validate('Tr2ActionSetAttenuationScaling')
def ActionSetAttenuationScalingHasEmitter(context, action):
    if not action.emitter:
        context.Error(action, 'set attenuation scaling action must have an emitter name')
    if not action.scalingFactor:
        context.Error(action, 'set attenuation scaling action must have a scaling factor')
