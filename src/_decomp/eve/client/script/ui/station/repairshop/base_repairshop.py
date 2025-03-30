#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\repairshop\base_repairshop.py
import math
import evetypes
import inventorycommon.const as invConst
import localization
import uthread
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.util import uix
from eve.common.lib import appConst
from eve.common.script.sys import eveCfg
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from inventorycommon.util import IsFittingModule
from menu import MenuLabel
from repair import IsRepairable

class RepairSvc(Service):
    __guid__ = 'svc.repair'
    __notifyevents__ = ['OnSessionChanged']
    __servicename__ = 'repair'
    __displayname__ = 'Repair Service'

    def __init__(self):
        Service.__init__(self)
        self.repairMgr = None

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change or 'structureid' in change:
            self.repairMgr = None

    def GetRemoteRepairMgr(self):
        if session.stationid:
            dockableLocation = session.stationid
            locationID = session.stationid
            locationGroup = invConst.groupStation
            sessionCheckDict = {'stationid': session.stationid}
        elif session.structureid:
            dockableLocation = session.structureid
            locationID = session.solarsystemid2
            locationGroup = invConst.groupSolarSystem
            sessionCheckDict = {'structureid': session.structureid}
        else:
            raise RuntimeError('Trying to access repair manager when neither in station nor structure, that is not allowed!')
        self.repairMgr = Moniker('repairSvc', (dockableLocation, locationID, locationGroup))
        self.repairMgr.SetSessionCheck(sessionCheckDict)
        return self.repairMgr

    def GetRepairQuotes(self, itemIDs):
        return self.GetRemoteRepairMgr().GetRepairQuotes(itemIDs)

    def RepairItems(self, itemIDs, payment):
        if session.stationid:
            self.GetRemoteRepairMgr().RepairItemsInStation(itemIDs, payment)
        elif session.structureid:
            self.GetRemoteRepairMgr().RepairItemsInStructure(itemIDs)
        else:
            raise RuntimeError('Must be in station or structure to use repair service')


class RepairShopWindow(Window):
    __guid__ = 'form.RepairShopWindow'
    default_width = 400
    default_height = 300
    default_minSize = (350, 270)
    default_windowID = 'repairshop'
    default_captionLabelPath = 'UI/Station/Repair/RepairShopHeader'
    default_descriptionLabelPath = 'Tooltips/StationServices/Repairshop_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/repairshop.png'
    default_scope = uiconst.SCOPE_DOCKED

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.invCookie = None
        self.invReady = 0
        self.optionsByItemType = {}
        self.itemToRepairDescription = ''
        self.invCache = sm.GetService('invCache')
        self.ConstructTopParent()
        buttonGroup = ButtonGroup(parent=self.sr.main)
        self.pickBtn = buttonGroup.AddButton(localization.GetByLabel('UI/Commands/PickNewItem'), self.DisplayItems)
        self.repairItemBtn = buttonGroup.AddButton(localization.GetByLabel('UI/Commands/RepairItem'), self.QuoteItems)
        self.repairAllBtn = buttonGroup.AddButton(localization.GetByLabel('UI/Commands/RepairAll'), self.DoNothing)
        self.scroll = eveScroll.Scroll(parent=self.sr.main, padding=(0, 16, 0, 0))
        self.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 30}
        uthread.new(self.DisplayItems)

    def ConstructTopParent(self):
        topParent = ContainerAutoSize(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, clipChildren=True)
        self.avgDamageLabel = eveLabel.EveLabelLarge(parent=topParent, name='avgDamage', state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.totalCostLabel = eveLabel.EveLabelLarge(parent=topParent, name='totalCost', state=uiconst.UI_NORMAL, align=uiconst.TOTOP, padTop=4)

    def DisplayItems(self, *args):
        self.itemToRepairDescription = ''
        self.HideButtons()
        btnSetup = {self.pickBtn: uiconst.UI_HIDDEN,
         self.repairItemBtn: uiconst.UI_NORMAL,
         self.repairAllBtn: uiconst.UI_HIDDEN}
        self.SetHint()
        self.avgDamageLabel.Hide()
        self.totalCostLabel.Hide()
        try:
            hangarInv = sm.GetService('invCache').GetInventory(appConst.containerHangar)
            items = hangarInv.List(invConst.flagHangar)
            ships = []
            tmplst = []
            for item in items:
                if IsRepairable(item):
                    if item.categoryID == invConst.categoryShip:
                        ships.append(item)
                    else:
                        tmplst.append((evetypes.GetName(item.typeID), item))

            shipIDs = [ s.itemID for s in ships ]
            cfg.evelocations.Prime(shipIDs)
            for item in ships:
                tmplst.append((cfg.evelocations.Get(item.itemID).name, item))

            if len(tmplst) == 0:
                self.SetHint(localization.GetByLabel('UI/Station/Repair/NothingToRepair', repairShop=localization.GetByLabel('UI/Station/Repair/RepairFacilities')))
            else:
                scrolllist = []
                currIndex = 1
                for label, item in tmplst:
                    scrolllist.append(GetFromClass(Item, {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': label,
                     'getIcon': 1,
                     'GetMenu': self.GetItemInHangarMenu,
                     'OnDblClick': self.OnDblClick,
                     'name': 'repairEntry%s' % currIndex,
                     'GetSortValue': self.GetNodeSortValue}))

                self.scroll.sr.id = None
                self.scroll.sr.ignoreTabTrimming = 1
                self.state = uiconst.UI_NORMAL
                self.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Type')])
        finally:
            self.state = uiconst.UI_NORMAL

        self.DisplayButtons(btnSetup)

    def GetNodeSortValue(self, node, by, sortDirection, idx):
        ret = self.scroll._GetSortValue(by, node, idx)
        if node.itemID == session.shipid:
            return (sortDirection, ret)
        return (not sortDirection, ret)

    def GetSelected(self):
        return [ node.info for node in self.scroll.GetSelected() ]

    def GetAll(self):
        return [ node.info for node in self.scroll.GetNodes() ]

    def QuoteItems(self, *args):
        self.DisplayRepairQuote(self.GetSelected())

    def SetHint(self, hintstr = None):
        if self.scroll:
            self.scroll.ShowHint(hintstr)

    def DoNothing(self, *args):
        pass

    def GetItemInHangarMenu(self, entry):
        item = entry.sr.node.info
        items = self.GetSelected()
        if item not in items:
            items.append(item)
        m = GetMenuService().GetMenuFromItemIDTypeID(item.itemID, item.typeID)
        m += [(MenuLabel('UI/Inventory/ItemActions/GetRepairQuote'), self.DisplayRepairQuote, (items,))]
        return m

    def OnDblClick(self, *args):
        self.DisplayRepairQuote(self.GetSelected())

    def GetItemMenu(self, entry):
        info = entry.sr.node.info
        m = GetMenuService().GetMenuFromItemIDTypeID(info.itemID, info.typeID)
        items = self.GetSelected()
        if info not in items:
            items.append(info)
        if info.damage > 0.0:
            m += [(MenuLabel('UI/Commands/Repair'), self.Repair, (items,))]
        return m

    def OnItemDblClick(self, entry):
        info = entry.sr.node.info
        items = self.GetSelected()
        if info not in items:
            items.append(info)
        if info.damage > 0.0:
            uthread.new(self.Repair, items)

    def DisplayRepairQuote(self, items, *args):
        if not len(items):
            return
        self.itemToRepairDescription = ''
        self.HideButtons()
        btnSetup = {self.pickBtn: uiconst.UI_HIDDEN,
         self.repairItemBtn: uiconst.UI_HIDDEN}
        self.SetHint()
        totalitems = 0
        totaldamage = 0.0
        totalcost = 0
        self.itemToRepairDescription = ''
        scrolllist = []
        listEntryData = []
        repairQuotes = {}
        itemIDs = []
        for item in items:
            itemIDs.append(item.itemID)

        if len(itemIDs):
            repairQuotes = sm.GetService('repair').GetRepairQuotes(itemIDs)
        currIndex = 1
        for item in items:
            for quote in repairQuotes[item.itemID]:
                if quote.itemID in [ entryData['itemID'] for entryData in listEntryData ]:
                    continue
                damage = math.ceil(quote.damage)
                if damage == 0:
                    continue
                dmg = localization.GetByLabel('UI/Station/Repair/CurrentDamage', curHealth=max(0, int(quote.maxHealth - damage)), maxHealth=quote.maxHealth, percentHealth=damage / float(quote.maxHealth or 1) * 100.0)
                cst = localization.GetByLabel('UI/Station/Repair/RepairCostNumberOnly', isk=int(math.ceil(damage * quote.costToRepairOneUnitOfDamage)))
                totalitems += 1
                totaldamage += damage / float(quote.maxHealth or 1) * 100.0
                totalcost += damage * quote.costToRepairOneUnitOfDamage
                label = evetypes.GetName(quote.typeID) + '<t>' + dmg + '<t>' + cst
                listEntryData.append({'info': quote,
                 'itemID': quote.itemID,
                 'typeID': quote.typeID,
                 'label': label,
                 'getIcon': 1,
                 'GetMenu': self.GetItemMenu,
                 'OnDblClick': self.OnItemDblClick,
                 'name': 'subRepairEntry%s' % currIndex})
                currIndex += 1

        listEntryData.sort(lambda a, b: -(a['label'].upper() < b['label'].upper()))
        for entryData in listEntryData:
            scrolllist.append(GetFromClass(Item, entryData))

        if not totaldamage:
            activeShip = eveCfg.GetActiveShip()
            if activeShip is not None and activeShip in [ item.itemID for item in items ]:
                btnSetup[self.repairAllBtn] = uiconst.UI_HIDDEN
        else:
            self.repairAllBtn.OnClick = self.RepairAll
            self.repairAllBtn.SetLabel(localization.GetByLabel('UI/Commands/RepairAll'))
            btnSetup[self.repairAllBtn] = uiconst.UI_NORMAL
        self.scroll.sr.id = 'repair3'
        self.scroll.sr.ignoreTabTrimming = 0
        hint = localization.GetByLabel('UI/Station/Repair/NothingToRepair', repairShop=localization.GetByLabel('UI/Station/Repair/RepairFacilities'))
        headers = [localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Damage'), localization.GetByLabel('UI/Common/Cost')]
        self.scroll.Load(fixedEntryHeight=35, contentList=scrolllist, headers=headers, noContentHint=hint)
        self.avgDamageLabel.Show()
        self.avgDamageLabel.text = localization.GetByLabel('UI/Station/Repair/AverageDamage', damage=totaldamage / (totalitems or 1))
        self.totalCostLabel.Show()
        self.totalCostLabel.text = localization.GetByLabel('UI/Station/Repair/RepairCost', isk=int(math.ceil(totalcost)))
        self.state = uiconst.UI_NORMAL
        btnSetup[self.pickBtn] = uiconst.UI_NORMAL
        self.DisplayButtons(btnSetup)

    def Repair(self, items, *args):
        self.RepairItems(items)

    def RepairAll(self, *args):
        self.RepairItems(self.GetAll())

    def RepairItems(self, items):
        totalCost = 0
        hasModule = False
        for item in items:
            totalCost += math.ceil(item.damage) * item.costToRepairOneUnitOfDamage
            categoryID = evetypes.GetCategoryIDByGroup(item.groupID)
            if IsFittingModule(categoryID):
                hasModule = True

        btnSetup = {self.repairItemBtn: uiconst.UI_HIDDEN,
         self.pickBtn: uiconst.UI_NORMAL}
        amount = None
        if totalCost > 0.0:
            if hasModule:
                if eve.Message('RepairNonPartialConfirmation', {'isk': FmtISK(totalCost)}, uiconst.YESNO) == uiconst.ID_YES:
                    amount = totalCost
            else:
                dialogResult = uix.QtyPopup(totalCost, 0, totalCost, hint=localization.GetByLabel('UI/Station/Repair/FullRepair', isk=totalCost), label=localization.GetByLabel('UI/Station/Repair/RepairCostLabel'), digits=2)
                if dialogResult is not None:
                    amount = dialogResult['qty']
        else:
            amount = 0.0
        if amount is not None:
            itemIDs = []
            try:
                for item in items:
                    if self.invCache.IsItemLocked(item.itemID):
                        raise UserError('ItemLocked', {'item': evetypes.GetName(item.typeID)})
                    if not self.invCache.TryLockItem(item.itemID, 'lockUnassemblingItem', {}, 1):
                        raise UserError('ItemLocked', {'item': evetypes.GetName(item.typeID)})
                    itemIDs.append(item.itemID)

                if len(itemIDs):
                    sm.GetService('repair').RepairItems(itemIDs, amount)
            finally:
                for itemID in itemIDs:
                    self.invCache.UnlockItem(itemID)

                sm.ScatterEvent('OnRepairDone', itemIDs)
                uthread.new(self.DisplayRepairQuote, self.GetAll())

        else:
            btnSetup[self.repairAllBtn] = uiconst.UI_NORMAL
        self.DisplayButtons(btnSetup)

    def HideButtons(self):
        btnParent = self.pickBtn.parent
        for btn in btnParent.children:
            btn.state = uiconst.UI_HIDDEN

    def DisplayButtons(self, btnSetup):
        for btn, state in btnSetup.iteritems():
            btn.state = state

        totalWidth = 0
        btnParent = self.pickBtn.parent
        for btn in btnParent.children:
            if btn.state != uiconst.UI_HIDDEN:
                totalWidth = totalWidth + btn.width

        left = self.pickBtn.parent.width / 2 - totalWidth / 2
        for btn in btnParent.children:
            if btn.state != uiconst.UI_HIDDEN:
                btn.left = left
                left = left + btn.width + 4
