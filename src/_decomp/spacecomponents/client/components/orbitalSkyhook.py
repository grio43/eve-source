#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\orbitalSkyhook.py
from __future__ import absolute_import
import carbon.common.script.util.mathCommon as mathCommon
import eve.common.lib.appConst as appConst
import eveicon
import gametime
import logging
import orbitalSkyhook.const as skyhookConst
import traceback
import uthread
from localization import GetByLabel
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LOAD_OBJECT, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_SKYHOOK_REAGENT_SILO_SLIM_ITEM_UPDATED
from spacecomponents.client.components.activate import GetActivationDurationForItem
from spacecomponents.common.componentConst import ORBITAL_SKYHOOK
from spacecomponents.common.components.linkWithShip import LINKSTATE_RUNNING
logger = logging.getLogger(__name__)
REMOTE_CALL_EXTRACT_REAGENTS_TO_SHIP = 'ExtractReagentsToShip'
REMOTE_CALL_IS_CHARACTER_AUTHORISED = 'IsCharacterAuthorised'

class OrbitalSkyhook(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_SKYHOOK_REAGENT_SILO_SLIM_ITEM_UPDATED, self.on_skyhook_reagent_silo_slim_item_updated)
        self.model = None
        self.planetID = None
        self.itemID = itemID
        self.workforceProduction = False
        self.powerProduction = False
        self.reagentsProduction = None
        self.fxCleared = False
        self._is_being_raided = False
        self._is_vulnerable_to_theft = None

    def OnAddedToSpace(self, slimItem):
        self.OnSlimItemUpdated(slimItem)

    def _SetStructureConstructionVariables(self, ball, slimItem):
        totalDuration = GetActivationDurationForItem(ball.ballpark, slimItem.itemID) or 120
        if slimItem.component_activate is None:
            return
        if slimItem.component_activate[0] is True:
            elapsedTime = totalDuration + 1
        else:
            activationTime = slimItem.component_activate[1] or -1
            remainingDuration = -gametime.GetSecondsSinceSimTime(activationTime)
            elapsedTime = max(0, totalDuration - remainingDuration)
        self.model.SetControllerVariable('IsBuilt', 1)
        self.model.SetControllerVariable('BuildDuration', totalDuration)
        self.model.SetControllerVariable('BuildElapsedTime', elapsedTime)

    def OnSlimItemUpdated(self, slimItem):
        self.planetID = slimItem.planetID
        shieldDamage = 0
        skyhookState = slimItem.skyhook_state
        sm.ScatterEvent('OnOrbitalSkyhookUpdated', slimItem.itemID, shieldDamage, skyhookState)
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if self.model is not None:
            if skyhookState in skyhookConst.STATE_CTRL_MAPPING:
                stateEnumValue = skyhookConst.STATE_CTRL_MAPPING.index(skyhookState) + 1
                self.model.SetControllerVariable('operatingState', float(stateEnumValue))
        if ball is not None:
            self._UpdateModel(ball)

    def on_skyhook_reagent_silo_slim_item_updated(self, silo_slim_item):

        def get_is_being_raided(slim_item):
            if slim_item.component_linkWithShip is not None:
                link_state = slim_item.component_linkWithShip[1]
                if link_state == LINKSTATE_RUNNING:
                    return True
            return False

        self._is_being_raided = get_is_being_raided(silo_slim_item)
        self._update_raiding_state()

    def is_vulnerable_to_theft(self):
        return bool(self._is_vulnerable_to_theft)

    def set_theft_vulnerability(self, is_vulnerable_to_theft):
        if self._is_vulnerable_to_theft == is_vulnerable_to_theft:
            return
        self._is_vulnerable_to_theft = is_vulnerable_to_theft
        self._update_raiding_state()

    def _update_raiding_state(self):
        if not self.model:
            return
        raiding_state = skyhookConst.RAIDING_STATE_INVULNERABLE
        if self._is_being_raided:
            raiding_state = skyhookConst.RAIDING_STATE_RAIDED
        elif self._is_vulnerable_to_theft:
            raiding_state = skyhookConst.RAIDING_STATE_VULNERABLE
        self.model.SetControllerVariable(skyhookConst.RAIDING_STATE, raiding_state)

    def _SetControllerHookup(self, resourceType, planetRadius, siloValue, siloMaxValue = 0):
        self.model.SetControllerVariable(skyhookConst.TRANSPORT_TYPE, resourceType)
        self.model.SetControllerVariable(skyhookConst.PLANET_RADIUS, planetRadius)
        if siloValue > 0 and siloMaxValue > 0:
            normalizedSiloValue = round(float(siloValue) / float(siloMaxValue), 3)
        else:
            normalizedSiloValue = float(siloValue)
        self.model.SetControllerVariable(skyhookConst.SILO_VALUE, normalizedSiloValue)
        if resourceType == skyhookConst.WORKFORCE and planetRadius < skyhookConst.SMALL_SIZE_CLASS.get(resourceType):
            self.model.SetControllerVariable(skyhookConst.PLANET_SIZE, skyhookConst.EXTRA_SMALL)
        elif planetRadius < skyhookConst.LARGE_SIZE_CLASS.get(resourceType):
            if planetRadius >= skyhookConst.MEDIUM_SIZE_CLASS.get(resourceType):
                self.model.SetControllerVariable(skyhookConst.PLANET_SIZE, skyhookConst.MEDIUM)
            else:
                self.model.SetControllerVariable(skyhookConst.PLANET_SIZE, skyhookConst.SMALL)
        else:
            self.model.SetControllerVariable(skyhookConst.PLANET_SIZE, skyhookConst.LARGE)
        self.model.SetControllerVariable('isDataReady', skyhookConst.CTRL_ON)
        self._update_raiding_state()

    def _SetSkyhookResourceData(self, planetRadius):
        colonyResourcesSvc = sm.GetService('sovereigntyResourceSvc')
        try:
            skyhook_data = colonyResourcesSvc.GetSkyhook(self.itemID)
            theft_vulnerability = skyhook_data.vulnerability_data
            resource_version = skyhook_data.resource_version
            reagentDefinition = skyhook_data.get_first_reagent_data()
            reagentTypeID = reagentDefinition.type_id if reagentDefinition else None
            workforce = skyhook_data.workforce
            power = colonyResourcesSvc.GetPlanetPowerProduction(self.planetID, resource_version)
            powerConfigurations = colonyResourcesSvc.GetAllPlanetPowerProduction(resource_version)
            max_power = max(powerConfigurations.values())
            workforceConfigurations = colonyResourcesSvc.GetAllPlanetWorkforceProduction(resource_version)
            max_workforce = max(workforceConfigurations.values())
        except Exception as e:
            logger.warning(e)
            return

        self._is_vulnerable_to_theft = theft_vulnerability is not None and theft_vulnerability.vulnerable
        fxNameToRemove = skyhookConst.ENERGY_VFX_NAME
        if workforce is not None and workforce > 0:
            self._SetControllerHookup(skyhookConst.WORKFORCE, planetRadius, workforce, max_workforce)
            self.workforceProduction = True
        elif reagentTypeID is not None and reagentTypeID > 0:
            try:
                siloSecure, siloInsecure = colonyResourcesSvc.GetReagentsInSkyhookNow(self.itemID)
                siloMaxSecure = reagentDefinition.configuration.secure_capacity
                if not siloSecure:
                    siloSecure = 0.0
                if not siloMaxSecure:
                    siloMaxSecure = 0.0
            except Exception as e:
                siloSecure = 0.0
                siloMaxSecure = 0.0

            if reagentTypeID == appConst.typeColonyReagentIce:
                self._SetControllerHookup(skyhookConst.ICE, planetRadius, siloSecure, siloMaxSecure)
                self.reagentsProduction = reagentTypeID
            elif reagentTypeID == appConst.typeColonyReagentLava:
                self._SetControllerHookup(skyhookConst.LAVA, planetRadius, siloSecure, siloMaxSecure)
                self.reagentsProduction = reagentTypeID
            if self.reagentsProduction:
                sm.ScatterEvent('OnBracketIconUpdated', self.itemID)
        elif power is not None and power > 0:
            self._SetControllerHookup(skyhookConst.POWER, planetRadius, power, max_power)
            self.powerProduction = True
            fxNameToRemove = skyhookConst.REAGENTS_VFX_NAME
        if not self.fxCleared and (self.workforceProduction or self.reagentsProduction or self.powerProduction):
            fxToClear = [ child for child in self.model.effectChildren if fxNameToRemove.lower() in child.name.lower() ]
            for fx in fxToClear:
                self.model.effectChildren.remove(fx)

            self.fxCleared = True

    def OnLoadObject(self, ball):
        self._UpdateModel(ball)
        if self.model:
            ballPark = ball.ballpark
            slimitem = ballPark.slimItems.get(ball.id)
            planetRadius = ballPark.balls[self.planetID].radius
            uthread.new(self._SetSkyhookResourceData, planetRadius)
            self._SetStructureConstructionVariables(ball, slimitem)
            self.model.StartControllers()

    def _UpdateModel(self, ball):
        try:
            self.model = ball.GetModel()
        except AttributeError:
            return

        if self.model and self.planetID:
            planetBall = ball.ballpark.balls[self.planetID]
            planetCenter = (planetBall.x, planetBall.y, planetBall.z)
            modelPosition = (ball.x, ball.y, ball.z)
            direction = mathCommon.GetNewQuatToFacePos(modelPosition, self.model.rotationCurve.value, planetCenter)
            self.model.rotationCurve.value = direction

    def GetBracketIcon(self, *args, **kwargs):
        if self.reagentsProduction:
            return eveicon.reagents_skyhook_bracket.resolve(16)
        else:
            return eveicon.skyhook_bracket.resolve(16)

    def GetProducingText(self):
        if self.reagentsProduction:
            return GetByLabel('Tooltips/Overview/ProducingReagents', reagentTypeID=self.reagentsProduction)
        if self.powerProduction:
            return GetByLabel('Tooltips/Overview/ProducingPower')
        if self.workforceProduction:
            return GetByLabel('Tooltips/Overview/ProducingWorkforce')

    def OnRemovedFromSpace(self):
        pass

    def OnReagentsUpdated(self):
        if self.reagentsProduction:
            colonyResourcesSvc = sm.GetService('sovereigntyResourceSvc')
            try:
                skyhookData = colonyResourcesSvc.GetSkyhook(self.itemID)
                siloSecure, siloInsecure = colonyResourcesSvc.GetReagentsInSkyhookNow(self.itemID)
                skyhookReagentDefinition = skyhookData.get_first_reagent_data()
                siloMaxSecure = skyhookReagentDefinition.configuration.secure_capacity
            except Exception as e:
                logger.warning(e)
                return

            if siloSecure > 0 and siloMaxSecure > 0:
                siloValue = round(float(siloSecure) / float(siloMaxSecure), 3)
            else:
                siloValue = 0.0
            self.model.SetControllerVariable(skyhookConst.SILO_VALUE, siloValue)

    def IsCharacterAuthorised(self, session_not_needed_on_client = None):
        return OrbitalSkyhook.is_character_authorised(self.itemID)

    @classmethod
    def is_character_authorised(cls, skyhookID):
        remoteBallpark = sm.GetService('michelle').GetRemotePark()
        isAuthorised = remoteBallpark.CallComponentFromClient(skyhookID, ORBITAL_SKYHOOK, REMOTE_CALL_IS_CHARACTER_AUTHORISED)
        return isAuthorised


def ExtractReagentsToShip(skyhookID, flagID, quantityToExtract):
    remoteBallpark = sm.GetService('michelle').GetRemotePark()
    quantityExtracted = remoteBallpark.CallComponentFromClient(skyhookID, ORBITAL_SKYHOOK, REMOTE_CALL_EXTRACT_REAGENTS_TO_SHIP, flagID, quantityToExtract)
    return quantityExtracted


def IsCharacterAuthorisedToTakeFromSkyhook(skyhookID):
    return OrbitalSkyhook.is_character_authorised(skyhookID)


def GetSkyhookComponent(skyhookID):
    try:
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return None
        comp = bp.componentRegistry.GetComponentForItem(skyhookID, ORBITAL_SKYHOOK)
        return comp
    except AttributeError:
        pass
    except KeyError:
        pass


def UpdateSkyhookOnReagentsUpdated(planetID, skyhookID):
    comp = GetSkyhookComponent(skyhookID)
    if not comp:
        return
    comp.OnReagentsUpdated()


def UpdateSkyhookOnTheftVulnerabilityChanged(skyhookID, is_vulnerable_to_theft):
    comp = GetSkyhookComponent(skyhookID)
    if not comp:
        return
    comp.set_theft_vulnerability(is_vulnerable_to_theft=is_vulnerable_to_theft)
