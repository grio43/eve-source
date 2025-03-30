#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\linkWithShip.py
import evetypes
import uthread2
from carbon.common.lib.const import SEC
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
from spacecomponents.client.display import EntryData, TIMER_ICON, RANGE_ICON
from spacecomponents.client.ui.link_with_ship.in_space_link_ui import InSpaceLinkUI
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_LINKWITHSHIP_TIMER_UPDATED, MSG_ON_LOAD_OBJECT, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_DAMAGE_UPDATED
from spacecomponents.common import componentConst
from spacecomponents.common.componentConst import LINK_WITH_SHIP
from spacecomponents.common.components.component import Component
from spacecomponents.common.components.linkWithShip import LINKSTATE_IDLE, LINKSTATE_RUNNING, LINKSTATE_COMPLETED
from localization import GetByLabel
import logging
from spacecomponents.common.helper import HasSkyhookReagentSiloComponent
logger = logging.getLogger(__name__)
REMOTE_CALL_INITIATE_LINK = 'InitiateLink'
REMOTE_CALL_INITIATE_LINK_QUICK = 'InitiateLinkQuick'
DELAY_BEFORE_MODEL_REMOVAL = 10

class LinkWithShip(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.onAddedToSpaceAt = None
        self.linkState = LINKSTATE_IDLE
        self.linkCompleteAtTime = None
        self._linkedShipID = None
        self.fxTargetShipID = None
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self._on_added_to_space)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self._on_removed_from_space)
        self.SubscribeToMessage(MSG_ON_DAMAGE_UPDATED, self.OnShieldValueUpdated)
        self._ui_bracket = None
        self.run_proximity_loop = False
        self.pendingFxCommand = False
        self.ballpark = None
        self._canLinkErrors = None
        self.ownerID = None
        self._effectTargetID = self.itemID
        self.solarsystemID = None

    def _on_added_to_space(self, slimItem):
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.solarsystemID = self.ballpark.solarsystemID
        self.ownerID = slimItem.ownerID
        self._effectTargetID = slimItem.parentID or self.itemID
        self.OnSlimItemUpdated(slimItem)
        self.run_proximity_loop = True
        uthread2.start_tasklet(self.proximity_loop, slimItem)

    def _on_removed_from_space(self):
        if HasSkyhookReagentSiloComponent(self.typeID):
            sm.ScatterEvent('OnLinkedWithShipSiloItemUpdated', self.itemID, self.solarsystemID, None, None, None)
        self.run_proximity_loop = False
        if self._ui_bracket is not None:
            self._ui_bracket.remove_from_space()

    @property
    def linkedShipID(self):
        return self._linkedShipID

    @linkedShipID.setter
    def linkedShipID(self, value):
        if self._linkedShipID == value:
            return
        self._linkedShipID = value
        sm.ScatterEvent('OnLinkedShipChanged', self.itemID, self._linkedShipID)

    def ReloadUI(self):
        if self._ui_bracket:
            self._ui_bracket.remove_from_space()
            self._ui_bracket = None
        self._ui_bracket = InSpaceLinkUI(item_id=self.itemID, space_component=self, initiate_link_function=InitiateLink, type_id=self.typeID, owner_id=self.ownerID)

    def proximity_loop(self, slimItem):
        from menucheckers import CelestialChecker
        while self.run_proximity_loop:
            celestialChecker = CelestialChecker(slimItem, cfg)
            if celestialChecker.OfferLinkWithShip(checkLinkState=False) and self.linkedShipID != session.shipid:
                if self._ui_bracket is None:
                    self._ui_bracket = InSpaceLinkUI(item_id=self.itemID, space_component=self, initiate_link_function=InitiateLink, type_id=self.typeID, owner_id=self.ownerID)
                else:
                    errors, busy = self.CanCreateLink(celestialChecker)
                    if self._canLinkErrors != errors:
                        tooltip = self._GetTooltipFromErrors(errors)
                        self._ui_bracket.set_can_link(tooltip, busy)
                        self._canLinkErrors = errors
            elif self._ui_bracket is not None:
                self._ui_bracket.remove_from_space()
                self._ui_bracket = None
            if self.pendingFxCommand:
                ball = sm.GetService('michelle').GetBall(self.linkedShipID)
                if ball is not None:
                    self._UpdateModel(self.fxTargetShipID)
                    self.pendingFxCommand = False
            uthread2.sleep_sim(0.5)

    def GetLinkState(self):
        return self.linkState

    def OnSlimItemUpdated(self, slimItem):
        if slimItem.component_linkWithShip is not None:
            self.onAddedToSpaceAt = slimItem.component_linkWithShip[0]
            self.linkState = slimItem.component_linkWithShip[1]
            self.linkCompleteAtTime = slimItem.component_linkWithShip[2]
            self.linkedShipID = slimItem.component_linkWithShip[3]
            self.SendMessage(MSG_ON_LINKWITHSHIP_TIMER_UPDATED, self, slimItem)
            if HasSkyhookReagentSiloComponent(self.typeID):
                duration = self.attributes.linkDuration * SEC
                sm.ScatterEvent('OnLinkedWithShipSiloItemUpdated', self.itemID, self.solarsystemID, self.linkCompleteAtTime, self.linkState, duration)
            if self._ui_bracket is not None:
                self._ui_bracket.set_link_state(self.linkState)
        ball = sm.GetService('michelle').GetBall(self.itemID)
        if ball is not None:
            self._UpdateModel(ball)

    def OnShieldValueUpdated(self, instance, shieldPercentage):
        sm.ScatterEvent('OnSkyhookSiloDamageUpdated', shieldPercentage)

    def OnLoadObject(self, ball):
        self._UpdateModel(ball)

    def _UpdateModel(self, ball):
        if not self.attributes.linkEffectGraphicIDOverride:
            return
        if self.fxTargetShipID is not None and self.fxTargetShipID != self.linkedShipID:
            self._UpdateFX(self.fxTargetShipID, start=0)
            self.fxTargetShipID = None
        if self.linkedShipID is not None:
            self._UpdateFX(self.linkedShipID)
            self.fxTargetShipID = self.linkedShipID

    def _UpdateFX(self, shipID, start = 1):
        if sm.GetService('michelle').GetBall(shipID) is None:
            self.pendingFxCommand = True
            return
        fx = sm.GetService('FxSequencer')
        fx.OnSpecialFX(shipID=shipID, moduleID=None, moduleTypeID=None, targetID=self._effectTargetID, otherTypeID=None, guid='effects.LinkWithShipComponent', isOffensive=False, start=start, active=True, repeat=99, graphicInfo={'graphicIDOverride': self.attributes.linkEffectGraphicIDOverride,
         'locatorSetName': 'linkwithship',
         'deathTimer': DELAY_BEFORE_MODEL_REMOVAL,
         'controllerTrigger': {'LinkWithShip_Active': float(self.linkState == LINKSTATE_RUNNING),
                               'LinkWithShip_Complete': float(self.linkState == LINKSTATE_COMPLETED)}})

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/InfoAttributesHeader')),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/LinkableShipTypeListLabel'), evetypes.GetTypeListDisplayName(attributes.linkableShipTypeListID)),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/LinkDurationLabel'), localization.GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/LinkDurationValue', pingInterval=long(attributes.linkDuration * SEC)), iconID=TIMER_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/RangeLabel'), FmtDist(attributes.maxLinkRange), iconID=RANGE_ICON)]
        return attributeEntries

    def CanCreateLink(self, celestialChecker):
        errors = []
        busy = False
        if self.linkedShipID == session.shipid:
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/AlreadyLinkedByYou')
            busy = True
            return (errors, busy)
        if self.linkedShipID is not None:
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/AlreadyLinked')
        elif self.linkState != LINKSTATE_IDLE:
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/InvalidState')
        if self.IsSkyhookSiloWithEmptyReagents():
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/CannotStealFromEmptySilo')
        shipItem = celestialChecker.session.getActiveShipGodmaItem()
        linkableShipTypeListID = self.attributes.linkableShipTypeListID
        linkableShipTypeIDs = evetypes.GetTypeIDsByListID(linkableShipTypeListID)
        if shipItem.typeID not in linkableShipTypeIDs:
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/InvalidShip')
        omegaOnly = self.attributes.omegaOnly
        if omegaOnly and not sm.GetService('cloneGradeSvc').IsOmega():
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/OmegaOnly')
        try:
            distance = self.ballpark.DistanceBetween(self.itemID, shipItem.itemID)
            if distance > self.attributes.maxLinkRange:
                errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/TooFarAway')
        except:
            pass

        interferenceState = sm.GetService('solarsystemInterferenceSvc').GetLocalInterferenceStateNow()
        energyState = sm.GetService('characterEnergySvc').GetEnergyStateNow()
        if self.attributes.solarsystemInterferenceCost is not None and not interferenceState.CanAffordCost(self.attributes.solarsystemInterferenceCost):
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/InterferenceCost')
        if self.attributes.characterEnergyCost is not None and not energyState.CanAffordCost(self.attributes.characterEnergyCost):
            errors.append('UI/Inflight/SpaceComponents/LinkWithShip/Errors/EnergyCost')
        return (errors, busy)

    def _GetTooltipFromErrors(self, errors):
        if not errors:
            return ''
        return u'{}\n- {}'.format(GetByLabel('UI/Inflight/SpaceComponents/LinkWithShip/Errors/TooltipHeader'), u'\n- '.join((GetByLabel(error) for error in errors)))

    def IsSkyhookSiloWithEmptyReagents(self):
        if HasSkyhookReagentSiloComponent(self.typeID):
            skyhookReagentSiloComponent = self.ballpark.componentRegistry.GetComponentForItem(self.itemID, componentConst.SKYHOOK_REAGENT_SILO)
            sovereigntyResourceSvc = sm.GetService('sovereigntyResourceSvc')
            try:
                siloSecure, siloInsecure = sovereigntyResourceSvc.GetReagentsInSkyhookNow(skyhookReagentSiloComponent.skyhookID)
            except DataUnavailableError:
                pass
            else:
                if not siloSecure and not siloInsecure:
                    return True

        return False


def InitiateLink(michelleService, itemID):
    remoteBallpark = michelleService.GetRemotePark()
    remoteBallpark.CallComponentFromClient(itemID, LINK_WITH_SHIP, REMOTE_CALL_INITIATE_LINK)


def InitiateLinkQuick(michelleService, itemID):
    remoteBallpark = michelleService.GetRemotePark()
    remoteBallpark.CallComponentFromClient(itemID, LINK_WITH_SHIP, REMOTE_CALL_INITIATE_LINK_QUICK)


def IsAccessibleByCharacter(ballpark, linkWithShipItem):
    try:
        linkWithShipComponent = ballpark.componentRegistry.GetComponentForItem(linkWithShipItem.itemID, componentConst.LINK_WITH_SHIP)
    except KeyError:
        return False

    if linkWithShipComponent.linkState in (LINKSTATE_RUNNING, LINKSTATE_COMPLETED):
        return False
    if linkWithShipComponent.IsSkyhookSiloWithEmptyReagents():
        return False
    return True
