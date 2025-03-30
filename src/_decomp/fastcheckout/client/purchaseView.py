#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fastcheckout\client\purchaseView.py
import blue
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.vgs.currency import get_price_text
from eve.client.script.ui.shared.vgs.views.purchaseView import PurchaseSuccessPanel, PurchaseFailedPanel, ConfirmPurchasePanel
from eveexceptions import UserError
from fastcheckout.client.eventlogging.eventLoggers import event_logger
from fastcheckout.client.offerinfopanels.plexOffersInfoPanel import get_plex_icon_for_quantity
from fastcheckout.client.purchasepanels.loadingPanel import LoadingPanel
from fastcheckout.client.purchasepanels.passwordInputPanel import PasswordInputPanel
from fastcheckout.client.purchasepanels.purchaseButton import AnimatedPurchaseButton, SecondaryPurchaseButton
from fastcheckout.const import FULL_WINDOW_WIDTH
from localization import GetByLabel
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import LazyUrlSprite
LEFT_PANEL_PROP = 0.6
RIGHT_PANEL_PROP = 0.35
LEFT_PANEL_WIDTH = LEFT_PANEL_PROP * FULL_WINDOW_WIDTH
RIGHT_PANEL_WIDTH = RIGHT_PANEL_PROP * FULL_WINDOW_WIDTH
PLEX_IMAGE_MARGIN = 10
PLEX_IMAGE_SIZE = 350
PLEX_IMAGE_TEXTURE_SIZE = 888
LABEL_LEFT_INDENT = 6
PURCHASE_INFO_HEIGHT_FACTOR = 0.5
LINE_COLOR = (0.5, 0.5, 0.5, 0.4)
LINE_HEIGHT = 1
PADDING_TITLE_TO_LINE = 6
PADDING_LINE_TO_PRICE = 10
PADDING_TOP_TO_TITLE = 30
PADDING_LINE_TO_DESCRIPTION = 14
PADDING_BOTTOM_TO_PRICE = 10
PADDING_BOTTOM_TO_BUTTONS = 30
PADDING_BETWEEN_TWO_BUTTONS = 10
PURCHASE_SUCCESS_PANEL_TOP = 10
PURCHASE_FAILED_PANEL_TOP = 10
CONFIRM_PURCHASE_PANEL_TOP = 10
BUTTON_WIDTH_BIG = 200
BUTTON_WIDTH_SMALL = 150
BUTTON_HEIGHT = 35
BACK_BUTTON_HEIGHT = 10
BACK_BUTTON_ARROW_WIDTH = 7
FONTSIZE_TITLE = 14
FONTSIZE_DESCRIPTION = 16
FONTSIZE_PRICE = 30
FONTSIZE_BUTTON_BIG = 18
FONTSIZE_BUTTON_SMALL = 14

class PlexPurchaseView(Container):
    default_bgColor = None

    def ApplyAttributes(self, attributes):
        super(PlexPurchaseView, self).ApplyAttributes(attributes)
        offer = attributes.get('offer', None)
        self.offer = offer
        self.offer_id = offer['id']
        self.offer_quantity = offer['quantity']
        self.offer_currency = offer['currency']
        self.offer_price = offer['price']
        self.close_function = attributes.get('close_function', None)
        self.opened_from_nes = attributes.get('opened_from_nes', False)
        self.log_context = attributes.get('log_context')
        self.panel = None
        self.is_purchase_processed = False
        self.service = sm.GetService('fastCheckoutClientService')
        self.construct_layout()
        self.display_panel(self.panel)

    def _OnClose(self, *args, **kw):
        self.parent.display_elements()

    def construct_layout(self):
        main_container = Container(name='main_container', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.left_panel = Container(name='left_panel', parent=main_container, align=uiconst.TOLEFT_PROP, width=LEFT_PANEL_PROP, clipChildren=True)
        self.construct_back_button()
        self.construct_offer_image()
        self.right_panel = Container(name='right_panel', parent=main_container, align=uiconst.TOLEFT_PROP, width=RIGHT_PANEL_PROP)
        self.construct_plex_info()
        self.construct_action_panel()
        self.construct_button_container()

    def construct_back_button(self):
        back_button_container = ContainerAutoSize(name='back_button_container', parent=self.left_panel, align=uiconst.ANCH_TOPLEFT, height=BACK_BUTTON_HEIGHT, top=25, left=30, state=uiconst.UI_NORMAL)
        back_button_container.OnClick = lambda *args: self.Close()
        Sprite(name='arrow_icon', parent=back_button_container, align=uiconst.CENTERLEFT, width=BACK_BUTTON_ARROW_WIDTH, height=BACK_BUTTON_HEIGHT, texturePath='res:/UI/Texture/classes/FastCheckout/back_arrow.png', state=uiconst.UI_DISABLED)
        Label(name='back_label', parent=back_button_container, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Common/Buttons/Back').upper(), fontsize=14, letterspace=1, bold=True, color=Color.WHITE, left=BACK_BUTTON_ARROW_WIDTH + 10, state=uiconst.UI_DISABLED)

    def construct_offer_image(self):
        container_size = PLEX_IMAGE_SIZE + 2 * PLEX_IMAGE_MARGIN
        image_container = Container(name='offer_image_container', parent=self.left_panel, align=uiconst.CENTER, width=container_size, height=container_size, state=uiconst.UI_DISABLED)
        if self.offer.imageUrl is not None:
            LazyUrlSprite(parent=image_container, align=uiconst.CENTER, width=PLEX_IMAGE_SIZE, height=PLEX_IMAGE_SIZE, imageUrl=self.offer.imageUrl, state=uiconst.UI_DISABLED)
        else:
            Sprite(name='offer_image', parent=image_container, align=uiconst.CENTER, width=PLEX_IMAGE_SIZE, height=PLEX_IMAGE_SIZE, texturePath=get_plex_icon_for_quantity(self.offer_quantity, size=PLEX_IMAGE_TEXTURE_SIZE), state=uiconst.UI_DISABLED)

    def construct_plex_info(self):
        self.purchase_info_container = Container(name='purchase_info_container', parent=self.right_panel, align=uiconst.TOTOP_PROP, height=PURCHASE_INFO_HEIGHT_FACTOR, state=uiconst.UI_DISABLED, padTop=PADDING_TOP_TO_TITLE)
        self._construct_purchase_title()
        self._construct_purchase_description()
        self._construct_purchase_price()

    def _construct_purchase_title(self):
        purchase_title_container = ContainerAutoSize(name='purchase_title_container', parent=self.purchase_info_container, align=uiconst.TOTOP)
        Label(name='purchase_title_label', parent=purchase_title_container, align=uiconst.TOTOP, text=GetByLabel('UI/FastCheckout/ItemsLabel'), color=Color.ORANGE, fontsize=FONTSIZE_TITLE, padLeft=LABEL_LEFT_INDENT)
        Line(name='purchase_title_line', parent=purchase_title_container, align=uiconst.TOTOP, height=LINE_HEIGHT, color=LINE_COLOR, padTop=PADDING_TITLE_TO_LINE)

    def _construct_purchase_description(self):
        text = self.offer.name
        purchase_description_container = ContainerAutoSize(name='purchase_description_container', parent=self.purchase_info_container, align=uiconst.TOTOP, top=PADDING_LINE_TO_DESCRIPTION)
        Label(name='purchase_description_label', parent=purchase_description_container, align=uiconst.TOTOP, text=text, fontsize=FONTSIZE_DESCRIPTION, padLeft=LABEL_LEFT_INDENT)

    def _construct_purchase_price(self):
        price_text = get_price_text(self.offer_price, self.offer_currency)
        purchase_price_container = ContainerAutoSize(name='purchase_price_container', parent=self.purchase_info_container, align=uiconst.TOBOTTOM, padBottom=PADDING_BOTTOM_TO_PRICE)
        Line(name='purchase_title_line', parent=purchase_price_container, align=uiconst.TOTOP, height=LINE_HEIGHT, color=LINE_COLOR, padBottom=PADDING_LINE_TO_PRICE)
        purchase_price_label_container = ContainerAutoSize(name='purchase_price_label_container', parent=purchase_price_container, align=uiconst.TOTOP)
        Label(name='purchase_price_label', parent=purchase_price_label_container, align=uiconst.TOPRIGHT, text=price_text, fontsize=FONTSIZE_PRICE, color=Color.ORANGE)

    def construct_action_panel(self):
        self.action_panel = Container(name='action_panel', parent=self.right_panel, align=uiconst.TOTOP_PROP, height=1.0 - PURCHASE_INFO_HEIGHT_FACTOR)
        self.panel = PasswordInputPanel(enter_password_func=self.send_purchase_confirmation, forgot_password_func=self.request_password_reset, close_func=self.cancel_password_input)

    def construct_button_container(self):
        self.button_container = Container(name='button_container', parent=self.right_panel, align=uiconst.TOBOTTOM, height=BUTTON_HEIGHT, padBottom=PADDING_BOTTOM_TO_BUTTONS)

    def complete_plex_purchase(self):
        animations.FadeOut(self, callback=self.Close)

    def construct_flow_buttons(self):
        if self.web_flow_url is not None:
            self.construct_confirm_button()
        elif self.opened_from_nes:
            self.construct_continue_button()
        else:
            if session.stationid is not None:
                self.construct_sell_now_button()
            self.construct_redeem_button()

    def construct_sell_now_button(self):
        self.sell_now_button = SecondaryPurchaseButton(name='SellNowButton', parent=self.button_container, align=uiconst.TORIGHT, width=BUTTON_WIDTH_SMALL if session.stationid else BUTTON_WIDTH_BIG, height=BUTTON_HEIGHT, opacity=0, fontsize=FONTSIZE_BUTTON_SMALL if session.stationid else FONTSIZE_BUTTON_BIG, cornerSize=20, text=GetByLabel('UI/FastCheckout/SellNow'), delayedHint=GetByLabel('UI/FastCheckout/SellNowButtonHint'), func=lambda : self.sell_plex())

    def construct_redeem_button(self):
        self.redeem_button = AnimatedPurchaseButton(name='RedeemButton', parent=self.button_container, align=uiconst.TORIGHT, width=BUTTON_WIDTH_SMALL if session.stationid else BUTTON_WIDTH_BIG, height=BUTTON_HEIGHT, left=PADDING_BETWEEN_TWO_BUTTONS if session.stationid else 0, opacity=0, state=uiconst.UI_DISABLED, fontsize=FONTSIZE_BUTTON_SMALL if session.stationid else FONTSIZE_BUTTON_BIG, func=lambda : self.open_plex_vault(), text=GetByLabel('UI/FastCheckout/RedeemButtonLabel'), delayedHint=GetByLabel('UI/FastCheckout/RedeemButtonHint'))

    def construct_confirm_button(self):
        self.confirm_button = AnimatedPurchaseButton(name='ConfirmButton', parent=self.button_container, align=uiconst.TORIGHT, width=BUTTON_WIDTH_BIG, height=BUTTON_HEIGHT, opacity=0, state=uiconst.UI_DISABLED, fontsize=FONTSIZE_BUTTON_BIG, func=lambda : blue.os.ShellExecute(self.web_flow_url), text=GetByLabel('UI/VirtualGoodsStore/Purchase/ConfirmationButtonLabel'))

    def construct_continue_button(self):
        self.continue_button = AnimatedPurchaseButton(name='ContinueButton', parent=self.button_container, align=uiconst.TORIGHT, width=BUTTON_WIDTH_BIG, height=BUTTON_HEIGHT, opacity=0, state=uiconst.UI_DISABLED, fontsize=FONTSIZE_BUTTON_BIG, func=lambda : self.complete_plex_purchase(), text=GetByLabel('UI/VirtualGoodsStore/ContinueShopping'))

    def construct_purchase_failed_ok_button(self):
        self.purchase_failed_ok_button = AnimatedPurchaseButton(name='PurchaseFailedOkButton', parent=self.button_container, align=uiconst.TORIGHT_NOPUSH, width=BUTTON_WIDTH_BIG, height=BUTTON_HEIGHT, opacity=0, state=uiconst.UI_DISABLED, fontsize=FONTSIZE_BUTTON_BIG, func=lambda : animations.FadeOut(self, callback=self.Close), text=GetByLabel('UI/FastCheckout/ErrorPurchaseFailedButton'))

    @staticmethod
    def open_plex_vault():
        sm.GetService('cmd').OpenPlexVault()

    def sell_plex(self):
        try:
            from eve.client.script.ui.shared.inventory.plexVault import PlexVaultController
            controller = PlexVaultController()
            controller.SellPlex()
        finally:
            event_logger.log_plex_sell_now_button_pressed(self.log_context, self.offer_id, self.offer_quantity)

    def send_purchase_confirmation(self, password):
        if not password:
            return
        self.panel.Disable()
        self.display_panel(LoadingPanel())
        try:
            ret = self.service.buy_plex_offer(self.log_context, self.offer, password)
        except UserError as e:
            self.construct_purchase_failed_ok_button()
            self.show_error(e.msg)
        else:
            self.is_purchase_processed = True
            self.web_flow_url = None
            if ret['Message'] == 'WebFlowNeeded':
                self.web_flow_url = sm.GetService('cmd').GetURLWithParameters(ret['PaymentUrl'], ret['Message'])
            self.construct_flow_buttons()
            is_purchase_confirmed = self.web_flow_url is None
            if is_purchase_confirmed:
                self.process_successful_purchase()
            else:
                self.process_unconfirmed_purchase()
        finally:
            self.panel.Enable()

    def request_password_reset(self):
        self.service.request_password_recovery(self.log_context, self.offer_id, self.offer_quantity)

    def cancel_password_input(self):
        if self.is_purchase_processed:
            return
        event_logger.log_password_enter_cancelled(self.log_context, self.offer_id, self.offer_quantity)

    def show_error(self, error):
        if error == 'AuthFailed':
            self._show_error_wrong_password()
        elif error == 'OfferNotAvailable':
            self._show_error_offer_not_available()
        else:
            self._show_error_other()

    def _show_error_wrong_password(self):
        panel = PasswordInputPanel(enter_password_func=self.send_purchase_confirmation, forgot_password_func=self.request_password_reset, close_func=self.cancel_password_input)
        self.display_panel(panel)
        self.panel.notify_of_wrong_password()

    def _show_error_offer_not_available(self):
        panel = PurchaseFailedPanel(subText=GetByLabel('UI/FastCheckout/MaximumTransactionsReached'), padTop=PURCHASE_FAILED_PANEL_TOP, width=RIGHT_PANEL_WIDTH, padBottom=BUTTON_HEIGHT + PADDING_BOTTOM_TO_BUTTONS)
        self.display_panel(panel)
        self.purchase_failed_ok_button.FadeIn()

    def _show_error_other(self):
        panel = PurchaseFailedPanel(subText=GetByLabel('UI/FastCheckout/ErrorPurchaseFailed'), padTop=PURCHASE_FAILED_PANEL_TOP, width=RIGHT_PANEL_WIDTH, padBottom=BUTTON_HEIGHT + PADDING_BOTTOM_TO_BUTTONS)
        self.display_panel(panel)
        self.purchase_failed_ok_button.FadeIn()

    def process_unconfirmed_purchase(self):
        self.display_panel(ConfirmPurchasePanel(subTextTimeOffset=1, padTop=CONFIRM_PURCHASE_PANEL_TOP, width=RIGHT_PANEL_WIDTH, padBottom=BUTTON_HEIGHT + PADDING_BOTTOM_TO_BUTTONS))
        self.confirm_button.FadeIn()

    def process_successful_purchase(self):
        self.display_panel(PurchaseSuccessPanel(subText=GetByLabel('UI/FastCheckout/PLEXPurchaseSuccessSubText'), subTextTimeOffset=1, padTop=PURCHASE_SUCCESS_PANEL_TOP, width=RIGHT_PANEL_WIDTH, padBottom=BUTTON_HEIGHT + PADDING_BOTTOM_TO_BUTTONS))
        if self.opened_from_nes:
            self.continue_button.FadeIn()
        else:
            self.redeem_button.FadeIn()
            if session.stationid is not None:
                self.sell_now_button.FadeIn()

    def display_panel(self, panel):
        if self.panel:
            animations.StopAllAnimations(self.panel)
            self.panel.AnimExit()
        self.panel = panel
        self.panel.SetParent(self.action_panel)
        self.panel.AnimEntry()
