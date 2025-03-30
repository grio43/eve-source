#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\graphicEffects\skinChange.py
import time
import blue
import geo2
import trinity
import uthread
import evegraphics.settings as gfxsettings
from uthread2 import call_after_simtime_delay
from evegraphics.graphicEffects.audio import AddEmitterToModel
from evegraphics.utils import GetCorrectEffectPath
import logging
log = logging.getLogger(__name__)
SKIN_CHANGE_VFX_PATH = 'res:/fisfx/skinchange/skin_change.red'
SKINNED_SKIN_CHANGE_VFX_PATH = 'res:/fisfx/skinchange/skin_change_skinned.red'
STRUCTURE_SKIN_CHANGE_VFX_PATH = 'res:/fisfx/skinchange/mf_skinchange_01a.red'

def CopyModel(oldModel, newModel, skipEffects = False, skipTurrets = False):
    if not oldModel or not newModel:
        return
    newModel.name = str(oldModel.name)

    def copyOver(old, new, name):
        if hasattr(old, name):
            setattr(new, name, getattr(old, name))

    copyValues = ['modelTranslationCurve',
     'translationCurve',
     'rotationCurve',
     'modelRotationCurve',
     'activationStrength',
     'displayKillCounterValue']
    for each in copyValues:
        copyOver(oldModel, newModel, each)

    if not skipEffects:
        while len(oldModel.effectChildren) > 0:
            effectChildFromOldModel = oldModel.effectChildren.pop()
            if getattr(effectChildFromOldModel, 'origin', -1) != trinity.EveSpaceObjectChildOrigin.SOF:
                newModel.effectChildren.append(effectChildFromOldModel)

    if not skipTurrets:
        while len(oldModel.turretSets) > 0:
            oldModelTurretSet = oldModel.turretSets.pop()
            newModel.turretSets.append(oldModelTurretSet)

    for name, value in oldModel.GetControllerVariables().items():
        newModel.SetControllerVariable(name, value)


def IsSkinChangeEffectEnabled():
    try:
        return gfxsettings.Get(gfxsettings.UI_MODELSKINSINSPACE_ENABLED)
    except gfxsettings.UninitializedSettingsGroupError:
        pass

    return True


def GetModelsToBeRemovedFromScene(scene):
    return [ o for o in scene.objects if '_to_be_removed_' in o.name ]


def ChangeSkin(oldModel, newModel, scene, preSkinChangeCallback = None, postSkinChangeCallback = None, audioTranslationMatrix = None):
    if not oldModel:
        log.warning('SkinChange: Old model is none, no skinchange will occur')
        return
    if scene:
        if newModel in scene.objects:
            RemoveModel(newModel, scene)
        scene.objects.insert(0, newModel)
    CopyModel(oldModel, newModel, skipTurrets=True)
    newModel.StartControllers()
    oldModel.name += '_to_be_removed_' + str(time.time())
    if not IsSkinChangeEffectEnabled():
        if preSkinChangeCallback:
            preSkinChangeCallback(oldModel, newModel)
        if postSkinChangeCallback:
            postSkinChangeCallback(oldModel, newModel)
        RemoveModel(oldModel, scene)
        return
    modelPosition = getattr(oldModel.translationCurve, 'value', None)
    if audioTranslationMatrix:
        modelPosition = geo2.Vec3Transform(modelPosition, audioTranslationMatrix)
    effectDuration = min(3 + oldModel.boundingSphereRadius * 0.001, 9)
    audioSignal = unicode('ship_skin_change_play') if effectDuration < 9 else unicode('ship_skin_change_titan_play')
    emitter = AddEmitterToModel('effect_skin_change', oldModel, oldModel.boundingSphereRadius, position=modelPosition)
    emitter.SendEvent(audioSignal)
    gfx = SetupOverlayEffect(oldModel, newModel, effectDuration)
    if preSkinChangeCallback:
        preSkinChangeCallback(oldModel, newModel)
    gfx.curveSet.Play()
    uthread.new(DelayedRemoval, scene, oldModel, newModel, gfx, postSkinChangeCallback, effectDuration)


def ChangeStructureSkin(oldModel, newModel, scene, newDna = None, paintwork = None, postSkinChangeCallback = None):
    if oldModel is None:
        return
    CopyModel(oldModel, newModel, skipEffects=True)
    if scene:
        if newModel in scene.objects:
            RemoveModel(newModel, scene)
        scene.objects.insert(0, newModel)
    newModel.StartControllers()
    oldModel.name += '_to_be_removed_' + str(time.time())
    if not IsSkinChangeEffectEnabled():
        if preSkinChangeCallback:
            preSkinChangeCallback(oldModel, newModel)
        if postSkinChangeCallback:
            postSkinChangeCallback(oldModel, newModel)
        RemoveModel(oldModel, scene)
        return
    for each in newModel.effectChildren:
        each.alwaysOn = True

    for each in oldModel.effectChildren:
        each.alwaysOn = True

    respath = u'res:/fisfx/skinchange/mf_skinchange_01a.red'
    multiEffect = blue.resMan.LoadObject(respath)
    if multiEffect is None:
        return self.logger.error('structure.py: MultiEffect broken and that feels bad')
    blue.resMan.Wait()
    scene.objects.insert(0, multiEffect)
    multiEffect.SetParameter('objectB', newModel)
    multiEffect.SetParameter('objectA', oldModel)
    multiEffect.StartControllers()
    multiEffect.SetControllerVariable('skinChange', 1.0)
    newModel.StartControllers()
    effectDuration = 12

    def cleanUp(multiEffect, oldStructure, scene):
        if scene is None:
            return
        if oldStructure is not None and oldStructure in scene.objects:
            scene.objects.remove(oldStructure)
        if multiEffect is not None and multiEffect in scene.objects:
            for param in multiEffect.parameters:
                param.object = None

            scene.objects.remove(multiEffect)
        oldStructure = None
        multiEffect = None

    call_after_simtime_delay(cleanUp, effectDuration, multiEffect, oldModel, scene)


def SetupOverlayEffect(oldModel, newModel, duration):
    gfx = trinity.Load(GetCorrectEffectPath(SKIN_CHANGE_VFX_PATH, oldModel))
    for binding in gfx.curveSet.bindings:
        if binding.name.startswith('old'):
            binding.destinationObject = oldModel
        elif binding.name.startswith('new'):
            binding.destinationObject = newModel

    oldModel.overlayEffects.append(gfx)
    cloakingEffect = None
    for overlayEffect in oldModel.overlayEffects:
        if overlayEffect.name == 'Cloak':
            cloakingEffect = overlayEffect
            break

    if cloakingEffect:
        oldModel.overlayEffects.remove(cloakingEffect)
        del cloakingEffect
    oldModel.clipSphereCenter = (0, 0, 0)
    length = gfx.curveSet.GetMaxCurveDuration()
    if length > 0.0:
        scaleValue = length / duration
        gfx.curveSet.scale = scaleValue
    return gfx


def DelayedRemoval(scene, oldModel, newModel, gfx, postSkinChangeCallback, delayInSeconds):
    blue.synchro.SleepSim(delayInSeconds * 1000)
    if postSkinChangeCallback:
        postSkinChangeCallback(oldModel, newModel)
    RemoveModel(oldModel, scene)
    oldModel.overlayEffects.fremove(gfx)
    while len(gfx.curveSet.bindings) > 0:
        gfx.curveSet.bindings.pop()

    newModel.clipSphereFactor = 0
    newModel.clipSphereFactor2 = 0


def RemoveModel(oldModel, scene):
    if scene:
        for o in scene.objects:
            if o == oldModel:
                scene.objects.remove(o)
                return


def RemoveAllTemporaryModels(scene):
    objectsToRemove = [ o for o in scene.objects if '_to_be_removed_' in o.name ]
    for o in objectsToRemove:
        RemoveModel(o, scene)
