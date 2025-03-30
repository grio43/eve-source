#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\orders.py
import blue
import carbonui.const as uiconst
import eveicon
import evetypes
import log
import utillib
from caching import Memoize
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.control.dragdrop.dragdata import TypeDragData
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.quickFilter import QuickFilterEdit
from menu import MenuLabel, MenuList
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eveservices.menu import GetMenuService
from localization import GetByLabel
TOPCONTHEIGHT = 26

class MarketOrders(Container):
    __guid__ = 'form.MarketOrders'
    __nonpersistvars__ = []
    __notifyevents__ = ['OnOwnOrdersChanged']
    default_name = 'MarketOrders'
    lastUpdateTime = None
    refreshOrdersTimer = None

    def ApplyAttributes(self, attributes):
        super(MarketOrders, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.isInitialized = False
        self.totalEscrow = 0.0
        self.totalLeft = 0.0
        self.totalIncome = 0.0
        self.totalExpenses = 0.0

    def Close(self, *args, **kwds):
        Container.Close(self, *args, **kwds)
        sm.UnregisterNotify(self)
        self.lastUpdateTime = None
        self.refreshOrdersTimer = None

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        self.PopulateScroll()

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        if self.state == uiconst.UI_HIDDEN or self.destroyed:
            return
        self.RefreshOrders()

    def RefreshOrders(self):
        if self.lastUpdateTime and self.refreshOrdersTimer is None:
            diff = max(1, blue.os.TimeDiffInMs(self.lastUpdateTime, blue.os.GetWallclockTime()))
            if diff > 30000:
                self._RefreshOrders()
            else:
                self.refreshOrdersTimer = AutoTimer(int(diff), self._RefreshOrders)
        else:
            self._RefreshOrders()

    def _RefreshOrders(self):
        if not self.isInitialized:
            self.ConstructLayout()
        self.PopulateScroll(refreshing=1)
        self.refreshOrdersTimer = None
        self.lastUpdateTime = blue.os.GetWallclockTime()

    def ConstructLayout(self):
        self.ConstructBottomCont()
        self.mainCont = Container(name='mainCont', parent=self)
        self.dividerCont = DragResizeCont(name='dividerCont', settingsID='marketOrders', parent=self.mainCont, align=uiconst.TOTOP_PROP, minSize=0.25, maxSize=0.75, defaultSize=0.5, clipChildren=True, show_line=True)
        self.sellParent = Container(name='sellParent', parent=self.dividerCont.mainCont)
        self.buyParent = Container(name='buyParent', parent=self.mainCont)
        self.ConstructSellCont()
        self.ConstructBuyCont()
        w, h = self.GetAbsoluteSize()
        self._OnSizeChange_NoBlock(w, h)

    def ConstructSellCont(self):
        self.ConstructSellTopCont()
        self.sellScroll = Scroll(name='sellscroll', parent=self.sellParent)
        self.sellScroll.multiSelect = 0
        self.sellScroll.smartSort = 1
        self.sellScroll.ignoreHeaderWidths = 1
        self.sellScroll.sr.id = 'ordersSellScroll'
        self.sellScroll.OnColumnChanged = self.OnOrderSellColumnChanged

    def ConstructSellTopCont(self):
        self.sellTopCont = Container(name='sellTopCont', parent=self.sellParent, align=uiconst.TOTOP, height=TOPCONTHEIGHT)
        self.sellFilter = QuickFilterEdit(name='sellFilter', parent=self.sellTopCont, left=const.defaultPadding, align=uiconst.CENTERRIGHT, width=150, hintText=GetByLabel('UI/Market/Orders/FilterTypes'), isTypeField=True)
        self.sellFilter.ReloadFunction = self.PopulateScroll
        EveCaptionSmall(text=GetByLabel('UI/Market/Orders/Selling'), parent=self.sellTopCont, align=uiconst.RELATIVE, left=4)

    def ConstructBuyCont(self):
        self.ConstructBuyTopCont()
        self.buyScroll = Scroll(name='buyscroll', parent=self.buyParent)
        self.buyScroll.multiSelect = 0
        self.buyScroll.smartSort = 1
        self.buyScroll.ignoreHeaderWidths = 1
        self.buyScroll.sr.id = 'ordersBuyScroll'
        self.buyScroll.OnColumnChanged = self.OnOrderBuyColumnChanged

    def ConstructBuyTopCont(self):
        self.buyTopCont = Container(name='buyTopCont', parent=self.buyParent, align=uiconst.TOTOP, height=TOPCONTHEIGHT)
        self.buyFilter = QuickFilterEdit(name='buyFilter', parent=self.buyTopCont, left=const.defaultPadding, align=uiconst.CENTERRIGHT, width=150, hintText=GetByLabel('UI/Market/Orders/FilterTypes'), isTypeField=True)
        self.buyFilter.ReloadFunction = self.PopulateScroll
        EveCaptionSmall(text=GetByLabel('UI/Market/Orders/Buying'), parent=self.buyTopCont, align=uiconst.RELATIVE, left=4)

    def ConstructBottomCont(self):
        pass

    def GetOrders(self):
        raise NotImplementedError

    def OnOrderBuyColumnChanged(self, *args):
        self.PopulateScroll()

    def OnOrderSellColumnChanged(self, *args):
        self.PopulateScroll()

    def PopulateScroll(self, refreshing = 0):
        sscrollList = []
        sheaders = self.GetSellHeaders()
        self.sellScroll.sr.headers = sheaders
        visibleSHeaders = self.sellScroll.GetColumns()
        bscrollList = []
        bheaders = self.GetBuyHeaders()
        self.buyScroll.sr.headers = bheaders
        visibleBHeaders = self.buyScroll.GetColumns()
        marketUtil = sm.GetService('marketutils')
        orders = self.GetOrders()
        if self.destroyed:
            return
        self.UpdateOrderTotals(orders)
        buySelected = self.buyScroll.GetSelected()
        sellSelected = self.sellScroll.GetSelected()
        funcs = sm.GetService('marketutils').GetFuncMaps()
        buyFilterValue = self.buyFilter.GetValue().strip().lower()
        sellFilterValue = self.sellFilter.GetValue().strip().lower()
        filteredOutOrders = [0, 0]
        for order in orders:
            data = utillib.KeyVal()
            data.label = ''
            data.typeID = order.typeID
            data.order = order
            data.OnDblClick = self.ShowMarketDetilsForTypeInOrder
            if evetypes.Exists(order.typeID):
                data.showinfo = 1
            if order.bid:
                filterValue = buyFilterValue
                selected = buySelected
                visibleHeaders = visibleBHeaders
                scrollList = bscrollList
            else:
                filterValue = sellFilterValue
                selected = sellSelected
                visibleHeaders = visibleSHeaders
                scrollList = sscrollList
            if filterValue and self.GetTypeNameLower(order.typeID).find(filterValue) < 0:
                filteredOutOrders[order.bid] += 1
                continue
            if selected and selected[0].order.orderID == order.orderID:
                data.isSelected = 1
            for header in visibleHeaders:
                header = StripTags(header, stripOnly=['localized'])
                funcName = funcs.get(header, None)
                if funcName == 'GetQuantity':
                    funcName = 'GetQuantitySlashVolume'
                if funcName and hasattr(marketUtil, funcName):
                    apply(getattr(marketUtil, funcName, None), (order, data))
                else:
                    log.LogWarn('Unsupported header in record', header, order)
                    data.label += '###<t>'

            data.label = data.label.rstrip('<t>')
            scrollList.append(GetFromClass(OrderEntry, data))

        buyScrollTo = None
        sellScrollTo = None
        if refreshing:
            buyScrollTo = self.buyScroll.GetScrollProportion()
            sellScrollTo = self.sellScroll.GetScrollProportion()
        filteredOutSell = filteredOutOrders[0]
        self.sellScroll.Load(contentList=sscrollList, headers=sheaders, scrollTo=sellScrollTo, noContentHint=GetByLabel('UI/Market/Marketbase/NoOrdersMatched') if filteredOutSell else GetByLabel('UI/Market/Orders/NoOrdersFound'))
        filteredOutBuy = filteredOutOrders[1]
        self.buyScroll.Load(contentList=bscrollList, headers=bheaders, scrollTo=buyScrollTo, noContentHint=GetByLabel('UI/Market/Marketbase/NoOrdersMatched') if filteredOutBuy else GetByLabel('UI/Market/Orders/NoOrdersFound'))

    @Memoize(10)
    def GetTypeNameLower(self, typeID):
        return evetypes.GetName(typeID).lower()

    def UpdateOrderTotals(self, orders):
        pass

    def GetBuyHeaders(self):
        return [GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Quantity'),
         GetByLabel('UI/Market/MarketQuote/headerPrice'),
         GetByLabel('UI/Common/Station'),
         GetByLabel('UI/Common/LocationTypes/Region'),
         GetByLabel('UI/Common/Range'),
         GetByLabel('UI/Market/MarketQuote/HeaderMinVolumn'),
         GetByLabel('UI/Market/Marketbase/ExpiresIn')]

    def GetSellHeaders(self):
        return [GetByLabel('UI/Common/Type'),
         GetByLabel('UI/Common/Quantity'),
         GetByLabel('UI/Market/MarketQuote/headerPrice'),
         GetByLabel('UI/Common/Station'),
         GetByLabel('UI/Common/LocationTypes/Region'),
         GetByLabel('UI/Market/Marketbase/ExpiresIn')]

    def ShowMarketDetilsForTypeInOrder(self, order):
        sm.StartService('marketutils').ShowMarketDetails(order.typeID, None)


class OrderEntry(Generic):
    __guid__ = 'listentry.OrderEntry'
    __nonpersistvars__ = []
    isDragObject = True

    def GetMenu(self):
        self.OnClick()
        m = MenuList()
        order = self.sr.node.order
        if order.charID == session.charid:
            m.append((MenuLabel('UI/Market/Orders/CancelOrder'), self.CancelOffer, (self.sr.node,)))
            m.append((MenuLabel('UI/Market/Orders/ModifyOrder'), self.ModifyPrice, (self.sr.node,)))
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
        return m

    def GetDragData(self, *args):
        order = self.sr.node.order
        return [TypeDragData(typeID=order.typeID)]

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.sr.node.order.typeID)

    def CancelOffer(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('marketutils').CancelOffer(node.order)

    def ModifyPrice(self, node = None):
        node = node if node != None else self.sr.node
        sm.GetService('marketutils').ModifyOrder(node.order)
