#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\multieffectValidation.py
from evegraphics.validation.commonUtilities import Validate, DeleteAction, DeleteTopAction
from evegraphics.validation.validationFunctions import ListAttributesAreDistinct
import trinity

def IsDynamicBindingPathOK(path, names):
    return any([ path == param for param in names ]) or any([ path.startswith(param + '.') for param in names ])


@Validate('List[EveMultiEffectParameter]')
def NoDuplicateName(context, eveMultiEffectParameterList):
    context.Expect(eveMultiEffectParameterList, None, ListAttributesAreDistinct('name'))


@Validate('EveMultiEffectParameter')
def ValidName(context, eveMultiEffectParameter):
    if eveMultiEffectParameter.name == '' or ' ' in eveMultiEffectParameter.name:
        context.Error(eveMultiEffectParameter, "Name '%s' is not valid, it cannot be empty or contain spaces" % eveMultiEffectParameter.name)


@Validate('Tr2DynamicBinding')
def ValidName(context, binding):
    if binding.name == '':
        context.Error(binding, "Parameter name '%s' can not be empty" % binding.name)


@Validate('EveMultiEffect(owner)/.../Tr2DynamicBinding(binding)')
def ValidDynamicBindingHasValidDestinationObjectPath(context, owner, binding):
    parameterNames = [ param.name for param in owner.parameters ]
    curveNames = [ curveset.name for curveset in owner.curveSets ]
    validNames = ['Owner'] + parameterNames + curveNames
    if binding.destinationObjectPath == '':
        context.Error(binding, 'Destination object path is empty')
    elif not IsDynamicBindingPathOK(binding.destinationObjectPath, validNames):
        context.Error(binding, "Destination '%s' does not refer to an existing parameter or curveset. Valid parameters are: %s" % (binding.sourceObjectPath, ', '.join(validNames)))
    elif IsDynamicBindingPathOK(binding.destinationObjectPath, curveNames) and not binding.isDestinationValid:
        context.Error(binding, "Destination '%s' is not valid" % binding.destinationObjectPath)


@Validate('EveMultiEffect(owner)/.../Tr2DynamicBinding(binding)')
def ValidDynamicBindingHasValidSourceObjectPath(context, owner, binding):
    parameterNames = [ param.name for param in owner.parameters ]
    curveNames = [ curveset.name for curveset in owner.curveSets ]
    validNames = ['Owner'] + parameterNames + curveNames
    if binding.sourceObjectPath == '':
        context.Error(binding, 'Source object path is empty')
    elif not IsDynamicBindingPathOK(binding.sourceObjectPath, validNames):
        context.Error(binding, "Source '%s' does not refer to an existing parameter or curveset. Valid parameters are: %s" % (binding.sourceObjectPath, ', '.join(validNames)))
    elif IsDynamicBindingPathOK(binding.sourceObjectPath, curveNames) and not binding.isSourceValid:
        context.Error(binding, "Source '%s' is not valid" % binding.sourceObjectPath)


@Validate('Tr2DynamicBinding')
def DynamicBindingScaleIsNotZero(context, binding):
    if binding.scale == 0 and not context.IsBoundAsDestination(binding, 'scale'):
        context.Error(binding, 'Scale is unbound and is set to 0 and can be deleted', actions=(DeleteTopAction(context, True),))
