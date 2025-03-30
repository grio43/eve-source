#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\itemtrader_legacy.py
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentConst import ITEM_TRADER
from menu import MenuLabel
from eve.client.script.ui.inflight.itemTrader.itemtraderwindow_legacy import ItemTraderWindow
import evetypes
from eveservices.menu import GetMenuService

class ItemTrader(Component):

    def __init__(self, *args, **kwargs):
        super(ItemTrader, self).__init__(*args, **kwargs)
        self.activeStackItemIDs = {}

    def RequestTrade(self):
        GetMenuService().GetCloseAndTryCommand(self.itemID, self.InitiateTrade, (), interactionRange=self.attributes.interactionRange)

    def InitiateTrade(self):
        shipInventory = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        cargoChecker = CargoChecker(shipInventory, self.attributes.inputItems, self.attributes.outputItems)
        ItemTraderWindow.CloseIfOpen()
        ItemTraderWindow(itemTrader=self, shipID=session.shipid, cargoChecker=cargoChecker)

    def ProcessTrade(self):
        success, self.activeStackItemIDs = self.CallServerComponent('ProcessTrade', activeStackItemIDs=self.activeStackItemIDs)
        return success

    def CallServerComponent(self, methodName, *args, **kwargs):
        remoteBallpark = sm.GetService('michelle').GetRemotePark()
        return remoteBallpark.CallComponentFromClient(self.itemID, ITEM_TRADER, methodName, *args, **kwargs)

    def GetInputItems(self):
        return {k:v for k, v in self.attributes.inputItems.iteritems()}

    def GetInputIsk(self):
        return self.attributes.inputIsk

    def GetOutputItems(self):
        return self.attributes.outputItems


class CargoChecker(object):

    def __init__(self, shipInventory, inputItems, outputItems):
        self.shipInventory = shipInventory
        self.inputItems = inputItems
        self.outputItems = outputItems
        self.requiredCapacity = self.GetCapacityForItems(outputItems) - self.GetCapacityForItems(inputItems)

    def GetCapacityForItems(self, items):
        capacity = 0
        for typeID, quantity in items.iteritems():
            typeVolume = evetypes.GetVolume(typeID)
            capacity += quantity * typeVolume

        return capacity

    def IsRequiredCargoSpaceAvailable(self):
        if self.requiredCapacity <= 0:
            return True
        shipCapacity = self.shipInventory.GetCapacity(const.flagCargo)
        availableCapacity = shipCapacity.capacity - shipCapacity.used
        return availableCapacity > self.requiredCapacity

    def AreRequiredItemsPresent(self):
        cargoItems = self.shipInventory.List(const.flagCargo)
        cargoItems += self.shipInventory.List(const.flagGeneralMiningHold)
        cargoItems += self.shipInventory.List(const.flagSpecializedIceHold)
        for requiredTypeID, requiredQuantity in self.inputItems.iteritems():
            if not self.IsTypeAndQuantityInCargo(requiredTypeID, requiredQuantity, cargoItems):
                return False

        return True

    def IsTypeAndQuantityInCargo(self, requiredTypeID, requiredQuantity, cargoItems):
        quantityInCargo = 0
        for item in cargoItems:
            if item.typeID == requiredTypeID:
                quantityInCargo += item.quantity
            if quantityInCargo >= requiredQuantity:
                return True

        return False


def GetMenu(ballpark, itemTraderItemID):
    itemTrader = ballpark.componentRegistry.GetComponentForItem(itemTraderItemID, ITEM_TRADER)
    menu = [[MenuLabel('UI/Inflight/SpaceComponents/ItemTrader/Access'), itemTrader.RequestTrade]]
    return menu
