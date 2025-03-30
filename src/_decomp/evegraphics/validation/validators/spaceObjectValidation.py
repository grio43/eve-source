#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\validation\validators\spaceObjectValidation.py
import trinity
from evegraphics.validation.commonUtilities import Validate, IsContent, SceneType
from evegraphics.validation.validators.meshValidation import IsMeshSkinned
SHADOW_EFFECT_PREFIX = 'res:/graphics/effect/managed/space/spaceobject/shadow/'

@Validate('EveSpaceObject2')
def DisplayShoudBeOn(context, spaceObject):
    if not spaceObject.display and not context.IsBoundAsDestination(spaceObject, 'display'):
        context.Error(spaceObject, 'display is off - object is not visible')


@Validate('EveSpaceObject2')
def UpdateShoudBeOn(context, spaceObject):
    if not spaceObject.update:
        context.Error(spaceObject, 'update is off - object will not work correctly')


@Validate('EveSpaceObject2')
def ShouldHaveMesh(context, spaceObject):
    if not isinstance(spaceObject, trinity.EveMissile) and not spaceObject.mesh:
        context.Error(spaceObject, 'should have a mesh')


@Validate('EveSpaceObject2')
def ModelScaleShouldBeOne(context, spaceObject):
    if isinstance(spaceObject, trinity.EveUiObject):
        return
    if context.GetArgument(SceneType) == SceneType.HANGAR:
        return
    if spaceObject.modelScale != 1:
        context.Error(spaceObject, 'modelScale should be 1.0')


@Validate('EveSpaceObject2', IsContent(IsContent.BRANCH))
def ShouldHaveBoundingSphere(context, spaceObject):
    if spaceObject.boundingSphereRadius <= 0:
        context.Error(spaceObject, 'should have a valid bounding sphere')


@Validate('EveSpaceObject2', SceneType)
def ShouldNotHaveTranslationCurve(context, spaceObject):
    isHangar = context.GetArgument(SceneType) == SceneType.HANGAR
    if not isHangar and spaceObject.translationCurve:
        context.Error(spaceObject, 'should not have translation curve')


@Validate('EveSpaceObject2', SceneType)
def ShouldNotHaveRotationCurve(context, spaceObject):
    isHangar = context.GetArgument(SceneType) == SceneType.HANGAR
    if not isHangar and spaceObject.rotationCurve:
        context.Error(spaceObject, 'should not have rotation curve')


@Validate('EveMobile')
def ShouldNotHaveRotationCurve(context, spaceObject):
    if spaceObject.turretSets:
        context.Error(spaceObject, 'should not have turret sets')
