#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\eveTransformValidation.py
from evegraphics.validation.commonUtilities import Validate, DeleteTopAction

@Validate('EveTransform')
def TransformNotEmpty(context, transform):
    if not transform.mesh and not transform.children and not transform.particleEmitters and not transform.particleSystems and not transform.observers and not transform.curveSets:
        context.Error(transform, 'transform is empty and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('EveTransform')
def DistanceBasedScaleIsDeprecated(context, transform):
    if context.IsBoundAsDestination(transform, 'useDistanceBasedScale') or transform.useDistanceBasedScale:
        context.Error(transform, 'useDistanceBasedScale is deprecated')


@Validate('EveTransform')
def InvisibleTransform(context, transform):
    if not transform.display and not context.IsBoundAsDestination(transform, 'display'):
        context.Error(transform, 'display is turned off - transform is not visible', actions=[DeleteTopAction(context, False)])


@Validate('EveTransform')
def OverrideBoundsAreValid(context, transform):
    if any(transform.overrideBoundsMin) or any(transform.overrideBoundsMax):
        if transform.overrideBoundsMin == transform.overrideBoundsMax:
            context.Error(transform, 'overriden bounds are empty')
