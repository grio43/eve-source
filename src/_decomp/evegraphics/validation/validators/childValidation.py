#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\childValidation.py
from evegraphics.validation.commonUtilities import Validate, DeleteTopAction
from evegraphics.validation.validationFunctions import EndsWith, ListAttributesAreDistinct, ValidateResPath
from evegraphics.validation.validators.meshValidation import IsMeshSkinned

@Validate('List[EveSOFDataHullChild]')
def ValidateListOfEveSOFDataHullChild(context, children):
    context.Expect(children, None, ListAttributesAreDistinct('name'))
    context.Expect(children, None, ListAttributesAreDistinct(None, listAttributesToIgnore=['name']))


@Validate('EveSOFDataHullChild')
def ValidateEveSOFDataHullChild(context, child):
    ValidateResPath(context, child, 'redFilePath', extensions=('.red',))


@Validate('EveChildMesh')
def EveChildMeshIsNotEmpty(context, child):
    if not child.mesh:
        context.Error(child, 'child does not have a mesh and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('EveChildMesh')
def EveChildMeshHasValidMinScreenSize(context, child):
    if child.minScreenSize == 0.0:
        context.Error(child, 'child does not have a valid minscreensize. Put it to -1 to show always or any positive number to have it lod out')


@Validate('EveChildMesh')
def AnimatedEveChildMeshWithUnskinnedGranny(context, mesh):
    if not mesh.mesh or not mesh.animationUpdater:
        return
    isSkinned = IsMeshSkinned(context, mesh.mesh)
    if isSkinned is False:
        context.Error(mesh, 'child mesh has an animation updater, but its mesh is not skinned')


@Validate('EveChildMesh/Tr2GrannyAnimation')
def EveChildMeshAnimationPathIsValidOrEmpty(context, animation):
    if not animation.resPath:
        return
    ValidateResPath(context, animation, 'resPath', extensions=('.gr2',))


@Validate('EveChildMesh')
@Validate('EveChildQuad')
@Validate('=EveChildContainer')
def EveChildIsVisible(context, child):
    if not child.display and not context.IsBoundAsDestination(child, 'display'):
        context.Error(child, 'display is off so the object is not visible and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('=EveChildContainer')
def EveChildIsScaledToZero(context, child):
    if child.scaling == (0.0, 0.0, 0.0) and not context.IsBoundAsDestination(child, 'scaling'):
        context.Error(child, 'Scaling is zero so the object is not visible and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('=EveChildContainer')
def EveChildContainerIsNotEmpty(context, child):
    if not child.objects and not child.curveSets and not child.observers and not child.lights and not child.controllers:
        context.Error(child, 'child is empty and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('EveChildExplosion')
def EveChildExplosionIsNotEmpty(context, child):
    if not child.localExplosion and not child.localExplosions and not child.localExplosionShared and not child.globalExplosion and not child.globalExplosions:
        context.Error(child, 'child is empty and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('=EveChildParticleSystem')
def EveChildParticleSystemIsNotEmpty(context, child):
    if not child.particleSystems and not child.particleEmitters:
        if not child.mesh:
            context.Error(child, 'child does not have mesh, particle systems or particle emitters and can be deleted', actions=[DeleteTopAction(context, True)])
        else:
            context.Error(child, 'child does not have particle systems or particle emitters and should be turned into an EveChildMesh')


@Validate('=EveChildParticleSystem')
def EveChildParticleSystemHasValidMinScreenSize(context, child):
    if child.minScreenSize <= 0.0 and child.minScreenSize != -1.0:
        context.Error(child, 'child does not have a valid minscreensize. Put it to -1 to show always or any positive number to have it lod out')


@Validate('=EveChildParticleSystem')
def EveChildParticleSystemHasValidLodVariables(context, child):
    if child.lodFactorMedium > 1 or child.lodFactorLow > child.lodFactorMedium:
        context.Error(child, 'child does not have a valid LOD variable setup. lodFactor should follow the order: lodFactorLow <= lodFactorMedium <= 1')


@Validate('=EveChildParticleSystem')
def EveChildParticleSystemHasValidScalingVariables(context, child):
    if child.scaling == (0.0, 0.0, 0.0) and not context.IsBoundAsDestination(child, 'scaling'):
        context.Error(child, 'Scaling is zero so the object is not visible and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('=EveChildParticleSystem')
def EveChildParticleSystemHasValidScalingVariables(context, child):
    if not child.display and not context.IsBoundAsDestination(child, 'display'):
        context.Error(child, 'display is off so the object is not visible and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('EveChildQuad')
def EveChildQuadIsNotEmpty(context, child):
    if not child.effect:
        context.Error(child, 'child is empty and can be deleted', actions=[DeleteTopAction(context, True)])


@Validate('EveChildQuad')
def EveChildQuadHasValidMinScreenSize(context, child):
    if child.minScreenSize == 0.0:
        context.Error(child, 'child does not have a valid minscreensize. Put it to -1 to show always or any positive number to have it lod out')
