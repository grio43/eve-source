#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\ledger\ledgerEntry.py
import evetypes
import telemetry
from caching.memoize import Memoize
from carbon.common.script.util.format import FmtDate, FmtAmt
from eve.client.script.ui.control.entries.util import GetFromClass
from menu import MenuLabel
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.shared.ledger.ledgerUtil import IsInRange, GetColorForBaseTypeID
from eve.common.lib import appConst as const
from eve.common.script.util.eveFormat import FmtISK
from eveservices.menu import GetMenuService
from inventorycommon.typeHelpers import GetAveragePrice
import carbonui.const as uiconst
from localization import GetByLabel
from threadutils import throttled
PERSONAL = 1
CORP = 2

def GetLedgerEntriesPersonal(allData, start = None, end = None):
    contentList = []
    for eachData in allData:
        isInRange = IsInRange(eachData.eventDate, start, end)
        if not isInRange:
            continue
        locationName = cfg.evelocations.Get(eachData.solarsystemID).name
        estPrice = _GetAveragePrice(eachData.typeID)
        qty = eachData.quantity
        qtyWasted = eachData.quantityWasted
        totalEstPrice = (estPrice or 0) * qty
        estPriceText = FmtISK(totalEstPrice, 0) if totalEstPrice else '-'
        wastedEstPrice = (estPrice or 0) * qtyWasted
        wastedEstPriceText = FmtISK(wastedEstPrice, 0) if wastedEstPrice else '-'
        volume = _GetVolume(eachData.typeID) * qty
        volumeWasted = _GetVolume(eachData.typeID) * qtyWasted
        formattedDate = FmtDate(eachData.eventDate, 'ln')
        typeName = evetypes.GetName(eachData.typeID)
        contentList.append(GetFromClass(LedgerEntry, {'label': '<t>'.join([formattedDate,
                   ' ' + typeName,
                   '<right>%s' % FmtAmt(qty),
                   '<right>%s' % FmtAmt(qtyWasted),
                   '<right>%s' % GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(volume)),
                   '<right>%s' % GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(volumeWasted)),
                   '<right>%s' % estPriceText,
                   '<right>%s' % wastedEstPriceText,
                   locationName]),
         'charID': session.charid,
         'corpID': session.corpid,
         'ledgerData': eachData,
         'formattedText': {'locationName': locationName,
                           'date': formattedDate,
                           'typeName': typeName,
                           'qty': qty,
                           'qtyWasted': qtyWasted,
                           'volume': volume,
                           'volumeWasted': volumeWasted,
                           'estPrice': int(totalEstPrice) if totalEstPrice else '',
                           'estPriceWasted': int(wastedEstPrice) if wastedEstPrice else ''},
         'entryType': PERSONAL,
         'sort_%s' % GetByLabel('UI/Ledger/OreQtyHeader'): qty,
         'sort_%s' % GetByLabel('UI/Ledger/OreWasteHeader'): qtyWasted,
         'sort_%s' % GetByLabel('UI/Common/Volume'): volume,
         'sort_%s' % GetByLabel('UI/Ledger/VolumeWastedHeader'): volumeWasted,
         'sort_%s' % GetByLabel('UI/Inventory/EstPrice'): totalEstPrice or None,
         'sort_%s' % GetByLabel('UI/Ledger/WastedPriceHeader'): wastedEstPrice or None}))

    return contentList


def GetLedgerEntriesCorp(allData, filterText):
    contentList = []
    for eachData in allData:
        data = _GetDataForEntry(eachData)
        if filterText and data['filterText'].find(filterText) < 0:
            continue
        contentList.append(GetFromClass(LedgerEntry, data))

    return contentList


@telemetry.ZONE_METHOD
def _GetDataForEntry(eachData):
    typeName = _GetTypeName(eachData.typeID)
    estPrice = _GetAveragePrice(eachData.typeID)
    qty = eachData.quantity
    totalEstPrice = (estPrice or 0) * qty
    estPriceText = FmtISK(totalEstPrice, 0) if totalEstPrice else ''
    volume = _GetVolume(eachData.typeID) * qty
    formattedDate = FmtDate(eachData.eventDate, 'ln')
    corpName = _GetOwnerName(eachData.corporationID)
    charName = _GetOwnerName(eachData.characterID)
    labelParts = [formattedDate,
     corpName,
     charName,
     typeName,
     '<right>%s' % FmtAmt(qty),
     '<right>%s' % GetByLabel('UI/Moonmining/NumM3', amount=FmtAmt(volume)),
     '<right>%s' % estPriceText]
    formattedText = {'date': formattedDate,
     'typeName': typeName,
     'qty': qty,
     'volume': volume,
     'estPrice': int(totalEstPrice) if totalEstPrice else '',
     'charName': charName,
     'corpName': corpName}
    label = '<t>'.join(labelParts)
    filterText = '%s %s %s' % (corpName, typeName, charName)
    data = {'label': label,
     'charID': eachData.characterID,
     'corpID': eachData.corporationID,
     'ledgerData': eachData,
     'formattedText': formattedText,
     'entryType': CORP,
     'filterText': filterText.lower(),
     'sort_%s' % GetByLabel('UI/Ledger/OreQtyHeader'): qty,
     'sort_%s' % GetByLabel('UI/Common/Volume'): volume,
     'sort_%s' % GetByLabel('UI/Inventory/EstPrice'): totalEstPrice or None}
    return data


@Memoize(1)
def _GetTypeName(typeID):
    return evetypes.GetName(typeID)


@Memoize(1)
def _GetAveragePrice(typeID):
    return GetAveragePrice(typeID) or evetypes.GetBasePrice(typeID) or 0


@Memoize(1)
def _GetOwnerName(corpID):
    return cfg.eveowners.Get(corpID).name


@Memoize(1)
def _GetLocationName(solarSystemID):
    return cfg.evelocations.Get(solarSystemID).name


@Memoize(1)
def _GetVolume(typeID):
    return evetypes.GetVolume(typeID)


def GetObserverLocation(observerItemID):
    return cfg.evelocations.Get(observerItemID).name


class LedgerEntry(Generic):
    __guid__ = 'listentry.LedgerEntry'
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, *args)
        self.legendFill = Fill(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 8, 8))
        self.legendFill.display = False

    def Load(self, node):
        Generic.Load(self, node)
        if node.entryType == PERSONAL:
            self.legendFill.display = True
            color = GetColorForBaseTypeID(node.ledgerData.typeID)
            newColor = tuple(color[:3]) + (0.5,)
            self.legendFill.SetRGBA(*newColor)

    def GetMenu(self):
        data = self.sr.node
        m = []
        if data.entryType == PERSONAL:
            m += [(MenuLabel('UI/Common/SolarSystem'), GetMenuService().CelestialMenu(data.ledgerData.solarsystemID))]
        elif data.entryType == CORP:
            m += [(MenuLabel('UI/Common/Pilot', {'character': data.charID}), GetMenuService().CharacterMenu(data.charID))]
            m += [(MenuLabel('UI/Common/Corporation'), GetMenuService().GetMenuFromItemIDTypeID(data.corpID, const.typeCorporation))]
        m += [None]
        oreTypeID = data.ledgerData.typeID
        m += [(evetypes.GetName(oreTypeID), GetMenuService().GetMenuFromItemIDTypeID(None, oreTypeID, includeMarketDetails=True))]
        return m

    def OnMouseEnter(self, *args):
        Generic.OnMouseEnter(self, *args)
        ScatterMouseOverChange(self.sr.node.ledgerData.typeID)

    def OnMouseExit(self, *args):
        Generic.OnMouseExit(self, *args)
        ScatterMouseOverChange(None)

    def UpdateLegendFillPos(self, left):
        self.legendFill.left = left + 2


@throttled(0.1)
def ScatterMouseOverChange(typeID):
    sm.ScatterEvent('OnLedgerMouseOverChanged', typeID)
