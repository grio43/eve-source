#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipscan.py
from carbonui.primitives.frame import Frame
from collections import OrderedDict, defaultdict
import dogma.data
import evetypes
import localization
import utillib
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.sortUtil import SortListOfTuples
from dogma import units
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.util import uix
from eve.client.script.ui.control import eveLabel, eveScroll
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.fittingScreen.fittingSearchUtil import SearchFittingHelper
from eve.client.script.ui.shared.info.panels.panelFitting import FITTING_SLOT_INFO
from eve.common.script.util.eveFormat import FmtISKAndRound, GetAveragePrice

class ShipScan(Window):
    default_windowID = 'shipscan'
    default_iconNum = 'res:/ui/Texture/WindowIcons/shipScan.png'
    default_minSize = (200, 200)
    default_width = 400
    default_height = 300

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.DefineButtons(uiconst.CLOSE)
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        self.sr.capacityText = eveLabel.EveHeaderSmall(text=' ', name='capacityText', parent=self.topParent, left=8, top=4, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED)
        self.sr.gaugeParent = Container(name='gaugeParent', align=uiconst.TOPRIGHT, parent=self.topParent, left=const.defaultPadding, height=7, width=100, state=uiconst.UI_DISABLED, top=self.sr.capacityText.top + self.sr.capacityText.textheight + 1)
        Frame(parent=self.sr.gaugeParent, color=(0.5, 0.5, 0.5, 0.3))
        self.sr.gauge = Container(name='gauge', align=uiconst.TOLEFT, parent=self.sr.gaugeParent, state=uiconst.UI_PICKCHILDREN, width=0)
        Fill(parent=self.sr.gaugeParent, color=(0.0, 0.521, 0.67, 0.1), align=uiconst.TOALL)
        Fill(parent=self.sr.gauge, color=(0.0, 0.521, 0.67, 0.6))
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        t = eveLabel.EveHeaderSmall(text=localization.GetByLabel('UI/Ship/ShipScan/hdrModulesFitted'), parent=self.topParent, left=8, state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT)
        self.LoadResult(*attributes.results)

    def LoadResult(self, capacitorCharge, capacitorCapacity, moduleList):
        total, full = capacitorCapacity, capacitorCharge
        if total:
            proportion = min(1.0, max(0.0, full / float(total)))
        else:
            proportion = 1.0
        self.sr.gauge.width = int(proportion * self.sr.gaugeParent.width)
        unit = units.get_display_name(const.unitCapacitorUnits)
        self.sr.capacityText.text = localization.GetByLabel('UI/Ship/ShipScan/CapacityResults', full=full, total=total, units=unit)
        scrolllist = []
        slotTypeDict = OrderedDict([(const.effectHiPower, defaultdict(int)),
         (const.effectMedPower, defaultdict(int)),
         (const.effectLoPower, defaultdict(int)),
         (const.effectSubSystem, defaultdict(int)),
         (const.effectRigSlot, defaultdict(int)),
         (const.effectServiceSlot, defaultdict(int))])
        slotInfoBySlotType = {x['effectID']:x for x in FITTING_SLOT_INFO}
        charges = set()
        other = defaultdict(int)
        fittingHelper = SearchFittingHelper(cfg)
        for info in moduleList:
            if type(info) == type(()):
                typeID, quantity = info
            else:
                typeID, quantity = info.typeID, info.stacksize
            if evetypes.GetCategoryID(typeID) == const.categoryCharge:
                charges.add(typeID)
            else:
                slotType = fittingHelper.GetSlotTypeForModuleType(typeID)
                if slotType in slotTypeDict:
                    slotTypeDict[slotType][typeID] += quantity
                else:
                    other[typeID] += quantity

        scrolllist = []
        for slotType, moduleList in slotTypeDict.iteritems():
            if not moduleList:
                continue
            toSort = []
            for typeID, quantity in moduleList.iteritems():
                typeName = evetypes.GetName(typeID)
                for i in range(quantity):
                    entry = self.GetData(typeID, typeName)
                    toSort.append((typeName, entry))

            slotInfo = slotInfoBySlotType.get(slotType)
            if slotInfo:
                iconID = dogma.data.get_attribute_icon_id(slotInfo['attributeID'])
                scrolllist.append(GetFromClass(HeaderEntry, {'text': self.GetFittingSlotEntryLabel(slotInfo),
                 'iconID': iconID,
                 'line': 1}))
                scrolllist += SortListOfTuples(toSort)

        if charges:
            scrolllist.append(GetFromClass(HeaderEntry, {'text': localization.GetByLabel('UI/Common/ItemTypes/Charges'),
             'line': 1}))
            toSort = []
            for eachChargeTypeID in charges:
                entry = self.GetData(eachChargeTypeID, evetypes.GetName(eachChargeTypeID))
                toSort.append((evetypes.GetName(eachChargeTypeID), entry))

            scrolllist += SortListOfTuples(toSort)
        if other:
            scrolllist.append(GetFromClass(HeaderEntry, {'text': localization.GetByLabel('UI/Common/Other'),
             'line': 1}))
            toSort = []
            for typeID, quantity in other.iteritems():
                typeName = evetypes.GetName(typeID)
                label = '%sx %s' % (quantity, typeName)
                entry = self.GetData(typeID, label)
                toSort.append((typeName, entry))

            scrolllist += SortListOfTuples(toSort)
        self.sr.scroll.Load(contentList=scrolllist)
        if len(scrolllist) == 0:
            self.SetHint(localization.GetByLabel('UI/Ship/ShipScan/hintNoModulesDetected'))
        else:
            self.SetHint(None)

    def GetFittingSlotEntryLabel(self, slotInfo):
        if slotInfo['attributeID'] == const.attributeUpgradeSlotsLeft:
            return localization.GetByLabel('UI/Corporations/Wars/Killmails/RigSlots')
        return localization.GetByLabel(slotInfo['label'])

    def GetData(self, typeID, typeName):
        entry = GetFromClass(Item, {'label': typeName,
         'itemID': None,
         'typeID': typeID,
         'getIcon': 1,
         'sublevel': 1})
        return entry

    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)


class CargoScan(Window):
    default_windowID = 'cargoScan'
    default_iconNum = 'res:/ui/Texture/WindowIcons/cargoScan.png'
    default_minSize = (200, 200)
    default_width = 400
    default_height = 300

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        shipID = attributes.shipID
        cargoList = attributes.cargoList
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        shipName = uix.GetSlimItemName(slimItem)
        self.SetCaption(localization.GetByLabel('UI/Ship/ShipScan/ShipNameCargo', shipName=shipName, cargoListLen=len(cargoList)))
        self.DefineButtons(uiconst.CLOSE)
        eveLabel.EveHeaderSmall(text=localization.GetByLabel('UI/Ship/ShipScan/hdrCargoScan'), parent=self.sr.main, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        self.bottomRightCont = Container(name='bottomRightcont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=40, clipChildren=True)
        self.bottomRightLabelCont = Container(name='bottomRightLabelCont', parent=self.bottomRightCont, clipChildren=True)
        self.totalPriceLabel = eveLabel.Label(name='totalPriceLabel', parent=self.bottomRightLabelCont, align=uiconst.BOTTOMRIGHT, pos=(5, 4, 0, 0))
        self.numItemsLabel = eveLabel.Label(name='numItemsLabel', parent=self.bottomRightLabelCont, align=uiconst.BOTTOMRIGHT, pos=(5, 20, 0, 0))
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.OnSelectionChange = self.OnItemSelectionChanged

    def ShowInfo(self, typeID, isCopy):
        sm.GetService('info').ShowInfo(typeID)

    def LoadResult(self, cargoList):
        scrolllist = []
        for typeID, quantity in cargoList:
            qty = quantity if quantity > 0 else 1
            isCopy = False
            param = {'qty': qty,
             'typeID': typeID}
            categoryID = evetypes.GetCategoryID(typeID)
            if categoryID == const.categoryBlueprint:
                if quantity == -const.singletonBlueprintCopy:
                    typeName = 'UI/Ship/ShipScan/BlueprintCopy'
                    quantity = 1
                    isCopy = True
                else:
                    typeName = 'UI/Ship/ShipScan/BlueprintOriginal'
            else:
                typeName = 'UI/Ship/ShipScan/FoundTypes'
            data = {'label': localization.GetByLabel(typeName, **param),
             'itemID': None,
             'typeID': typeID,
             'isCopy': isCopy,
             'getIcon': True,
             'qty': qty}
            if categoryID == const.categoryBlueprint:
                data['abstractinfo'] = utillib.KeyVal(categoryID=const.categoryBlueprint, isCopy=isCopy)
            scrolllist.append(GetFromClass(Item, data))

        self.sr.scroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Ship/ShipScan/NoBookmarksFound'))
        self.UpdateNumbers()

    def OnItemSelectionChanged(self, *args):
        self.UpdateNumbers()

    def UpdateNumbers(self):
        self.UpdateNumberOfItems()
        self.UpdateIskPriceLabel()

    def UpdateNumberOfItems(self):
        numSelected = len(self.sr.scroll.GetSelected())
        numTotal = len(self.sr.scroll.sr.nodes)
        if numSelected:
            text = localization.GetByLabel('UI/Inventory/NumItemsAndSelected', numItems=numTotal, numSelected=numSelected, numFilteredTxt='')
        else:
            text = localization.GetByLabel('UI/Inventory/NumItems', numItems=numTotal, numFilteredTxt='')
        self.numItemsLabel.text = text

    def UpdateIskPriceLabel(self):
        total = 0
        numSelected = len(self.sr.scroll.GetSelected())
        for eachNode in self.sr.scroll.GetNodes():
            if eachNode.isCopy:
                continue
            if numSelected and not eachNode.selected:
                continue
            price = GetAveragePrice(eachNode)
            if price:
                total += price * eachNode.qty

        text = localization.GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(total, False))
        self.totalPriceLabel.text = text


class HeaderEntry(Text):

    def Startup(self, *args):
        super(HeaderEntry, self).Startup(*args)
        FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT)

    def GetHeight(self, *args):
        node, width = args
        node.height = 28
        return 28
