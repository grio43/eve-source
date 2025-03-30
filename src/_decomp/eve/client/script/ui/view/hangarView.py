#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarView.py
import math
import random
import evecamera
import evegraphics.utils as gfxutils
import evetypes
import geo2
import inventorycommon.const as invconst
import signals
import telemetry
import logging
import trinity
import uthread
import uthread2
import blue
import hangarRegistry as hangar
from fsdBuiltData.common.soundIDs import GetSoundEventName
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.ui.camera.cameraUtil import IsDynamicCameraMovementEnabled
from eve.client.script.ui.services.viewStateSvc import View
from eve.client.script.ui.station.navigation import HangarLayer
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib import appConst as const
from eve.common.script.sys.idCheckers import IsHighSecSystem
from shipcosmetics.common.const import CosmeticsType
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from eveSpaceObject import spaceobjanimation
from evegraphics.graphicEffects.skinChange import ChangeSkin, GetModelsToBeRemovedFromScene
from fsdBuiltData.common.graphicIDs import GetGraphicFile, GetSofHullName, GetSofFactionName, GetSofRaceName, GetSofLayoutNames, GetControllerVariableOverrides
from inventorycommon.util import IsSubsystemFlagVisible
from shipcosmetics.client.fittingsgateway.fittingsSignals import on_ship_cosmetics_changed
from shipprogression.boarding_moment.boardingMomentSvc import GetBoardingMomentService
from shipprogression.boarding_moment import get_boarding_moment_details, should_autoplay_boarding_moment, get_ship_shape_group, get_ship_size_group, get_ship_faction_group, get_unique_moment_id
from shipprogression.boarding_moment.skip import SkipController
from shipprogression.boarding_moment.ui.boarding_ui_controller import BoardingUIController
from stackless_response_router.exceptions import TimeoutException
from evegraphics.CosmeticsLoader import CosmeticsLoader
from uthread2 import call_after_simtime_delay
from evetypes import GetGraphicID
from eveaudio.helpers import CreateAudioObserver
from cosmetics.client.ships.ship_skin_signals import on_skin_state_set
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from uihider import CommandBlockerService
log = logging.getLogger(__name__)
REPLACE_DOCK = 1
REPLACE_SWITCHSHIPS = 2
REPLACE_UPDATE = 3
ACTIVITY_LEVEL_LOW = 0
ACTIVITY_LEVEL_MID = 1
ACTIVITY_LEVEL_HIGH = 2
HANGAR_DOCKING_STATE = 0
HANGAR_DOCKED_STATE = 1
HANGAR_UNDOCKING_STATE = 2
USE_CITADEL_HANGAR = False
PROPAGANDA_LAYOUT_NAME = 'hangar_announcements'

class HangarView(View):
    __guid__ = 'viewstate.HangarView'
    __notifyevents__ = ['OnDogmaItemChange',
     'OnDogmaAttributeChanged',
     'ProcessActiveShipChanged',
     'OnDamageStateChanged',
     'OnDirtLevelChanged',
     'OnStanceActive',
     'OnGraphicSettingsChanged',
     'OnEndChangeDevice',
     'OnRepairDone',
     'OnSpinThresholdReached',
     'OnHangarViewStateUpdated_Local',
     'OnSessionChanged',
     'OnItemChangeProcessed',
     'OnCorpLogoReady',
     'OnAllianceLogoReady']
    __dependencies__ = ['godma',
     'loading',
     'station',
     'invCache',
     'sceneManager',
     'clientDogmaIM',
     'cosmeticsSvc',
     'photo',
     'dockingHeroNotification']
    __overlays__ = {'sidePanels'}
    __layerClass__ = HangarLayer
    HANGAR_TYPE_OVERRIDE = None
    HANGAR_TYPE_OVERRIDE_VALUES = hangar.GetHangarTypeOverrideKeys()

    @classmethod
    def SetHangarOverride(cls, override):
        cls.HANGAR_TYPE_OVERRIDE = override
        hangar.HANGAR_TYPE_OVERRIDE = override
        currentView = sm.GetService('viewState').GetCurrentView()
        if currentView is not None and currentView.name == 'hangar':
            currentView.ReloadView()

    def __init__(self):
        View.__init__(self)
        self.scenePath = ''
        self.activeShipItem = None
        self.activeShipModel = None
        self.activeHangarScene = None
        self.activeHangarModel = None
        self.log = log
        self.activeHangarType = None
        self.sceneNeedsApplying = False
        self.restartHangarControllers = False
        self.skipDockingAnimation = False
        self.currentSceneGraphicID = -1
        self.currentHangarGraphicID = -1
        self.shipBehaviour = None
        self.droneBehaviour = None
        self._backupLights = None
        self._vfxMultiEffect = None
        self._fsbThread = None
        self._starting_boarding_moment = False
        self._undocking_in_progress = False
        self._undocking_started_signal = signals.Signal()
        self.cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))
        self.initialFogSceneSetting = 1.0
        on_ship_cosmetics_changed.connect(self.OnShipCosmeticsChanged)
        on_skin_state_set.connect(self._on_skin_state_set)

    def _on_skin_state_set(self, ship_instance_id, skin_state):
        if ship_instance_id != session.shipid:
            return
        log.info('SKIN STATES - space object %s received on_skin_state_set with %s' % (ship_instance_id, skin_state))
        if skin_state is not None:
            self.OnActiveShipSkinChange(self.GetActiveShipItemID(), None, updateSkin=True, reloadSubsystems=True)
        else:
            log.error('Failed to apply SKIN to ship: SKIN state is missing for ship: %s', ship_instance_id)

    def GetActiveShipTypeID(self):
        if self.activeShipItem is None:
            return
        return self.activeShipItem.typeID

    def GetActiveShipItemID(self):
        if self.activeShipItem is None:
            return
        return self.activeShipItem.itemID

    @telemetry.ZONE_METHOD
    def ShowView(self, **kwargs):
        if not session.stationid and not session.structureid:
            return
        if self.activeHangarScene is None:
            self.SetUpModels()
        if self.sceneManager.GetActiveScene() is None or self.sceneNeedsApplying:
            self.sceneManager.ApplyScene(self.activeHangarScene, ViewState.Hangar)
            self.DisableReflectionProbe()
            self.DisableShadows()
            self.sceneNeedsApplying = False
        View.ShowView(self, **kwargs)
        settings.user.ui.Set('defaultDockingView', ViewState.Hangar)
        if session.structureid:
            settings.user.ui.Set('defaultStructureView', ViewState.Hangar)
        sm.GetService('loginCampaignService').try_displaying_rookie_reward_pointer()
        if self._starting_boarding_moment:
            self.play_boarding_moment()

    @telemetry.ZONE_METHOD
    def HideView(self, **kwargs):
        pass

    def GetStationItemID(self):
        itemID = None
        if hasattr(self, 'station') and self.station is not None:
            if self.station.GetStationItem() is not None:
                itemID = self.station.GetStationItem().itemID
        return itemID

    def SetUpModels(self):
        self.activeShipModel = None
        self.activeShipItem = self.GetShipItemFromHangar(session.shipid)
        scMethods = hangar.GetHangarBehaviours(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID())
        self.shipBehaviour = scMethods['ship']()
        self.droneBehaviour = scMethods['drone']()
        self.LoadAndSetupScene(self.GetActiveShipTypeID())
        self.UpdateActivityLevel()

    def CleanUp(self):
        self.layer.camera = None
        self.sceneManager.UnregisterScene(ViewState.Hangar)
        self.ClearScene()

    def OnDocking(self):
        uthread.new(self.ReplaceExistingShipModel, REPLACE_DOCK)

    def OnSpinThresholdReached(self, spins):
        if self.activeHangarModel is not None:
            self.activeHangarModel.SetControllerVariable('spinCounter', spins)

    def OnItemChangeProcessed(self, item, itemInfo):
        if hasattr(self.shipBehaviour, 'OnItemChangeProcessed'):
            self.shipBehaviour.OnItemChangeProcessed(item, itemInfo)

    def OnHangarViewStateUpdated_Local(self, structureID, hangarViewState):
        self.updateHangarState(hangarViewState)

    def updateHangarState(self, hangarViewState = None):
        if session.structureid is None or self.activeHangarModel is None:
            return
        if not hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            return
        if hangarViewState is None:
            svc = sm.GetService('structureHangarViewSvc')
            if svc is None:
                return
            hangarViewState = svc.GetStructureHangarState()
        self.shipBehaviour.UpdateStructureState(hangarViewState, self.activeHangarModel)

    def OnHangarToHangar(self):
        uthread.new(self.ReplaceExistingShipModel, REPLACE_DOCK, fade=False)

    def LoadAndSetupScene(self, shipTypeID):
        self._undocking_in_progress = False
        itemID = self.GetStationItemID()
        self.shipBehaviour.SetDockingEffectGraphicID(hangar.GetDockingEffectGraphicID(self.GetStationType(), self.GetActiveShipTypeID(), itemID))
        self.shipBehaviour.SetEnlistmentDockingEnabled(hangar.isEnlistmentDockingEnabled(self.GetStationType(), self.GetActiveShipTypeID(), itemID))
        isANewHangar = hangar.GetHangarType(self.GetStationType(), self.GetActiveShipTypeID(), itemID) != self.activeHangarType
        if HangarView.HANGAR_TYPE_OVERRIDE is not None or isANewHangar or self.activeHangarScene is not None:
            self.currentHangarGraphicID = hangar.GetHangarModelGraphicID(self.GetStationType(), shipTypeID, itemID)
            self.activeHangarModel = self._LoadHangarModel(self.currentHangarGraphicID)
            self.activeHangarScene = self.LoadScene(shipTypeID, itemID)
            self.shipBehaviour.SetAnchorPoint(self.activeHangarModel, self.activeHangarScene)
            self.activeHangarScene.objects.append(self.activeHangarModel)
            self.activeHangarType = hangar.GetHangarType(self.GetStationType(), self.GetActiveShipTypeID(), itemID)
            self.StartHangarAnimations(self.activeHangarScene)
            uthread2.StartTasklet(self.updateCorruptionAndSuppressionStates)
            self.updateHangarState()
        self.restartHangarControllers = True

    def updateCorruptionAndSuppressionStates(self):
        if self.activeHangarModel is None:
            return
        try:
            css = sm.GetService('corruptionSuppressionSvc')
            if css is not None and hasattr(session, 'solarsystemid2'):
                suppressionStage, corruptionStage = (0, 0)
                maximumSuppressionStage = max(len(css.GetSuppressionStages()), 5)
                maximumCorruptionStage = max(len(css.GetCorruptionStages()), 5)
                corruptionStateData = css.GetCurrentSystemCorruption_Cached()
                if corruptionStateData is not None:
                    corruptionStage = corruptionStateData.stage or 0
                suppressionStateData = css.GetCurrentSystemSuppression_Cached()
                if suppressionStateData is not None:
                    suppressionStage = suppressionStateData.stage or 0
                suppression = float(suppressionStage) / float(maximumSuppressionStage)
                corruption = float(corruptionStage) / float(maximumCorruptionStage)
                self.activeHangarModel.SetControllerVariable('corruption', corruption)
                self.activeHangarModel.SetControllerVariable('suppression', suppression)
                if corruption > 0.0 or suppression > 0.0:
                    self.restartHangarControllers = True
        except TimeoutException:
            self.LogError('hangarView.updateCorruptionAndSuppressionStates: Timeout when getting corruption/suppression data')

    def _LoadHangarModel(self, graphicID):
        hangarModel = self._LoadSOFHangarModel(graphicID)
        controllerOverrides = GetControllerVariableOverrides(graphicID, {})
        for name, value in controllerOverrides.iteritems():
            hangarModel.SetControllerVariable(name, float(value))

        return hangarModel

    def StartHangarControllers(self):
        if self.activeHangarModel:
            try:
                self.activeHangarModel.StartControllers()
            except AttributeError:
                pass

    def _LoadSOFHangarModel(self, graphicID):
        if IsTriglavianSystem(session.solarsystemid2) and session.stationid:
            hull = GetSofHullName(graphicID)
            stationGraphicId = cfg.mapSolarSystemContentCache.npcStations[session.stationid].graphicID
            faction = GetSofFactionName(stationGraphicId)
            race = GetSofRaceName(stationGraphicId)
            hangarDna = '%s:%s:%s' % (hull, faction, race)
        else:
            typeID = self.GetStationType()
            outerStationGID = GetGraphicID(typeID)
            hull = GetSofHullName(graphicID)
            faction = GetSofFactionName(outerStationGID)
            race = GetSofRaceName(outerStationGID)
            layouts = list(GetSofLayoutNames(graphicID))
            if not IsHighSecSystem(session.solarsystemid2) and PROPAGANDA_LAYOUT_NAME in layouts:
                layouts.remove(PROPAGANDA_LAYOUT_NAME)
            layoutString = ''
            if layouts is not None and len(layouts) > 0:
                layoutString = 'layout?' + ';'.join(layouts)
            factionOverride = hangar.GetHangarFactionDataOverwrite(typeID, self.GetActiveShipTypeID(), self.GetStationItemID())
            if factionOverride is not None:
                hangarDna = '%s:%s:%s:%s' % (hull,
                 factionOverride,
                 race,
                 layoutString)
            else:
                hangarDna = '%s:%s:%s:%s' % (hull,
                 faction,
                 race,
                 layoutString)
        if hangarDna is None:
            self.LogError('%s._LoadSOFHangar(graphicID = %s): Trying to show a SOF hangar that is not in the SOF, Loading up scene only' % (self, graphicID))
            return
        return GetSofService().spaceObjectFactory.BuildFromDNA(hangarDna)

    @telemetry.ZONE_METHOD
    def LoadView(self, change = None, **kwargs):
        self.station.CleanUp()
        self.station.StopAllStationServices()
        self.station.Setup()
        self.SetUpModels()
        self.skipDockingAnimation = not IsDynamicCameraMovementEnabled()
        if 'lastView' in kwargs:
            lastView = kwargs.get('lastView')
            if lastView.name == 'structure':
                self.skipDockingAnimation = True
        View.LoadView(self, **kwargs)

    def LoadCamera(self, cameraID = None, reopen = False):
        cam = sm.GetService('sceneManager').SetPrimaryCamera(self.GetCameraID())
        if not hangar.isHangarCapital(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            camDist = 2050
            if self.activeHangarModel and hasattr(self.activeHangarModel, 'locatorSets'):
                maxCamDistanceLocatorSet = self.activeHangarModel.locatorSets.FindByName('maxCameraDistance')
                if maxCamDistanceLocatorSet and len(maxCamDistanceLocatorSet.locators) > 0:
                    locatorPosition = maxCamDistanceLocatorSet.locators[0][0]
                    camDist = geo2.Vec3Length(locatorPosition)
            cam.SetMinMaxZoomDefaults(camDist, 10.0)
            self._ConfigureCameraDockingAnimation(cam)
        if not reopen or self.activeShipModel is None:
            self.ReplaceExistingShipModel(REPLACE_UPDATE, fade=True)

    def GetCameraID(self):
        isInStation = session.stationid or session.structureid
        itemID = self.GetStationItemID()
        if hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), itemID):
            if hangar.isHangarCapital(self.GetStationType(), self.GetActiveShipTypeID(), itemID):
                return evecamera.CAM_MODULARHANGAR_CAPITAL
            else:
                return evecamera.CAM_MODULARHANGAR
        else:
            if not isInStation or not hangar.isHangarCapital(self.GetStationType(), self.GetActiveShipTypeID(), itemID):
                return evecamera.CAM_HANGAR
            return evecamera.CAM_CAPITALHANGAR

    @telemetry.ZONE_METHOD
    def UnloadView(self):
        self.CleanUp()

    def ReloadView(self):
        sm.GetService('viewState').ActivateView(ViewState.Hangar)

    def ClearScene(self):
        if self.shipBehaviour is not None:
            self.shipBehaviour.CleanScene()
            self.shipBehaviour = None
        if self.activeHangarScene:
            self.activeHangarScene.objects.removeAt(-1)
            self.activeHangarScene.postprocess = None
        self.activeHangarScene = None
        self.activeHangarModel = None
        self.activeShipModel = None
        self._vfxMultiEffect = None
        self.activeShipItem = None
        self.shipBehaviour = None
        self.droneBehaviour = None
        self.activeHangarType = None
        self.sceneNeedsApplying = False
        self._fsbThread = None

    def LoadScene(self, shipTypeID, itemID = None):
        self.currentSceneGraphicID = hangar.GetHangarSceneGraphicID(self.GetStationType(), shipTypeID, itemID)
        stationGraphicFile = GetGraphicFile(self.currentSceneGraphicID)
        if stationGraphicFile is None:
            self.LogError("Could not find a graphic file for graphicID '%s', returning and showing nothing" % self.currentSceneGraphicID)
        if HangarView.HANGAR_TYPE_OVERRIDE is not None:
            trinity.Load(stationGraphicFile, nonCached=True)
        scene, _ = self.sceneManager.LoadScene(stationGraphicFile, registerKey=ViewState.Hangar, applyScene=False)
        self.sceneNeedsApplying = True
        if scene is not None:
            if scene.postprocess is not None:
                if scene.postprocess.fog.intensity is not None:
                    self.initialFogSceneSetting = scene.postprocess.fog.intensity
        return scene

    def fadeToFromBlack(self, fadeToBlack, isQuick = None):
        if self._vfxMultiEffect is None:
            return
        if isQuick is not None:
            self._vfxMultiEffect.SetControllerVariable('F2B_isQuick', float(isQuick))
        self._vfxMultiEffect.SetControllerVariable('F2B_isBlack', float(fadeToBlack))

    def ReplaceExistingShipModel(self, eventType, fade = True, skipAnimation = False):
        itemID = self.GetActiveShipItemID()
        typeID = self.GetActiveShipTypeID()
        if not itemID or not typeID:
            return
        if self._starting_boarding_moment:
            fade = True
        if hangar.isHangarModular(self.GetStationType(), typeID, self.GetStationItemID()):
            self._ReplaceExistingShipModelModular(eventType, itemID, typeID, skipAnimation)
        else:
            newModel = self.shipBehaviour.LoadShipModel(itemID, typeID)
            isTooBig = self.IsShipTooBigToAnimate(typeID)
            if fade and (eventType == REPLACE_SWITCHSHIPS or isTooBig):
                if not self._starting_boarding_moment:
                    call_after_simtime_delay(self.fadeToFromBlack, 0.3, False)
            if self.activeShipModel:
                self.RemoveModelWithNameFromScene(self.activeShipModel.name)
                self.AddModelToScene(newModel)
            else:
                self.AddModelToScene(newModel)
            self.GetCamera().SetShip(newModel, typeID)
            if eventType == REPLACE_UPDATE or isTooBig or not IsDynamicCameraMovementEnabled():
                if fade and not self._starting_boarding_moment:
                    call_after_simtime_delay(self.fadeToFromBlack, 0.3, False)
                self.shipBehaviour.PlaceShip(newModel, typeID)
                self.shipBehaviour.PlaceReflectionProbe(self.activeHangarScene.reflectionProbe)
                self.SetHangarControllerStates(HANGAR_DOCKING_STATE if IsDynamicCameraMovementEnabled() else HANGAR_DOCKED_STATE)
                self.PlayUpdateShipSequence(fade)
            elif eventType == REPLACE_DOCK:
                duration = 12.0
                self.shipBehaviour.AnimateShipEntry(newModel, typeID, duration=duration)
                self.shipBehaviour.AnimateReflectionProbeEntry(self.activeHangarScene.reflectionProbe, duration)
                self.SetHangarControllerStates(HANGAR_DOCKING_STATE)
                self.PlayDockSequence(duration)
            elif eventType == REPLACE_SWITCHSHIPS:
                if skipAnimation:
                    self.shipBehaviour.PlaceShip(newModel, typeID)
                else:
                    duration = 7.0
                    self.shipBehaviour.AnimateShipEntry(newModel, typeID, duration=duration)
                    self.shipBehaviour.AnimateReflectionProbeEntry(self.activeHangarScene.reflectionProbe, duration)
            self._SetUpLightingRig(self.activeShipModel)
        if self.activeHangarScene:
            shipSkinModels = GetModelsToBeRemovedFromScene(self.activeHangarScene)
            for ship in shipSkinModels:
                self.activeHangarScene.objects.remove(ship)

            if self.activeShipModel is not None:
                self.ConfigureVFXMultiEffect(eventType == REPLACE_UPDATE or eventType == REPLACE_DOCK)
        if self.restartHangarControllers:
            self.StartHangarControllers()
            self.restartHangarControllers = False

    def SetHangarControllerStates(self, dockingState):
        self.activeHangarModel.SetControllerVariable('Docking_State', dockingState)

    def IsShipTooBigToAnimate(self, typeID):
        if hangar.isHangarCapital(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            return False
        groupID = evetypes.GetGroupID(typeID)
        return groupID in (invconst.groupSupercarrier,
         invconst.groupTitan,
         invconst.groupDreadnought,
         invconst.groupForceAux,
         invconst.groupLancerDreadnought)

    def PlayDockSequence(self, duration):
        endPos = self.shipBehaviour.GetAnimEndPosition()
        startPos = self.shipBehaviour.GetAnimStartPosition()
        camera = self.GetCamera()
        camera.AnimEnterHangar(self.activeShipModel, startPos=startPos, endPos=endPos, duration=duration)

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(self.GetCameraID())

    def GetAllDockedShips(self):
        if hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            if hasattr(self.shipBehaviour, 'GetAllDockedShips'):
                return self.shipBehaviour.GetAllDockedShips()
        else:
            return [self.activeShipModel]

    def PlaySwitchShipSequence(self, duration, fade = True):
        endPos = self.shipBehaviour.GetAnimEndPosition()
        startPos = self.shipBehaviour.GetAnimStartPosition()
        camera = self.GetCamera()
        camera.AnimSwitchShips(self.activeShipModel, startPos=startPos, endPos=endPos, duration=duration)
        if fade:
            self.sceneManager.FadeOut(1.0)

    def PlayUpdateShipSequence(self, fade = True):
        endPos = self.shipBehaviour.GetAnimEndPosition()
        self.GetCamera().PlaceShip(endPos)

    def StartHangarAnimations(self, scene):
        for obj in scene.objects:
            try:
                children = obj.children
            except AttributeError:
                continue

            for fx in children:
                if fx.name.startswith('sfx_'):
                    fx.display = True

    def ConfigureVFXMultiEffect(self, makeSceneBlack = False):
        if self.activeHangarScene is None or self.activeHangarScene.postprocess is None:
            return
        if self._vfxMultiEffect is None:
            self._vfxMultiEffect = trinity.Load(hangar.HANGAR_VFX_TRIGGERS_MULTIEFFECT)
            self.activeHangarScene.objects.append(self._vfxMultiEffect)
        if self._vfxMultiEffect is not None:
            self._vfxMultiEffect.SetParameter('PostProcess', self.activeHangarScene.postprocess)
            self._vfxMultiEffect.SetParameter('ship', self.activeShipModel)
            self._vfxMultiEffect.SetParameter('Hangar', self.activeHangarModel)
            if self.IsHangarModular():
                dock = self.shipBehaviour.GetActiveDock()
                if dock is not None:
                    self._vfxMultiEffect.SetParameter('activeDock', dock)
            shipTypeID = self.GetActiveShipTypeID()
            hType = hangar.GetHangarIdentifier(self.GetStationType(), shipTypeID, self.GetStationItemID())
            self._vfxMultiEffect.SetControllerVariable('HangarType', float(hType))
            self._vfxMultiEffect.SetControllerVariable('initialSceneFog', float(self.initialFogSceneSetting))
            unique_moment_id = get_unique_moment_id(shipTypeID)
            if unique_moment_id != 0.0:
                shape_group = 0.0
            else:
                shape_group = get_ship_shape_group(shipTypeID, self.activeShipModel)
            size_group = get_ship_size_group(shipTypeID, self.activeShipModel.GetBoundingSphereRadius())
            faction_group = get_ship_faction_group(shipTypeID)
            self._vfxMultiEffect.SetControllerVariable('shipShape', float(shape_group))
            self._vfxMultiEffect.SetControllerVariable('ShipSize', float(size_group))
            self._vfxMultiEffect.SetControllerVariable('faction', float(faction_group))
            self._vfxMultiEffect.SetControllerVariable('SpecificShip', float(unique_moment_id))
            if makeSceneBlack:
                self._vfxMultiEffect.SetControllerVariable('F2B_isBlack', 1.0)
            if not self._starting_boarding_moment and not GetBoardingMomentService().is_playing:
                call_after_simtime_delay(self.fadeToFromBlack, 0.3, False)
            for controller in self._vfxMultiEffect.controllers:
                controller.Start()

            for curveSet in self._vfxMultiEffect.curveSets:
                curveSet.Play()

    def RemoveModelWithNameFromScene(self, modelName):
        if self.activeHangarScene:
            modelToRemove = self.activeHangarScene.objects.FindByName(modelName)
            if modelToRemove:
                self.activeHangarScene.objects.remove(modelToRemove)

    def AddModelToScene(self, model):
        if self.activeHangarScene and model:
            self.activeHangarScene.objects.append(model)
        self.activeShipModel = model
        self._SetUpLightingRig(self.activeShipModel)
        enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, self.activeShipModel, enabledCosmetics)

    def PreSkinChange(self, oldModel, newModel):
        self.activeShipModel = newModel

    def PostSkinChange(self, oldModel, newModel):
        self._SetUpLightingRig(self.activeShipModel)
        enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, self.activeShipModel, enabledCosmetics)

    def _SetUpLightingRig(self, ship):
        if self.activeHangarModel is None:
            return
        if hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            return
        lightRigContainer = self.activeHangarModel.effectChildren.FindByName('ShipLights_Scaler')
        typeID = self.GetActiveShipTypeID()
        if ship is not None and lightRigContainer:
            lightRigContainer.scaling = (ship.boundingSphereRadius, ship.boundingSphereRadius, ship.boundingSphereRadius)
            shipCenter = self.shipBehaviour.GetShipCenter(ship, typeID)
            lightRigContainer.translation = (lightRigContainer.translation[0], shipCenter[1], lightRigContainer.translation[2])

    def GetStationType(self):
        if session.structureid:
            if hasattr(self, 'invCache'):
                return self.invCache.GetInventory(const.containerStructure).typeID
        else:
            stationItem = sm.GetService('station').stationItem
            if stationItem is not None and hasattr(stationItem, 'stationTypeID'):
                return sm.GetService('station').stationItem.stationTypeID
        return 0

    def GetShipItemFromHangar(self, shipID):
        hangarInv = self.invCache.GetInventory(const.containerHangar)
        hangarItems = hangarInv.List(const.flagHangar)
        for each in hangarItems:
            if each.itemID == shipID and each.categoryID == const.categoryShip:
                return each

    @telemetry.ZONE_METHOD
    def StartExitAnimation(self):
        self._undocking_in_progress = True
        self._undocking_started_signal()
        if hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            self.shipBehaviour.UpdateUndockStatus(1.0)
        elif self.activeHangarModel is not None:
            self.activeHangarModel.SetControllerVariable('Undock', 1.0)
            self.activeHangarModel.SetControllerVariable('Docking_State', HANGAR_UNDOCKING_STATE)
            if self.activeHangarScene is not None:
                for curveSet in self.activeHangarScene.curveSets:
                    if curveSet.name == 'Undock':
                        curveSet.scale = 1.0
                        curveSet.PlayFrom(0.0)
                        break

    @telemetry.ZONE_METHOD
    def StopExitAnimation(self):
        self._undocking_in_progress = False
        if hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            self.shipBehaviour.UpdateUndockStatus(0.0)
        else:
            self.activeHangarModel.SetControllerVariable('Undock', 0.0)
            self.activeHangarModel.SetControllerVariable('Docking_State', HANGAR_DOCKED_STATE)
            if self.activeHangarScene is not None:
                for curveSet in self.activeHangarScene.curveSets:
                    if curveSet.name == 'Undock':
                        curveSet.scale = -1.0
                        curveSet.PlayFrom(curveSet.GetMaxCurveDuration())
                        break

    def IsHangarModular(self):
        return hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID())

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if shipID == oldShipID:
            return
        newShipItem = self.GetShipItemFromHangar(shipID)
        if newShipItem is None:
            return
        self.activeShipItem = newShipItem
        self._starting_boarding_moment = should_autoplay_boarding_moment(newShipItem.typeID)
        if self.currentSceneGraphicID != hangar.GetHangarSceneGraphicID(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            self.ReloadView()
            return
        if self._starting_boarding_moment:
            self.play_boarding_moment()
        else:
            if not self.IsHangarModular():
                self.fadeToFromBlack(True, True)
            call_after_simtime_delay(self.ReplaceExistingShipModel, 0.2, REPLACE_SWITCHSHIPS)

    def play_boarding_moment(self):
        if self._undocking_in_progress:
            return
        uthread2.StartTasklet(self._play_boarding_moment)

    def OnStanceActive(self, shipID, stanceID):
        if shipID != session.shipid:
            return
        if self.activeShipModel is not None:
            spaceobjanimation.SetShipAnimationStance(self.activeShipModel, stanceID)

    def OnEndChangeDevice(self, *args):
        self.shipBehaviour.PlaceReflectionProbe(self.activeHangarScene.reflectionProbe)

    def OnGraphicSettingsChanged(self, *args):
        self.shipBehaviour.PlaceReflectionProbe(self.activeHangarScene.reflectionProbe)
        shaderQualityChanged = False
        shadowQualityChanged = False
        if len(args) > 0:
            for each in args[0]:
                shaderQualityChanged = shaderQualityChanged or 'shaderQuality' in each
                shadowQualityChanged = shadowQualityChanged or 'shadowQuality' in each

        if shaderQualityChanged:
            currentView = sm.GetService('viewState').GetCurrentView()
            if currentView is not None and currentView.name == 'hangar':
                currentView.ReloadView()
        if shadowQualityChanged:
            self.DisableShadows()
        self.DisableReflectionProbe()

    def OnEndChangeDevice(self, *args):
        self.DisableReflectionProbe()
        self.DisableShadows()

    def DisableReflectionProbe(self):
        if self.IsHangarModular():
            self.activeHangarScene.reflectionProbe = None

    def DisableShadows(self):
        sceneManager = sm.GetService('sceneManager')
        fisRenderjob = sceneManager.GetFisRenderJob()
        if fisRenderjob:
            fisRenderjob.DisableShadows()

    def OnActiveShipSkinChange(self, itemID, skinID, updateSkin = False, reloadSubsystems = False):
        isModularHangar = hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID())
        if updateSkin and (reloadSubsystems or self.shipBehaviour.ShouldSwitchSkin(skinID)) and itemID == session.shipid and itemID == self.GetActiveShipItemID() and self.activeShipModel:
            if isModularHangar and evetypes.GetGroupID(self.GetActiveShipTypeID()) == const.groupTacticalDestroyer:
                newShipModel = self.shipBehaviour.LoadShipModel(itemID, self.GetActiveShipTypeID(), skipSetupAnimation=True)
            else:
                newShipModel = self.shipBehaviour.LoadShipModel(itemID, self.GetActiveShipTypeID())
            if newShipModel is not None:
                ChangeSkin(self.activeShipModel, newShipModel, self.activeHangarScene, self.PreSkinChange, self.PostSkinChange)
                if isModularHangar:
                    self.shipBehaviour.ProcessSkinChange(newShipModel)
                self.ConfigureVFXMultiEffect()

    def OnShipCosmeticsChanged(self, ship_id, cosmetics_types):
        stationType = self.GetStationType()
        if stationType is 0 or not hasattr(self, 'station'):
            return
        if not hangar.isHangarModular(stationType, self.GetActiveShipTypeID(), self.GetStationItemID()):
            uthread.new(self.cosmeticsLoader.SetCosmeticsOnShip, self.activeShipModel, cosmetics_types)
        elif hasattr(self.shipBehaviour, 'OnShipCosmeticsChanged'):
            self.shipBehaviour.OnShipCosmeticsChanged(ship_id, cosmetics_types)

    def OnCorpLogoReady(self, _corpID, _size):
        if not hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            self._UpdateShipCosmetics()

    def OnAllianceLogoReady(self, _allianceID, _size):
        if not hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            self._UpdateShipCosmetics()

    def OnSessionChanged(self, _isremote, _session, change):
        if not hangar.isHangarModular(self.GetStationType(), self.GetActiveShipTypeID(), self.GetStationItemID()):
            if 'corpid' in change or 'allianceid' in change:
                self._UpdateShipCosmetics()

    def _UpdateShipCosmetics(self):
        enabledCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        self.OnShipCosmeticsChanged(session.shipid, enabledCosmetics)

    def OnDamageStateChanged(self, itemID, _attributeID, _newValue, _oldValue):
        if self.GetActiveShipItemID() == itemID:
            if self.droneBehaviour.GetDronesActive():
                self.droneBehaviour.StartRepairDroneSequence(itemID, self.activeShipModel, self.shipBehaviour)
            else:
                self.shipBehaviour.SetShipDamage(itemID, self.activeShipModel)

    def OnRepairDone(self, itemIDs):
        if hasattr(self.shipBehaviour, 'OnShipsRepaired'):
            self.shipBehaviour.OnShipsRepaired(itemIDs)
        if session.shipid in itemIDs:
            if self.droneBehaviour.GetSeekTargetData(self.activeHangarModel):
                self.droneBehaviour.SetDronesActive(True)
        if self._vfxMultiEffect:
            self._vfxMultiEffect.SetControllerVariable('triggerRepairDrones', 1.0)

    def OnDirtLevelChanged(self, itemID):
        if self.GetActiveShipItemID() == itemID:
            self.shipBehaviour.SetShipDirtLevel(itemID, self.activeShipModel)

    def OnDogmaItemChange(self, item, change):
        if item.locationID == change.get(const.ixLocationID, None) and item.flagID == change.get(const.ixFlag):
            return
        if IsSubsystemFlagVisible(item.flagID):
            if self.activeShipItem.itemID is not item.itemID:
                self.OnActiveShipSkinChange(self.GetActiveShipItemID(), None, updateSkin=True, reloadSubsystems=True)
        elif self.activeShipItem and self.activeShipModel is not None:
            self.shipBehaviour.FitTurrets(self.activeShipItem.itemID, self.activeShipItem.typeID, self.activeShipModel)

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if shipID != session.shipid or attributeID != const.attributeIsOnline:
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if itemID not in dogmaLocation.dogmaItems:
            return
        dogmaItem = dogmaLocation.dogmaItems[itemID]
        self.shipBehaviour.UpdateTurretState(dogmaItem)

    def UpdateActivityLevel(self):
        activityLevel = self._GetActivityLevel(len(self.station.guests))
        if self.activeHangarModel is not None:
            self.activeHangarModel.SetControllerVariable('activityLevel', activityLevel)
            if IsHighSecSystem(session.solarsystemid2):
                self.activeHangarModel.SetControllerVariable('enablePropaganda', 1.0)

    def _GetActivityLevel(self, numGuests):
        itemID = self.GetStationItemID()
        midTH, highTH = hangar.GetHangarMidAndHighActivityThresholds(self.GetStationType(), self.GetActiveShipTypeID(), itemID)
        if numGuests > highTH:
            return ACTIVITY_LEVEL_HIGH
        elif numGuests > midTH:
            return ACTIVITY_LEVEL_MID
        else:
            return ACTIVITY_LEVEL_LOW

    def _ConfigureCameraDockingAnimation(self, cam):

        def _pickRandomAnim(mapping):
            if len(mapping) < 1:
                self.LogError('Hangar camera dock-animation mapping is misconfigured. defaulting to the basic dock')
                return None
            totalWeight = 0
            thresholds = []
            for each in mapping:
                if len(each) != 8:
                    self.LogError('Hangar camera dock-animation mapping is misconfigured. defaulting to the basic dock')
                    return None
                totalWeight += each[0]
                thresholds.append(totalWeight)

            if totalWeight < 1:
                return None
            randomNbr = random.randint(0, totalWeight - 1)
            i = 0
            for i, t in enumerate(thresholds):
                if randomNbr < t:
                    break

            return mapping[i][1:8]

        itemID = None
        if self.station.GetStationItem() is not None:
            itemID = self.station.GetStationItem().itemID
        mapping = hangar.GetHangarDockCameraMapping(self.GetStationType(), self.GetActiveShipTypeID(), itemID)
        c = _pickRandomAnim(mapping)
        if c is not None and len(c) == 7:
            cam.SetHangarAnimationParameters(tuple(c[0:2]), tuple(c[2:4]), tuple(c[4:6]), c[6])

    def _ReplaceExistingShipModelModular(self, eventType, itemID, typeID, skipAnimation):
        if eventType == REPLACE_DOCK:
            if not self._starting_boarding_moment:
                call_after_simtime_delay(self.fadeToFromBlack, 0.1, False, False)
            camera = self.GetCamera()
            self.SetHangarControllerStates(HANGAR_DOCKING_STATE)
            camera.AnimEnterHangar(self.activeShipModel, None, None)
            if not self.shipBehaviour.IsInitialized():
                eventType = REPLACE_UPDATE
                self.LogWarn('hangarView._ReplaceExistingShipModelModular: swap event received before initial load')
        if eventType == REPLACE_UPDATE:
            hangarItems = []
            if self.invCache is not None:
                hangarInv = self.invCache.GetInventory(const.containerHangar)
                hangarItems = hangarInv.List(const.flagHangar)
            listOfOtherShips = []
            for each in hangarItems:
                if each.categoryID == const.categoryShip:
                    if hasattr(each, 'singleton') and each.singleton:
                        listOfOtherShips.append(self.GetShipItemFromHangar(each.itemID))

            self.shipBehaviour.UpdateActiveShipIDs(self.GetActiveShipTypeID(), self.GetActiveShipItemID())
            self.shipBehaviour.populateDocksWithInventoryShips(listOfOtherShips, self.activeHangarScene, self.activeHangarModel)
            ship = self.shipBehaviour.PlaceShip(itemID, typeID, self.skipDockingAnimation)
            if ship is not None and self.activeShipModel is not None:
                if ship.name == self.activeShipModel.name:
                    self.activeShipModel = ship
                    return
            self.GetCamera().AnimEnterHangar(ship, None, None)
            if not self._starting_boarding_moment:
                call_after_simtime_delay(self.fadeToFromBlack, 0.1, False, False)
            self.activeShipModel = ship
        elif eventType == REPLACE_SWITCHSHIPS:
            self.shipBehaviour.UpdateActiveShipIDs(self.GetActiveShipTypeID(), self.GetActiveShipItemID())
            ship = self.shipBehaviour.PlaceShip(itemID, typeID, self.skipDockingAnimation or skipAnimation)
            self.activeShipModel = ship
            for each in self.activeHangarModel.controllers:
                each.HandleEvent('platform_switch_audio')

    def _play_boarding_moment(self):
        ui_controller = BoardingUIController()
        bmSvc = GetBoardingMomentService()
        bmSvc.is_playing = True
        sm.GetService('ui').SetUiToggleState(False)
        sm.GetService('ui').HideUi(duration=1.0, except_layers=[ui_controller.get_layer()])
        command_blocker = CommandBlockerService.instance()
        block_token = command_blocker.block(['cmd.category.window', 'window', 'menucore'])
        self.fadeToFromBlack(True, True)
        if self._vfxMultiEffect:
            self._vfxMultiEffect.SetControllerVariable('firstShipBoarding_ME', 1.0)
            self._vfxMultiEffect.SetControllerVariable('MomentSteps', 0.0)
        uthread2.sleep(1.0)
        self.ReplaceExistingShipModel(REPLACE_SWITCHSHIPS, skipAnimation=True)
        trinity.WaitForResourceLoads()
        moments, shape_group, size_group, faction_group, unique_moment_id = get_boarding_moment_details(self.GetActiveShipTypeID(), self.activeShipModel)
        if not moments or self._undocking_in_progress:
            ui_controller.Close()
            sm.GetService('ui').SetUiToggleState(True)
            sm.GetService('ui').ShowUi(duration=1.0)
            block_token.dispose()
            bmSvc.is_playing = False
            if self._vfxMultiEffect:
                self._vfxMultiEffect.SetControllerVariable('MomentSteps', 0.0)
                self._vfxMultiEffect.SetControllerVariable('fsbSkip', 1.0)
            return
        if self._vfxMultiEffect:
            self._vfxMultiEffect.SetControllerVariable('firstShipBoarding_ME', 1.0)
            self._vfxMultiEffect.SetControllerVariable('MomentSteps', 0.0)
            self._vfxMultiEffect.SetControllerVariable('shipShape', float(shape_group))
            self._vfxMultiEffect.SetControllerVariable('ShipSize', float(size_group))
            self._vfxMultiEffect.SetControllerVariable('faction', float(faction_group))
            self._vfxMultiEffect.SetControllerVariable('SpecificShip', float(unique_moment_id))
        oldNebulaIntensity = 1.0
        if self.activeHangarScene:
            oldNebulaIntensity = self.activeHangarScene.nebulaIntensity
            self.activeHangarScene.nebulaIntensity = 0.2
        bmSvc.SetSeen(self.GetActiveShipTypeID())
        scene_manager = sm.GetService('sceneManager')
        scene_manager.UnregisterCamera(evecamera.CAM_VCS_CONSUMER)
        vcs_camera = scene_manager.GetVirtualCamera()
        vcs_camera.vcsInterface.SetScene(self.activeHangarScene)
        ui_controller.SetContext(context={'typeID': self.GetActiveShipTypeID(),
         'shape': shape_group,
         'size': size_group,
         'model': self.activeShipModel,
         'moments': moments})

        def _offset_camera_by_locator(camera, locator_name):
            if not locator_name:
                return
            camera_offset_pos = camera.positionBehaviours.FindByName('Offset')
            camera_offset_poi = camera.pointOfInterestBehaviours.FindByName('Offset')
            if not camera_offset_pos and not camera_offset_poi:
                return
            locator = self.activeShipModel.locators.FindByName(locator_name)
            if locator and camera_offset_pos:
                camera_offset_pos.offset = locator.transform[3][:3]
            if locator and camera_offset_poi:
                camera_offset_poi.offset = locator.transform[3][:3]

        def _offset_camera_by_model_position(camera, offset):
            camera_offset_pos = camera.positionBehaviours.FindByName('BoundingSphereOffset')
            camera_offset_poi = camera.pointOfInterestBehaviours.FindByName('BoundingSphereOffset')
            if camera_offset_pos:
                camera_offset_pos.offset = offset
            if camera_offset_poi:
                camera_offset_poi.offset = offset

        def _handle_cleanup():
            self._undocking_started_signal.disconnect(do_skip)
            if self.GetCameraID() == evecamera.CAM_MODULARHANGAR:
                self.GetCamera().SetShip(self.activeShipModel, self.GetActiveShipTypeID(), changingShip=False)
            else:
                self.GetCamera().SetShip(self.activeShipModel, self.GetActiveShipTypeID())
            if self._vfxMultiEffect:
                self._vfxMultiEffect.SetControllerVariable('MomentSteps', 0.0)
                self._vfxMultiEffect.SetControllerVariable('fsbSkip', 1.0)
            scene_manager.SwitchFromVirtualCamera()
            scene_manager.UnregisterCamera(vcs_camera.cameraID)
            self.activeHangarScene.nebulaIntensity = oldNebulaIntensity
            if hasattr(self.activeShipModel, 'observers'):
                obs = self.activeShipModel.observers.FindByName('ship_sfx')
                if obs is not None:
                    obs.observer.SendEvent('shipsounds_stop', True)
            self.fadeToFromBlack(False, False)
            skip_controller.Stop()
            ui_controller.Close()
            sm.GetService('ui').SetUiToggleState(True)
            sm.GetService('ui').ShowUi(duration=1.0)
            block_token.dispose()
            if self.IsHangarModular():
                self.shipBehaviour.FinishFSB()
            bmSvc.is_playing = False

        def do_skip():
            _fsbThread.Kill()
            _handle_cleanup()

        def handle_fsb():
            soundID = evetypes.GetSoundID(self.GetActiveShipTypeID())
            fadedSleepDuration = 0.2
            if soundID is not None:
                soundUrl = GetSoundEventName(soundID)
                if hasattr(self.activeShipModel, 'observers'):
                    obs = self.activeShipModel.observers.FindByName('ship_sfx')
                    if obs is not None:
                        obs.observer.SendEvent(unicode(soundUrl), True)
                    else:
                        newObserver = CreateAudioObserver('ship_sfx')
                        self.activeShipModel.observers.append(newObserver)
                        uthread2.sleep(0.1)
                        fadedSleepDuration = 0.1
                        newObserver.observer.SendEvent(unicode(soundUrl), True)
            uthread2.sleep(fadedSleepDuration)
            if self.IsHangarModular():
                self.shipBehaviour.PrepareFSB(self._vfxMultiEffect)
            modelOffset = getattr(self.activeShipModel, 'boundingSphereCenter', (0.0, 0.0, 0.0))
            modelOffset = geo2.Vec3Scale(modelOffset, -1.0)
            self.activeShipModel.clipSphereFactor = 0.001
            scene_manager.SwitchToVirtualCamera()
            for i, moment in enumerate(moments):
                res_path = moment['camera']
                try:
                    camera = vcs_camera.vcsInterface.AddCameraFromFile(res_path)
                except Exception as exception:
                    log.exception('Boarding Moment - error loading camera {}'.format(res_path))
                    continue

                camera.positionAnchors.extend([self.activeShipModel])
                camera.pointOfInterestAnchors.extend([self.activeShipModel])
                _offset_camera_by_locator(camera, moment.get('locator', None))
                _offset_camera_by_model_position(camera, modelOffset)
                vcs_camera.vcsInterface.LerpToCamera(camera, 0)
                animationLength = camera.animationTimelineLength
                if self._vfxMultiEffect:
                    self._vfxMultiEffect.SetControllerVariable('MomentSteps', moment['step'])
                    self._vfxMultiEffect.SetControllerVariable('boardingStepDuration', animationLength)
                ui_controller.TriggerStep(moment, animationLength)
                uthread2.sleep(animationLength)

            vcs_camera.vcsInterface.LerpToCamera(vcs_camera.vcsInterface.externalCamera, 0)
            scene_manager.SnapLastCameraToVirtualCamera()
            _handle_cleanup()

        if self._fsbThread is not None:
            self._fsbThread.Kill()
        _fsbThread = uthread2.start_tasklet(handle_fsb)
        self._fsbThread = _fsbThread
        skip_controller = SkipController(skip_func=do_skip)
        self._undocking_started_signal.connect(do_skip)
        skip_controller.Start(ui_controller.get_layer())
        self._starting_boarding_moment = False
