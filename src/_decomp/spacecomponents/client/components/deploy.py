#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\deploy.py
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eveexceptions import UserError
from inventorycommon.const import groupControlTower, groupStation, groupStargate, groupWormhole, groupMoonMiningBeacon, groupEncounterSurveillanceSystem
from carbon.common.script.util.format import FmtDist
from spacecomponents.client.display import EntryData, RANGE_ICON, BANNED_ICON
from spacecomponents.common.componentConst import DEPLOY_CLASS
from spacecomponents.common.components.component import Component
from menu import MenuLabel
from eve.client.script.util.eveMisc import LaunchFromShip
import evetypes
from spacecomponents.common.data import get_space_component_for_type

class Deploy(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/InfoAttributesHeader')),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DeployAtRange'), FmtDist(attributes.deployAtRange), iconID=RANGE_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromOwnGroup', groupName=evetypes.GetGroupName(typeID)), FmtDist(attributes.minDistanceFromOwnGroup), iconID=RANGE_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromControlTower', groupName=evetypes.GetGroupNameByGroup(groupControlTower)), FmtDist(attributes.minDistanceFromControlTower), iconID=RANGE_ICON)]
        if attributes.maxDistanceFromControlTower is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MaxDistanceFromControlTower', groupName=evetypes.GetGroupNameByGroup(groupControlTower)), FmtDist(attributes.maxDistanceFromControlTower), iconID=RANGE_ICON))
        if attributes.minDistanceFromStargatesAndStations is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromStargatesAndStations', stargateGroupName=evetypes.GetGroupNameByGroup(groupStargate), stationGroupName=evetypes.GetGroupNameByGroup(groupStation)), FmtDist(attributes.minDistanceFromStargatesAndStations), iconID=RANGE_ICON))
        if attributes.minDistanceFromWormhole is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromWormhole', wormholeGroupName=evetypes.GetGroupNameByGroup(groupWormhole)), FmtDist(attributes.minDistanceFromStargatesAndStations), iconID=RANGE_ICON))
        if attributes.minDistanceFromMoonBeacon is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromMoonBeacon', beaconGroupName=evetypes.GetGroupNameByGroup(groupMoonMiningBeacon)), FmtDist(attributes.minDistanceFromMoonBeacon), iconID=RANGE_ICON))
        if attributes.minDistanceFromESS is not None:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromESS', essGroupName=evetypes.GetGroupNameByGroup(groupEncounterSurveillanceSystem)), FmtDist(attributes.minDistanceFromESS), iconID=RANGE_ICON))
        if attributes.disallowInWormholeSpace:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DisallowedFromWormholeSpace'), '', iconID=BANNED_ICON))
        if attributes.disallowInTriglavianSpace:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DisallowedFromTriglavianSpace'), '', iconID=BANNED_ICON))
        if attributes.disallowInAbyssSpace:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DisallowedFromAbyssSpace'), '', iconID=BANNED_ICON))
        if attributes.disallowInWarpDisruptedDungeon:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DisallowInWarpDisruptedDungeon'), '', iconID=BANNED_ICON))
        if attributes.requiresFWFactionID:
            attributeEntries.append(EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/RequiredFactionAllegiance'), cfg.eveowners.Get(attributes.requiresFWFactionID).name))
        return attributeEntries


def DeployAction(invItems):
    for item in invItems:
        componentAttributes = get_space_component_for_type(item.typeID, DEPLOY_CLASS)
        if componentAttributes.requiresFleet and session.fleetid is None:
            raise UserError('CannotDeployRequireFleet', {'deployTypeID': item.typeID})

    LaunchFromShip(invItems, session.charid, maxQty=1)


def GetDeployMenu(invItem):
    itemIsInMyShip = invItem.locationID == session.shipid
    if itemIsInMyShip:
        return [[MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), DeployAction, [invItem]]]
    else:
        return []
