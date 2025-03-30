#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\spaceObject.py
import logging
import math
import random
import blue
import geo2
from evetypes import GetGraphicID, GetGroupID
from destructionEffect import destructionType as destructionEffectType
import carbon.common.script.util.mathCommon as mathCommon
import decometaclass
import eve.common.lib.appConst as const
import eveSpaceObject
import eveSpaceObject.spaceobjaudio as spaceobjaudio
import evegraphics.settings as gfxsettings
import evegraphics.utils as gfxutils
import fsdBuiltData.client.explosionBuckets as fsdExplosionBuckets
import locks
import trinity
import uthread2
from eve.client.script.environment.sofService import GetSofService
from evegraphics.controllers.clientControllerRegistry import ChangeControllerStateFromSlimItem
from evegraphics.graphicEffects.skinChange import ChangeSkin, RemoveAllTemporaryModels, ChangeStructureSkin
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from fsdBuiltData.common.graphicIDs import GetControllerVariableOverrides
from inventorycommon.const import TYPES_THAT_ALWAYS_FACE_THE_SUN
from signals.signal import Signal
from destructionEffect.destructioneffectmanager import DestructionEffectManager
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from uthread2 import call_after_simtime_delay, StartTasklet
import launchdarkly
import uthread
from logging import getLogger
from eve.common.lib.appConst import GRIDSIZE
from cosmeticsConst import PatternBlendMode
logger = getLogger(__name__)
STRUCTURE_SKINCHANGE_MULTIEFFECT_GRAPHIC_ID = 26134
BALL_REMOVAL_DELAY_TO_EXPLOSION_BUCKETS = {240: [3, 4, 5]}
SERVER_CONTROLLER_EVENT_NAMES_TO_CONTROLLER_VARIABLES = {'Activated': 'IsTriggered'}

def modify_dna(base_dna, mat1 = None, mat2 = None, mat3 = None, mat4 = None, patternMat1 = None, patternMat2 = None, patternName = None, isStructure = False):
    if isStructure:
        materials = [None,
         mat1,
         mat3,
         mat2]
    else:
        materials = [mat1,
         mat3,
         mat2,
         None]
    for i, material in enumerate(materials):
        if material is None:
            materials[i] = 'None'

    materials_string = 'material?' + ';'.join(materials)
    base_parts = base_dna.split(':')
    if len(base_parts) > 3:
        base_parts[3] = materials_string
    else:
        base_parts.append(materials_string)
    if patternMat1 is not None or patternMat2 is not None:
        pattern_components = []
        if patternName is not None:
            pattern_components.append(patternName)
        if patternMat1 is not None:
            pattern_components.append(patternMat1)
        if patternMat2 is not None:
            pattern_components.append(patternMat2)
        if pattern_components:
            base_parts.append('pattern?' + ';'.join(pattern_components))
    return ':'.join(base_parts)


class SpaceObjectLogAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra = None, so_id = None):
        self.so_id = so_id
        super(SpaceObjectLogAdapter, self).__init__(logger, extra)

    def add_so_id(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        so_id_arg = [self.so_id]
        if args:
            new_args = list(args)
            new_args = so_id_arg + new_args
        else:
            new_args = so_id_arg
        msg = '[%s] ' + msg
        return (msg, new_args, kwargs)

    def debug(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.debug(new_msg, *new_args, **kwargs)

    def info(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.info(new_msg, *new_args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.warning(new_msg, *new_args, **kwargs)

    def error(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.error(new_msg, *new_args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.critical(new_msg, *new_args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        kwargs['exc_info'] = 1
        self.logger.exception(new_msg, *new_args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.log(level, new_msg, *new_args, **kwargs)


class SpaceObject(decometaclass.WrapBlueClass('destiny.ClientBall')):
    __persistdeco__ = 0
    __update_on_reload__ = 1

    def __init__(self):
        self.destructionEffectId = destructionEffectType.NONE
        self.exploded = False
        self.unloaded = getattr(self, '__unloadable__', False)
        self.model = None
        self.additionalModels = []
        self.animationStateObjects = {}
        self.released = False
        self.wreckID = None
        self._audioEntity = None
        self.logger = logging.getLogger('spaceObject.' + self.__class__.__name__)
        self.logger = SpaceObjectLogAdapter(self.logger, so_id=self.id)
        self.modelLoadedEvent = locks.Event()
        self.modelLoadSignal = Signal(signalName='modelLoadSignal')
        self.explosionModel = None
        self.typeID = None
        self.explosionBucketID = None
        self.spaceMgr = None
        self.sm = None
        self.spaceObjectFactory = None
        self.nextModel = None
        self._modelChangeCallbacks = []
        self._skinChangeTasklets = []
        self.skinMaterialSetID = None
        self.lockedFromRelease = False
        self.globalObjectHandlerThread = None
        self.explosionManager = ExplosionManager()

    def GetPositionCurve(self):
        return self

    def GetTypeID(self):
        if self.typeID is None:
            self.typeID = self.typeData.get('typeID', None)
        return self.typeID

    def SetServices(self, spaceMgr, serviceMgr):
        self.spaceMgr = spaceMgr
        self.sm = serviceMgr
        self.spaceObjectFactory = GetSofService().spaceObjectFactory

    def Prepare(self):
        self.typeID = self.typeData.get('typeID', None)
        self.explosionBucketID = fsdExplosionBuckets.GetExplosionBucketIDByTypeID(self.typeID)
        self.LoadModel()
        self.Assemble()
        try:
            self.SetControllerVariablesFromSlimItem(self.typeData.get('slimItem', None))
            self.SetControllerVariablesFromGraphicID()
            self.model.StartControllers()
        except AttributeError:
            pass

    def SetControllerVariablesFromGraphicID(self):
        gid = GetGraphicID(self.typeID)
        overrides = GetControllerVariableOverrides(gid)
        if overrides is not None:
            for name, value in overrides.iteritems():
                self.SetControllerVariable(name, value)

    def SetControllerVariablesFromSlimItem(self, slimItem):
        if slimItem is None:
            return
        ChangeControllerStateFromSlimItem(self.GetTypeID(), self, slimItem)

    def SetControllerVariableFromEvent(self, eventName, value, delay = None):
        if delay:
            blue.pyos.synchro.SleepSim(delay)
        controllerVariableName = SERVER_CONTROLLER_EVENT_NAMES_TO_CONTROLLER_VARIABLES.get(eventName)
        if controllerVariableName is None:
            try:
                self.model.HandleControllerEvent(eventName)
            except AttributeError:
                pass

        else:
            self.SetControllerVariable(controllerVariableName, value)

    def UnblockModelEvent(self):
        self.modelLoadedEvent.set()

    def _GetComponentRegistry(self):
        return self.ballpark.componentRegistry

    def SetControllerVariable(self, name, value):
        self.logger.debug('SpaceObject: set controller variable %s to %s', name, value)
        try:
            self.model.SetControllerVariable(name, float(value))
        except AttributeError:
            pass

        for state, item in self.animationStateObjects.items():
            try:
                item.SetControllerVariable(name, float(value))
            except AttributeError:
                pass

    def TriggerStateObject(self, state):
        if state in self.animationStateObjects:
            self.RemoveAndClearModel(self.animationStateObjects[state])
            del self.animationStateObjects[state]
        if state in self.typeData['animationStateObjects']:
            dnaToLoad = self.typeData['animationStateObjects'][state]
            stateObject = self.spaceObjectFactory.BuildFromDNA(dnaToLoad)
            self._SetupModelAttributes(stateObject, '%d_%s' % (self.id, state))
            if self.model is not None:
                stateObject.rotationCurve = self.model.rotationCurve
                stateObject.StartControllers()
                self._AddModelToScene(stateObject)
                self.animationStateObjects[state] = stateObject

    def GetModel(self):
        if not self.model:
            try:
                self.modelLoadedEvent.wait()
            except RuntimeError:
                return None

        return self.model

    def GetSkinState(self):
        characterID = self.typeData['slimItem'].charID
        itemID = self.typeData['slimItem'].itemID
        skinState = sm.GetService('cosmeticsSvc').GetCachedAppliedSkinState(characterID, itemID)
        return skinState

    def GetDNA(self):
        if self.skinMaterialSetID is None:
            skinState = self.GetSkinState()
            if skinState is None:
                materialSetID = self.typeData.get('slimItem').skinMaterialSetID
                if materialSetID is not None:
                    self.skinMaterialSetID = materialSetID
                    self.logger.info('SKIN STATES - Apply SKIN to NPC, material set: %s', materialSetID)
            else:
                skin_type = skinState.skin_type
                if skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                    return CosmeticsManager.CreateSOFDNAfromSkinState(skinState, self.GetTypeID())
                if skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                    skinData = skinState.skin_data
                    if skinData is not None:
                        self.skinMaterialSetID = sm.GetService('cosmeticsSvc').GetFirstPartySkinMaterialSetID(skinID=skinData.skin_id)
                elif skin_type == ShipSkinType.NO_SKIN:
                    pass
        return self._BuildSOFDNAFromTypeID()

    def _BuildSOFDNAFromTypeID(self):
        return gfxutils.BuildSOFDNAFromTypeID(typeID=self.GetTypeID(), materialSetID=self.skinMaterialSetID)

    def _LoadModelResource(self, fileName = None, sofDna = None):
        model = None
        sofDNA = sofDna or self.GetDNA()
        self.logger.debug("LoadModel fileName='%s' sofDNA='%s'", fileName, sofDNA)
        if sofDNA is not None and fileName is None:
            model = self.spaceObjectFactory.BuildFromDNA(sofDNA)
            skinState = self.GetSkinState()
            if skinState is not None:
                skin_type = skinState.skin_type
                if skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                    CosmeticsManager.UpdatePatternProjectionParametersFromSkinState(skinState, model, self.GetTypeID())
                    blend_mode = skinState.skin_data.slot_layout.pattern_blend_mode
                    if blend_mode is not None:
                        CosmeticsManager.SetBlendMode(model, blendMode=blend_mode)
        else:
            if fileName is None:
                fileName = self.typeData.get('graphicFile')
            if fileName is not None and len(fileName):
                model = blue.resMan.LoadObject(fileName)
        if model is None:
            self.logger.error('Error: Object type %s has invalid graphicFile, using graphicID: %s', self.typeData['typeID'], self.typeData['graphicID'])
        return model

    def _SetupModelAndAddToScene(self, fileName = None, loadedModel = None, addToScene = True, sofDna = None):
        if loadedModel:
            model = loadedModel
        else:
            model = self._LoadModelResource(fileName, sofDna)
        if self.released:
            return None
        if not model:
            self.logger.error('Could not load model for spaceobject. FileName:%s SofDna:%s typeID:%s', fileName, sofDna, getattr(self, 'typeID', '?'))
            return None
        self._SetupModelAttributes(model, '%d' % self.id)
        if addToScene:
            self._AddModelToScene(model)
        return model

    def _SetupModelAttributes(self, model, objectName):
        model.translationCurve = self
        model.rotationCurve = self
        model.name = objectName
        if hasattr(model, 'albedoColor'):
            model.albedoColor = eveSpaceObject.GetAlbedoColor(model)

    def _AddModelToScene(self, model):
        if model is not None:
            scene = self.spaceMgr.GetScene()
            if scene is not None:
                objectIsGlobal = False
                if hasattr(model, 'translationCurve'):
                    if model.translationCurve is not None and hasattr(model.translationCurve, 'isGlobal'):
                        objectIsGlobal = model.translationCurve.isGlobal
                scene.objects.append(model)
                if objectIsGlobal and type(model) == trinity.EveStation2:
                    if not self.globalObjectHandlerThread:
                        self.model = model
                        self.globalObjectHandlerThread = uthread.new(self._GlobalObjectHandlerThread)
            else:
                raise RuntimeError('Invalid object loaded by spaceObject: %s' % str(model))

    def IsModelWithinDistance(self, distance):
        distanceToObject = 0.0
        if self.model is not None:
            try:
                distanceToObject = self.model.translationCurve.surfaceDist
            except AttributeError:
                distanceToObject = geo2.Vec3Length(self.model.modelWorldPosition)

        return distanceToObject < distance

    def _GlobalObjectHandlerThread(self):
        while True:
            if self.model is not None:
                try:
                    shouldUpdate = self.IsModelWithinDistance(float(GRIDSIZE) * 1000.0)
                    self.model.mute = not shouldUpdate
                    self.model.display = shouldUpdate
                    self.model.update = shouldUpdate
                    blue.synchro.SleepSim(1000)
                except AttributeError:
                    break

            else:
                blue.synchro.Yield()
            if not self.globalObjectHandlerThread:
                break

    def LoadAdditionalModel(self, fileName = None, sofDna = None):
        model = self._SetupModelAndAddToScene(fileName=fileName, sofDna=sofDna)
        if model is not None:
            model.StartControllers()
        if fileName is not None:
            self.additionalModels.append(model)
        return model

    def NotifyModelLoaded(self):
        if self.model is not None:
            self.logger.debug('SpaceObject - NotifyModelLoaded')
            self.modelLoadedEvent.set()
            self.modelLoadSignal()
            self.sm.GetService('FxSequencer').NotifyModelLoaded(self.id)
        else:
            self.logger.warning('SpaceObject - NotifyModelLoaded called without a model present, no notification was done')

    def RegisterForModelLoad(self, func):
        self.modelLoadSignal.connect(func)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        self.model = self._SetupModelAndAddToScene(fileName, loadedModel, addToScene)
        if self.model is None:
            return
        if GetGroupID(self.GetTypeID()) == const.groupMercenaryDen:
            self.SetStaticRotation()
        self.SetupAnimationInformation(self.model)
        if notify:
            self.NotifyModelLoaded()

    def SetupAnimationInformation(self, model):
        if not hasattr(model, 'animationUpdater'):
            return
        if self._audioEntity is None:
            self._audioEntity = self._GetGeneralAudioEntity(model=model)
        if model is not None and model.animationUpdater is not None:
            model.animationUpdater.eventListener = self._audioEntity

    def Assemble(self):
        pass

    def _ShouldFaceTheSun(self):
        slimItem = self.typeData.get('slimItem')
        return slimItem.typeID in TYPES_THAT_ALWAYS_FACE_THE_SUN

    def _RotateToFaceTheSun(self):
        if (self.x, self.y, self.z) == (0.0, 0.0, 0.0):
            directionFromSunToMe = (1.0, 0.0, 0.0)
        else:
            directionFromSunToMe = (self.x, self.y, self.z)
        self.AlignToDirection(directionFromSunToMe)

    def SetStaticRotation(self):
        if self.model is None:
            return
        if self._ShouldFaceTheSun():
            self._RotateToFaceTheSun()
            return
        self.model.rotationCurve = None
        rot = self.typeData.get('dunRotation', None)
        if rot:
            yaw, pitch, roll = map(math.radians, rot)
            quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            if hasattr(self.model, 'rotation'):
                self.model.rotation = quat
            else:
                self.model.rotationCurve = trinity.Tr2RotationAdapter()
                self.model.rotationCurve.value = quat
                for stateObject in self.animationStateObjects.values():
                    stateObject.rotationCurve = self.model.rotationCurve

    def _FindClosestBallDir(self, constgrp):
        bp = self.sm.StartService('michelle').GetBallpark()
        dist = 1e+100
        closestID = None
        for ballID, slimItem in bp.slimItems.iteritems():
            if slimItem.groupID == constgrp:
                test = bp.DistanceBetween(self.id, ballID)
                if test < dist:
                    dist = test
                    closestID = ballID

        if closestID is None:
            return (1.0, 0.0, 0.0)
        ball = bp.GetBall(closestID)
        direction = geo2.Vec3SubtractD((self.x, self.y, self.z), (ball.x, ball.y, ball.z))
        return direction

    def FindClosestMoonDir(self):
        return self._FindClosestBallDir(const.groupMoon)

    def FindClosestPlanetDir(self):
        return self._FindClosestBallDir(const.groupPlanet)

    def GetStaticDirection(self):
        return self.typeData.get('dunDirection', None)

    def SetStaticDirection(self):
        if self.model is None:
            return
        self.model.rotationCurve = None
        direction = self.GetStaticDirection()
        if direction is None:
            self.logger.warning('No static direction defined - no rotation will be applied')
            return
        self.AlignToDirection(direction)

    def AlignToDirection(self, direction):
        if not self.model:
            return
        zaxis = direction
        if geo2.Vec3LengthSqD(zaxis) > 0.0:
            zaxis = geo2.Vec3NormalizeD(zaxis)
            xaxis = geo2.Vec3CrossD(zaxis, (0, 1, 0))
            if geo2.Vec3LengthSqD(xaxis) == 0.0:
                zaxis = geo2.Vec3AddD(zaxis, mathCommon.RandomVector(0.0001))
                zaxis = geo2.Vec3NormalizeD(zaxis)
                xaxis = geo2.Vec3CrossD(zaxis, (0, 1, 0))
            xaxis = geo2.Vec3NormalizeD(xaxis)
            yaxis = geo2.Vec3CrossD(xaxis, zaxis)
        else:
            self.logger.error('Invalid direction (%s). Unable to rotate it.', direction)
            return
        mat = ((xaxis[0],
          xaxis[1],
          xaxis[2],
          0.0),
         (yaxis[0],
          yaxis[1],
          yaxis[2],
          0.0),
         (-zaxis[0],
          -zaxis[1],
          -zaxis[2],
          0.0),
         (0.0, 0.0, 0.0, 1.0))
        quat = geo2.QuaternionRotationMatrix(mat)
        if hasattr(self.model, 'modelRotationCurve'):
            if not self.model.modelRotationCurve:
                self.model.modelRotationCurve = trinity.Tr2RotationAdapter()
            self.model.modelRotationCurve.value = quat
        else:
            self.model.rotationCurve = None

    def UnSync(self, model = None):
        if model is None:
            model = self.model
        if model is None:
            return
        scaling = 0.95 + random.random() * 0.1
        for adapter in model.Find(['trinity.Tr2RotationAdapter', 'trinity.Tr2TranslationAdapter']):
            adapter.RandomizeStart()
            adapter.ScaleTime(scaling)

    def Display(self, display = 1, canYield = True):
        if self.model is None:
            if display:
                self.logger.warning('Display - No model')
            return
        if canYield:
            blue.synchro.Yield()
        if eve.session.shipid == self.id and display and self.IsCloaked():
            self.sm.StartService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, 'effects.CloakNoAmim', 0, 1, 0, 5, 0)
            return
        if self.model:
            self.model.display = display

    def IsCloaked(self):
        return self.isCloaked

    def OnDamageState(self, damageState):
        pass

    def _OnDamageState(self, damageState):
        if self.model is not None and damageState is not None:
            if not hasattr(self.model, 'SetImpactDamageState'):
                return
            states = [ (d if d is not None else 0.0) for d in damageState ]
            self.model.SetImpactDamageState(states[0], states[1], states[2], False)

    def GetDamageState(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            return bp.GetDamageState(self.id)

    def _UpdateImpacts(self, model = None):
        if model is None:
            model = self.model
        states = self.GetDamageState()
        if states is not None and model is not None:
            damageState = [ (d if d is not None else 0.0) for d in states ]
            model.SetImpactDamageState(damageState[0], damageState[1], damageState[2], True)

    def DoFinalCleanup(self):
        if not self.sm.IsServiceRunning('FxSequencer'):
            return
        self.sm.GetService('FxSequencer').RemoveAllBallActivations(self.id)
        self.globalObjectHandlerThread = None
        if destructionEffectType.isExplosionOrOverride(self.destructionEffectId):
            self.ClearExplosion()
        if not self.released:
            self.destructionEffectId = destructionEffectType.NONE
            self.Release()
            SpaceObjectExplosionManager.AddExplosionTimeNotifications(self.id, 0, 0)
        elif self.HasModels():
            scene = self.spaceMgr.GetScene()
            self.ClearAndRemoveAllModels(scene)

    def ClearExplosion(self, model = None):
        if hasattr(self, 'gfx') and self.gfx is not None:
            self.RemoveAndClearModel(self.gfx)
            self.gfx = None
        if self.explosionModel is not None:
            if getattr(self, 'explosionDisplayBinding', False):
                self.explosionDisplayBinding.destinationObject = None
                self.explosionDisplayBinding = None
            self.RemoveAndClearModel(self.explosionModel)
            self.explosionModel = None

    def Release(self, origin = None):
        uthread2.StartTasklet(self._Release, origin)

    def _Release(self, origin = None):
        if self.released and not self.lockedFromRelease:
            return
        self.released = True
        if self.lockedFromRelease:
            return
        self._modelChangeCallbacks = []
        if destructionEffectType.isExplosionOrOverride(self.destructionEffectId):
            delay = self.Explode()
            if delay:
                blue.synchro.SleepSim(delay)
        elif self.destructionEffectId == destructionEffectType.DISSOLVE:
            destructionEffectManager = DestructionEffectManager(self)
            destructionEffectManager.PlayDissolveEffect()
        if self.destructionEffectId in destructionEffectType.DURATION_BY_DESTRUCTION_TYPE:
            delay = destructionEffectType.DURATION_BY_DESTRUCTION_TYPE[self.destructionEffectId]
            if delay:
                blue.synchro.SleepSim(delay)
        self.Display(display=0, canYield=False)
        for model in self.additionalModels:
            if model is not None:
                model.display = False

        if hasattr(self.model, 'animationUpdater') and self.model.animationUpdater is not None:
            self.model.animationUpdater.eventListener = None
        self.ClearAudio()
        scene = self.spaceMgr.GetScene()
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        lookingAt = camera.GetLookAtItemID()
        interestID = camera.GetTrackItemID()
        if self.destructionEffectId != destructionEffectType.NONE and (self.id == lookingAt or interestID == self.id):
            self.RemoveAllModelsFromScene(scene)
        else:
            self.ClearAndRemoveAllModels(scene)

    def ClearAudio(self):
        self._audioEntity = None
        if self.model is not None:
            if hasattr(self.model, 'observers') and len(self.model.observers) > 0:
                for observer in self.model.observers:
                    observer.observer = None

            if hasattr(self.model, 'animationUpdater') and self.model.animationUpdater is not None:
                self.model.animationUpdater.eventListener = None

    def HasModels(self):
        return self.model is not None

    def ClearAnimationStateObjects(self, scene = None):
        scene = scene or self.spaceMgr.GetScene()
        for stateObject in self.animationStateObjects.values():
            self.RemoveAndClearModel(stateObject, scene)

        self.animationStateObjects.clear()

    def ClearAndRemoveAllModels(self, scene):
        self.RemoveAndClearModel(self.model, scene)
        self.model = None
        for m in self.additionalModels:
            self.RemoveAndClearModel(m, scene)

        self.additionalModels = []
        self.ClearAnimationStateObjects()

    def RemoveAllModelsFromScene(self, scene):
        if scene is None:
            return
        scene.objects.fremove(self.model)
        for m in self.additionalModels:
            scene.objects.fremove(m)

        self.ClearAnimationStateObjects()

    def RemoveAndClearModel(self, model, scene = None):
        if model:
            self._Clearcurves(model)
        else:
            self.released = True
            return
        self.RemoveFromScene(model, scene)

    def _Clearcurves(self, model):
        if hasattr(model, 'translationCurve'):
            model.translationCurve = None
            model.rotationCurve = None

    def RemoveFromScene(self, model, scene):
        if scene is None:
            scene = self.spaceMgr.GetScene()
        if scene:
            scene.objects.fremove(model)

    def GetExplosionLookAtDelay(self):
        return eveSpaceObject.GetDeathExplosionLookDelay(self.model, self.radius)

    def GetTotalDestructionEffectTime(self):
        if destructionEffectType.isExplosionOrOverride(self.destructionEffectId):
            for delay, explosionBucketList in BALL_REMOVAL_DELAY_TO_EXPLOSION_BUCKETS.iteritems():
                if self.explosionBucketID in explosionBucketList:
                    return delay

        elif self.destructionEffectId in destructionEffectType.DURATION_BY_DESTRUCTION_TYPE:
            return destructionEffectType.DURATION_BY_DESTRUCTION_TYPE[self.destructionEffectId]
        return 60

    def Explode(self):
        if self.exploded:
            return 0
        slimItem = self.typeData.get('slimItem')
        self.sm.ScatterEvent('OnObjectExplode', slimItem.typeID, slimItem.itemID)
        self.exploded = True
        if gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            if self.explosionBucketID is not None and self.model is not None:
                locator = getattr(self.model, 'lastDamageLocatorHit', -1)
                self.logger.debug("Exploding explosion bucket '%s' at locator %s", self.explosionBucketID, locator)
                scene = self.spaceMgr.GetScene()
                special = self.destructionEffectId == destructionEffectType.EXPLOSION_OVERRIDE
                wreckSwitchTime, _, __ = SpaceObjectExplosionManager.ExplodeBucketForBall(self, scene, locator, special=special)
                return wreckSwitchTime
            self.logger.warning('GraphicID %s does not have an explosionBucketID. typeID: %s', self.typeData['graphicID'], self.typeID)
        return 0

    def IsTriggeredForDestruction(self):
        return self.destructionEffectId is not None and self.destructionEffectId is not destructionEffectType.NONE

    def PrepareForFiring(self):
        pass

    def GetEventNameFromSlimItem(self, defaultSoundUrl):
        slimItem = self.typeData.get('slimItem')
        eventName = spaceobjaudio.GetSoundUrl(slimItem, defaultSoundUrl)
        return eventName

    def SetupAmbientAudio(self, defaultSoundUrl = None, model = None):
        audioUrl = self.GetEventNameFromSlimItem(defaultSoundUrl)
        if audioUrl is None:
            return
        audentity = self._GetGeneralAudioEntity(model=model)
        if audentity is not None:
            spaceobjaudio.PlayAmbientAudio(audentity, audioUrl)

    def SetupSharedAmbientAudio(self, defaultSoundUrl = None):
        eventName = self.GetEventNameFromSlimItem(defaultSoundUrl)
        if eventName is None or self.model is None:
            return
        spaceobjaudio.SetupSharedEmitterForAudioEvent(self.id, self.model, eventName)

    def LookAtMe(self):
        pass

    def _GetGeneralAudioEntity(self, model = None, recreate = False):
        if model is None:
            model = self.model
        if model is None:
            self._audioEntity = None
            self.logger.warning('model is None, cannot play audio.')
        elif recreate or self._audioEntity is None:
            self._audioEntity = spaceobjaudio.SetupAudioEntity(model, self.id)
        return self._audioEntity

    def PlayGeneralAudioEvent(self, eventName):
        audentity = self._GetGeneralAudioEntity()
        if audentity is not None:
            spaceobjaudio.SendEvent(audentity, eventName)

    def GetNamedAudioEmitterFromObservers(self, emitterName):
        if getattr(self, 'model', None) is None:
            return
        for triObserver in self.model.Find('trinity.TriObserverLocal'):
            if triObserver.observer.name.lower() == emitterName:
                return triObserver.observer

    def PlaySound(self, event):
        if self.model is None:
            return
        if hasattr(self.model, 'observers'):
            for obs in self.model.observers:
                obs.observer.SendEvent(unicode(event))
                return

        self.logger.error("Space Object: %s can't play sound. Sound observer not found.", self.typeData.get('typeName', None))

    def OnSlimItemUpdated(self, slimItem):
        oldSlim = self.typeData['slimItem']
        self.typeData['slimItem'] = slimItem
        if getattr(oldSlim, 'skinMaterialSetID') != getattr(slimItem, 'skinMaterialSetID'):
            self._skinChangeTasklets.append(uthread2.StartTasklet(self.ChangeSkin))
        self.SetControllerVariablesFromSlimItem(slimItem)

    def ChangeSkin(self, structure_id = None, paintwork = None):
        if self.model is None:
            return
        oldModel = self.nextModel or self.model
        nextModel = self._LoadModelResource(None)
        blue.resMan.Wait()
        handled = False
        if sm.GetService('subway').InJump():
            handled = sm.GetService('subway').HandleSkinChange(nextModel)
        if not handled:
            self.fitted = False
            self.nextModel = self._SetupModelAndAddToScene(loadedModel=nextModel, addToScene=False)
            if self.nextModel is None:
                return
            self.SetupAnimationInformation(self.nextModel)
            self._SetupModelAttributes(self.nextModel, '%d' % self.id)
            self.ChangingSkin(self.nextModel)
            ChangeSkin(oldModel, self.nextModel, self.spaceMgr.GetScene(), postSkinChangeCallback=self.PostSkinChangeCallback)

    def ChangingSkin(self, nextModel):
        uthread.new(self.logoLoader.Load, self.nextModel, self.typeData.get('slimItem'))

    def PostChangingSkin(self):
        pass

    def CancelSkinChange(self):
        for skinChangeTasklet in self._skinChangeTasklets:
            skinChangeTasklet.kill()

        self._skinChangeTasklets = []
        if self.model != self.nextModel and self.nextModel is not None:
            self.PostSkinChangeCallback(self.model, self.nextModel)
        RemoveAllTemporaryModels(self.spaceMgr.GetScene())

    def PostSkinChangeCallback(self, oldModel, newModel):
        self.RemoveAndClearModel(oldModel)
        self.model = newModel
        self.model.clipSphereFactor2 = 0.0
        self.PostChangingSkin()
        self._GetGeneralAudioEntity(self.model, recreate=True)
        self.NotifyModelLoaded()
        for callback in self._modelChangeCallbacks:
            callback(newModel)

    def RegisterModelChangeNotification(self, callback):
        self._modelChangeCallbacks.append(callback)

    def UnregisterModelChangeNotification(self, callback):
        if callback in self._modelChangeCallbacks:
            self._modelChangeCallbacks.remove(callback)

    def LockFromRelease(self):
        self.lockedFromRelease = True

    def UnlockFromRelease(self, scene):
        self.lockedFromRelease = False
        if self.released:
            self.ClearAudio()
            self.ClearAndRemoveAllModels(scene)
