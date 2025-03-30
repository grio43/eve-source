#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\dynamicItemSvc.py
import dynamicitemattributes
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.dynamicItem.craftingWindow import CraftingWindow
from eve.client.script.ui.shared.fittingScreen.ghostFittingUtil import GetOriganlItemIDFromItemKey

class DynamicItemSvc(Service):
    __guid__ = 'svc.dynamicItemSvc'

    def Run(self, memStream = None):
        self.dynamicItemCache = {}

    def IsDynamicItem(self, typeID):
        return dynamicitemattributes.IsDynamicType(typeID)

    def GetDynamicItem(self, itemID):
        itemID = self._DecodeItemID(itemID)
        if itemID not in self.dynamicItemCache:
            remoteSvc = sm.RemoteSvc('dynamicItemService')
            self.dynamicItemCache[itemID] = remoteSvc.GetDynamicItemInfo(itemID)
        return self.dynamicItemCache[itemID]

    def GetDynamicItemAttributes(self, itemID):
        itemID = self._DecodeItemID(itemID)
        item = self.GetDynamicItem(itemID)
        return item.attributes

    def GetMutatedAttributes(self, itemID):
        itemID = self._DecodeItemID(itemID)
        item = self.GetDynamicItem(itemID)
        mutatorAttributes = dynamicitemattributes.GetMutatorAttributes(item.mutatorTypeID)
        return {attributeID:item.attributes[attributeID] for attributeID in mutatorAttributes}

    def OpenCraftWindow(self, item):
        CraftingWindow.Open(mutator=item, session=session)

    def CreateDynamicItem(self, mutatorID, sourceID):
        return sm.RemoteSvc('dynamicItemService').CreateDynamicItem(mutatorID, sourceID)

    def _DecodeItemID(self, itemID):
        if sm.GetService('info').IsItemSimulated(itemID):
            return GetOriganlItemIDFromItemKey(itemID)
        else:
            return itemID
