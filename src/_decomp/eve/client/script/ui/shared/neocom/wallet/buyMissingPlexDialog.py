#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\buyMissingPlexDialog.py
import carbonui
from carbonui import Align, TextAlign, ButtonStyle, ButtonVariant, Density, TextColor
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui import eveColor
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtISK
from fastcheckout.const import FROM_BUY_MISSING_PLEX_WND
from inventorycommon.typeHelpers import GetAveragePrice
from localization import GetByLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty

class BuyMissingPlexDialog(Window):
    default_windowID = 'BuyMissingPlexDialog'
    default_fixedWidth = 512
    default_height = 400
    default_iconNum = 'res:/UI/Texture/Plex/plex_128_gradient_yellow.png'
    default_isCollapseable = False
    default_isMinimizable = False
    default_isStackable = False
    default_isLockable = False
    default_isLightBackgroundConfigurable = False
    default_isOverlayable = False
    default_useDefaultPos = True

    def __init__(self, required_amount, **kwargs):
        super(BuyMissingPlexDialog, self).__init__(**kwargs)
        self.required_amount = required_amount
        self.construct_top(required_amount)
        self.construct_bottom()
        self.update_headline_text()
        self.connect_signals()

    def Close(self, setClosed = False, *args, **kwds):
        try:
            self.disconnect_signals()
        finally:
            super(BuyMissingPlexDialog, self).Close(setClosed, *args, **kwds)

    def connect_signals(self):
        self.content.on_size_changed.connect(self.on_content_size_changed)
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.connect(self.on_plex_amount_changed)

    def disconnect_signals(self):
        self.content.on_size_changed.disconnect(self.on_content_size_changed)
        sm.GetService('vgsService').GetStore().GetAccount().accountAurumBalanceChanged.disconnect(self.on_plex_amount_changed)

    def on_content_size_changed(self, width, height):
        _, height = self.GetWindowSizeForContentSize(height=height)
        self.SetFixedHeight(height)

    def update_headline_text(self):
        amount = self.get_required_plex_amount()
        self.headline.text = GetByLabel('UI/Wallet/MissingPlex', amount_missing=int(amount))

    def construct_content_cont(self):
        return ContainerAutoSize(parent=self.sr.maincontainer, name='main', align=Align.TOTOP, padding=self.content_padding)

    def construct_bottom(self):
        bottom_cont = ContainerAutoSize(name='bottomCont', parent=self.content, align=Align.TOTOP, padTop=32)
        layout_grid = LayoutGrid(parent=bottom_cont, columns=3, cellSpacing=(16, 16))
        self.isk_container = ContainerAutoSize(align=Align.TOPLEFT, width=200)
        layout_grid.AddCell(self.isk_container, bgColor=(0, 0, 0, 0.3), cellPadding=8)
        self.reconstruct_isk_container()
        carbonui.TextBody(parent=layout_grid, align=Align.TOPLEFT, text=GetByLabel('UI/Common/Or'), top=14)
        self.nes_container = ContainerAutoSize(align=Align.TOPLEFT, width=200)
        layout_grid.AddCell(self.nes_container, bgColor=(0, 0, 0, 0.3), cellPadding=8)
        self.reconstruct_nes_container()
        self.construct_buttons(layout_grid)

    def construct_buttons(self, layout_grid):
        Button(parent=layout_grid, align=Align.TOTOP, label=GetByLabel('UI/Wallet/BuyOnMarket'), func=self.on_market_button, variant=ButtonVariant.PRIMARY, padTop=16, density=Density.EXPANDED)
        layout_grid.AddCell()
        Button(parent=layout_grid, align=Align.TOTOP, label=GetByLabel('UI/Wallet/BuyInNES'), func=self.on_nes_button, variant=ButtonVariant.PRIMARY, style=ButtonStyle.MONETIZATION, padTop=16, density=Density.EXPANDED)

    def on_nes_button(self, *args):
        sm.GetService('fastCheckoutClientService').buy_plex(log_context=FROM_BUY_MISSING_PLEX_WND)
        self.Close()

    def construct_top(self, required_amount):
        self.headline = carbonui.TextHeadline(parent=self.content, align=Align.TOTOP, textAlign=TextAlign.CENTER, color=eveColor.DANGER_RED)
        DividerLine(parent=self.content, align=Align.TOTOP, padTop=16)
        self.subtract_wallet_checkbox = Checkbox(parent=ContainerAutoSize(parent=self.content, align=Align.TOTOP, padTop=16), text=GetByLabel('UI/Wallet/SubtractPlexInWallet'), align=Align.CENTERTOP, callback=self.on_subtract_wallet_checkbox, checked=True)

    def on_subtract_wallet_checkbox(self, *args):
        self.update()

    def on_plex_amount_changed(self, *args):
        self.update()

    def update(self):
        self.update_headline_text()
        self.reconstruct_isk_container()

    def on_market_button(self, *args):
        amount = self.get_required_plex_amount()
        BuyMultipleTypesWithQty({appConst.typePlex: amount})
        self.Close()

    def get_required_plex_amount(self):
        amount = self.required_amount
        if self.subtract_wallet_checkbox.checked:
            amount -= sm.GetService('vgsService').GetPLEXBalance()
        amount = max(1, amount)
        return amount

    def reconstruct_isk_container(self):
        self.isk_container.Flush()
        carbonui.TextBody(parent=Container(parent=self.isk_container, align=Align.TOTOP, bgColor=(1, 1, 1, 0.1), height=32), align=Align.CENTERLEFT, text=GetByLabel('UI/Wallet/PLEXForISK'), left=8)
        price = GetAveragePrice(appConst.typePlex) or 100
        if price:
            price *= self.get_required_plex_amount()
            carbonui.TextBody(parent=self.isk_container, align=Align.TOTOP, text=GetByLabel('UI/SkillTrading/EstimatedPrice', price=FmtISK(price, False)), padTop=8)
        self.isk_container.SetSizeAutomatically()

    def reconstruct_nes_container(self):
        self.nes_container.Flush()
        carbonui.TextBody(parent=Container(parent=self.nes_container, align=Align.TOTOP, bgColor=(1, 1, 1, 0.1), height=32), align=Align.CENTERLEFT, text=GetByLabel('UI/Wallet/PLEXInNES'), left=4)
        carbonui.TextBody(parent=self.nes_container, align=Align.TOTOP, padTop=8, color=TextColor.SECONDARY, text=GetByLabel('UI/Wallet/PlexPackagesInNES'))
        self.nes_container.SetSizeAutomatically()
