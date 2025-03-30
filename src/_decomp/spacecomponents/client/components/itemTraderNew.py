#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\itemTraderNew.py
from eve.client.script.ui.inflight.itemTrader.itemTraderNewWindow import ItemTraderWindow
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentConst import ITEM_TRADER

class ItemTrader(Component):

    def __init__(self, *args, **kwargs):
        super(ItemTrader, self).__init__(*args, **kwargs)

    def RequestTrade(self):
        wnd = ItemTraderWindow.GetIfOpen(windowInstanceID=self.itemID)
        if wnd and not wnd.destroyed:
            wnd.Maximize()
        else:
            ItemTraderWindow.Open(item_trader=self, windowInstanceID=self.itemID)

    def GetRecipes(self):
        return self.attributes.recipes

    def GetInteractionRange(self):
        return self.attributes.interactionRange

    def CallServerComponent(self, methodName, *args, **kwargs):
        remoteBallpark = sm.GetService('michelle').GetRemotePark()
        return remoteBallpark.CallComponentFromClient(self.itemID, ITEM_TRADER, methodName, *args, **kwargs)

    def ProcessTrade(self, recipeID, multiplier, inputISK):
        success, items = self.CallServerComponent('ProcessTrade', recipeID=recipeID, multiplier=multiplier, inputISK=inputISK)
        return (success, items)
