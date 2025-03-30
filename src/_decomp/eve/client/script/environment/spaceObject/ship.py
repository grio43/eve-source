#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\ship.py
from eveexceptions.exceptionEater import ExceptionEater
from inventorycommon.util import IsModularShip
import blue
import uthread2
import uthread
import eve.common.lib.appConst as const
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from eveSpaceObject import multiHullComponent
from eveSpaceObject import spaceobjanimation
import destiny
import geo2
import evegraphics.utils as gfxutils
from evegraphics.CosmeticsLoader import CosmeticsLoader
from eveaudio.const import ActingParty
from eveaudio.turrets import setupTurretMovementAudio
from cosmetics.client.ships.ship_skin_signals import on_skin_state_set
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from logging import getLogger
logger = getLogger(__name__)

class Ship(SpaceObject):
    __notifyevents__ = ['OnAllianceLogoReady', 'OnCorpLogoReady']

    def __init__(self):
        SpaceObject.__init__(self)
        self.cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))
        sm.RegisterNotify(self)
        self.cosmeticsItems = []
        on_skin_state_set.connect(self._on_skin_state_set)
        self.cosmeticsManager = CosmeticsManager()
        self.activeTargetID = None
        self.fitted = False
        self.cachedShip = None
        self.fittingThread = None
        self.turrets = []
        self.modules = {}
        self.stanceID = None
        self.lastStanceID = None
        self._multiHullComponent = multiHullComponent.MultiHullComponent(self.id) if self.IsModularShip() else None
        self.damageOverTimeTaken = 0.0
        self.visualDamageThread = None
        if self._multiHullComponent is not None:
            self._multiHullComponent.SetSubsystemModules(self.typeData.get('slimItem').modules)

    def _on_skin_state_set(self, ship_instance_id, skin_state):
        if ship_instance_id != self.id:
            return
        logger.info('SKIN STATES - space object %s received on_skin_state_set with %s' % (ship_instance_id, skin_state))
        if skin_state is not None:
            skin_type = skin_state.skin_type
            if skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                skinID = skin_state.skin_data.skin_id
                self.skinMaterialSetID = sm.GetService('cosmeticsSvc').GetFirstPartySkinMaterialSetID(skinID)
                self._ApplySkin(skinMaterialSetID=self.skinMaterialSetID)
            elif skin_type == ShipSkinType.NO_SKIN:
                self.skinMaterialSetID = None
                self._ApplySkin(skinMaterialSetID=self.skinMaterialSetID)
            elif skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                self.skinMaterialSetID = None
                self._ApplySkin(skinMaterialSetID=self.skinMaterialSetID)
            else:
                logger.error('Failed to apply SKIN to ship: SKIN type %s is not supported', skin_type)

    def _ApplySkin(self, skinMaterialSetID):
        self._skinChangeTasklets.append(uthread2.StartTasklet(self.ChangeSkin))

    def IsModularShip(self):
        return IsModularShip(self.GetTypeID())

    def _BuildSOFDNAFromTypeID(self):
        multiHullTypeIDList = None if self._multiHullComponent is None else self._multiHullComponent.GetTypeIDList()
        return gfxutils.BuildSOFDNAFromTypeID(typeID=self.GetTypeID(), materialSetID=self.skinMaterialSetID, multiHullTypeIDList=multiHullTypeIDList)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True, canYield = True):
        SpaceObject.LoadModel(self, fileName, loadedModel, notify, addToScene)
        self.UpdateCosmeticsItems()
        self.Display(1, canYield=False)

    def OnSubSystemChanged(self, newSlim):
        self.typeData['slimItem'] = newSlim
        if self._multiHullComponent is not None:
            self._multiHullComponent.SetSubsystemModules(self.typeData.get('slimItem').modules)
            self.UnfitHardpoints()
            self.RemoveAndClearModel(self.model)
            self.LoadModel(canYield=False)
            self.FitHardpoints(self.model)

    def GetStanceIDFromSlimItem(self, slimItem):
        if slimItem.shipStance is None:
            return
        _, _, stanceID = slimItem.shipStance
        return stanceID

    def OnAllianceLogoReady(self, allianceID, _size):
        if self.cosmeticsLoader.HasID(allianceID):
            uthread.new(self.cosmeticsLoader.Update, self.model, self.cosmeticsItems)

    def OnCorpLogoReady(self, corpID, _size):
        if self.cosmeticsLoader.HasID(corpID):
            uthread.new(self.cosmeticsLoader.Update, self.model, self.cosmeticsItems)

    def GetCosmeticsFromSlimItem(self, slimItem):
        if slimItem.cosmeticsItems is None:
            return
        items = slimItem.cosmeticsItems
        return items

    def UpdateCosmeticsItems(self):
        uthread.new(self.cosmeticsLoader.Load, self.model, self.typeData['slimItem'])

    def OnDamageState(self, damageState):
        self._OnDamageState(damageState)

    def GracefulEffectPropagatorRemover(self, sleepTime):
        self.model.SetControllerVariable('gracefullyRemove', 1.0)
        blue.synchro.SleepSim(sleepTime)
        if not self.visualDamageThread:
            self.model.SetControllerVariable('gracefullyRemove', 0.0)
            self.model.SetControllerVariable('explosive_damageAmount', self.damageOverTimeTaken)
            return
        fxSequencer = sm.GetService('FxSequencer')
        fxSequencer.OnSpecialFX(self.id, None, None, self.id, None, 'effects.VisualDamageSystemShipEffect', 1, 0, None, graphicInfo={})

    def UpdateDamageOverTime(self):
        currentDamageOverTimeTaken = getattr(self.typeData['slimItem'], 'dotHpPercentageApplied', 0.0)
        if currentDamageOverTimeTaken > 0.0:
            self.damageOverTimeTaken = currentDamageOverTimeTaken / 4.0
            self.visualDamageThread = None
            fxSequencer = sm.GetService('FxSequencer')
            fxSequencer.OnSpecialFX(self.id, None, None, self.id, None, 'effects.VisualDamageSystemShipEffect', 1, 1, None, graphicInfo={})
            self.model.SetControllerVariable('gracefullyRemove', 0.0)
            self.model.SetControllerVariable('explosive_damageAmount', self.damageOverTimeTaken)
            if self.model:
                self.model.SetControllerVariable('boundingSphereRadius', self.model.boundingSphereRadius)
        elif self.damageOverTimeTaken > 0.0 and self.visualDamageThread is None:
            self.visualDamageThread = uthread.new(self.GracefulEffectPropagatorRemover, 18000)

    def OnSlimItemUpdated(self, slimItem):
        SpaceObject.OnSlimItemUpdated(self, slimItem)
        with ExceptionEater('ship::OnSlimItemUpdated failed'):
            self.typeData['slimItem'] = slimItem
            stanceID = self.GetStanceIDFromSlimItem(self.typeData['slimItem'])
            if stanceID != self.stanceID:
                self.lastStanceID = self.stanceID
                self.stanceID = stanceID
                spaceobjanimation.SetShipAnimationStance(self.model, stanceID)
            if hasattr(self.typeData['slimItem'], 'cosmeticsItems'):
                self.cosmeticsItems = self.GetCosmeticsFromSlimItem(slimItem)
                self.UpdateCosmeticsItems()
            if hasattr(self.typeData['slimItem'], 'dotHpPercentageApplied'):
                self.UpdateDamageOverTime()

    def AddChildEffect(self, effect):
        if self.model:
            self.model.effectChildren.append(effect)

    def RemoveChildEffect(self, effect):
        if not self.model:
            return
        if effect in self.model.effectChildren:
            effect.mute = True
            self.model.effectChildren.fremove(effect)

    def _SetInitialState(self, model = None):
        if model is None:
            model = self.model
        stanceID = self.GetStanceIDFromSlimItem(self.typeData['slimItem'])
        if stanceID is not None:
            self.stanceID = stanceID
            spaceobjanimation.SetShipAnimationStance(model, self.stanceID)
        if self.mode == destiny.DSTBALL_WARP:
            self.SetControllerVariable('IsWarping', True)
            try:
                model.boosters.warpIntensity = 1
            except AttributeError:
                pass

            if session.shipid != self.id:
                self.sm.GetService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, 'effects.WarpIn', 0, 1, 0)
        if session.shipid == self.id:
            self.SetControllerVariable(ActingParty.__name__, ActingParty.firstParty.value)

    def Assemble(self):
        self.AssembleModel(self.model)

    def AssembleModel(self, model):
        if model is None:
            return
        self.UnSync(model)
        if self.id == eve.session.shipid:
            self.CheckAmbientAudio()
        self.FitHardpoints(model)
        self._SetInitialState(model)
        self._UpdateImpacts(model)

    def Release(self):
        if self.released:
            return
        if self.model is None:
            return
        self.modules = {}
        SpaceObject.Release(self, 'Ship')
        audsvc = self.sm.GetServiceIfRunning('audio')
        if audsvc.lastLookedAt == self:
            audsvc.lastLookedAt = None

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()
        self.CheckAmbientAudio()

    def CheckAmbientAudio(self):
        audsvc = self.sm.GetServiceIfRunning('audio')
        if audsvc.active:
            lookedAt = audsvc.lastLookedAt
            if lookedAt is None:
                self.SetupAmbientAudio()
                audsvc.lastLookedAt = self
            elif lookedAt is not self:
                lookedAt.PlayGeneralAudioEvent('shipsounds_stop')
                self.SetupAmbientAudio()
                audsvc.lastLookedAt = self
            else:
                return

    def FitBoosters(self, alwaysOn = False, enableTrails = True, isNPC = False):
        if self.typeID is None:
            return
        raceName = self.typeData.get('sofRaceName', None)
        if raceName is None:
            self.logger.error('SpaceObject type %s has invaldi raceID (not set!)', self.typeID)
            raceName = 'generic'
        if self.model is None:
            self.logger.warning('No model to fit boosters')
            return
        if not hasattr(self.model, 'boosters'):
            self.logger.warning('Model has no attribute boosters')
            return
        if self.model.boosters:
            self.model.boosters.maxVel = self.maxVelocity
            self.model.boosters.alwaysOn = alwaysOn
            if not enableTrails:
                self.model.boosters.trails = None
            dogmaAttr = const.attributeMaxVelocity
            if isNPC:
                dogmaAttr = const.attributeEntityCruiseSpeed
            velocity = self.sm.GetService('godma').GetTypeAttribute(self.typeID, dogmaAttr)
            if velocity is None:
                velocity = 1.0
            self.model.maxSpeed = velocity

    def EnterWarp(self):
        for t in self.turrets:
            t.EnterWarp()

        self.SetControllerVariable('IsWarping', True)
        try:
            self.model.boosters.warpIntensity = 1
        except AttributeError:
            pass

    def ExitWarp(self):
        for t in self.turrets:
            t.ExitWarp()

        self.SetControllerVariable('IsWarping', False)
        try:
            self.model.boosters.warpIntensity = 0
        except AttributeError:
            pass

    def UnfitHardpoints(self):
        if not self.fitted:
            return
        newModules = {}
        for key, val in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False

    def FitHardpoints(self, model = None, blocking = False):
        if model is None:
            model = self.model
        if getattr(self.fittingThread, 'alive', False):
            self.fitted = False
            self.fittingThread.kill()
        if blocking:
            self._FitHardpoints(model)
        else:
            self.fittingThread = uthread2.StartTasklet(self._FitHardpoints, model)

    def _FitHardpoints(self, model = None):
        if self.fitted:
            return
        if model is None:
            model = self.model
        if model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.fitted = True
        newTurretSetDict = TurretSet.FitTurrets(self.id, model, self.typeData.get('sofFactionName', None))
        self.turrets = []
        for key, val in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)

        if model and hasattr(model, 'locators') and hasattr(model, 'GetLocalBoundingBox'):
            setupTurretMovementAudio([ x.GetTurretSet() for x in self.turrets ], model.locators, model.GetLocalBoundingBox())

    def ApplyTorqueAtDamageLocator(self, damageLocatorID, impactVelocity, impactObjectMass):
        if not self.model:
            return
        damageLocatorPosition = self.model.GetDamageLocator(damageLocatorID)
        bsCenter = geo2.Vector(*self.model.GetBoundingSphereCenter())
        damageLocatorPosition -= bsCenter
        q = self.GetQuaternionAt(blue.os.GetSimTime())
        damageLocatorPosition = geo2.QuaternionTransformVector((q.x,
         q.y,
         q.z,
         q.w), damageLocatorPosition)
        self.ApplyTorqueAtPosition(damageLocatorPosition, impactVelocity, impactObjectMass)

    def ApplyTorqueAtPosition(self, position, impactVelocity, impactObjectMass):
        if not self.model:
            return
        impactForce = geo2.Vec3Scale(impactVelocity, impactObjectMass)
        self.ApplyImpulsiveForceAtPosition(impactForce, geo2.Vector(*position))

    def ChangingSkin(self, nextModel):
        self._FitHardpoints(self.nextModel)

    def PostChangingSkin(self):
        self.FitBoosters()
        if self.stanceID is not None:
            spaceobjanimation.SetShipAnimationStance(self.model, self.stanceID)
        self.UpdateCosmeticsItems()
