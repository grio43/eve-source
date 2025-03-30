#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\hangarBehaviours\baseHangarBehaviours.py
import evetypes
import trinity
import logging
import geo2
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from fsdBuiltData.common.graphicIDs import GetSofFactionName
from inventorycommon.util import GetSubSystemTypeIDs
import evegraphics.utils as gfxutils
from eve.common.script.net import eveMoniker
from eveSpaceObject.spaceobjanimation import SetShipAnimationStance, TriggerDefaultStates
from eve.client.script.ui.inflight.shipstance import get_ship_stance
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.environment.spaceObject.cosmeticsManager import CosmeticsManager
from evegraphics.CosmeticsLoader import CosmeticsLoader
log = logging.getLogger(__name__)

class BaseHangarShipBehaviour(object):
    MIN_SHIP_BOBBING_TIME = 10
    MAX_SHIP_BOBBING_TIME = 300
    MIN_SHIP_BOBBING_HALF_DISTANCE = 100

    def __init__(self):
        self._activeMaterialSetID = None
        self._activeSkinID = None
        self.log = log
        self.shipAnchorPoint = (0.0, 0.0, 0.0)
        self.shipSwitchingInProcess = False
        self.turretSets = {}
        self.cosmeticsLoader = CosmeticsLoader((CosmeticsLoader.ALLIANCE, CosmeticsLoader.CORP))

    def LoadShipModel(self, itemID, typeID):
        self.shipSwitchingInProcess = True
        model = self._LoadSOFShipModel(itemID, typeID)
        model.name = str(itemID)
        model.FreezeHighDetailMesh()
        self.SetShipDirtLevel(itemID, model)
        self.SetShipKillCounter(itemID, model)
        self.SetupShipAnimation(model, typeID, itemID)
        self.SetShipDamage(itemID, model)
        self.FitTurrets(itemID, typeID, model)
        self.shipSwitchingInProcess = False
        return model

    def CleanScene(self):
        self.turretSets = None

    def _LoadSOFShipModel(self, itemID, typeID):
        self._activeSkinID = None
        self._activeMaterialSetID = None
        skin_state = self.GetShipSkinState(itemID, typeID)
        if skin_state:
            if skin_state.skin_type == ShipSkinType.THIRD_PARTY_SKIN:
                thirdPartyDNA = CosmeticsManager.CreateSOFDNAfromSkinState(skin_state, typeID)
                ship = GetSofService().spaceObjectFactory.BuildFromDNA(thirdPartyDNA)
                CosmeticsManager.UpdatePatternProjectionParametersFromSkinState(skin_state, ship, typeID)
                blend_mode = skin_state.skin_data.slot_layout.pattern_blend_mode
                if blend_mode is not None:
                    CosmeticsManager.SetBlendMode(ship, blendMode=blend_mode)
                return ship
            if skin_state.skin_type == ShipSkinType.FIRST_PARTY_SKIN:
                self._activeSkinID = skin_state.skin_data.skin_id
                self._activeMaterialSetID = sm.GetService('cosmeticsSvc').GetFirstPartySkinMaterialSetID(self._activeSkinID)
            elif skin_state.skin_type == ShipSkinType.NO_SKIN:
                pass
        shipDna = gfxutils.BuildSOFDNAFromTypeID(typeID, materialSetID=self._activeMaterialSetID, multiHullTypeIDList=GetSubSystemTypeIDs(itemID, typeID))
        if shipDna is None:
            self.log.error('%s._LoadSOFShip(itemID = %s, typeID = %s): Trying to show a SOF ship that is not in the SOF' % (self, itemID, typeID))
            return
        return GetSofService().spaceObjectFactory.BuildFromDNA(shipDna)

    def SetupShipAnimation(self, model, typeID, itemID):
        if model is None:
            return
        if not evetypes.Exists(typeID):
            return
        SetShipAnimationStance(model, get_ship_stance(itemID, typeID))
        TriggerDefaultStates(model)

    def SetShipDirtLevel(self, itemID, model):
        dirtTimeStamp = eveMoniker.GetShipAccess().GetDirtTimestamp(itemID)
        dirtLevel = gfxutils.CalcDirtLevelFromAge(dirtTimeStamp)
        model.dirtLevel = dirtLevel

    def SetShipKillCounter(self, itemID, model):
        killCounter = sm.RemoteSvc('shipKillCounter').GetItemKillCountPlayer(itemID)
        model.displayKillCounterValue = min(killCounter, 999)

    def SetShipDamage(self, itemID, model):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        dogmaLocation.LoadItem(itemID)
        shipState = dogmaLocation.GetDamageStateEx(itemID)
        if shipState is None:
            self.log.error('%s.SetShipDamage(itemID = %s, model = %s): Got no shipstate from dogma', self, itemID, model)
            return
        shieldState, armorState, hullState = shipState
        if isinstance(shieldState, tuple):
            shieldState = shieldState[0]
        if model is not None:
            model.SetImpactDamageState(shieldState, armorState, hullState, True)

    def FitTurrets(self, itemID, typeID, model):
        graphicID = evetypes.GetGraphicID(typeID)
        sofFactionName = GetSofFactionName(graphicID)
        self.turretSets = TurretSet.FitTurrets(itemID, model, sofFactionName)
        self._SetHighLodForTurrets(model)

    def UpdateTurretState(self, dogmaItem):
        if dogmaItem.itemID not in self.turretSets:
            return
        turret = self.turretSets[dogmaItem.itemID]
        if dogmaItem.IsOnline():
            turret.Online()
        else:
            turret.Offline()

    def _SetHighLodForTurrets(self, model):
        for turretSet in model.turretSets:
            turretSet.FreezeHighDetailLOD()

    def GetShipSkinState(self, itemID, typeID):
        return sm.GetService('cosmeticsSvc').GetAppliedSkinState(session.charid, itemID)

    def ShouldSwitchSkin(self, skinID):
        return skinID != getattr(self._activeSkinID, 'skinID', None) and not self.shipSwitchingInProcess

    def SetAnchorPoint(self, hangarModel, hangarScene):
        raise NotImplementedError("%s does not implement 'SetAnchorPoint'", self)

    def PlaceShip(self, model, typeID):
        raise NotImplementedError("%s does not implement 'PlaceShip'", self)

    def GetShipCenter(self, model, typeID):
        raise NotImplementedError("%s does not implement 'GetShipCenter'", self)

    def AnimateShipEntry(self, model, typeID, scene = None, duration = 5.0):
        self.PlaceShip(model, typeID)

    def AnimateReflectionProbeEntry(self, reflectionProbe, duration = 5.0):
        self.PlaceReflectionProbe(reflectionProbe)

    def PlaceReflectionProbe(self, reflectionProbe):
        if reflectionProbe:
            reflectionProbe.lockPosition = True
            reflectionProbe.position = self.shipAnchorPoint

    def ApplyShipBobbing(self, model, initialPosition, deltaPosition, cycleLengthInSec):
        curve = trinity.Tr2CurveVector3()
        topPosition = geo2.Vec3Add(initialPosition, deltaPosition)
        bottomPosition = geo2.Vec3Subtract(initialPosition, deltaPosition)
        curve.AddKey(0.0, initialPosition, trinity.Tr2CurveInterpolation.HERMITE)
        curve.AddKey(0.25 * cycleLengthInSec, bottomPosition, trinity.Tr2CurveInterpolation.HERMITE)
        curve.AddKey(0.75 * cycleLengthInSec, topPosition, trinity.Tr2CurveInterpolation.HERMITE)
        curve.AddKey(1.0 * cycleLengthInSec, initialPosition, trinity.Tr2CurveInterpolation.HERMITE)
        curve.x.extrapolationAfter = trinity.Tr2CurveExtrapolation.CYCLE
        curve.y.extrapolationAfter = trinity.Tr2CurveExtrapolation.CYCLE
        curve.z.extrapolationAfter = trinity.Tr2CurveExtrapolation.CYCLE
        model.modelTranslationCurve = trinity.Tr2TranslationAdapter()
        model.modelTranslationCurve.curve = curve


class BaseHangarShipDroneBehaviour(object):

    def __init__(self):
        self.dronesActive = False
        self.seekTargetBehaviourData = None
        self.collisionAvoidanceBehaviourData = None
        self.repairDroneBehaviourGroup = None
        self.hasEllipsoid = False

    def Setup(self, hangarModel, shipModel):
        self.repairDroneBehaviourGroup = self.GetRepairDroneBehaviourGroup(hangarModel)
        self.seekTargetBehaviourData = self.GetSeekTargetData(self.repairDroneBehaviourGroup)
        self.collisionAvoidanceBehaviourData = self.GetCollisionAvoidanceData(hangarModel)
        if self.seekTargetBehaviourData:
            self.seekTargetBehaviourData.ResetBehavior()
        self.SetRepairDroneCount(shipModel.boundingSphereRadius)
        self.dronesActive = False

    def SplitBoundingBox(self):
        if self.seekTargetBehaviourData:
            self.seekTargetBehaviourData.SplitBoundingBox()

    def GetSeekTargetData(self, repairDroneBehaviourGroup):
        behavior = repairDroneBehaviourGroup.Find('trinity.SeekTarget')
        for data in behavior:
            return data

    def GetCollisionAvoidanceData(self, hangarModel):
        behavior = hangarModel.Find('trinity.CollisionAvoidance')
        for data in behavior:
            return data

    def GetRepairDroneBehaviourGroup(self, hangarModel):
        behaviorGroups = hangarModel.Find('trinity.BehaviorGroup')
        for each in behaviorGroups:
            if each.name == 'RepairDrone':
                return each

    def GetShipArmorImpactLifeTime(self, shipModel):
        return shipModel.impactOverlay.GetArmorImpactLifeTime()

    def GetDronesActive(self):
        return self.dronesActive

    def SetDronesActive(self, value):
        self.dronesActive = value
        self.seekTargetBehaviourData.SetupShipRepair()

    def SetTarget(self, shipModel):
        self.seekTargetBehaviourData.SetTarget(shipModel)

    def SetExit(self):
        if self.seekTargetBehaviourData:
            self.seekTargetBehaviourData.SetExit(True)
        self.dronesActive = False

    def StartRepairDroneSequence(self, itemID, shipModel, shipBehaviour):
        self.SetEllipsoidVolume(shipModel)
        self.SetTarget(shipModel)
        if shipModel.boundingSphereRadius >= 2250:
            self.SplitBoundingBox()
        sec = self.GetShipArmorImpactLifeTime(shipModel)
        if self.seekTargetBehaviourData:
            self.seekTargetBehaviourData.SetTotalRepairTime(sec)
        self.seekTargetBehaviourData.onFirstDroneArrivedCallback = lambda : self.StartEffectAndTimer(itemID, shipModel, shipBehaviour)

    def StartEffectAndTimer(self, itemID, shipModel, shipBehaviour):
        shipBehaviour.SetShipDamage(itemID, shipModel)

    def SetRepairDroneCount(self, boundingRadius):
        raise NotImplementedError("%s does not implement 'SetCount'", self)

    def SetEllipsoidVolume(self, shipModel):
        if self.collisionAvoidanceBehaviourData and self.seekTargetBehaviourData:
            volume = trinity.EveEllipsoidVolume()
            scale = 1.5
            volume.shape = (shipModel.shapeEllipsoidRadius[0] * scale, shipModel.shapeEllipsoidRadius[1] * scale, shipModel.shapeEllipsoidRadius[2] * scale)
            volume.innerShape = shipModel.shapeEllipsoidRadius
            volume.position = shipModel.translationCurve.value
            self.collisionAvoidanceBehaviourData.exclusionVolumes[0] = volume
            self.hasEllipsoid = True
