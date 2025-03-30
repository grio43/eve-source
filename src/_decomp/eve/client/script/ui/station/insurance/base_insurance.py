#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\insurance\base_insurance.py
import blue
import evetypes
import localization
from caching.memoize import Memoize
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from carbonui.control.radioButton import RadioButton
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import WndCaptionLabel, EveLabelLargeBold, EveLabelMedium, EveCaptionSmall
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.script.sys.rowset import Rowset
from eve.common.script.util.eveFormat import FmtISK
from eve.common.script.util.insuranceConst import get_insurance_fractions_and_prices, get_insurance_package_by_fraction, INSURANCE_ICON
from eve.common.lib import appConst as const
from eveexceptions import UserError
from eveservices.menu import GetMenuService
from menu import MenuLabel, MenuList
HIGHLIGHT_ON_SHIP_INSURED = 2261

class InsuranceSvc(Service):
    __exportedcalls__ = {'CleanUp': [],
     'Reset': [],
     'GetContracts': []}
    __guid__ = 'svc.insurance'
    __notifyevents__ = ['OnSessionChanged', 'OnItemChange', 'OnShipInsured']
    __servicename__ = 'insurance'
    __displayname__ = 'Insurance Service'
    __dependencies__ = ['station']

    def __init__(self):
        Service.__init__(self)
        self.scroll = None
        self.insurance = None
        self.contracts = {}
        self.stuff = {}
        self.insurancePrice = {}

    def Run(self, memStream = None):
        self.LogInfo('Insurance Service Started')
        self.wnd = None
        self.CleanUp()

    def Stop(self, memStream = None):
        self.LogInfo('Insurance Medical Service')
        self.CleanUp()
        Service.Stop(self)

    def CleanUp(self):
        self.insurance = None
        self.contracts = {}
        self.stuff = {}

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change or 'structureid' in change:
            self.insurance = None

    def OnItemChange(self, item, change, location):
        if const.ixOwnerID not in change:
            return
        if change[const.ixOwnerID] not in (session.charid, session.corpid):
            return
        if item.categoryID != const.categoryShip:
            return
        wnd = InsuranceWindow.GetIfOpen()
        if not wnd or wnd.destroyed:
            return
        wnd.ShowInsuranceInfo()

    def Reset(self):
        pass

    def GetInsuranceMgr(self):
        if session.stationid:
            dockableLocation = session.stationid
            locationID = session.stationid
            locationGroup = const.groupStation
            sessionCheckDict = {'stationid': session.stationid}
        elif session.structureid:
            dockableLocation = session.structureid
            locationID = session.solarsystemid2
            locationGroup = const.groupSolarSystem
            sessionCheckDict = {'structureid': session.structureid}
        else:
            raise RuntimeError('Trying to insure when neither in station nor structure, that is not allowed!')
        self.insurance = Moniker('insuranceSvc', (dockableLocation, locationID, locationGroup))
        self.insurance.SetSessionCheck(sessionCheckDict)
        return self.insurance

    @Memoize(0.05)
    def GetContracts(self):
        if session.stationid:
            insuranceMgr = self.GetInsuranceMgr()
        else:
            insuranceMgr = sm.RemoteSvc('insuranceSvc')
        self.contracts = {contract.shipID:contract for contract in insuranceMgr.GetContracts()}
        if session.corprole & (const.corpRoleJuniorAccountant | const.corpRoleAccountant) != 0:
            self.contracts.update({contract.shipID:contract for contract in insuranceMgr.GetContracts(1)})
        return self.contracts

    def GetContractForShip(self, itemID):
        return sm.RemoteSvc('insuranceSvc').GetContractForShip(itemID)

    def GetInsurancePrice(self, typeID):
        if typeID in self.insurancePrice:
            return self.insurancePrice[typeID]
        if session.stationid:
            self.insurancePrice[typeID] = self.GetInsuranceMgr().GetInsurancePrice(typeID)
        else:
            self.insurancePrice[typeID] = sm.RemoteSvc('insuranceSvc').GetInsurancePrice(typeID)
        return self.insurancePrice[typeID]

    def PrimeInsurancePrices(self, typeSet):
        missingTypeList = [ t for t in typeSet if t not in self.insurancePrice ]
        if session.stationid:
            pricesByTypeIDs = self.GetInsuranceMgr().GetInsurancePrices(missingTypeList)
        else:
            pricesByTypeIDs = sm.RemoteSvc('insuranceSvc').GetInsurancePrices(missingTypeList)
        self.insurancePrice.update(pricesByTypeIDs)

    def GetItems(self):
        self.stuff = {}
        items = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = items.List(const.flagHangar)
        insurableItems = self.GetInsurableItems(items)
        self.stuff.update(insurableItems)
        hasAccountantRole = session.corprole & (const.corpRoleAccountant | const.corpRoleJuniorAccountant) != 0
        dockableLocationID = session.stationid or session.structureid
        if dockableLocationID and hasAccountantRole:
            office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
            if office is not None:
                items = sm.GetService('invCache').GetInventoryFromId(office.officeID, locationID=dockableLocationID)
                items = items.List()
                insurableCorpItems = self.GetInsurableItems(items)
                self.stuff.update(insurableCorpItems)
        return self.stuff

    def GetInsurableItems(self, items):
        validShips = set()
        for item in items:
            if not self.IsSingletonShip(item):
                continue
            validShips.add(item)

        toPrime = {s.typeID for s in validShips}
        self.PrimeInsurancePrices(toPrime)
        insurableItems = {}
        for item in validShips:
            if self.GetInsurancePrice(item.typeID) <= 0:
                continue
            insurableItems[item.itemID] = item

        return insurableItems

    def IsSingletonShip(self, item):
        if item.categoryID == const.categoryShip and item.singleton:
            return True
        return False

    def GetQuoteForShip(self, ship):
        if ship is None:
            raise UserError('InsCouldNotFindItem')
        fullInsurancePrice = self.GetInsurancePrice(ship.typeID)
        quotes = Rowset(['fraction', 'amount'])
        for fraction, cost in get_insurance_fractions_and_prices(fullInsurancePrice):
            quotes.lines.append([fraction, cost])

        return quotes

    def GetInsuranceName(self, fraction):
        insurance_package = get_insurance_package_by_fraction(fraction)
        return localization.GetByLabel('UI/Insurance/QuoteWindow/%s' % insurance_package)

    def Insure(self, item):
        if item.ownerID == session.corpid:
            isCorpItem = True
        else:
            isCorpItem = False
        wnd = InsuranceTermsWindow.GetIfOpen()
        if wnd:
            if wnd.itemID == item.itemID and not wnd.destroyed:
                wnd.Maximize()
                return
            wnd.Close()
        if isCorpItem:
            msg = 'InsAskAcceptTermsCorp'
        else:
            msg = 'InsAskAcceptTerms'
        if eve.Message(msg, {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        InsuranceTermsWindow.Open(item=item, isCorpItem=isCorpItem)

    def OnShipInsured(self):
        sm.GetService('uiHighlightingService').highlight_ui_element(HIGHLIGHT_ON_SHIP_INSURED)


class InsuranceWindow(Window):
    __guid__ = 'form.InsuranceWindow'
    default_width = 400
    default_height = 560
    default_minSize = (400, 400)
    default_windowID = 'insurance'
    default_captionLabelPath = 'Tooltips/StationServices/Insurance'
    default_descriptionLabelPath = 'Tooltips/StationServices/Insurance_description'
    default_iconNum = INSURANCE_ICON

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.contracts = {}
        self.stuff = {}
        self.corpShipsScroll = None
        self.scope = uiconst.SCOPE_DOCKED
        self.sr.insureBtns = Button(parent=ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOBOTTOM, padTop=16), align=uiconst.CENTER, label=localization.GetByLabel('UI/Insurance/InsuranceWindow/Commands/Insure'), func=self.InsureFromBtn)
        self.headers = [localization.GetByLabel('UI/Common/Type'),
         localization.GetByLabel('UI/Common/DateWords/FromDate'),
         localization.GetByLabel('UI/Common/DateWords/ToDate'),
         localization.GetByLabel('UI/Insurance/InsuranceWindow/Level'),
         localization.GetByLabel('UI/Insurance/InsuranceWindow/Name')]
        if self.ShouldShowCorpSection():
            self.DrawSplitList()
        else:
            self.DrawMyShipsScroll(parentCont=self.sr.main)
        self._insurance = None
        self.ShowInsuranceInfo()

    @property
    def insuranceSvc(self):
        if self._insurance is None:
            self._insurance = sm.GetService('insurance')
        return self._insurance

    def ShouldShowCorpSection(self):
        shouldShowCorpSection = self.CheckCorpRoles()
        return shouldShowCorpSection

    def DrawSplitList(self):
        myShipsCont = DragResizeCont(name='myShipsCont', parent=self.sr.main, align=uiconst.TOTOP_PROP, minSize=0.3, maxSize=0.7, defaultSize=0.45)
        EveLabelLargeBold(parent=myShipsCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Insurance/InsuranceWindow/MyShips'))
        self.DrawMyShipsScroll(parentCont=myShipsCont)
        corpShipsCont = Container(parent=self.sr.main, name='corpShipsCont', align=uiconst.TOALL)
        EveLabelLargeBold(parent=corpShipsCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Insurance/InsuranceWindow/CorpShips'))
        self.corpShipsScroll = Scroll(parent=corpShipsCont, multiSelect=False)
        self.corpShipsScroll.sr.id = 'corpinsurance'
        self.corpShipsScroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 30}

    def DrawMyShipsScroll(self, parentCont):
        self.myShipsScroll = Scroll(parent=parentCont, multiSelect=False)
        self.myShipsScroll.sr.id = 'insurance'
        self.myShipsScroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 30}

    def SetHint(self, hintstr = None, isCorp = False):
        if not isCorp:
            if self.myShipsScroll:
                self.myShipsScroll.ShowHint(hintstr)
        elif self.corpShipsScroll:
            self.corpShipsScroll.ShowHint(hintstr)

    def GetItemMenu(self, entry):
        item = entry.sr.node.info
        contract = self.contracts.get(item.itemID, None)
        m = MenuList()
        if contract and contract.ownerID == session.charid:
            m += [(MenuLabel('UI/Insurance/InsuranceWindow/Commands/CancelInsurance'), self.UnInsure, (item,)), None]
        m += GetMenuService().InvItemMenu(item, 1)
        return m

    def ShowInsuranceInfo(self):
        self.contracts = self.insuranceSvc.GetContracts()
        self.stuff = self.insuranceSvc.GetItems()
        myShipsList = self.GetMyShips()
        self.myShipsScroll.Load(contentList=myShipsList, headers=self.headers)
        if not len(myShipsList):
            self.SetHint(localization.GetByLabel('UI/Insurance/InsuranceWindow/NothingToInsure'))
        if self.ShouldShowCorpSection():
            corpShipsList = self.GetCorpShips()
            self.corpShipsScroll.Load(contentList=corpShipsList, headers=self.headers)
            if not len(corpShipsList):
                self.SetHint(localization.GetByLabel('UI/Insurance/InsuranceWindow/NothingToInsure'), isCorp=True)

    def CheckCorpRoles(self):
        if session.corprole & const.corpRoleAccountant != 0:
            return True
        return False

    def GetMyShips(self):
        ownerID = session.charid
        self.PrimeItems(ownerID)
        return self.CreateScrolllist(ownerID)

    def GetCorpShips(self):
        ownerID = session.corpid
        self.PrimeItems(ownerID)
        return self.CreateScrolllist(ownerID)

    def PrimeItems(self, ownerID):
        itemList = []
        for itemID in self.stuff:
            item = self.stuff[itemID]
            if item.ownerID != ownerID:
                continue
            if item.categoryID == const.categoryShip:
                itemList.append(item.itemID)

        cfg.evelocations.Prime(itemList)

    def CreateScrolllist(self, ownerID):
        scrolllist = []
        for itemID in self.stuff:
            item = self.stuff[itemID]
            if item.ownerID != ownerID:
                continue
            itemName = ''
            if item.categoryID == const.categoryShip:
                shipName = cfg.evelocations.GetIfExists(item.itemID)
                if shipName is not None:
                    itemName = shipName.locationName
            contract = None
            if self.contracts.has_key(item.itemID):
                contract = self.contracts[item.itemID]
            name = evetypes.GetName(item.typeID)
            if contract is None:
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                 '-',
                 '-',
                 '-',
                 itemName)
            else:
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (name,
                 FmtDate(contract.startDate, 'ls'),
                 FmtDate(contract.endDate, 'ls'),
                 self.insuranceSvc.GetInsuranceName(contract.fraction),
                 itemName)
            if ownerID == session.charid:
                onDblClickFunc = self.OnEntryDblClick
                onClickFunc = self.OnEntryClick
            else:
                onDblClickFunc = self.OnCorpEntryDblClick
                onClickFunc = self.OnCorpEntryClick
            entry = GetFromClass(Item, {'info': item,
             'itemID': item.itemID,
             'typeID': item.typeID,
             'label': label,
             'getIcon': 1,
             'GetMenu': self.GetItemMenu,
             'OnDblClick': onDblClickFunc,
             'selected': True,
             'OnClick': onClickFunc,
             'genericDisplayLabel': itemName})
            scrolllist.append(entry)

        return scrolllist

    def OnEntryClick(self, entry):
        if self.corpShipsScroll:
            self.corpShipsScroll.DeselectAll()

    def OnCorpEntryClick(self, entry):
        self.myShipsScroll.DeselectAll()

    def OnEntryDblClick(self, entry):
        self.Insure(None)

    def OnCorpEntryDblClick(self, entry):
        self.Insure(None)

    def UnInsure(self, item, *args):
        if item is None or not len(item):
            return
        if eve.Message('InsAskUnInsure', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        self.insuranceSvc.GetInsuranceMgr().UnInsureShip(item.itemID)
        self.ShowInsuranceInfo()

    def GetSelected(self):
        corpSelected = None
        if self.corpShipsScroll:
            corpSelected = self.corpShipsScroll.GetSelected()
        mySelected = self.myShipsScroll.GetSelected()
        if mySelected:
            return [ node.info for node in mySelected ]
        if corpSelected:
            return [ node.info for node in corpSelected ]

    def InsureFromBtn(self, *args):
        self.Insure(None)

    def Insure(self, item, *args):
        if item is None or not len(item):
            item = self.GetSelected()
            if not item:
                eve.Message('SelectShipToInsure')
                return
            item = item[0]
        return self.insuranceSvc.Insure(item)


iconsSize = 64

class InsuranceTermsWindow(Window):
    default_width = 440
    default_height = 300
    default_minSize = (default_width, default_height)
    default_windowID = 'InsuranceTermsWindow'
    default_caption = localization.GetByLabel('UI/Insurance/QuoteWindow/Title')

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.scope = uiconst.SCOPE_DOCKED
        self.isCorpItem = attributes.isCorpItem
        self.item = attributes.item
        self.itemID = self.item.itemID
        self.insuranceSvc = sm.GetService('insurance')
        self.mainCont = ContainerAutoSize(parent=self.sr.main, name='mainCont', align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=self._OnMainContSizeChanged, only_use_callback_when_size_changes=True)
        self.topCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=iconsSize, padding=(2, 2, 2, 6))
        self.ConstructTypeIcon()
        self.ConstructTypeNameLabel()
        text = localization.GetByLabel('UI/Insurance/QuoteWindow/SelectInsuranceLevel')
        EveCaptionSmall(parent=self.mainCont, name='nameLabel', align=uiconst.TOTOP, text=text)
        maxEntryWidth = self.ConstructRadioButtons()
        self.ConstructButtonGroup()

    def _OnMainContSizeChanged(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
        self.SetMinSize([self.default_width, max(self.height, self.default_height)])

    def ConstructRadioButtons(self):
        insurancePrice = self.insuranceSvc.GetInsurancePrice(self.item.typeID)
        quotes = self.insuranceSvc.GetQuoteForShip(self.item)
        self.quotesCbs = []
        maxEntryWidth = 0
        for quote in quotes:
            text = localization.GetByLabel('UI/Insurance/QuoteWindow/Line', name=self.insuranceSvc.GetInsuranceName(quote.fraction), cost=localization.GetByLabel('UI/Common/Cost'), amount=FmtISK(quote.amount), payout=localization.GetByLabel('UI/Insurance/QuoteWindow/EstimatedPayout'), price=FmtISK(quote.fraction * insurancePrice))
            cb = RadioButton(parent=self.mainCont, align=uiconst.TOTOP, text=text, retval=str(quote.fraction), checked=quote.fraction == 0.5, groupname='quotes')
            cb.quote = quote
            self.quotesCbs.append(cb)
            maxEntryWidth = max(maxEntryWidth, cb.padLeft + cb.label.textwidth + cb.label.padLeft + 20)

        return maxEntryWidth

    def ConstructTypeNameLabel(self):
        shipTextList = self.GetShipTextList()
        shipText = '<br>'.join(shipTextList)
        typeNameLabel = EveLabelMedium(parent=self.topCont, name='nameLabel', align=uiconst.TOTOP, text=shipText, padding=(6, 0, 6, 0))

    def GetShipTextList(self):
        shipTextList = [evetypes.GetName(self.item.typeID)]
        shipInfo = cfg.evelocations.GetIfExists(self.item.itemID)
        if shipInfo:
            shipTextList.append(shipInfo.locationName)
        contracts = self.insuranceSvc.GetContracts()
        shipContract = contracts.get(self.item.itemID)
        if shipContract:
            if shipContract.ownerID in (session.corpid, session.charid):
                insuranceName = self.insuranceSvc.GetInsuranceName(shipContract.fraction)
                timeDiff = shipContract.endDate - blue.os.GetWallclockTime()
                timeLeft = localization.GetByLabel('UI/Insurance/TimeLeft', time=timeDiff)
                currentLevelText = localization.GetByLabel('UI/Insurance/QuoteWindow/CurrentLevel', insuranceLevel=insuranceName, timeLeft=timeLeft)
                shipTextList.append(currentLevelText)
        return shipTextList

    def ConstructTypeIcon(self):
        typeIcon = Icon(parent=self.topCont, width=iconsSize, align=uiconst.TOLEFT)
        typeIcon.LoadIconByTypeID(typeID=self.item.typeID, size=iconsSize, ignoreSize=True)
        typeIcon.GetMenu = lambda *args: GetMenuService().InvItemMenu(self.item)

    def ConstructButtonGroup(self):
        btnGroup = ButtonGroup(btns=[], parent=self.mainCont, align=uiconst.TOTOP, padTop=16)
        btnGroup.AddButton(label=localization.GetByLabel('UI/Insurance/InsuranceWindow/Commands/Insure'), func=self.Accept, args=(self.item.itemID, self.isCorpItem), isDefault=True)
        btnGroup.AddButton(label=localization.GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, isDefault=False)

    def Accept(self, itemID, isCorpItem):
        quote = None
        for cb in self.quotesCbs:
            if cb.checked:
                quote = cb.quote
                break

        if quote is None:
            raise RuntimeError('No insurance option chosen')
        insuringText = localization.GetByLabel('UI/Insurance/ProgressWindow/Insuring')
        cancelledText = localization.GetByLabel('UI/Insurance/QuoteWindow/InsuringCancelled')
        sm.GetService('loading').ProgressWnd(insuringText, '', 0, 1)
        try:
            self.insuranceSvc.GetInsuranceMgr().InsureShip(itemID, quote.amount, isCorpItem)
            sm.GetService('loading').ProgressWnd(insuringText, '', 1, 1)
        except UserError as e:
            if e.msg == 'InsureShipFailedSingleContract':
                ownerID = e.args[1]['ownerName']
                ownerInfo = cfg.eveowners.Get(ownerID)
                ownerName = GetShowInfoLink(ownerInfo.typeID, ownerInfo.name, ownerID)
                if eve.Message('InsureShipAlreadyInsured', {'ownerName': ownerName}, uiconst.YESNO) == uiconst.ID_YES:
                    cancelledText = ''
                    self.insuranceSvc.GetInsuranceMgr().InsureShip(itemID, quote.amount, isCorpItem, voidOld=True)
            else:
                cancelledText = localization.GetByLabel('UI/Insurance/QuoteWindow/InsuringFailed')
                raise
        finally:
            self.Close()
            sm.GetService('loading').ProgressWnd(insuringText, cancelledText, 1, 1)
            self.TryUpdateInsuranceWindow()

    def Cancel(self, btn):
        self.Close()

    def TryUpdateInsuranceWindow(self):
        wnd = InsuranceWindow.GetIfOpen()
        if not wnd or wnd.destroyed:
            return
        wnd.ShowInsuranceInfo()
