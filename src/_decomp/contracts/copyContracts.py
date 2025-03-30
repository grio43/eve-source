#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contracts\copyContracts.py
from collections import defaultdict
import evetypes
from brennivin.itertoolsext import Bundle
from inventorycommon.const import categoryBlueprint, flagHangar

def GetByLabelX(messageLabel, *args, **kwargs):
    from localization import GetByLabel
    return GetByLabel(messageLabel, *args, **kwargs)


class CopyContractObject(object):

    def __init__(self, startStation, forCorp, contractItems, getItemsInStationFunc, corpFlagID):
        self.startStation = startStation
        self.forCorp = forCorp
        self.contractItems = contractItems
        self.getItemsInStationFunc = getItemsInStationFunc
        self.corpFlagID = corpFlagID

    def FindItemToSellInHangar(self, itemsToSell, sellBlueprintCopies, sellBlueprintOriginals):
        itemsToSellCopy = itemsToSell.copy()
        itemsInStation = self.GetItemsForCorrectFlag()
        itemsInStationByTypeID = defaultdict(list)
        for eachItem in itemsInStation:
            itemsInStationByTypeID[eachItem.typeID].append(eachItem)

        foundItems = self._GetFoundItems(itemsInStationByTypeID, itemsToSellCopy)
        foundBPC = self._GetFoundBlueprints(sellBlueprintCopies, itemsInStationByTypeID, True)
        foundBPO = self._GetFoundBlueprints(sellBlueprintOriginals, itemsInStationByTypeID, False)
        return (foundItems, foundBPC, foundBPO)

    def _GetFoundItems(self, itemsInStationByTypeID, itemsToSellCopy):
        foundItems = defaultdict(list)
        for sellTypeID, sellQty in itemsToSellCopy.items():
            itemsByType = itemsInStationByTypeID.get(sellTypeID, [])
            foundItemsForSell = []
            for each in itemsByType:
                if each.itemID == session.shipid:
                    continue
                if sellQty == each.stacksize:
                    foundItemsForSell.append(each)
                    itemsToSellCopy.pop(sellTypeID)
                    break

            if foundItemsForSell:
                foundItems[sellTypeID] = foundItemsForSell

        return foundItems

    def _GetFoundBlueprints(self, sellBlueprints, itemsInStationByTypeID, findingCopies):
        foundBluprints = defaultdict(list)
        for eachBPCTypeID, qty in sellBlueprints.iteritems():
            itemsByType = itemsInStationByTypeID.get(eachBPCTypeID, [])
            itemsByType.sort(key=lambda x: x.stacksize)
            itemQty = 0
            for each in itemsByType:
                if eachBPCTypeID in foundBluprints and len(foundBluprints[eachBPCTypeID]) >= qty:
                    break
                if IsRightBlueprintVersion(each, findingCopies):
                    if itemQty + each.stacksize > qty:
                        break
                    foundBluprints[eachBPCTypeID].append(each)
                    itemQty += each.stacksize

        return foundBluprints

    def GetItemsForCorrectFlag(self):
        correctFlagID = flagHangar if not self.forCorp else self.corpFlagID
        itemsInStation = self.getItemsInStationFunc(self.startStation, self.forCorp)
        itemsInFlag = {x for x in itemsInStation if x.flagID == correctFlagID}
        return itemsInFlag

    def GetSellAndRequestedItems(self):
        requestItems = defaultdict(int)
        sellItems = defaultdict(int)
        sellBlueprintCopies = defaultdict(int)
        sellBlueprintOriginals = defaultdict(int)
        for contractItem in self.contractItems:
            if contractItem.inCrate:
                sellDictToUse = sellItems
                if IsBlueprint(contractItem.itemTypeID):
                    if IsItemBlueprintCopy(contractItem):
                        sellDictToUse = sellBlueprintCopies
                    else:
                        sellDictToUse = sellBlueprintOriginals
                sellDictToUse[contractItem.itemTypeID] += contractItem.quantity
            else:
                requestItems[contractItem.itemTypeID] += contractItem.quantity

        return (sellItems,
         sellBlueprintCopies,
         sellBlueprintOriginals,
         requestItems)

    def FindItemsInCorrectFlag(self, foundItemsByFlagID):
        if not self.forCorp:
            if len(foundItemsByFlagID) > 1:
                raise UserError('A character that has found more than one hangar to pick from? ')
            return foundItemsByFlagID[flagHangar]
        return foundItemsByFlagID.get(self.corpFlagID, [])


def IsBlueprint(typeID):
    return evetypes.GetCategoryID(typeID) == categoryBlueprint


def IsRightBlueprintVersion(item, findingCopies):
    if findingCopies:
        return IsItemBlueprintCopy(item)
    else:
        return not IsItemBlueprintCopy(item)


def IsItemBlueprintCopy(item):
    typeID = getattr(item, 'itemTypeID', None) or getattr(item, 'typeID', None)
    if not IsBlueprint(typeID):
        return False
    isCopy = item.get('copy', None) if isinstance(item, Bundle) else getattr(item, 'copy', None)
    if isCopy is not None:
        return isCopy
    if item.quantity == -2:
        return True
    return False


def FindMissingTypesAndQty(foundItems, sellItems):
    notFound = []
    for typeID, quantity in sellItems.iteritems():
        foundItemsByType = foundItems.get(typeID, [])
        for item in foundItemsByType:
            if item.typeID == typeID and item.stacksize == quantity:
                break
        else:
            notFound.append((typeID, quantity))

    return notFound


def FindMissingBlueprints(foundItems, sellItems):
    notFound = []
    for typeID, quantity in sellItems.iteritems():
        qtyFound = 0
        foundItemsByType = foundItems.get(typeID, [])
        for item in foundItemsByType:
            if item.typeID == typeID:
                qtyFound += item.stacksize

        if qtyFound != quantity:
            notFound.append((typeID, quantity - qtyFound))

    return notFound


def GetMissingTypesTxt(notFound):
    textList = []
    for t, q in notFound:
        t = u'  \u2022' + GetByLabelX('UI/Contracts/ContractsService/NameXQuantity', typeID=t, quantity=q)
        textList.append(t)

    return '<br>'.join(textList)
