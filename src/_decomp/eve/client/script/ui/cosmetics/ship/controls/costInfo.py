#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\controls\costInfo.py
import eveformat
import eveicon
import uthread2
from carbonui import Align, PickState, TextBody, TextColor, TextDetail, TextHeader, uiconst
from carbonui.control.button import Button, ButtonStyle
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from cosmetics.client.ships import ship_skin_signals
from cosmetics.client.ships.skins.errors import NoTimeRemainingException
from cosmetics.client.ships.skins.live_data import current_skin_design, current_skin_design_signals
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from cosmetics.common.ships.skins.util import Currency
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.warningIcon import WarningIcon
from eve.client.script.ui.shared.neocom.wallet.buyMissingPlexDialog import BuyMissingPlexDialog
from eve.client.script.ui.shared.neocom.wallet.walletWnd import WalletWindow
from inventorycommon.const import typeLoyaltyPointsHeraldry
from localization import GetByLabel
from publicGateway.grpc.exceptions import GenericException
from stackless_response_router.exceptions import TimeoutException

class CostInfo(ContainerAutoSize):
    default_display = False
    LEFT_WIDTH = 40
    SPACING = 4

    def __init__(self, cost = None, currency = None, discount = None, *args, **kwargs):
        super(CostInfo, self).__init__(*args, **kwargs)
        self._cost = cost
        self._discount = discount
        self._currency = currency
        self.construct_layout()
        self.update()

    def construct_layout(self):
        self.construct_header()
        self.construct_cost()

    def construct_header(self):
        header_container = Container(name='header_container', parent=self, align=Align.TOTOP, height=16)
        left_container = Container(parent=header_container, align=Align.TOLEFT, width=self.LEFT_WIDTH)
        Sprite(parent=left_container, texturePath='res:/UI/Texture/classes/Cosmetics/Ship/overlays/cost_info_corner.png', width=self.LEFT_WIDTH, height=16)
        right_container = Container(parent=header_container, align=Align.TOALL, padLeft=self.SPACING)
        Fill(parent=right_container, color=eveColor.WHITE, opacity=0.1)
        TextDetail(parent=right_container, align=Align.CENTERLEFT, text=self.cost_header_text, color=TextColor.SECONDARY, padLeft=8)

    def construct_cost(self):
        cost_container = Container(name='cost_container', parent=self, align=Align.TOTOP, height=32, padTop=self.SPACING)
        left_container = Container(parent=cost_container, align=Align.TOLEFT, width=self.LEFT_WIDTH)
        Fill(parent=left_container, color=eveColor.WHITE, opacity=0.1)
        self.construct_currency_icon(parent=left_container)
        self.right_container = Container(name='rightContainer', parent=cost_container, align=Align.TOALL, padLeft=self.SPACING)
        Fill(parent=self.right_container, color=eveColor.SMOKE_BLUE, opacity=0.2)
        self.layout_grid = LayoutGrid(parent=self.right_container, align=Align.CENTERLEFT, left=8, cellSpacing=8)
        self.cost_label = TextHeader(parent=self.layout_grid, align=Align.CENTERLEFT)
        self.discount_label = TextBody(parent=self.layout_grid, align=Align.CENTERLEFT, color=eveColor.SUCCESS_GREEN)
        warning_icon_container = Container(name='warning_icon_container', parent=self.right_container, align=Align.TOLEFT, width=16, padLeft=8)
        self.warning_icon = WarningIcon(name='warning_icon', parent=warning_icon_container, align=Align.CENTER, display=False, top=1)

    def construct_currency_icon(self, parent):
        self.currency_icon = Sprite(parent=parent, align=Align.CENTER, state=uiconst.UI_DISABLED, width=16, height=16)

    def update(self):
        self.display = self.cost is not None
        if self.cost is None:
            return
        if self.currency == Currency.PLEX:
            self.currency_icon.texturePath = eveicon.plex
            self.currency_icon.color = eveColor.PLEX_YELLOW
            self.cost_label.text = eveformat.number(self.cost, decimal_places=0)
            text_padding = 40
        elif self.currency == Currency.ISK:
            self.currency_icon.texturePath = eveicon.isk
            self.currency_icon.color = eveColor.WHITE
            self.cost_label.text = eveformat.number(self.cost)
            text_padding = 16
        self._update_discount_text()
        if self.cost:
            cost_header_text_width, _ = TextDetail.MeasureTextSize(self.cost_header_text)
            cost_amount_text_width, _ = TextHeader.MeasureTextSize(self.cost)
            discount_text_width, _ = TextBody.MeasureTextSize(self.discount_label.text)
            longest_text_width = max(cost_header_text_width, cost_amount_text_width + discount_text_width)
            desired_width = self.LEFT_WIDTH + self.SPACING + longest_text_width + text_padding
            self.width = max(self.minWidth, desired_width)

    def _update_discount_text(self):
        if self._discount:
            self.discount_label.text = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CostWithDiscount', discount_percentage=self._discount)
        else:
            self.discount_label.text = ''

    @property
    def cost_header_text(self):
        return GetByLabel('UI/Common/Cost')

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        if self._cost == value:
            return
        self._cost = value
        self.update()

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        if self._currency == value:
            return
        self._currency = value
        self.update()

    def set_cost(self, cost, discount = None):
        self._cost = cost
        self._discount = discount
        self.update()


class SequencingJobCostInfo(CostInfo):

    def __init__(self, sequencing_job = None, *args, **kwargs):
        self._sequencing_job = sequencing_job
        self._update_thread = None
        super(SequencingJobCostInfo, self).__init__(currency=Currency.PLEX, *args, **kwargs)

    def Close(self):
        try:
            self.kill_update_thread()
        finally:
            super(SequencingJobCostInfo, self).Close()

    def kill_update_thread(self):
        if self._update_thread is not None:
            self._update_thread.kill()
            self._update_thread = None

    @property
    def sequencing_job(self):
        return self._sequencing_job

    @sequencing_job.setter
    def sequencing_job(self, value):
        self._sequencing_job = value
        self.update_sequencing_job()

    def update_sequencing_job(self):
        if self.sequencing_job:
            self.kill_update_thread()
            self._update_thread = uthread2.start_tasklet(self.update_sequencing_job_async)
        else:
            self.display = False

    def update_sequencing_job_async(self):
        try:
            try:
                plex_cost = get_ship_skin_sequencing_svc().get_early_completion_cost(self.sequencing_job.job_id)
            except (GenericException, TimeoutException):
                ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
                plex_cost = None

            self.cost = plex_cost
            self.display = plex_cost is not None
        except NoTimeRemainingException:
            self.display = False


class StudioCostInfo(CostInfo):

    def __init__(self, *args, **kwargs):
        super(StudioCostInfo, self).__init__(currency=Currency.PLEX, *args, **kwargs)
        self._update_thread = None
        self.connect_signals()
        self.update_cost_label()

    def Close(self):
        try:
            self.kill_update_thread()
            self.disconnect_signals()
        finally:
            super(StudioCostInfo, self).Close()

    def kill_update_thread(self):
        if self._update_thread:
            self._update_thread.kill()
            self._update_thread = None

    def connect_signals(self):
        current_skin_design_signals.on_design_reset.connect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.connect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.connect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.connect(self.on_slot_fitting_changed)
        ship_skin_signals.on_skin_sequencing_cache_invalidated.connect(self.on_skin_sequencing_cache_invalidated)

    def disconnect_signals(self):
        current_skin_design_signals.on_design_reset.disconnect(self.on_design_reset)
        current_skin_design_signals.on_existing_design_loaded.disconnect(self.on_existing_design_loaded)
        current_skin_design_signals.on_ship_type_id_changed.disconnect(self.on_ship_type_id_changed)
        current_skin_design_signals.on_slot_fitting_changed.disconnect(self.on_slot_fitting_changed)
        ship_skin_signals.on_skin_sequencing_cache_invalidated.disconnect(self.on_skin_sequencing_cache_invalidated)

    def update_cost_label(self):
        self.kill_update_thread()
        self._update_thread = uthread2.start_tasklet(self.update_cost_label_async)

    def update_cost_label_async(self):
        try:
            plex_cost, discount = get_ship_skin_sequencing_svc().get_sequencing_plex_price(design=current_skin_design.get(), nb_runs=1)
        except (GenericException, TimeoutException):
            ShowQuickMessage(GetByLabel('UI/Common/CannotConnectToServer'))
            plex_cost = None
            discount = None

        self.set_cost(plex_cost, discount)
        self.display = plex_cost is not None

    def on_design_reset(self, *args):
        self.update_cost_label()

    def on_existing_design_loaded(self, *args):
        self.update_cost_label()

    def on_ship_type_id_changed(self, *args):
        self.update_cost_label()

    def on_slot_fitting_changed(self, *args):
        self.update_cost_label()

    def on_skin_sequencing_cache_invalidated(self, *args):
        self.update_cost_label()

    @property
    def cost_header_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/CostPreviewDescription')


class SequencingPanelCostInfo(CostInfo):
    default_state = uiconst.UI_NORMAL

    def update(self):
        super(SequencingPanelCostInfo, self).update()
        self.cost_label.rgba = eveColor.DANGER_RED if self.insufficient_balance else TextColor.HIGHLIGHT
        self.warning_icon.display = self.insufficient_balance
        self.layout_grid.left = 32 if self.insufficient_balance else 8

    @property
    def cost_header_text(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/TotalPLEXCost')

    @property
    def plex_balance(self):
        return sm.GetService('vgsService').GetPLEXBalance()

    @property
    def insufficient_balance(self):
        return self.cost > self.plex_balance

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadStandardSpacing()
        tooltipPanel.columns = 1
        tooltipPanel.pickState = PickState.ON
        tooltipPanel.cellSpacing = (8, 16)
        if self.insufficient_balance:
            TextBody(parent=tooltipPanel, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/InsufficientPLEX', plex_balance=int(self.plex_balance) or 0), maxWidth=220, align=Align.CENTERLEFT)
            Button(parent=tooltipPanel, label=GetByLabel('UI/Wallet/BuyMore'), func=self.on_buy_more_plex_button, style=ButtonStyle.MONETIZATION, align=Align.TOTOP)
        else:
            TextBody(parent=tooltipPanel, text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/PLEXBalance', plex_balance=int(self.plex_balance) or 0), maxWidth=220, align=Align.CENTERLEFT)

    def on_buy_more_plex_button(self, *args):
        buy_missing_plex_dialog = BuyMissingPlexDialog(required_amount=self.cost)
        buy_missing_plex_dialog.ShowModal()

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2


class BuyersFeeCostInfo(CostInfo):
    default_display = False

    def __init__(self, cost, listing, *args, **kwargs):
        self.listing = listing
        self._buyer_fee_amount = None
        super(BuyersFeeCostInfo, self).__init__(cost, *args, **kwargs)

    def construct_header(self):
        pass

    def construct_layout(self):
        super(BuyersFeeCostInfo, self).construct_layout()
        self.right_container.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/BuyersFeeHint')

    def construct_currency_icon(self, parent):
        self.currency_icon = ItemIcon(name='currency_icon', parent=parent, align=uiconst.CENTER, width=20, height=20, typeID=typeLoyaltyPointsHeraldry)

    def update(self):
        self.display = self.buyer_fee_amount is not None
        if self.buyer_fee_amount is None:
            return
        self.cost_label.text = eveformat.number(self.buyer_fee_amount)
        evermark_balance = sm.GetService('loyaltyPointsWalletSvc').GetCharacterEvermarkBalance()
        if self.listing.seller_id == session.charid:
            show_warning = False
        else:
            show_warning = evermark_balance < self.buyer_fee_amount
        if show_warning:
            self.cost_label.color = TextColor.DANGER
            self.warning_icon.display = True
            self.state = uiconst.UI_NORMAL
            self.hint = GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/ListingErrors/InsufficientFunds')
        else:
            self.cost_label.color = TextColor.NORMAL
            self.warning_icon.display = False
            self.state = uiconst.UI_PICKCHILDREN
            self.hint = None
        self.layout_grid.left = 32 if show_warning else 8
        additional_padding = 40 if show_warning else 16
        cost_amount_text_width, _ = TextHeader.MeasureTextSize(self.cost_label.text)
        desired_width = self.LEFT_WIDTH + self.SPACING + cost_amount_text_width + additional_padding
        self.width = max(self.minWidth, desired_width)

    @property
    def buyer_fee_amount(self):
        return self._buyer_fee_amount

    @buyer_fee_amount.setter
    def buyer_fee_amount(self, value):
        self._buyer_fee_amount = value
        self.update()
