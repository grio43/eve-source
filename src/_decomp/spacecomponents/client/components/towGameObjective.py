#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\towGameObjective.py
import evetypes
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.common.script.util.facwarCommon import GetCaptureFaction
from menu import MenuLabel
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.componentConst import TOW_GAME_OBJECTIVE
from spacecomponents.common.components.component import Component
import logging
from spacecomponents.common.components.towGameObjective import SLIM_KEY_TOWED_STATE, SLIM_KEY_TOWING_ID, SLIM_KEY_VALID_FACTIONS
from spacecomponents.common.data import type_has_space_component
logger = logging.getLogger(__name__)
REMOTE_CALL_START_TOWING = 'RequestStartTowing'
REMOTE_CALL_STOP_TOWING = 'RequestStopTowing'

class TowGameObjective(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/TowGameObjective/InfoAttributesHeader')), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/TowGameObjective/StartTowingMaxRange'), FmtDist(attributes.startTowingMaxRange), iconID=RANGE_ICON), EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/TowGameObjective/BreakTowAboveRange'), FmtDist(attributes.breakTowAboveRange), iconID=RANGE_ICON)]
        return attributeEntries


def GetFailureReason(ballpark, towableItem, charID, shipItem, warFactionID):
    try:
        towableComponent = ballpark.componentRegistry.GetComponentForItem(towableItem.itemID, TOW_GAME_OBJECTIVE)
    except KeyError:
        return 'UI/Inflight/SpaceComponents/TowGameObjective/notTowable'

    myTowedObjective = _GetTowedObjective(ballpark, shipItem.itemID)
    if myTowedObjective is not None and myTowedObjective != towableItem.itemID:
        return 'UI/Inflight/SpaceComponents/TowGameObjective/linkedToDifferentItem'
    captureFactionID = GetCaptureFaction(warFactionID)
    if captureFactionID not in _GetTowFactions(ballpark, towableItem.itemID):
        return 'UI/Inflight/SpaceComponents/TowGameObjective/wrongFaction'
    towedByShipID = _GetTowingShip(ballpark, towableItem.itemID)
    if towedByShipID:
        if towedByShipID == shipItem.itemID:
            return
        else:
            return 'UI/Inflight/SpaceComponents/TowGameObjective/someoneElseLinked'
    towingShipTypeListID = towableComponent.attributes.towingShipTypeListID
    towingShipTypeIDs = evetypes.GetTypeIDsByListID(towingShipTypeListID)
    if shipItem.typeID not in towingShipTypeIDs:
        return 'UI/Inflight/SpaceComponents/TowGameObjective/wrongShip'
    distance = ballpark.DistanceBetween(towableItem.itemID, shipItem.itemID)
    if distance > towableComponent.attributes.startTowingMaxRange:
        return 'UI/Inflight/SpaceComponents/TowGameObjective/tooFarAway'


def GetMenuEntries(celestialChecker):
    entries = []
    if not type_has_space_component(celestialChecker.item.typeID, TOW_GAME_OBJECTIVE):
        return entries
    towedByShipID = _GetTowingShip(celestialChecker.GetBallpark(), celestialChecker.item.itemID)
    if towedByShipID is None:
        entries += [[MenuLabel('UI/Inflight/SpaceComponents/TowGameObjective/startTowing'), _StartTowing, [celestialChecker.item.itemID]]]
    elif towedByShipID == celestialChecker.session.shipid:
        entries += [[MenuLabel('UI/Inflight/SpaceComponents/TowGameObjective/stopTowing'), _StopTowing, [celestialChecker.item.itemID]]]
    return entries


def _GetTowFactions(ballpark, towableItemID):
    slimItem = ballpark.slimItems.get(towableItemID)
    if not slimItem:
        return []
    factionIDs = getattr(slimItem, SLIM_KEY_VALID_FACTIONS)
    return factionIDs


def _GetTowedObjective(ballpark, shipID):
    slimItem = ballpark.slimItems.get(shipID)
    if not slimItem:
        return None
    towedItemID = getattr(slimItem, SLIM_KEY_TOWING_ID)
    return towedItemID


def _GetTowingShip(ballpark, towableItemID):
    towedState = _GetTowedState(ballpark, towableItemID)
    if towedState is not None:
        towedByShipID, targetGoalpostID = towedState
        return towedByShipID


def _GetTowTargetGoalpost(ballpark, towableItemID):
    towedState = _GetTowedState(ballpark, towableItemID)
    if towedState is not None:
        towedByShipID, targetGoalpostID = towedState
        return targetGoalpostID


def _GetTowedState(ballpark, towableItemID):
    slimItem = ballpark.slimItems.get(towableItemID)
    if not slimItem:
        return None
    towedState = getattr(slimItem, SLIM_KEY_TOWED_STATE)
    return towedState


def _StartTowing(itemID):
    remoteBallpark = sm.GetService('michelle').GetRemotePark()
    remoteBallpark.CallComponentFromClient(itemID, TOW_GAME_OBJECTIVE, REMOTE_CALL_START_TOWING)


def _StopTowing(itemID):
    remoteBallpark = sm.GetService('michelle').GetRemotePark()
    remoteBallpark.CallComponentFromClient(itemID, TOW_GAME_OBJECTIVE, REMOTE_CALL_STOP_TOWING)
