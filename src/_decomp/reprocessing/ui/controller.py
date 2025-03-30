#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\ui\controller.py
from collections import defaultdict
from reprocessing.ui.efficiencyCalculator import CalculateTheoreticalEfficiency

class Controller(object):
    __notifyevents__ = ['OnItemChange']

    def __init__(self, wnd, inputItems, inputGroups, quotes, outputItems, reprocessor, GetActiveShipID):
        self.window = wnd
        self.inputItems = inputItems
        self.inputGroups = inputGroups
        self.quotes = quotes
        self.outputItems = outputItems
        self.reprocessor = reprocessor
        self.GetActiveShipID = GetActiveShipID

    def AddItems(self, items):
        self.window.ShowInputLoading()
        try:
            itemsByGroup = defaultdict(list)
            for i in items:
                if not self.IsValid(i):
                    continue
                group = self.inputGroups.grouper.GetGroupID(i)
                itemsByGroup[group].append(i)

            for itemsInGroup in itemsByGroup.itervalues():
                self._AddItemsInGroup(itemsInGroup)

        finally:
            self.window.HideInputLoading()

    def IsValid(self, item):
        activeShipID = self.GetActiveShipID()
        if item.flagID == const.flagReward:
            return False
        if item.groupID == const.groupMineral:
            return False
        if item.itemID in (activeShipID, session.charid):
            return False
        return True

    def _AddItemsInGroup(self, items):
        self.inputGroups.UpdateGroups(items)
        self.inputItems.AddItems(items)
        self.SetEfficiency()
        self._UpdateOutputItems()

    def RemoveItem(self, itemID):
        item = self.inputItems.RemoveItem(itemID)
        self.inputGroups.RemoveItem(item)
        self.quotes.RemoveItem(itemID)
        self.SetEfficiency()
        self._UpdateOutputItems()

    def _UpdateOutputItems(self):
        self.outputItems.UpdateItems()
        self.window.UpdateTotalIskCost(self.outputItems.GetTotalIskCost())
        sm.ScatterEvent('OnReprocessingMaterialsChanged')

    def Reprocess(self, outputLocationID, outputFlagID):
        itemsToReprocess = self.inputItems.GetItems()
        reprocessed = set(self.reprocessor.Reprocess(itemsToReprocess, self.GetActiveShipID(), outputLocationID, outputFlagID))
        remaining = [ i for i in itemsToReprocess if i.itemID not in reprocessed ]
        return (reprocessed, remaining)

    def OnItemChange(self, item, change, location):
        if item.typeID == const.typeOffice and const.ixFlag in change and item.flagID == const.flagImpounded:
            for inputItem in (i for i in self.inputItems.GetItems() if i.locationID == item.itemID):
                self.RemoveItem(inputItem.itemID)

        if self.inputGroups.HasItem(item):
            if const.ixOwnerID in change and item.ownerID not in (session.charid, session.corpid):
                self.RemoveItem(item.itemID)
            elif item.locationID == const.locationJunkyard:
                self.RemoveItem(item.itemID)

    def SetEfficiency(self):
        typeIDs = self.inputItems.GetTypeIDsByGroup()
        if len(typeIDs):
            for group in self.inputGroups.groups:
                typeID = typeIDs[group][0]
                efficiency = self.quotes.GetStationEfficiencyForType(typeID)
                tax = self.quotes.stationTax
                self.inputGroups.SetEfficiency(group, CalculateTheoreticalEfficiency(typeIDs[group], efficiency), typeIDs)
                self.inputGroups.SetTaxAndStationEfficiency(group, efficiency, tax)

    def GetOutputItems(self):
        return self.outputItems.GetItems()

    def GetInputItems(self):
        return self.inputItems.GetItems()

    def Close(self):
        sm.ScatterEvent('OnReprocessingMaterialsChanged')


def NodesToItems(nodes):
    ret = []
    for node in nodes:
        if getattr(node, '__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
            itemID = getattr(node, 'itemID', None)
            if itemID is not None:
                ret.append(node.rec)

    return ret
