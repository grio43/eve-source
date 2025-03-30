#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\cargobay.py
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from inventorycommon.const import groupNpcIndustrialCommand
from carbon.common.script.util.format import FmtDist, FmtYesNo
from dogma.attributes.format import GetFormattedAttributeAndValue
from dogma.const import attributeCapacity
from spacecomponents.client.display import EntryData, DogmaEntryData, RANGE_ICON
from spacecomponents.common.components.component import Component
from menu import MenuLabel
from spacecomponents.common.componentConst import CARGO_BAY
import evetypes
from spacecomponents.common.data import get_space_component_for_type

class CargoBay(Component):

    @staticmethod
    def GetAttributeInfo(typeID, attributes, instance, localization):
        attributeEntries = [EntryData(Header, localization.GetByLabel('UI/Inflight/SpaceComponents/CargoBay/InfoAttributesHeader')),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/CargoBay/AccessRangeLabel'), FmtDist(attributes.accessRange), iconID=RANGE_ICON),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/CargoBay/AllowUserAdd'), FmtYesNo(attributes.allowUserAdd), iconID=0),
         EntryData(LabelTextSides, localization.GetByLabel('UI/Inflight/SpaceComponents/CargoBay/AllowFreeForAll'), FmtYesNo(attributes.allowFreeForAll), iconID=0)]
        capacity = evetypes.GetCapacity(typeID)
        if evetypes.GetGroupID(typeID) == groupNpcIndustrialCommand:
            haulerCapacity = sm.GetService('rwService').get_hauler_capacity(instance.itemID)
            if haulerCapacity is not None:
                capacity = haulerCapacity
        if capacity:
            cargoCapacity = GetFormattedAttributeAndValue(attributeCapacity, capacity)
            attributeEntries.append(DogmaEntryData(LabelTextSides, cargoCapacity))
        return attributeEntries

    @staticmethod
    def GetSuppressedDogmaAttributeIDs():
        return [attributeCapacity]


def OpenCargoWindow(cargoBayItemID, typeID, menuSvc):
    accessRange = get_space_component_for_type(typeID, CARGO_BAY).accessRange
    menuSvc.GetCloseAndTryCommand(cargoBayItemID, menuSvc.OpenSpaceComponentInventory, (cargoBayItemID,), interactionRange=accessRange)
    if menuSvc.IsTooFarToExecuteCommand(cargoBayItemID):
        eve.Message('OpenCargoTooFar')


def GetMenu(cargoBayItemID, typeID, menuSvc, *args):
    return [[MenuLabel('UI/Commands/OpenCargo'), OpenCargoWindow, [cargoBayItemID, typeID, menuSvc]]]


def IsAccessibleByCharacter(cargoBayItem, charID):
    if cargoBayItem.ownerID == charID:
        return True
    if get_space_component_for_type(cargoBayItem.typeID, CARGO_BAY).allowFreeForAll:
        return True
    return False
