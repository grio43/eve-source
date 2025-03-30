#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\marketHistory.py
import blue
import carbonui.const as uiconst
import eveicon
import evetypes
from caching import Memoize
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtDate
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.common.script.util.eveFormat import FmtISK
from menu import MenuLabel, MenuList
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eveservices.menu import GetMenuService
from localization import GetByLabel
from utillib import KeyVal
from eve.common.lib import appConst as const
TOPCONTHEIGHT = 26

class MarketHistory(Container):
    __guid__ = 'MarketHistory'
    __notifyevents__ = ['OnOwnOrdersChanged']
    default_name = 'MarketHistory'
    lastUpdateTime = None
    refrehHistoryTimer = None

    def ApplyAttributes(self, attributes):
        self.isInitialized = False
        self.includesCorpOrders = False
        super(MarketHistory, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)

    def Close(self, *args, **kwds):
        Container.Close(self, *args, **kwds)
        sm.UnregisterNotify(self)

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.PopulateScroll()

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        if not self.display or self.destroyed:
            return
        self.RefreshHistory()

    def RefreshHistory(self):
        if self.refrehHistoryTimer:
            return
        if self.lastUpdateTime:
            diff = max(1, blue.os.TimeDiffInMs(self.lastUpdateTime, blue.os.GetWallclockTime()))
            BUFFER_TIME = 30000
            if diff > BUFFER_TIME:
                self._RefreshHistory()
            else:
                waitTime = int(max(1, BUFFER_TIME - diff))
                self.refrehHistoryTimer = AutoTimer(waitTime, self._RefreshHistory)
        else:
            self._RefreshHistory()

    def _RefreshHistory(self):
        if self.destroyed or not session.charid:
            return
        if not self.isInitialized:
            self.ConstructLayout()
        self.PopulateScroll(refreshing=1)
        self.refrehHistoryTimer = None
        self.lastUpdateTime = blue.os.GetWallclockTime()

    def ConstructLayout(self):
        self.topCont = Container(parent=self, align=uiconst.TOTOP, height=32)
        options = [(GetByLabel('UI/Market/Orders/AllOrders'), None), (GetByLabel('UI/Market/Orders/UI/Market/Orders/PersonalOrders'), 0), (GetByLabel('UI/Market/Orders/CorporationOrders'), 1, GetByLabel('UI/Market/Orders/CorpHistoryHint'))]
        comboPrefsKey = ('char', 'ui', 'marketOrderHistory')
        ownerTypeSelected = settings.char.ui.Get('marketOrderHistory', None)
        self.ownerCombo = Combo(parent=self.topCont, options=options, name='marketOrder_history', prefskey=comboPrefsKey, callback=self.OnOwnerComboChanged, select=ownerTypeSelected, pos=(6, 6, 0, 0), width=200)
        self.mainCont = Container(name='mainCont', parent=self)
        self.dividerCont = DragResizeCont(name='dividerCont', settingsID='marketOrderHistory', parent=self.mainCont, align=uiconst.TOTOP_PROP, minSize=0.25, maxSize=0.75, defaultSize=0.5, clipChildren=True, show_line=True)
        self.sellParent = Container(name='sellParent', parent=self.dividerCont.mainCont)
        self.buyParent = Container(name='buyParent', parent=self.mainCont)
        self.ConstructSellCont()
        self.ConstructBuyCont()

    def ConstructSellCont(self):
        self.sellTopCont = Container(name='sellTopCont', parent=self.sellParent, align=uiconst.TOTOP, height=TOPCONTHEIGHT)
        self.sellFilter = QuickFilterEdit(name='sellFilter', parent=self.sellTopCont, left=const.defaultPadding, align=uiconst.CENTERRIGHT, width=150, hintText=GetByLabel('UI/Market/Orders/FilterTypes'), isTypeField=True)
        self.sellFilter.ReloadFunction = self.ReloadSellScroll
        EveCaptionSmall(text=GetByLabel('UI/Market/Orders/Selling'), parent=self.sellTopCont, align=uiconst.RELATIVE, left=4)
        self.sellScroll = Scroll(name='orderHistorySellScroll', parent=self.sellParent)
        self.sellScroll.multiSelect = 0
        self.sellScroll.sr.id = 'orderHistorySellScroll'

    def ConstructBuyCont(self):
        self.buyTopCont = Container(name='buyTopCont', parent=self.buyParent, align=uiconst.TOTOP, height=TOPCONTHEIGHT)
        self.buyFilter = QuickFilterEdit(name='buyFilter', parent=self.buyTopCont, left=const.defaultPadding, align=uiconst.CENTERRIGHT, width=150, hintText=GetByLabel('UI/Market/Orders/FilterTypes'), isTypeField=True)
        self.buyFilter.ReloadFunction = self.ReloadBuyScroll
        EveCaptionSmall(text=GetByLabel('UI/Market/Orders/Buying'), parent=self.buyTopCont, align=uiconst.RELATIVE, left=4)
        self.buyScroll = Scroll(name='orderHistoryBuyScroll', parent=self.buyParent)
        self.buyScroll.multiSelect = 0
        self.buyScroll.sr.id = 'orderHistoryBuyScroll'

    def ReloadSellScroll(self):
        history = sm.GetService('marketQuote').GetMarketOrderHistory()
        self.LoadSellcroll(history)

    def ReloadBuyScroll(self):
        history = sm.GetService('marketQuote').GetMarketOrderHistory()
        self.LoadBuyScroll(history)

    def OnOwnerComboChanged(self, *args):
        self.ownerCombo.UpdateSettings()
        self.PopulateScroll()

    def IsShowingExtraColumn(self):
        if not self.includesCorpOrders:
            return False
        if self.ownerCombo.GetValue() is None:
            return True
        return False

    def PopulateScroll(self, refreshing = 0):
        history = sm.GetService('marketQuote').GetMarketOrderHistory()
        self.includesCorpOrders = any((x for x in history if x.isCorp))
        if self.includesCorpOrders:
            self.topCont.display = True
        else:
            self.topCont.display = False
        self.LoadBuyScroll(history, refreshing)
        self.LoadSellcroll(history, refreshing)

    def LoadBuyScroll(self, history, refreshing = 0):
        buyScrollList = self.GetScrollList(history, self.buyFilter, self.buyScroll)
        self.LoadScroll(self.buyScroll, buyScrollList, refreshing=refreshing)

    def LoadSellcroll(self, history, refreshing = 0):
        sellScrollList = self.GetScrollList(history, self.sellFilter, self.sellScroll)
        self.LoadScroll(self.sellScroll, sellScrollList, refreshing=refreshing)

    def LoadScroll(self, scroll, scrollList, refreshing = 0):
        scrollTo = None
        if refreshing:
            scrollTo = scroll.GetScrollProportion()
        headers = [' '] if self.IsShowingExtraColumn() else []
        headers += [GetByLabel('UI/Generic/Status'),
         GetByLabel('UI/Common/Updated'),
         GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Market/MarketQuote/RemainingQuantity'),
         GetByLabel('UI/Market/MarketQuote/headerPrice'),
         GetByLabel('UI/Common/Station'),
         GetByLabel('UI/Common/LocationTypes/Region')]
        scroll.Load(contentList=scrollList, scrollTo=scrollTo, headers=headers, noContentHint=GetByLabel('UI/Market/Orders/NoOrdersFound'))

    def GetScrollList(self, history, filterField, scroll):
        ownerTypeToShow = self.ownerCombo.GetValue() if self.includesCorpOrders else None
        showExtraColumn = self.IsShowingExtraColumn()
        unknownText = GetByLabel('UI/Generic/Unknown')
        structureDirectorySvc = sm.GetService('structureDirectory')
        scrollList = []
        filterValue = filterField.GetValue().strip().lower()
        for eachRecord in history:
            if eachRecord.duration < 1:
                continue
            if ownerTypeToShow is not None and ownerTypeToShow != eachRecord.isCorp:
                continue
            if not self.IsOrderRelevantForThisScroll(scroll, eachRecord):
                continue
            if filterValue and self.GetTypeNameLower(eachRecord.typeID).find(filterValue) < 0:
                continue
            data = self.GetEntryDataForOrder(eachRecord, unknownText, showExtraColumn, structureDirectorySvc)
            entry = GetFromClass(OrderHistoryEntry, data)
            scrollList.append(entry)

        return scrollList

    def IsOrderRelevantForThisScroll(self, scroll, orderRecord):
        if scroll == self.buyScroll:
            return orderRecord.bid
        if scroll == self.sellScroll:
            return not orderRecord.bid
        return True

    @Memoize(2)
    def GetTypeNameLower(self, typeID):
        return evetypes.GetName(typeID).lower()

    def GetEntryDataForOrder(self, orderRecord, unknownText, showExtraColumn, structureDirectorySvc):
        orderState = unknownText
        volRemaining = int(orderRecord.volRemaining)
        lastStateChange = orderRecord.lastStateChange
        if orderRecord.orderState == 2:
            if volRemaining == 0:
                orderState = '<color=green>%s</color>' % GetByLabel('UI/Market/Orders/StatusCompleted')
            else:
                if lastStateChange is None:
                    lastStateChange = orderRecord.issueDate + orderRecord.duration * const.DAY
                orderState = '<color=red>%s</color>' % GetByLabel('UI/Market/Orders/StatusExpired')
        elif orderRecord.orderState == 3:
            orderState = GetByLabel('UI/Market/Orders/StatusCancelled')
        stationInfo = sm.GetService('ui').GetStationStaticInfo(orderRecord.stationID)
        if stationInfo:
            stationName = cfg.evelocations.Get(orderRecord.stationID).name
        else:
            structureInfo = structureDirectorySvc.GetStructureInfo(orderRecord.stationID)
            stationName = structureInfo.itemName if structureInfo else unknownText
        updateText = FmtDate(lastStateChange) if lastStateChange else '-'
        labelList = [orderState,
         updateText,
         evetypes.GetName(orderRecord.typeID),
         '%s / %s' % (volRemaining, orderRecord.volEntered),
         '<right>%s</right>' % FmtISK(orderRecord.price),
         stationName,
         cfg.evelocations.Get(orderRecord.regionID).name]
        if showExtraColumn:
            labelPath = 'UI/Market/Orders/CorporationOrderShort' if orderRecord.isCorp else 'UI/Market/Orders/PersonalOrderShort'
            labelList.insert(0, GetByLabel(labelPath))
        label = '<t>'.join(labelList)
        data = KeyVal(label=label, order=orderRecord, OnDblClick=self.ShowMarketDetilsForTypeInOrder)
        data.Set('sort_%s' % GetByLabel('UI/Market/MarketQuote/RemainingQuantity'), (int(orderRecord.volRemaining), orderRecord.volEntered))
        data.Set('sort_%s' % GetByLabel('UI/Market/MarketQuote/headerPrice'), float(orderRecord.price))
        data.Set('sort_%s' % GetByLabel('UI/Common/Updated'), lastStateChange or -1)
        data.Set('sort_%s' % GetByLabel('UI/Common/Station'), stationName.lower())
        return data

    def ShowMarketDetilsForTypeInOrder(self, order):
        sm.StartService('marketutils').ShowMarketDetails(order.typeID, None)


class OrderHistoryEntry(Generic):

    def GetMenu(self):
        self.OnClick()
        m = MenuList()
        order = self.sr.node.order
        m.append(None)
        m += GetMenuService().GetMenuFromItemIDTypeID(None, order.typeID, includeMarketDetails=True)
        m.append(None)
        stationID = order.stationID
        solarSystemID = order.solarSystemID
        stationInfo = sm.GetService('ui').GetStationStaticInfo(stationID)
        if stationInfo:
            m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(stationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID, mapItem=None), texturePath=eveicon.location))
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
            if structureInfo:
                m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(stationID, typeID=structureInfo.typeID, parentID=stationID), texturePath=eveicon.location))
            elif solarSystemID:
                m += [(MenuLabel('UI/Common/SolarSystem'), GetMenuService().CelestialMenu(solarSystemID))]
        if session.role & ROLE_GML > 0:
            m.append(('GM - orderID: %s' % order.orderID, blue.pyos.SetClipboardData, (str(order.orderID),)))
        return m
