#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\buySellItemContainerBase.py
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from localization import GetByLabel
from carbonui.uicore import uicore

class BuySellItemContainerBase(Container):
    default_height = 40
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_padTop = 2
    default_padBottom = 2
    belowColor = '<color=0xffffffff>'
    aboveColor = '<color=0xffffffff>'
    totaLabelPath = 'UI/Market/MarketQuote/AskTotal'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.quoteSvc = sm.GetService('marketQuote')
        self.mouseovertimer = None
        self.averagePrice = self.quoteSvc.GetAveragePrice(self.typeID)
        self.parentFunc = attributes.parentFunc
        self.parentEditFunc = attributes.editFunc

    def DrawTotal(self):
        self.totalLabel = EveLabelMedium(text=self.totalSum, parent=self.totalCont, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL)
        self.totalLabel.hint = GetByLabel(self.totaLabelPath)

    def OpenMarket(self, *args):
        sm.GetService('marketutils').ShowMarketDetails(self.typeID, None, silently=True)
        self._BringMarketToFrontOfOtherWnds()
        tradeWndClass = self.GetTradeWndClass()
        wnd = tradeWndClass.GetIfOpen()
        if wnd:
            wnd.Maximize()

    def _BringMarketToFrontOfOtherWnds(self):
        from eve.client.script.ui.shared.market.marketbase import RegionalMarket
        marketWnd = RegionalMarket.GetIfOpen()
        if not marketWnd or marketWnd.destroyed:
            return
        marketWndToBringToFront = marketWnd.GetStack() or marketWnd
        if marketWndToBringToFront.GetOrder() > 1:
            marketWndToBringToFront.SetOrder(1)

    def GetDelta(self):
        price = self.GetPrice()
        if price is None:
            return 0
        percentage = (price - self.averagePrice) / self.averagePrice
        return percentage

    def GetDeltaText(self):
        price = self.GetPrice()
        if not price:
            return ''
        percentage = (price - self.averagePrice) / self.averagePrice
        if percentage < 0:
            color = self.belowColor
        else:
            color = self.aboveColor
        percText = '%s%s</color>' % (color, GetByLabel('UI/Common/Percentage', percentage=FmtAmt(percentage * 100, showFraction=1)))
        return percText

    def UpdateDelta(self):
        delta = self.GetDelta()
        self.deltaContainer.UpdateDelta(delta)

    def OnMouseEnter(self, *args):
        self.mouseovertimer = AutoTimer(1, self.UpdateMouseOver)
        self.deleteCont.display = True

    def UpdateMouseOver(self):
        mo = uicore.uilib.mouseOver
        if mo != self and not mo.IsUnder(self):
            self.mouseovertimer = None
            self.deleteCont.display = False

    def ShowNoSellOrders(self):
        pass

    def HideNoSellOrders(self):
        uicore.animations.FadeOut(self.errorBg, duration=0.3)

    def RemoveItem(self, *args):
        self.parentFunc(self, *args)

    def Close(self, *args):
        self.mouseovertimer = None
        self.parentFunc = None
        Container.Close(self)

    def GetTradeWndClass(self):
        pass

    def GetPrice(self):
        pass
