#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\purchasepanels\purchaseDetailsPanel.py
import localization
import logging
from carbonui import const as uiconst
from carbonui.fontconst import STYLE_HEADER
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.vgs.priceTag import PriceTagLarge
from eve.client.script.ui.shared.vgs.currency import OFFER_CURRENCY_PLEX, OFFER_CURRENCY_YUAN, OFFER_CURRENCY_GEM
from eve.client.script.ui.view.aurumstore.vgsUiConst import STORE_PRODUCT_PANEL_PADDING
from eve.client.script.ui.view.aurumstore.purchasepanels.basePurchasePanel import BasePurchasePanel
from eve.client.script.ui.view.aurumstore.purchasepanels.giftInputPanel import GiftingInputPanel
from eve.client.script.ui.view.aurumstore.purchasepanels.currencySelectionPanel import PurchaseCurrencySelectionPanel
from eve.client.script.ui.view.aurumstore.purchasepanels.paymentPlatformSelectionPanel import PaymentPlatformSelectionPanel
from eve.client.script.ui.view.aurumstore.shared.const import QUANTITY_MIN, PRODUCTSCROLL_PANEL_HEIGHT, CONTAINER_WIDTH, PROGRESS_TRANSITION_TIME, TEXT_PADDING, QUANTITY_MAX
from eve.client.script.ui.view.aurumstore.shared.offerpricing import get_number_of_available_currencies, get_offer_price_and_base_price_in_currency, offer_is_available_in_currency
from eve.client.script.ui.view.aurumstore.shared.util import GetSortedTokens
from eve.client.script.ui.view.aurumstore.vgsDetailProduct import VgsDetailProduct
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.lib.vgsConst import CATEGORYTAG_PLEX, CATEGORYTAG_GEM
from fastcheckout.const import FROM_NES_PRODUCT
from fastcheckout.client.purchasepanels.purchaseButton import PurchaseButton
import trinity
SELECTION_PANEL_HEIGHT = 70
PRODUCT_SCROLL_MIN_HEIGHT = 38
PRODUCT_SCROLL_MAX_HEIGHT = 76
PRODUCT_SCROLL_PAD_BOT = 10
BOTTOM_CONTAINER_HEIGHT = 34
BUY_BUTTON_WIDTH = 160
BUY_BUTTON_HEIGHT = 30
PADDING_BETWEEN_BUTTONS = 10
PLEX_ICON_SIZE = 32
PLEX_ICON_MARGIN = 8
FADEOUT_DURATION = 0.5
logger = logging.getLogger(__name__)
STATE_SELECTCURRENCY = 1
STATE_SELECTPAYMENTPLATFORM = 2
STATE_CONFIRMPAYMENTMETHOD = 3
STATE_GIFTINFO = 4
STATE_RECEIPT = 5

class PurchaseDetailsPanel(BasePurchasePanel):
    default_name = 'purchaseDetailsPanel'

    def ApplyAttributes(self, attributes):
        super(PurchaseDetailsPanel, self).ApplyAttributes(attributes)
        self.offer = attributes.offer
        self.aurumBalance = attributes.aurumBalance
        self.gemBalance = attributes.gemBalance
        self.buyOfferCallback = attributes.buyOfferCallback
        self.previewCallback = attributes.previewCallback
        self.kiringPaymentInitiationCallback = attributes.kiringPaymentInitiationCallback
        self.buyAurumFunc = attributes.buyAurumFunc
        self.offerPrice = attributes.price
        self.basePrice = attributes.basePrice
        self.backButton = attributes.backButton
        self.buyButton = None
        self.buyAsGiftButton = None
        self.quantity = QUANTITY_MIN
        self.isSwitchingPanels = False
        self.currencySelectionPanel = None
        self.selectedCurrency = None
        self.productElements = []
        self.productScroll = None
        self.fastCheckoutService = sm.GetService('fastCheckoutClientService')
        self.vgsService = sm.GetService('vgsService')
        self.audioService = sm.GetService('audio')
        self.ReconstructPanel()

    def ReconstructPanel(self, animate = False):
        if self.isSwitchingPanels:
            return
        self.purchaseState = STATE_SELECTCURRENCY
        self.isSwitchingPanels = True
        if animate:
            animations.FadeOut(self, duration=0.3, sleep=True)
        self.Flush()
        self.ConstructProductLayout()
        self.ConstructGiftInputPanel()
        self.ConstructCurrencySelectionPanel()
        self.CreatePaymentPlatformSelectionPanel()
        self.ConstructBottomContainer()
        self.RestartPanel()
        if animate:
            animations.FadeIn(self, duration=0.3)
        self.isSwitchingPanels = False

    def RestartPanel(self):
        self.UpdateFrontPage()
        self.UpdateButtons()

    def ConstructProductLayout(self):
        self.productContainer = Container(name='productContainer', parent=self, align=uiconst.TOTOP, height=PRODUCTSCROLL_PANEL_HEIGHT)
        contentContainer = Container(name='contentContainer', parent=self.productContainer, align=uiconst.TOALL, padding=STORE_PRODUCT_PANEL_PADDING)
        productQuantities = GetSortedTokens(self.offer.productQuantities)
        if len(productQuantities) > 0:
            isOnlyOneItem = len(productQuantities) <= 1
            isOnlyOneCurrency = get_number_of_available_currencies(self.offer) <= 1
            isCurrencyPlex = offer_is_available_in_currency(self.offer, OFFER_CURRENCY_PLEX)
            showQuantity = isOnlyOneItem
            showPrice = isOnlyOneItem and isOnlyOneCurrency and isCurrencyPlex
            self.productScroll = ScrollContainer(name='productScroll', parent=contentContainer, align=uiconst.TOTOP, height=PRODUCT_SCROLL_MIN_HEIGHT if isOnlyOneItem else PRODUCT_SCROLL_MAX_HEIGHT, padBottom=PRODUCT_SCROLL_PAD_BOT)
            for product in productQuantities:
                Line(parent=self.productScroll, align=uiconst.TOTOP, height=1)
                self.productElements.append(VgsDetailProduct(name=product.name, parent=self.productScroll, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, typeID=product.typeId, quantity=product.quantity, price=self.offerPrice, isSinglePurchase=self.offer.singlePurchase, onClick=self.previewCallback, onQuantityChangeCallback=self.OnQuantityChange, showQuantity=showQuantity, showPrice=showPrice))

            Line(parent=self.productScroll, align=uiconst.TOTOP, height=1)
        priceContainer = Container(name='priceContainer', parent=contentContainer, align=uiconst.TOALL)
        self.priceLabelInProductContainer = PriceTagLarge(parent=priceContainer, align=uiconst.TOPRIGHT, currency=self.selectedCurrency, price=self.offerPrice, basePrice=self.basePrice, showBasePrice=False, opacity=0.0, height=BOTTOM_CONTAINER_HEIGHT, fontClass=Label, fontsize=27)

    def ConstructGiftInputPanel(self):
        self.giftInputPanel = GiftingInputPanel(parent=self, align=uiconst.TOPLEFT, opacity=0, height=PRODUCTSCROLL_PANEL_HEIGHT, width=CONTAINER_WIDTH, offer=self.offer, left=self.width)

    def ConstructCurrencySelectionPanel(self):
        self.currencySelectionPanel = PurchaseCurrencySelectionPanel(parent=self, align=uiconst.TOPLEFT, width=CONTAINER_WIDTH, height=SELECTION_PANEL_HEIGHT, top=PRODUCTSCROLL_PANEL_HEIGHT - SELECTION_PANEL_HEIGHT, padding=(30, 0, 30, 0), offer=self.offer, defaultValue=self.offer.offerPricings[0].currency, onSelect=self.OnCurrencySelectionPanel)

    def _UpdateGiftButtonState(self):
        if self.buyAsGiftButton is None:
            return
        if self.selectedCurrency == OFFER_CURRENCY_PLEX:
            canAffordPurchase = self.aurumBalance >= self.offerPrice * self.quantity
            if canAffordPurchase and not self.offer.singlePurchase:
                if not session.charid:
                    self.DisableGiftButton()
                else:
                    self.buyAsGiftButton.Show()
            else:
                self.buyAsGiftButton.Hide()
        elif self.currencySelectionPanel and self.currencySelectionPanel.GetSelectedCurrency() != OFFER_CURRENCY_PLEX:
            self.buyAsGiftButton.Hide()

    def OnCurrencySelectionPanel(self, value):
        self.SetSelectedCurrency(value)

    def UpdateFrontPage(self):
        numCurrencies = get_number_of_available_currencies(self.offer)
        if numCurrencies > 1:
            if self.productScroll:
                self.productScroll.height = PRODUCT_SCROLL_MIN_HEIGHT
                self.productContainer.height = 2 * STORE_PRODUCT_PANEL_PADDING + PRODUCT_SCROLL_MIN_HEIGHT + PRODUCT_SCROLL_PAD_BOT
            else:
                top = (PRODUCTSCROLL_PANEL_HEIGHT - SELECTION_PANEL_HEIGHT) / 2
                self.paymentPlatformSelectionPanel.top = top
                self.currencySelectionPanel.top = top
                self.productContainer.height = 0
        if numCurrencies > 1:
            self.currencySelectionPanel.Show()
        else:
            currency = self.offer.offerPricings[0].currency
            self.SetSelectedCurrency(currency)
            self.ShowPriceLabelInProductContainer()
        isSingleItem = len(self.offer.productQuantities) == 1
        self.quantityEditBottom.SetOpacity(0.0 if isSingleItem else 1.0)

    def SetSelectedCurrency(self, currency):
        self.selectedCurrency = currency
        self.UpdateOfferAndBasePrice()
        self.UpdateButtons()

    def CreatePaymentPlatformSelectionPanel(self):
        self.paymentPlatformSelectionPanel = PaymentPlatformSelectionPanel(parent=self, align=uiconst.TOPLEFT, height=SELECTION_PANEL_HEIGHT, top=PRODUCTSCROLL_PANEL_HEIGHT - SELECTION_PANEL_HEIGHT, padding=(30, 0, 30, 0), width=CONTAINER_WIDTH, defaultValue=settings.user.ui.Get('NESStorePaymentPlatformSelected', None))

    def SwitchToGiftInputPanel(self):
        if self.isSwitchingPanels:
            return
        self.isSwitchingPanels = True
        self.purchaseState = STATE_GIFTINFO
        self.backButton.Show()
        self.buyAsGiftButton.Disable()
        self.buyButton.Disable()
        self.productContainer.Disable()
        self.ShowPriceLabelBottom()
        animations.FadeOut(self.buyButton, duration=PROGRESS_TRANSITION_TIME)
        animations.MoveOutLeft(self.buyAsGiftButton, self.buyButton.width + PADDING_BETWEEN_BUTTONS, PROGRESS_TRANSITION_TIME, callback=lambda : self.buyButton.SetOpacity(0.0))
        isOnlyOneItem = len(self.offer.productQuantities) <= 1
        if isOnlyOneItem:
            self.DisableQuantityEdits()
        else:
            animations.FadeTo(self.quantityEditBottom, startVal=self.quantityEditBottom.opacity, endVal=0.3, callback=self.DisableQuantityEdits())
        animations.FadeOut(self.buyAsGiftButton.label, duration=PROGRESS_TRANSITION_TIME, callback=self.SwitchGiftButtonState)
        animations.MoveOutLeft(self.productContainer, self.width, PROGRESS_TRANSITION_TIME)
        animations.MoveOutLeft(self.currencySelectionPanel, self.width, PROGRESS_TRANSITION_TIME)
        self.giftInputPanel.OnPanelActivated()
        animations.MoveOutLeft(self.giftInputPanel, self.width, PROGRESS_TRANSITION_TIME, sleep=True, callback=self.CompletePanelTransition)
        sm.ScatterEvent('OnGiftingPanelActivated')

    def HideGiftingPanel(self):
        animations.MoveOutLeft(self.giftInputPanel, self.width, PROGRESS_TRANSITION_TIME, sleep=True, callback=lambda : self.CompletePanelTransition(self.giftInputPanel))

    def CompletePanelTransition(self, panel_to_hide = None):
        self.isSwitchingPanels = False
        if panel_to_hide:
            panel_to_hide.Hide()

    def SwitchGiftButtonState(self):
        if self.purchaseState == STATE_GIFTINFO:
            self.buyAsGiftButton.SetText(localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyGift'))
            self.buyAsGiftButton.func = self.OnBuyAsGiftBtn
        else:
            self.buyAsGiftButton.SetText(localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyAsGift'))
            self.buyAsGiftButton.func = self.SwitchToGiftInputPanel
        animations.FadeIn(self.buyAsGiftButton.label, duration=0.5, callback=self.buyAsGiftButton.Enable)

    def ConstructBottomContainer(self):
        bottomContainer = Container(name='bottomContainer', parent=self, align=uiconst.TOBOTTOM, height=BOTTOM_CONTAINER_HEIGHT, padding=(30, 10, 30, 30))
        self.priceLabelBottom = PriceTagLarge(parent=bottomContainer, align=uiconst.CENTERLEFT, currency=self.selectedCurrency, price=self.offerPrice, basePrice=self.basePrice, showBasePrice=False, opacity=0.0, height=BOTTOM_CONTAINER_HEIGHT, fontClass=Label, fontsize=27)
        actionsContainer = ContainerAutoSize(name='actionsContainer', parent=bottomContainer, align=uiconst.CENTERRIGHT, height=BUY_BUTTON_HEIGHT)
        self.buyButton = PurchaseButton(name='buyButton', parent=actionsContainer, align=uiconst.TORIGHT, width=BUY_BUTTON_WIDTH, height=BUY_BUTTON_HEIGHT)
        self.buyAsGiftButton = PurchaseButton(name='buyAsGiftButton', parent=actionsContainer, align=uiconst.TORIGHT, width=BUY_BUTTON_WIDTH, height=BUY_BUTTON_HEIGHT, text=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyAsGift'), func=self.SwitchToGiftInputPanel, left=PADDING_BETWEEN_BUTTONS)
        self._UpdateGiftButtonState()
        self.quantityEditBottom = SingleLineEditInteger(parent=actionsContainer, minValue=QUANTITY_MIN, maxValue=QUANTITY_MAX, fontsize=18, fontStyle=STYLE_HEADER, bold=True, width=56, height=24, top=0, align=uiconst.TORIGHT, left=TEXT_PADDING, bgColor=Color.GRAY7, arrowIconColor=(0.0, 0.0, 0.0, 1.0), arrowIconGlowColor=(0.2, 0.2, 0.2, 1.0), arrowIconClass=Sprite, arrowIconBlendMode=trinity.TR2_SBM_BLEND, arrowUseThemeColor=False, caretColor=(0.0, 0.0, 0.0, 0.75), selectColor=(0.0, 0.0, 0.0, 0.25), fontcolor=(0.0, 0.0, 0.0, 1.0), OnChange=self.OnQuantityChange, maxLength=2, hint=localization.GetByLabel('UI/Common/Quantity'), state=uiconst.UI_NORMAL)
        if self.offer.singlePurchase:
            self.quantityEditBottom.Disable()
        self.quantityEditBottom.underlay.Hide()

    def OnCurrencySelected(self):
        self.UpdateOfferAndBasePrice()
        self.HideCurrencySelectionPanel()
        if self.selectedCurrency in [OFFER_CURRENCY_PLEX, OFFER_CURRENCY_GEM]:
            self.purchaseState = STATE_CONFIRMPAYMENTMETHOD
            self.OnBuyForPLEXClick()
        elif self.selectedCurrency == OFFER_CURRENCY_YUAN:
            self.purchaseState = STATE_SELECTPAYMENTPLATFORM
            self.ShowPaymentPlatformSelectionPanel()
        self.ShowPriceLabelBottom()
        self.UpdateButtons()
        isSingleItem = len(self.offer.productQuantities) == 1
        self.quantityEditBottom.SetOpacity(0.0 if isSingleItem else 1.0)

    def UpdateOfferAndBasePrice(self):
        self.offerPrice, self.basePrice = get_offer_price_and_base_price_in_currency(self.offer, self.selectedCurrency)
        self._UpdateGiftButtonState()

    def ShowPriceLabelBottom(self):
        self.UpdatePriceLabel()
        self.priceLabelInProductContainer.SetOpacity(0.0)
        animations.FadeTo(self.priceLabelBottom, self.priceLabelBottom.opacity, 1.0, duration=0.6)

    def ShowPriceLabelInProductContainer(self):
        self.UpdatePriceLabel()
        self.priceLabelBottom.SetOpacity(0.0)
        animations.FadeTo(self.priceLabelInProductContainer, self.priceLabelInProductContainer.opacity, 1.0, duration=0.6)

    def ShowPaymentPlatformSelectionPanel(self):
        self.paymentPlatformSelectionPanel.left = 0
        animations.MorphScalar(self.paymentPlatformSelectionPanel, 'left', CONTAINER_WIDTH, duration=PROGRESS_TRANSITION_TIME)
        self.paymentPlatformSelectionPanel.opacity = 1.0
        self.paymentPlatformSelectionPanel.Show()

    def HideCurrencySelectionPanel(self):
        animations.MorphScalar(self.currencySelectionPanel, 'left', self.currencySelectionPanel.left, -CONTAINER_WIDTH, duration=PROGRESS_TRANSITION_TIME)
        animations.FadeOut(self.currencySelectionPanel, duration=PROGRESS_TRANSITION_TIME)

    def OnPaymentPlatformSelected(self):
        paymentMethod = self.paymentPlatformSelectionPanel.GetSelectedPaymentMethod()
        settings.user.ui.Set('NESStorePaymentPlatformSelected', paymentMethod)
        self.kiringPaymentInitiationCallback(paymentMethod, self.selectedCurrency, self.offerPrice, self.offer.goodsID, self.GetQuantity(), self.offer.id)

    def UpdateButtons(self):
        if self.purchaseState == STATE_SELECTPAYMENTPLATFORM:
            self.buyAsGiftButton.Hide()
            self.DisableQuantityEdits()
            self.buyButton.SetOpacity(1.0)
        self.backButton.display = self.purchaseState in (STATE_GIFTINFO, STATE_SELECTPAYMENTPLATFORM)
        self._UpdateGiftButtonState()
        func, text = self._GetButtonFuncTextAndColor()
        if self.buyButton:
            self.buyButton.func = func
            self.buyButton.SetText(text)

    def _GetButtonFuncTextAndColor(self):
        if self.purchaseState == STATE_SELECTCURRENCY:
            isPlexSelected = self.selectedCurrency == OFFER_CURRENCY_PLEX
            isGemSelected = self.selectedCurrency == OFFER_CURRENCY_GEM
            if isPlexSelected and self.aurumBalance < self.offerPrice * self.quantity:
                shouldUsePlex = self.fastCheckoutService.should_use_plex()
                func = self.buyAurumFunc if shouldUsePlex else self._BuyAurum
                text = localization.GetByLabel('UI/VirtualGoodsStore/BuyAurOnline')
            elif isGemSelected and self.gemBalance < self.offerPrice * self.quantity:
                func = self._BuyGem
                text = localization.GetByLabel('UI/VirtualGoodsStore/BuyGemOnline')
            else:
                func = self.OnCurrencySelected
                if self.offerPrice == 0:
                    text = localization.GetByLabel('UI/FastCheckout/AurumSavingsLabel')
                else:
                    text = localization.GetByLabel('UI/VirtualGoodsStore/OfferDetailBuyNowButton')
        elif self.purchaseState == STATE_SELECTPAYMENTPLATFORM:
            func = self.OnPaymentPlatformSelected
            text = localization.GetByLabel('UI/DynamicItem/Continue')
        else:
            func = None
            text = ''
        return (func, text)

    def DisableGiftButton(self):
        self.buyAsGiftButton.func = None
        self.buyAsGiftButton.SetOpacity(0.5)
        self.buyAsGiftButton.SetHint(localization.GetByLabel('UI/VirtualGoodsStore/LoginRequiredForGiftingHint'))

    def GetQuantityEditValue(self):
        if len(self.productElements) == 1:
            return self.productElements[0].GetQuantityEditValue()
        return self.quantityEditBottom.GetValue()

    def SetQuantityEditValue(self, quantity):
        self.quantityEditBottom.SetValue(quantity, docallback=False)
        for productElement in self.productElements:
            productElement.SetQuantityEditValue(quantity)

    def DisableQuantityEdits(self):
        self.quantityEditBottom.Disable()
        for productElement in self.productElements:
            productElement.DisableQuantityEdit()

    def OnQuantityChange(self, newQuantity):
        try:
            quantity = max(QUANTITY_MIN, min(int(newQuantity), QUANTITY_MAX))
        except ValueError:
            quantity = QUANTITY_MIN

        if self.quantity != quantity:
            self.quantity = quantity
            self.currencySelectionPanel.SetQuantity(self.quantity)
            self.UpdatePriceLabel()
            self.UpdateButtons()
            self.SetQuantityEditValue(self.quantity)

    def UpdatePriceLabel(self):
        newOfferPrice = self.offerPrice * self.quantity
        newOfferBasePrice = self.basePrice * self.quantity
        self.priceLabelBottom.UpdatePrice(newOfferPrice, newOfferBasePrice, self.selectedCurrency)
        self.priceLabelInProductContainer.UpdatePrice(newOfferPrice, newOfferBasePrice, self.selectedCurrency)

    def GetQuantity(self):
        return self.quantity

    def _BuyAurum(self):
        self.audioService.SendUIEvent('store_aur')
        if self.fastCheckoutService.is_china_funnel():
            uiController = self.vgsService.GetUiController()
            uiController.CloseOffer()
            uiController.view.storeContainer.SelectCategoryByCategoryTag(CATEGORYTAG_PLEX)
        else:
            sm.GetService('viewState').GetView(ViewState.VirtualGoodsStore)._LogBuyAurum('DetailButton')
            uicore.cmd.CmdBuyPlex(logContext=FROM_NES_PRODUCT)

    def _BuyGem(self):
        self.vgsService.GetUiController().CloseOffer()
        self.audioService.SendUIEvent('store_aur')
        self.vgsService.GetUiController().view.storeContainer.SelectCategoryByCategoryTag(CATEGORYTAG_GEM)

    def OnBuyForPLEXClick(self, *args):
        logger.debug('OnBuyClick %s' % (self.offer,))
        self.audioService.SendUIEvent('store_buy')
        self.buyButton.Disable()
        self.buyOfferCallback(self.offer, currency=self.selectedCurrency, quantity=self.GetQuantityEditValue())

    def OnBuyAsGiftBtn(self):
        giftingInfo = self.giftInputPanel.get_gifting_information()
        if not giftingInfo:
            return
        sm.ScatterEvent('OnGiftingPurchasePressed')
        self.buyAsGiftButton.Disable()
        self.audioService.SendUIEvent('store_buy')
        self.SetSelectedCurrency(self.currencySelectionPanel.GetSelectedCurrency())
        if self.selectedCurrency == OFFER_CURRENCY_YUAN:
            self._OnBuyAsGiftBtnYuanSelected()
        else:
            self.buyOfferCallback(self.offer, self.selectedCurrency, quantity=self.GetQuantityEditValue(), toCharacterID=giftingInfo.toCharacterID, message=giftingInfo.message)

    def _OnBuyAsGiftBtnYuanSelected(self):
        self.purchaseState = STATE_SELECTPAYMENTPLATFORM
        self.HideGiftingPanel()
        self.ShowPaymentPlatformSelectionPanel()
        self.buyButton.Enable()
        animations.FadeIn(self.buyButton, duration=PROGRESS_TRANSITION_TIME)
        self.UpdateButtons()

    def UpdateValues(self):
        account = self.vgsService.GetStore().GetAccount()
        self.aurumBalance = account.GetAurumBalance()
        self.gemBalance = account.GetGemBalance()
        self.UpdateButtons()
