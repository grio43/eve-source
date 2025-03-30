#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\entries.py
import eveicon
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from chroma import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from menu import MenuLabel
from carbonui import uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.fitting.ghostFittingHelpers import TryPreviewFitItemOnMouseAction
import localization
from eve.common.script.util.eveFormat import GetAveragePrice, FmtISKAndRound
from marketutil.quickbarUtil import GetTypesUnderFolder, TICKER_SETTING_NAME, TICKER_MAX_ITEMS_FROM_QUICKBAR
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
import evetypes
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
import blue
BLUE_COLOR = Color.from_rgba(*eveColor.ULTRAMARINE_BLUE)
GREEN_COLOR = Color.from_rgba(*eveColor.SUCCESS_GREEN)
YELLOW_COLOR = Color.from_rgba(*eveColor.SAND_YELLOW)
BACKGROUND_OPACITY = 0.3

class MarketOrder(Generic):
    __guid__ = 'listentry.MarketOrder'

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.sr.bgFill = None
        self.orderMarker = None

    def Load(self, node):
        Generic.Load(self, node)
        data = self.sr.node
        if data.inMyPath:
            self.sr.label.color = YELLOW_COLOR
        if data.markAsMine:
            self.ShowBackground(BLUE_COLOR.with_alpha(BACKGROUND_OPACITY))
            self.ShowOrderMarker(eveicon.person, BLUE_COLOR)
        elif data.flag == 1 and data.mode == 'sell':
            self.ShowBackground(color=GREEN_COLOR.with_alpha(BACKGROUND_OPACITY))
            self.ShowOrderMarker(eveicon.checkmark, GREEN_COLOR)
        else:
            if data.inMyPath:
                self.ShowOrderMarker(eveicon.location, YELLOW_COLOR)
            elif self.orderMarker:
                self.orderMarker.display = False
            if self.sr.bgFill:
                self.sr.bgFill.display = False
        if data.isLabelOffset:
            self.sr.label.left = 20

    def ShowBackground(self, color, *args):
        if self.sr.bgFill is None:
            self.sr.bgFill = Fill(bgParent=self, color=color, state=uiconst.UI_DISABLED)
        self.sr.bgFill.SetRGBA(*color)
        self.sr.bgFill.display = True

    def ShowOrderMarker(self, texturePath, color):
        if self.orderMarker is None or self.orderMarker.destroyed:
            self.orderMarker = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(2, 0, 16, 16), state=uiconst.UI_NORMAL)
            self.orderMarker.LoadTooltipPanel = self.LoadMarkerTooltipPanel
        self.orderMarker.texturePath = texturePath
        self.orderMarker.SetRGBA(*color)
        self.orderMarker.display = True

    def Buy(self, node = None, ignoreAdvanced = False, *args):
        if not hasattr(self, 'sr'):
            return
        node = node if node is not None else self.sr.node
        sm.GetService('marketutils').Buy(self.sr.node.order.typeID, node.order, 0, ignoreAdvanced=ignoreAdvanced)

    def ShowInfo(self, node = None, *args):
        node = node if node is not None else self.sr.node
        sm.GetService('info').ShowInfo(node.order.typeID)

    def GetMenu(self):
        self.OnClick()
        m = []
        if self.sr.node.mode == 'buy':
            m.append((MenuLabel('UI/Market/Marketbase/BuyThis'), self.Buy, (self.sr.node, True)))
        else:
            m += [(MenuLabel('UI/Market/Marketbase/CommandPlaceBuyOrder'), self.Buy)]
        m.append(None)
        m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.sr.node,))]
        stationID = self.sr.node.order.stationID
        solarSystemID = self.sr.node.order.solarSystemID
        if stationID:
            stationInfo = sm.GetService('ui').GetStationStaticInfo(stationID)
            if stationInfo:
                m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(stationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID, mapItem=None), texturePath=eveicon.location))
            else:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
                if structureInfo:
                    m.append(MenuEntryData(MenuLabel('UI/Common/Location'), subMenuData=GetMenuService().CelestialMenu(stationID, typeID=structureInfo.typeID, parentID=stationID), texturePath=eveicon.location))
                elif solarSystemID:
                    m += [(MenuLabel('UI/Common/SolarSystem'), GetMenuService().CelestialMenu(solarSystemID))]
        if self.sr.node.markAsMine:
            m.append((MenuLabel('UI/Market/Orders/ModifyOrder'), self.ModifyPrice, (self.sr.node,)))
            m.append((MenuLabel('UI/Market/Orders/CancelOrder'), self.CancelOffer, (self.sr.node,)))
        return m

    def _GetStationInvItemInBallpark(self, stationID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if not ballpark:
            return None
        return ballpark.GetInvItem(stationID)

    def OnDblClick(self, *args):
        if self.sr.node.mode == 'buy':
            self.Buy(ignoreAdvanced=True)

    def ModifyPrice(self, node):
        sm.GetService('marketutils').ModifyOrder(node.order)

    def CancelOffer(self, node):
        sm.GetService('marketutils').CancelOffer(node.order)

    def LoadMarkerTooltipPanel(self, tooltipPanel, *args):
        data = self.sr.node
        tooltipPanel.LoadGeneric1ColumnTemplate()
        if bool(bool(data.markAsMine) + bool(data.flag)) + bool(data.inMyPath) > 1:
            prefix = '- '
        else:
            prefix = ''
        if data.markAsMine:
            text = prefix + localization.GetByLabel('UI/Market/Marketbase/YourOrderHint')
            tooltipPanel.AddLabelMedium(text=text)
        elif data.flag:
            text = prefix + localization.GetByLabel('UI/Market/Marketbase/CanSellToOrderHint')
            tooltipPanel.AddLabelMedium(text=text)
        if data.inMyPath:
            text = prefix + localization.GetByLabel('UI/Market/Marketbase/InRouteHint')
            tooltipPanel.AddLabelMedium(text=text)


class MarketListGroup(ListGroup):

    def GetMenu(self):
        m = super(MarketListGroup, self).GetMenu()
        if session.role & ROLE_GML:
            market_group_info = self.sr.node.get('marketGroupInfo', None)
            if market_group_info:
                m.append(MenuEntryData('QA: MarketGroupID={}'.format(market_group_info.marketGroupID), func=lambda : blue.pyos.SetClipboardData(str(market_group_info.marketGroupID))))
        return m


class GenericMarketItem(Generic):
    __guid__ = 'listentry.GenericMarketItem'
    isDragObject = True

    def Startup(self, *args):
        labelCont = Container(name='labelCont', parent=self, padRight=20)
        Generic.Startup(self, *args)
        self.sr.label.SetParent(labelCont)

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.label.autoFadeSides = 16
        if not node.get('inRange', True):
            self.SetOpacity(0.5)
            self.hint = localization.GetByLabel('UI/Market/Marketbase/NotAvailableInRange')

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def OnMouseEnter(self, *args):
        Generic.OnMouseEnter(self, *args)
        TryPreviewFitItemOnMouseAction(self.sr.node, oldWindow=False)

    def OnMouseExit(self, *args):
        Generic.OnMouseExit(self, *args)
        TryPreviewFitItemOnMouseAction(None, oldWindow=False)

    def GetHint(self):
        return GetHintWithAvgPrice(self.sr.node)


class QuickbarItem(GenericMarketItem):
    __guid__ = 'listentry.QuickbarItem'

    def Load(self, node):
        GenericMarketItem.Load(self, node)
        self.sr.sublevel = node.Get('sublevel', 0)
        self.sr.label.left = 12 + max(0, self.sr.sublevel * 16)
        if node.get('extraText', ''):
            self.sr.label.text = localization.GetByLabel('UI/Market/Marketbase/QuickbarTypeNameWithExtraText', typeName=node.label, extraText=node.get('extraText', ''))
        else:
            self.sr.label.text = node.label
        if evetypes.GetMarketGroupID(node.invtype) is None:
            self.SetOpacity(0.5)
            if self.hint is not None:
                self.hint += '<br>'
            else:
                self.hint = ''
            self.hint += localization.GetByLabel('UI/Market/Marketbase/NotAvailableOnMarket')

    def OnClick(self, *args):
        if self.sr.node:
            if evetypes.GetMarketGroupID(self.sr.node.invtype) is None:
                return
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetMenu(self):
        m = []
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            m += self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            m += GetMenuService().GetMenuFromItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None), includeMarketDetails=True)
        return m

    def GetDragData(self, *args):
        nodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        return nodes

    def OnDropData(self, dragObj, nodes):
        if self.sr.node.get('DropData', None):
            self.sr.node.DropData(('quickbar', self.sr.node.parent), nodes)


class QuickbarGroup(ListGroup):
    __guid__ = 'listentry.QuickbarGroup'
    __notifyevents__ = ['OnMarketTickerSettingsUpdated']
    isDragObject = True

    def Startup(self, *etc):
        ListGroup.Startup(self, *etc)
        self.favoriteIcon = Sprite(name='favoriteIcon', parent=self, align=uiconst.CENTERRIGHT, left=4, width=16, height=16, texturePath=eveicon.star, color=TextColor.NORMAL, hint=localization.GetByLabel('UI/Market/TickerFolderHint', maxItems=TICKER_MAX_ITEMS_FROM_QUICKBAR))
        self.favoriteIcon.display = False
        sm.RegisterNotify(self)

    def Load(self, node):
        ListGroup.Load(self, node)
        if node.isTickerFolder:
            self.favoriteIcon.display = True
        else:
            self.favoriteIcon.display = False

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def GetMenu(self):
        m = ListGroup.GetMenu(self)
        quickbar = settings.user.ui.Get('quickbar', {})
        folderID = self.sr.node.id[1]
        buyDict = GetTypesUnderFolder(folderID, quickbar)
        if buyDict:
            m += [(MenuLabel('UI/Market/MarketQuote/BuyAll'),
              BuyMultipleTypesWithQty,
              (buyDict,),
              eveicon.isk.resolve(16))]
        if self.IsCurrentTickerFolder():
            m += [(MenuLabel('UI/Market/TickerRemoveAsMarketTickerFolder'),
              self.ToggleAsMarketTickerFolder,
              (False,),
              eveicon.star_slash.resolve(16))]
        else:
            m += [(MenuLabel('UI/Market/TickerSetAsMarketTickerFolder'),
              self.ToggleAsMarketTickerFolder,
              (True,),
              eveicon.star.resolve(16))]
        return CreateMenuDataFromRawTuples(m)

    def ToggleAsMarketTickerFolder(self, setAsFolder):
        if self.IsCurrentTickerFolder():
            newTickerFolder = None
        else:
            newTickerFolder = self.sr.node.id[1]
        settings.char.ui.Set(TICKER_SETTING_NAME, newTickerFolder)
        sm.ScatterEvent('OnMarketTickerSettingsUpdated', newTickerFolder)

    def IsCurrentTickerFolder(self):
        folderID = self.sr.node.id[1]
        currentMarketTickerFolder = settings.char.ui.Get(TICKER_SETTING_NAME, 0)
        if folderID == currentMarketTickerFolder:
            return True
        return False

    def SetFavoriteState(self, tickerFolderID):
        self.favoriteIcon.display = tickerFolderID == self.sr.node.id[1]

    def OnMarketTickerSettingsUpdated(self, newTickerFolder):
        self.SetFavoriteState(newTickerFolder)


class MarketMetaGroupEntry(ListGroup):
    __guid__ = 'listentry.MarketMetaGroupEntry'

    def Load(self, node):
        ListGroup.Load(self, node)
        self.OnToggle = node.OnToggle

    def OnClick(self, *args, **kwargs):
        ListGroup.OnClick(self, *args)
        if self.OnToggle is not None:
            self.OnToggle()


def GetHintWithAvgPrice(data):
    hintTextList = []
    if data.showNameHint and not getattr(uicore.uilib, 'auxiliaryTooltip', None):
        typeName = evetypes.GetName(data.typeID)
        hintTextList.append(typeName)
    dataHint = data.hint
    if dataHint and dataHint not in hintTextList:
        hintTextList += [data.hint]
    marketPrice = GetAveragePrice(data)
    if marketPrice:
        marketPriceStr = FmtISKAndRound(marketPrice)
        estimatedPrice = localization.GetByLabel('UI/Inventory/ItemEstimatedPrice', estPrice=marketPriceStr)
        hintTextList.append(estimatedPrice)
    hint = '<br>'.join(filter(None, hintTextList))
    return hint
