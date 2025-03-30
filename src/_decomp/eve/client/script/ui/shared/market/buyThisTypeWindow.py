#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\buyThisTypeWindow.py
import sys
import carbonui.const as uiconst
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui import ButtonVariant, TextColor
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.fontconst import EVE_SMALL_FONTSIZE, STYLE_SMALLTEXT
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetAttrs
from carbonui.button.group import ButtonGroup
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionMedium
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.utilButtons.marketDetailsButton import ShowMarketDetailsButton
from carbonui.window.header.default import DefaultWindowHeader
from eve.client.script.ui.shared.cloneGrade import ORIGIN_BUYONMARKET
from eve.client.script.ui.shared.cloneGrade.omegaRestrictedEntry import OmegaRestrictedEntry
from eve.client.script.ui.shared.market.singleLineEditMarketPrice import SingleLineEditMarketPrice
from eve.client.script.ui.util.qtyTooltipUtil import AssignQtyTooltipFunc
from eve.client.script.ui.util.searchOld import Search
from eve.client.script.ui.util.uix import HybridWnd
from eve.common.script.util.eveFormat import FmtISK
from eve.common.lib.appConst import corpRoleAccountant, corpRoleTrader, mktMinimumFee
from eve.common.script.sys.idCheckers import IsStation
from eveexceptions import UserError
from evetypes import GetName
from inventorycommon.const import groupStation, categoryStructure
from localization import GetByLabel, GetByMessageID
from log import LogException
from marketutil.const import rangeRegion, rangeStation, rangeSolarSystem
from menu import MenuLabel
from qtyTooltip.qtyConst import EDIT_INPUT_TYPE_ISK
LINE_HEIGHT = 40
LEFT_SIDE_LABEL_WIDTH = 110
LEFT_SIDE_LABEL_WIDTH_PADDING = 24
LEFT_SIDE_LABEL_PATHS = ['UI/Common/Location',
 'UI/Market/MarketQuote/labelBidPrice',
 'UI/Market/MarketQuote/RegionalAdverage',
 'UI/Market/MarketQuote/BestRegional',
 'UI/Market/MarketQuote/BestMatchable',
 'UI/Common/Quantity',
 'UI/Market/MarketQuote/Duration',
 'UI/Common/Range',
 'UI/Market/MarketQuote/BrokersFee',
 'UI/Generic/Total']

class MarketActionWindowHeader(DefaultWindowHeader):

    def _create_icon(self, window):
        icon_size = self._get_icon_size(window)
        self._caption_icon = Icon(parent=ContainerAutoSize(parent=self._main_cont, align=uiconst.TOLEFT, left=-5), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=icon_size, height=icon_size)

    def _layout(self, window):
        super(MarketActionWindowHeader, self)._layout(window)
        self.show_market_details_btn = ShowMarketDetailsButton(parent=self.extra_content, align=uiconst.CENTERLEFT, width=16, height=16)
        self.info_icon = InfoIcon(parent=self.extra_content, align=uiconst.CENTERLEFT, left=20)

    def set_type_id(self, type_id):
        self._caption_icon.LoadIconByTypeID(type_id)
        self.show_market_details_btn.SetTypeID(type_id)
        self.info_icon.SetTypeID(type_id)


class MarketActionWindow(Window):
    default_windowID = 'marketbuyaction'
    default_iconNum = 'res:/ui/Texture/WindowIcons/market.png'
    default_fixedWidth = 470
    default_isCollapseable = False

    def ApplyAttributes(self, attributes):
        super(MarketActionWindow, self).ApplyAttributes(attributes)
        self.clipChildren = 1
        self.sr.currentOrder = None
        self.sr.stationID = None
        self.mainCont = None
        self.quantity = 1
        self.remoteBuyLocation = None
        self.lastTotalValue = None
        self.bestAskDict = {}
        self.bestMatchableAskDict = {}
        self.bestBidDict = {}
        self.durations = [[GetByLabel('UI/Market/MarketQuote/Immediate'), 0],
         [GetByLabel('UI/Common/DateWords/Day'), 1],
         [GetByLabel('UI/Market/MarketQuote/ThreeDays'), 3],
         [GetByLabel('UI/Common/DateWords/Week'), 7],
         [GetByLabel('UI/Market/MarketQuote/TwoWeeks'), 14],
         [GetByLabel('UI/Common/DateWords/Month'), 30],
         [GetByLabel('UI/Market/MarketQuote/ThreeMonths'), 90]]
        self.ranges = [[GetByLabel('UI/Common/LocationTypes/Station'), rangeStation],
         [GetByLabel('UI/Common/LocationTypes/SolarSystem'), rangeSolarSystem],
         [GetByLabel('UI/Common/LocationTypes/Region'), rangeRegion],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=1), 1],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=2), 2],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=3), 3],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=4), 4],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=5), 5],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=10), 10],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=20), 20],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=30), 30],
         [GetByLabel('UI/Market/MarketQuote/NumberOfJumps', num=40), 40]]
        leftSideLabelsWidths = [ uicore.font.GetTextWidth(GetByLabel(label), fontsize=EVE_SMALL_FONTSIZE, fontStyle=STYLE_SMALLTEXT) for label in LEFT_SIDE_LABEL_PATHS ]
        self.leftSideLabelsWidth = max(LEFT_SIDE_LABEL_WIDTH, max(leftSideLabelsWidths) + LEFT_SIDE_LABEL_WIDTH_PADDING)
        self.mainCont = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, callback=self._OnMainContSizeChanged)
        self.bidprice = None
        self.qty = None
        self.min = None
        self.duration = None
        self.range = None
        self.useCorp = None
        self.singleOrderBrokerFee = None
        self.currentBrokerFeePerc = None
        self.originalBrokersFeePerc = None

    def CalculateAndSetOriginalBrokersFee(self):
        self.originalBrokersFeePerc = sm.GetService('marketQuote').GetBrokersFeeCommissionFromStationID(self.sr.stationID)

    def FlushMain(self):
        if self.mainCont is not None:
            self.mainCont.Flush()
        self.lastTotalValue = None

    def _OnMainContSizeChanged(self):
        if self.mainCont is not None:
            _, height = self.GetWindowSizeForContentSize(height=self.mainCont.height)
            self.SetFixedHeight(height)

    def LoadBuy_Detailed(self, typeID, order = None, duration = 1, locationID = None, forceRange = False, quantity = 1):
        settings.char.ui.Set('advancedBuyWnd', 1)
        self.remoteBuyLocation = None
        if locationID:
            self.remoteBuyLocation = locationID
            location = cfg.evelocations.Get(locationID)
        elif order:
            location = cfg.evelocations.Get(order.stationID)
        else:
            location = None
        setattr(self, 'order', order)
        if location is None:
            return
        self.sr.stationID = location.locationID
        self.CalculateAndSetOriginalBrokersFee()
        self.loading = 'buy'
        self.ready = False
        self.FlushMain()
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        bestMatchableAsk = quote.GetBestAskInRange(typeID, self.sr.stationID, rangeStation, 1)
        if bestMatchableAsk:
            self.sr.hasMatch = True
        else:
            self.sr.hasMatch = False
        self.typeID = typeID
        self.SetCaption(GetByLabel('UI/Market/MarketQuote/BuyItem', typeID=typeID))
        self.header.set_type_id(typeID)
        self.sr.isBuy = True
        strippedName = StripTags(location.name)
        fullName = location.name
        shortName = strippedName
        if len(shortName) > 64:
            shortName = shortName[:61] + '...'
        if fullName == strippedName:
            name = strippedName
        else:
            name = fullName.replace(strippedName, shortName)
        locationText = self.AddText(GetByLabel('UI/Common/Location'), '<color=0xffffbb00>%s</color>' % name, ui_name='location')
        lt = locationText.children[1]
        lt.GetMenu = self.GetLocationMenu
        lt.expandOnLeft = 1
        lt.hint = GetByLabel('UI/Search/SelectStation')
        lt.height += 1
        self.AddSpace(where=self.sr.main)
        if order:
            price = self.bidprice if self.bidprice is not None else order.price
            self.AddPriceEditLine(GetByLabel('UI/Market/MarketQuote/labelBidPrice'), price, True, ui_name='price')
        else:
            if bestMatchableAsk:
                bestPrice = bestMatchableAsk.price
            else:
                bestPrice = averagePrice
            price = self.bidprice if self.bidprice is not None else bestPrice
            self.AddPriceEditLine(GetByLabel('UI/Market/MarketQuote/labelBidPrice'), price, True, ui_name='price')
        self.AddSpace(where=self.sr.main)
        self.AddText(GetByLabel('UI/Market/MarketQuote/RegionalAdverage'), FmtISK(averagePrice))
        self.AddText(GetByLabel('UI/Market/MarketQuote/BestRegional'), '', 'quoteText')
        self.AddText(GetByLabel('UI/Market/MarketQuote/BestMatchable'), '', refName='matchText')
        self.AddSpace(where=self.sr.main)
        quantity = self.qty if self.qty is not None else quantity
        self.AddQuantityEditLine(quantity, showMin=1)
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and 'duration' in buySettings:
            duration = buySettings['duration']
        limits = quote.GetSkillLimits(self.sr.stationID)
        dist = quote.GetStationDistance(self.sr.stationID)
        canRemoteTrade = False
        if dist <= limits['bid']:
            canRemoteTrade = True
        duration2 = self.duration if self.duration is not None else duration
        if canRemoteTrade:
            self.AddCombo(GetByLabel('UI/Market/MarketQuote/Duration'), self.durations, duration2, 'duration', refName='duration', maxVisibleEntries=len(self.durations))
        else:
            self.AddCombo(GetByLabel('UI/Market/MarketQuote/Duration'), self.durations[0:1], 0, 'duration', refName='duration')
        ranges = self._GetAvailableRanges(canRemoteTrade, locationID, forceRange, limits, order)
        firstRange = rangeStation
        buySettings = settings.user.ui.Get('buydefault', {})
        if buySettings and 'range' in buySettings:
            firstRange = buySettings['range']
        orderRange = self.range if self.range is not None else firstRange
        combo = self.AddCombo(GetByLabel('UI/Common/Range'), ranges, orderRange, 'duration', refName='range')
        self.OnComboChange(combo, GetByLabel('UI/Common/LocationTypes/Station'), rangeStation)
        self.AddSpace(where=self.sr.main)
        self.AddText(GetByLabel('UI/Market/MarketQuote/BrokersFee'), '-', 'fee')
        if not IsStation(self.sr.stationID):
            self.AddSpace(where=self.sr.main)
            self.AddText(GetByLabel('UI/Market/MarketQuote/SccSurchargeFee'), '-', 'sccSurcharge')
        t = self.AddBigText(GetByLabel('UI/Generic/Total'), '-', 'totalOrder')
        t.state = uiconst.UI_NORMAL
        self.MakeCorpCheckboxMaybe()
        self.AddSpace(where=self.sr.main)
        self.sr.rememberBuySettings = Checkbox(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, minHeight=LINE_HEIGHT), align=uiconst.CENTERLEFT, padding=0, text=GetByLabel('UI/Market/MarketQuote/RememberSettings'), settingsKey='rememberBuySettings')
        bottomCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.CENTER, padTop=16)
        mainButtons = ButtonGroup(parent=bottomCont, align=uiconst.CENTER)
        buyButton = mainButtons.AddButton(label=GetByLabel('UI/Market/MarketQuote/CommandBuy'), func=self.Buy, args=(), isDefault=True)
        mainButtons.AddButton(label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, args=())
        Button(parent=bottomCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Market/MarketQuote/SimpleOrder'), func=self.GoPlaceBuyOrder, args=(typeID,
         order,
         1,
         locationID), hint=GetByLabel('Tooltips/Market/MarketBuySimpleButton'), variant=ButtonVariant.GHOST)
        if not sm.GetService('marketutils').HasAccessToMarketAtLocation(location.locationID):
            self.AddSpace(where=self.sr.main)
            textPar = self.AddText('hide', GetByMessageID(516618, structureName=fullName))
            textPar.padLeft = 4
            buyButton.Disable()
            self.SetFixedHeight(230)
            return
        buyButton.Enable()
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()

    def Prepare_Header_(self):
        self.header = MarketActionWindowHeader()

    def CheckAddOmegaBanner(self):
        if sm.GetService('cloneGradeSvc').IsRestricted(self.typeID):
            OmegaRestrictedEntry(parent=self.mainCont, align=uiconst.TOTOP, height=30, padTop=8, origin=ORIGIN_BUYONMARKET, reason=self.typeID)
            return True
        return False

    def _GetAvailableRanges(self, canRemoteTrade, locationID, forceRange, limits, order):
        atSelectedLocation = session.stationid == locationID or session.structureid == locationID
        if atSelectedLocation:
            return self.ranges
        notDocked = session.stationid is None and session.structureid is None
        if order or notDocked or forceRange:
            ranges = [self.ranges[0]]
            if canRemoteTrade:
                for orderRange in self.ranges[1:]:
                    if orderRange[1] <= limits['vis'] or limits['vis'] > self.ranges[-1][1]:
                        ranges.append(orderRange)

        else:
            ranges = self.ranges
        return ranges

    def MakeCorpCheckboxMaybe(self):
        if session.corprole & (corpRoleAccountant | corpRoleTrader):
            n = sm.GetService('corp').GetMyCorpAccountName()
            if n is not None:
                useCorpWallet = False
                buySettings = settings.user.ui.Get('buydefault', {})
                if buySettings and 'useCorpWallet' in buySettings:
                    useCorpWallet = buySettings['useCorpWallet']
                useCorpWallet2 = self.useCorp if self.useCorp is not None else useCorpWallet
                self.sr.usecorp = Checkbox(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, minHeight=LINE_HEIGHT), align=uiconst.CENTERLEFT, padding=0, text=GetByLabel('UI/Market/MarketQuote/UseCorpAccount', accountName=n), settingsKey='usecorp', checked=useCorpWallet2)

    def TradeSimple(self, typeID = None, order = None, locationID = None, ignoreAdvanced = False, quantity = 1):
        if not ignoreAdvanced:
            settings.char.ui.Set('advancedBuyWnd', 0)
        self.remoteBuyLocation = None
        self.SetFixedHeight(230)
        quote = sm.GetService('marketQuote')
        averagePrice = quote.GetAveragePrice(typeID)
        marketRange = sm.GetService('marketutils').GetMarketRange()
        self.typeID = typeID
        if locationID:
            self.remoteBuyLocation = locationID
            location = cfg.evelocations.Get(locationID)
        elif order:
            location = cfg.evelocations.Get(order.stationID)
        else:
            location = None
        if location is None:
            return
        self.sr.stationID = location.locationID
        if order is None and not eve.session.stationid:
            marketRange = rangeStation
            order = quote.GetBestAskInRange(typeID, self.sr.stationID, rangeStation, 1)
            if order:
                order.jumps = quote.GetStationDistance(self.sr.stationID, False)
        else:
            order = order or quote.GetBestAskInRange(typeID, self.sr.stationID, marketRange, 1)
        if order is not None:
            location = cfg.evelocations.Get(order.stationID)
            locationID = location.locationID
            self.remoteBuyLocation = locationID
            self.sr.stationID = locationID
        self.CalculateAndSetOriginalBrokersFee()
        self.SetCaption(GetByLabel('UI/Market/MarketQuote/BuyType', typeID=typeID))
        self.loading = 'buy'
        self.ready = False
        self.FlushMain()
        self.header.set_type_id(typeID)
        if order:
            locationText = self.AddText(GetByLabel('UI/Common/Location'), location.name, ui_name='location')
            self.sr.isBuy = False
            lt = locationText.children[1]
            lt.GetMenu = self.GetLocationMenu
            lt.height += 1
            if session.stationid and order.stationID != session.stationid:
                if order.jumps == 0:
                    self.AddText(GetByLabel('UI/Market/MarketQuote/headerWarrning'), GetByLabel('UI/Market/MarketQuote/InDifferentStationInSystem'), color=(1.0, 0.0, 0.0, 1.0))
                else:
                    self.AddText(GetByLabel('UI/Market/MarketQuote/headerWarrning'), GetByLabel('UI/Market/MarketQuote/InDifferentStationInDifferntSystem', jumps=order.jumps), color=(1.0, 0.0, 0.0, 1.0))
            elif session.solarsystemid and order.jumps > 0:
                self.AddText(GetByLabel('UI/Market/MarketQuote/headerWarrning'), GetByLabel('UI/Market/MarketQuote/InDifferentStationInDifferntSystem', jumps=order.jumps), color=(1.0, 0.0, 0.0, 1.0))
        if order:
            colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
            if order.bid:
                colors.reverse()
            self.sr.percentage = (order.price - averagePrice) / averagePrice
            p = {'price': order.price,
             'percentage': round(100 * self.sr.percentage, 2),
             'aboveBelow': GetByLabel('UI/Market/MarketQuote/PercentBelow') if order.price < averagePrice else GetByLabel('UI/Market/MarketQuote/PercentAbove'),
             'colorFormat': colors[order.price >= averagePrice],
             'colorFormatEnd': '</color>'}
            self.AddText(GetByLabel('UI/Market/MarketQuote/headerPrice'), GetByLabel('UI/Market/MarketQuote/PriceDisplay', **p), ui_name='price')
        else:
            msg = 'UI/Market/MarketQuote/NoOneIsSellingHere'
            p = {'typeID': typeID}
            if marketRange == rangeStation:
                p['location'] = GetByLabel('UI/Common/LocationTypes/Station')
            elif marketRange == rangeSolarSystem:
                p['location'] = GetByLabel('UI/Common/LocationTypes/SolarSystem')
            elif marketRange == rangeRegion:
                p['location'] = GetByLabel('UI/Common/LocationTypes/Region')
            if sm.GetService('marketutils').HasAccessToMarketAtLocation(location.locationID):
                self.AddText('hide', GetByLabel(msg, **p))
            else:
                textPar = self.AddText('hide', GetByMessageID(516618, structureName=location.name))
                textPar.padLeft = 4
        if order:
            if order.bid:
                maxValue = order.volRemaining
            else:
                maxValue = sm.GetService('marketQuote').GetMaxAvailableAtPrice(order.typeID, order.stationID, order.price)
                maxValue = maxValue or order.volRemaining
            editBox = self.AddQuantityEditLine(quantity, maxValue=maxValue, rightText=GetByLabel('UI/Market/MarketQuote/SimpleOrderQuantity', qty=maxValue), autoselect=True)
            uicore.registry.SetFocus(editBox)
        if order:
            t = self.AddBigText(GetByLabel('UI/Generic/Total'), '-', 'totalOrder')
            t.state = uiconst.UI_NORMAL
        if order:
            self.MakeCorpCheckboxMaybe()
        bottomCont = ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, alignMode=uiconst.CENTER, padTop=16)
        mainButtons = ButtonGroup(parent=bottomCont, align=uiconst.CENTER)
        if order:
            mainButtons.AddButton(label=GetByLabel('UI/Market/MarketQuote/CommandBuy'), func=self.Buy, args=(), isDefault=True)
        mainButtons.AddButton(label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel, args=())
        Button(parent=bottomCont, align=uiconst.CENTERRIGHT, label=GetByLabel('UI/Market/MarketQuote/btnAdvancedOrder'), func=self.GoPlaceBuyOrder, args=(typeID,
         order,
         0,
         locationID), hint=GetByLabel('Tooltips/Market/MarketBuyAdvancedButton'), variant=ButtonVariant.GHOST)
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()

    def GetLocationMenu(self):
        m = [(MenuLabel('UI/Search/SelectStation'), self.SelectStation)]
        if self.sr.stationID:
            m += sm.GetService('menu').GetMenuFromItemIDTypeID(self.sr.stationID, typeID=1930)
        return m

    def SelectStation(self):
        format_ = [{'type': 'header',
          'text': GetByLabel('UI/Market/MarketQuote/SelectStationForBuyOrder'),
          'frame': 0,
          'hideLine': True}, {'type': 'edit',
          'labelwidth': 60,
          'label': GetByLabel('UI/Common/LocationTypes/Station'),
          'key': 'station',
          'required': 0,
          'frame': 0,
          'group': 'avail',
          'setvalue': '',
          'setfocus': 1}, {'type': 'push'}]
        left = uicore.desktop.width / 2 - 500 / 2
        top = uicore.desktop.height / 2 - 400 / 2
        retval = HybridWnd(format_, caption=GetByLabel('UI/Search/SelectStation'), windowID='selectStation', modal=1, buttons=uiconst.OKCANCEL, location=[left, top], minW=300, minH=100, unresizeAble=1, icon='res:/UI/Texture/WindowIcons/searchmarket.png')
        if retval:
            name = retval['station']
            if name:
                stationID = Search(name.lower(), groupStation, categoryID=categoryStructure, searchWndName='marketQuoteSelectStationSearch')
                if stationID:
                    retList = []
                    if not sm.GetService('marketQuote').CanTradeAtStation(self.sr.Get('isBuy', False), stationID, retList):
                        jumps = retList[0]
                        limit = retList[1]
                        if jumps == rangeRegion:
                            raise UserError('MktInvalidRegion')
                        else:
                            jumpText = GetByLabel('UI/Market/MarketQuote/JumpDistance', jumps=jumps)
                            limitText = GetByLabel('UI/Market/MarketQuote/JumpDistance', jumps=limit)
                            if limit >= 0:
                                raise UserError('MktCantSellItem2', {'numJumps': jumps,
                                 'jumpText1': jumpText,
                                 'numLimit': limit,
                                 'jumpText2': limitText})
                            else:
                                raise UserError('MktCantSellItemOutsideStation', {'numJumps': jumps,
                                 'jumpText': jumpText})
                    if self.sr.Get('price'):
                        self.bidprice = self.sr.price.GetValue()
                    if self.sr.Get('quantity'):
                        self.qty = self.sr.quantity.GetValue()
                    if self.sr.Get('duration'):
                        self.duration = self.sr.duration.GetValue()
                    if self.sr.Get('range'):
                        self.range = self.sr.range.GetValue()
                    if self.sr.Get('quantityMin', None):
                        self.min = self.sr.quantityMin.GetValue()
                    if GetAttrs(self, 'sr', 'usecorp') is not None:
                        self.useCorp = self.sr.usecorp.GetValue()
                    else:
                        self.useCorp = False
                    self.LoadBuy_Detailed(self.typeID, order=getattr(self, 'order', None), locationID=stationID, forceRange=True)

    def RemeberBuySettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        orderRange = rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            orderRange = self.sr.range.GetValue()
        settings.user.ui.Set('buydefault', {'duration': duration,
         'useCorpWallet': useCorp,
         'range': orderRange})

    def RemeberSellSettings(self, *args):
        duration = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        useCorp = 0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('usecorp') and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        settings.user.ui.Set('selldefault', {'duration': duration,
         'useCorpWallet': useCorp})

    def ViewDetails(self, typeID, simple = 0, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uthread.new(self.ViewDetails_, typeID, simple)

    def ViewDetails_(self, typeID, simple = 0, *args):
        sm.GetService('marketutils').ShowMarketDetails(typeID, None)
        self.SetOrder(0)

    def GoPlaceSellOrder(self, invItem, simple = 0, *args):
        settings.char.ui.Set('advancedSellWnd', not simple)
        uthread.new(sm.GetService('marketutils').Sell, invItem.typeID, invItem, not simple)
        self.Close()

    def GoPlaceBuyOrder(self, typeID, order = None, simple = 0, prePickedLocationID = None, *args):
        settings.char.ui.Set('advancedBuyWnd', not simple)
        uthread.new(sm.GetService('marketutils').Buy, typeID, order=order, placeOrder=not simple, prePickedLocationID=prePickedLocationID)
        self.Close()

    def LoadModify(self, order):
        if order is None:
            return
        self.loading = 'modify'
        self.ready = False
        self.FlushMain()
        self.ShowLoad()
        self.sr.stationID = order.stationID
        self.typeID = order.typeID
        location = cfg.evelocations.Get(order.stationID)
        self.header.set_type_id(self.typeID)
        self.SetCaption(GetByLabel('UI/Market/MarketQuote/labelModifyOrder'))
        self.AddText(GetByLabel('UI/Common/Type'), GetName(self.typeID))
        self.AddText(GetByLabel('UI/Common/Location'), location.name)
        self.AddText([GetByLabel('UI/Market/MarketQuote/labelOldSellPrice'), GetByLabel('UI/Market/MarketQuote/labelOldBuyPrice')][order.bid], FmtISK(order.price))
        self.AddText(GetByLabel('UI/Market/MarketQuote/labelQuantityRemaining'), FmtAmt(order.volRemaining))
        self.quantity = order.volRemaining
        isBuy = bool(order.bid)
        label = [GetByLabel('UI/Market/MarketQuote/NewSellPrice'), GetByLabel('UI/Market/MarketQuote/NewBuyPrice')][order.bid]
        edit = self.AddPriceEditLine(label, '%.2f' % order.price, autoselect=True, isBuy=isBuy)
        uicore.registry.SetFocus(edit)
        self.AddText(GetByLabel('UI/Market/MarketQuote/labelTotalChange'), '-', 'totalOrder')
        self.AddText(GetByLabel('UI/Market/MarketQuote/BrokersFee'), '-', 'fee')
        if not IsStation(self.sr.stationID):
            self.AddText(GetByLabel('UI/Market/MarketQuote/SccSurchargeFee'), '-', 'sccSurcharge')
        ButtonIcon(parent=self.mainCont, align=uiconst.BOTTOMRIGHT, texturePath='res:/UI/Texture/WindowIcons/searchmarket.png', hint=GetByLabel('UI/Market/MarketQuote/hintClickForDetails'), func=lambda : self.ViewDetails(order.typeID), iconSize=32, idx=0)
        btnGroup = ButtonGroup(parent=self.mainCont, align=uiconst.TOTOP)
        btnGroup.AddButton(label=GetByLabel('UI/Common/Buttons/OK'), func=self.Modify, isDefault=True)
        btnGroup.AddButton(label=GetByLabel('UI/Common/Buttons/Cancel'), func=self.Cancel)
        self.sr.currentOrder = order
        self.ready = True
        self.UpdateTotals()
        self.HideLoad()

    @staticmethod
    def AddSpace(where, height = 6):
        Container(name='space', parent=where, height=height, align=uiconst.TOTOP)

    def Confirm(self):
        self.Buy()

    def Cancel(self, *args):
        self.Close()

    def Modify(self, *args):
        if self.sr.currentOrder is None:
            return
        price = self.sr.price.GetValue()
        order = self.sr.currentOrder
        if self.sr.percentage < -0.5 or self.sr.percentage > 1.0:
            percentage = round(100 * abs(self.sr.percentage), 2)
            label = 'UI/Market/MarketQuote/PercentAboveWithQuantity'
            if self.sr.percentage < 0.0:
                label = 'UI/Market/MarketQuote/PercentBelowWithQuantity'
            ret = eve.Message('MktConfirmTrade', {'amount': GetByLabel(label, amount=percentage)}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return
        self.Close()
        sm.GetService('marketQuote').ModifyOrder(order, price)

    def BuySimple(self, *args):
        stationID = self.sr.currentOrder.stationID
        numItems = self.sr.quantity.GetValue()
        dockableLocationID = session.stationid or session.structureid
        if dockableLocationID and stationID != dockableLocationID:
            stationTypeID = stationName = None
            if IsStation(stationID):
                uiService = sm.GetService('ui')
                stationInfo = uiService.GetStationStaticInfo(stationID)
                stationTypeID = stationInfo.stationTypeID
                stationName = uiService.GetStationName(stationID)
            else:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(stationID)
                if structureInfo:
                    stationTypeID = structureInfo.typeID
                    stationName = structureInfo.itemName
            if stationTypeID and stationName:
                stationLink = GetShowInfoLink(stationTypeID, stationName, stationID)
                if eve.Message('ConfirmRemoteBuy', {'numItems': numItems,
                 'stationLink': stationLink}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                    return
        self.Buy()

    def Buy(self, *args):
        if self.typeID is None:
            return
        typeID = self.typeID
        quantity = self.sr.quantity.GetValue()
        duration = 0
        if self.sr.Get('fee') and not self.sr.fee.destroyed and self.sr.fee.text != '-' and eve.Message('ConfirmMarketOrder', {'isk': self.sr.fee.text}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        else:
            return
        if self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = self.sr.duration.GetValue()
        orderRange = rangeStation
        if self.sr.Get('range') and not self.sr.range.destroyed:
            orderRange = self.sr.range.GetValue()
        if self.remoteBuyLocation or not eve.session.stationid:
            stationID = self.remoteBuyLocation
        else:
            stationID = self.sr.currentOrder.stationID
        minVolume = 1
        if self.sr.Get('quantityMin', None) and not self.sr.quantityMin.destroyed:
            minVolume = self.sr.quantityMin.GetValue()
        if GetAttrs(self, 'sr', 'usecorp') is not None and not self.sr.usecorp.destroyed:
            useCorp = self.sr.usecorp.GetValue()
        else:
            useCorp = False
        if self.sr.percentage > 1.0:
            amount = round(100 * abs(self.sr.percentage), 2)
            ret = eve.Message('MktConfirmTrade', {'amount': GetByLabel('UI/Market/MarketQuote/PercentAboveWithQuantity', amount=amount)}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return
        if self.sr.Get('rememberBuySettings') and not self.sr.rememberBuySettings.destroyed and self.sr.rememberBuySettings.checked:
            self.RemeberBuySettings()
        if duration > 0:
            if not FloatCloseEnough(self.currentBrokerFeePerc, self.originalBrokersFeePerc):
                raise UserError('MktBrokersFeeUnexpected2', {'actualBrokerFeePerc': 100 * self.currentBrokerFeePerc,
                 'originalBrokersFeePerc': self.originalBrokersFeePerc})
        else:
            self.singleOrderBrokerFee = None
        self.Close()
        sm.GetService('marketQuote').BuyStuff(stationID, typeID, price, quantity, orderRange, minVolume, duration, useCorp, self.currentBrokerFeePerc)

    def AddText(self, label, text, refName = None, height = LINE_HEIGHT, color = TextColor.NORMAL, ui_name = 'textContainer'):
        par = Container(name=u'{}_{}'.format(self.windowID, ui_name), parent=self.mainCont, align=uiconst.TOTOP)
        left = self.leftSideLabelsWidth
        if label == 'hide':
            left = 0
        elif label:
            EveLabelMedium(text=label, parent=par, width=self.leftSideLabelsWidth, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, color=TextColor.SECONDARY)
        window_width, _ = self.GetAbsoluteSize()
        t = EveLabelMedium(parent=par, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, width=window_width - self.leftSideLabelsWidth - 32, left=left, text=text, color=color)
        par.height = max(height, t.textheight)
        if refName:
            setattr(self.sr, refName, t)
        return par

    def AddBigText(self, label, text, refName = None, height = LINE_HEIGHT):
        par = Container(name='text', parent=self.mainCont, align=uiconst.TOTOP, height=height)
        left = 0
        if label:
            EveLabelMedium(text=label, parent=par, width=self.leftSideLabelsWidth, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
            left = self.leftSideLabelsWidth
        window_width, _ = self.GetAbsoluteSize()
        t = EveCaptionMedium(text=text, parent=par, align=uiconst.CENTERLEFT, width=window_width - left - 16, left=left)
        if refName:
            setattr(self.sr, refName, t)
        par.height = max(par.height, t.textheight + 8)
        return t

    def AddPriceEditLine(self, label, price, isBuy, autoselect = False, ui_name = 'PriceEdit'):
        grid = LayoutGrid(parent=ContainerAutoSize(parent=self.mainCont, align=uiconst.TOTOP, padding=(0, 4, 0, 4)), align=uiconst.TOPLEFT, columns=2)
        EveLabelMedium(parent=grid, align=uiconst.CENTERLEFT, width=self.leftSideLabelsWidth, state=uiconst.UI_NORMAL, text=label, color=TextColor.SECONDARY)
        edit = SingleLineEditMarketPrice(name=label, parent=grid, align=uiconst.CENTERLEFT, width=240, autoselect=autoselect, isBuy=isBuy, OnChange=self.OnEditChange, OnFocusLost=self.OnEditChange)
        if price:
            edit.SetValue(price)
        Container(parent=grid)
        self.sr.price_rightText = EveLabelMedium(parent=grid, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, top=4, width=240, text='')
        self.sr.price = edit
        return edit

    def AddQuantityEditLine(self, quantity, maxValue = sys.maxint, showMin = 0, rightText = None, autoselect = False):
        label = GetByLabel('UI/Common/Quantity')
        width = 95
        minValue = 1
        minHeight = LINE_HEIGHT
        parent = Container(name=label, parent=self.mainCont, height=minHeight, align=uiconst.TOTOP)
        edit = SingleLineEditInteger(name=label, parent=parent, pos=(self.leftSideLabelsWidth,
         0,
         width,
         0), align=uiconst.CENTERLEFT, autoselect=autoselect)
        edit.OnChange = self.OnChanged_quantity
        edit.OnFocusLost = self.OnEditChange
        edit.SetMinValue(minValue)
        edit.SetMaxValue(maxValue)
        edit.AutoFitToText(FmtAmt(maxValue), minWidth=width)
        minHeight = max(minHeight, edit.height)
        if showMin:
            minimum = self.min if self.min is not None else 1
            minLabel = EveLabelMedium(text=GetByLabel('UI/Generic/Minimum'), parent=parent, left=edit.left + edit.width + 6, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
            minedit = SingleLineEditInteger(name=label, parent=parent, setvalue=minimum, minValue=1, width=40, left=minLabel.left + minLabel.width + 6, align=uiconst.CENTERLEFT)
            minedit.OnChange = self.OnEditChange
            minedit.AutoFitToText(FmtAmt(sys.maxint), minWidth=40)
            self.sr.quantityMin = minedit
            minHeight = max(minHeight, minedit.default_height)
        if quantity:
            edit.SetValue(quantity)
        _label = EveLabelMedium(text=label, parent=parent, width=self.leftSideLabelsWidth, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT, color=TextColor.SECONDARY)
        if rightText is not None:
            rightTextLeft = edit.left + edit.width + 6
            window_width, _ = self.GetAbsoluteSize()
            _rightText = EveLabelMedium(text=rightText, parent=parent, width=window_width - rightTextLeft - 6, left=rightTextLeft, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
            minHeight = max(minHeight, _rightText.textheight + 8)
            self.sr.quantity_rightText = _rightText
            parent.height = minHeight
        self.sr.quantity = edit
        parent.height = minHeight
        return edit

    def AddCombo(self, label, options, setvalue, configname, width = 95, refName = None, maxVisibleEntries = None):
        parent = ContainerAutoSize(name=configname, parent=self.mainCont, align=uiconst.TOTOP, top=4, minHeight=LINE_HEIGHT)
        maxVisibleEntries = maxVisibleEntries or Combo.default_maxVisibleEntries
        _label = EveLabelMedium(text=label, parent=parent, width=self.leftSideLabelsWidth, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, color=TextColor.SECONDARY)
        combo = Combo(label='', parent=parent, align=uiconst.CENTERLEFT, options=options, name=configname, callback=self.OnComboChange, width=width, pos=(self.leftSideLabelsWidth,
         0,
         0,
         0), maxVisibleEntries=maxVisibleEntries)
        combo.sr.label = _label
        if setvalue is not None:
            combo.SelectItemByValue(setvalue)
        if refName:
            setattr(self.sr, refName, combo)
        return combo

    def OnChanged_quantity(self, quantity):
        self.quantity = int(quantity or 0)
        if not self.ready:
            return
        uthread.pool('MarketActionWindow::OnChanged_quantity', self.OnChanged_quantityThread, quantity)

    def OnChanged_quantityThread(self, quantity):
        try:
            self.UpdateTotals()
        except StandardError:
            LogException()
            sys.exc_clear()

    def OnEditChange(self, *args):
        if not self or self.destroyed:
            return
        uthread.pool('MarketActionWindow::OnEditChange', self.OnEditChangeThread, *args)

    def OnEditChangeThread(self, *args):
        self.UpdateTotals()

    def OnComboChange(self, combo, header, value, *args):
        uthread.pool('MarketActionWindow::OnComboChange', self.OnComboChangeThread, combo, header, value, *args)

    def OnComboChangeThread(self, combo, header, value, *args):
        self.UpdateTotals()

    def UpdateTotals(self):
        if self.destroyed:
            return
        if not self.ready:
            return
        if not self.typeID:
            return
        if not hasattr(self, 'sr'):
            return
        quote = sm.GetService('marketQuote')
        limits = quote.GetSkillLimits(self.sr.stationID)
        averagePrice = quote.GetAveragePrice(self.typeID)
        colors = ['<color=0xff00ff00>', '<color=0xffff5050>']
        if not self or self.destroyed or not hasattr(self, 'sr'):
            return
        self.sr.percentage = 0
        price = 0
        duration = 0
        totalValue = None
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('duration') and not self.sr.duration.destroyed:
            duration = long(self.sr.duration.GetValue())
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price') and not self.sr.price.destroyed:
            price = self.sr.price.GetValue()
        elif self.sr.currentOrder is not None:
            price = self.sr.currentOrder.price
        if self.loading == 'modify':
            quantity = self.sr.currentOrder.volRemaining
        else:
            quantity = 1
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantity') and not self.sr.quantity.destroyed:
                quantity = self.sr.quantity.GetValue() or 0
            elif self.sr.currentOrder is not None:
                quantity = self.sr.currentOrder.volRemaining
        quantity = max(1, quantity)
        quantityMin = 1
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quantityMin') and not self.sr.quantityMin.destroyed:
            quantityMin = self.sr.quantityMin.GetValue()
        orderRange = rangeStation
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('range') and not self.sr.range.destroyed:
            orderRange = self.sr.range.GetValue()
        fee = 0.0
        sccFee = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('fee') and not self.sr.fee.destroyed:
            sccSurchargeText = '-'
            if duration > 0:
                feeRateAtLocation = limits.GetBrokersFeeForLocation(self.sr.stationID)
                if feeRateAtLocation is None:
                    self.sr.fee.text = '-'
                    self.singleOrderBrokerFee = None
                    self.currentBrokerFeePerc = self.originalBrokersFeePerc
                else:
                    _feeInfo = quote.GetBrokersFeeInfo(self.sr.stationID, None, price * quantity, feeRateAtLocation, None)
                    fee = _feeInfo.amt
                    if _feeInfo.usingMinimumValue:
                        p = GetByLabel('UI/Generic/Minimum')
                        self.currentBrokerFeePerc = self.originalBrokersFeePerc
                    else:
                        p = '%s%%' % round(_feeInfo.rawPercentage * 100, 2)
                        self.currentBrokerFeePerc = _feeInfo.rawPercentage
                    self.sr.fee.text = GetByLabel('UI/Market/MarketQuote/MarketFee', percentage=p, price=fee)
                    self.singleOrderBrokerFee = fee
                    _sccSurchargeFeeInfo = quote.GetSccSurchargeFeeInfo(self.sr.stationID, None, price * quantity)
                    sccSurchargeAmt = _sccSurchargeFeeInfo.sccSurchargeAmt
                    if sccSurchargeAmt:
                        sccFee = sccSurchargeAmt
                        if _sccSurchargeFeeInfo.usingMinimumValue:
                            scp = GetByLabel('UI/Generic/Minimum')
                        else:
                            scp = '%s%%' % round(_sccSurchargeFeeInfo.rawSccSurchargePercentage * 100, 2)
                        sccSurchargeText = GetByLabel('UI/Market/MarketQuote/MarketFee', percentage=scp, price=sccSurchargeAmt)
            else:
                self.sr.fee.text = '-'
                self.singleOrderBrokerFee = None
                self.currentBrokerFeePerc = self.originalBrokersFeePerc
            if self.sr.sccSurcharge:
                self.sr.sccSurcharge.text = sccSurchargeText
            self.CheckHeights(self.sr.fee, 'fee')
        tax = 0.0
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('transactionTax') and not self.sr.transactionTax.destroyed:
            tax = price * quantity * limits['acc']
            self.sr.transactionTax.text = GetByLabel('UI/Market/MarketQuote/MarketTax', percentage=limits['acc'] * 100.0, price=tax)
            self.CheckHeights(self.sr.transactionTax, 'transactionTax')
        if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('totalOrder') and not self.sr.totalOrder.destroyed:
            if self.loading == 'buy':
                sumTotal = -price * quantity
            else:
                sumTotal = price * quantity
            color = 'green'
            if sumTotal - tax - fee < 0.0:
                color = 'white'
            totalValue = abs(sumTotal - tax - fee - sccFee)
            self.sr.totalOrder.text = '<color=%s>' % color + FmtISK(totalValue)
            AssignQtyTooltipFunc(self.sr.totalOrder, totalValue, inputType=EDIT_INPUT_TYPE_ISK, tooltipPointer=uiconst.POINT_TOP_2)
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
        if self.loading == 'buy':
            colors.reverse()
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('matchText') and not self.sr.matchText.destroyed:
                bestMatchableAskKey = (self.typeID,
                 self.sr.stationID,
                 rangeRegion,
                 quantityMin)
                bestMatchableAsk = self.bestMatchableAskDict.get(bestMatchableAskKey, None)
                if bestMatchableAsk is None:
                    bestMatchableAsk = quote.GetBestAskInRange(self.typeID, self.sr.stationID, orderRange, amount=quantityMin)
                    self.ManageBestMatchableAskDict(key=bestMatchableAskKey, value=bestMatchableAsk)
                if bestMatchableAsk:
                    jumps = int(bestMatchableAsk.jumps)
                    if jumps == 0 and bestMatchableAsk.stationID == self.sr.stationID:
                        jumps = GetByLabel('UI/Market/MarketQuote/InSameStation')
                    else:
                        jumps = GetByLabel('UI/Market/MarketQuote/JumpsAway', jumps=jumps)
                    p = {'price': bestMatchableAsk.price,
                     'percentage': round(100 * (bestMatchableAsk.price - averagePrice) / averagePrice, 2),
                     'aboveBelow': GetByLabel('UI/Market/MarketQuote/PercentBelow') if bestMatchableAsk.price < averagePrice else GetByLabel('UI/Market/MarketQuote/PercentAbove'),
                     'volRemaining': int(bestMatchableAsk.volRemaining),
                     'jumps': jumps}
                    matchText = GetByLabel('UI/Market/MarketQuote/BestAskDisplay', **p)
                else:
                    matchText = GetByLabel('UI/Market/MarketQuote/NoMatchesAsk')
                self.sr.matchText.text = matchText
                self.CheckHeights(self.sr.matchText, 'matchText')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('quoteText') and not self.sr.quoteText.destroyed:
                bestAskKey = (self.typeID, self.sr.stationID, rangeRegion)
                bestAsk = self.bestAskDict.get(bestAskKey, None)
                if bestAsk is None:
                    bestAsk = quote.GetBestAskInRange(self.typeID, self.sr.stationID, rangeRegion)
                    self.bestAskDict[bestAskKey] = bestAsk
                if bestAsk:
                    jumps = int(bestAsk.jumps)
                    if jumps == 0 and bestAsk.stationID == self.sr.stationID:
                        jumps = GetByLabel('UI/Market/MarketQuote/InSameStation')
                    else:
                        jumps = GetByLabel('UI/Market/MarketQuote/JumpsAway', jumps=jumps)
                    p = {'price': bestAsk.price,
                     'percentage': round(100 * (bestAsk.price - averagePrice) / averagePrice, 2),
                     'aboveBelow': GetByLabel('UI/Market/MarketQuote/PercentBelow') if bestAsk.price < averagePrice else GetByLabel('UI/Market/MarketQuote/PercentAbove'),
                     'volRemaining': int(bestAsk.volRemaining),
                     'jumps': jumps}
                    quoteText = GetByLabel('UI/Market/MarketQuote/BestAskDisplay', **p)
                else:
                    quoteText = GetByLabel('UI/Market/MarketQuote/NoMatchesAsk')
                self.sr.quoteText.text = quoteText
                self.CheckHeights(self.sr.quoteText, 'quoteText')
            self.sr.percentage = (price - averagePrice) / averagePrice
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                bestMatchText = sm.GetService('marketutils').GetBestMatchText(price, averagePrice, self.sr.percentage)
                self.sr.price_rightText.text = bestMatchText
        elif self.loading == 'sell':
            LogException('TRYING TO USE OLD SELL WINDOW!!!')
        elif self.loading == 'modify':
            if self.sr.currentOrder.bid:
                colors.reverse()
            oldPrice = self.sr.currentOrder.price
            totalValue = (price - oldPrice) * quantity
            self.sr.totalOrder.text = FmtISK(totalValue)
            AssignQtyTooltipFunc(self.sr.totalOrder, totalValue, inputType=EDIT_INPUT_TYPE_ISK, tooltipPointer=uiconst.POINT_TOP_2)
            self.CheckHeights(self.sr.totalOrder, 'totalOrder')
            brokerFeeRate = limits.GetBrokersFeeForLocation(self.sr.currentOrder.stationID)
            modificationFeeDiscount = limits.GetModificationFeeDiscount()
            oldOrderValue = oldPrice * quantity
            newOrderValue = price * quantity
            brokerFeeInfo = quote.GetBrokersFeeInfo(self.sr.stationID, oldOrderValue, newOrderValue, brokerFeeRate, modificationFeeDiscount)
            sccSurchargeFeeInfo = quote.GetSccSurchargeFeeInfo(self.sr.stationID, oldOrderValue, newOrderValue, modificationFeeDiscount)
            fee = max(mktMinimumFee, brokerFeeInfo.amt)
            self.sr.fee.text = FmtISK(fee)
            self.singleOrderBrokerFee = fee
            self.currentBrokerFeePerc = brokerFeeInfo.rawPercentage
            if self.sr.sccSurcharge:
                self.sr.sccSurcharge.text = FmtISK(sccSurchargeFeeInfo.sccSurchargeAmt)
            self.CheckHeights(self.sr.fee, 'fee')
            if not self.destroyed and hasattr(self, 'sr') and self.sr.Get('price_rightText') and not self.sr.price_rightText.destroyed:
                self.sr.percentage = (price - averagePrice) / averagePrice
                p = {'colorText': colors[price < averagePrice],
                 'percentage': round(100 * self.sr.percentage, 2),
                 'aboveBelow': GetByLabel('UI/Market/MarketQuote/PercentAbove')}
                if price < averagePrice:
                    p['aboveBelow'] = GetByLabel('UI/Market/MarketQuote/PercentBelow')
                self.sr.price_rightText.text = GetByLabel('UI/Market/MarketQuote/MarketModifyPrice', **p)
        if totalValue is not None and totalValue != self.lastTotalValue:
            self.lastTotalValue = totalValue
            sm.ScatterEvent('OnBuyOrderWindowPriceChanged')

    def ManageBestMatchableAskDict(self, key, value):
        if len(self.bestMatchableAskDict) > 15:
            self.bestMatchableAskDict = {}
        else:
            self.bestMatchableAskDict[key] = value

    def CheckHeights(self, t, what = None):
        if not t or t.destroyed:
            return
        t.parent.height = max(t.textheight + t.top * 2, t.parent.height)
        height = sum([ each.height + each.padTop + each.padBottom for each in t.parent.parent.children if each.align == uiconst.TOTOP ])
        _, height = self.GetWindowSizeForContentSize(height=height + 56)
        self.SetFixedHeight(height)

    def GetBuyInfo(self):
        try:
            bidPrice = self.sr.price.GetValue()
        except:
            bidPrice = self.sr.currentOrder.price

        result = dict(typeID=self.typeID, stationID=self.sr.stationID, totalValue=self.lastTotalValue, quantity=self.quantity, bidPrice=bidPrice)
        return result


def CreateCaption(parent, align, typeID):
    captionGrid = LayoutGrid(parent=ContainerAutoSize(parent=parent, align=align), align=uiconst.TOPLEFT, columns=4, cellSpacing=(8, 0))
    ItemIcon(parent=captionGrid, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=32, height=32, typeID=typeID)
    EveCaptionMedium(parent=captionGrid, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, text=GetName(typeID))
    ShowMarketDetailsButton(parent=captionGrid, align=uiconst.CENTER, width=16, height=16, typeID=typeID)
    InfoIcon(parent=captionGrid, align=uiconst.CENTER, typeID=typeID)
