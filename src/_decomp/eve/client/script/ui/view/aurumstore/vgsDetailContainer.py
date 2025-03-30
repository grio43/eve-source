#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\aurumstore\vgsDetailContainer.py
import blue
import logging
import math
import time
import uthread
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.redeem.redeemPanel import GetOldRedeemPanel
from eve.client.script.ui.shared.redeem.oldRedeemPanel import StaticRedeemContainer
from eve.client.script.ui.shared.vgs.headerButton import HeaderButton
from eve.client.script.ui.shared.vgs.kiringPaymentProvider import get_element_for_payment_provider
from eve.client.script.ui.shared.vgs.priceTag import PriceTagLarge
from eve.client.script.ui.view.aurumstore.purchasepanels.purchaseDetailsPanel import PurchaseDetailsPanel
from eve.client.script.ui.view.aurumstore.purchasepanels.purchaseProgressPanel import PurchaseProgressPanel
from eve.client.script.ui.view.aurumstore.purchasepanels.purchaseResultPanel import PurchaseResultPanel
from eve.client.script.ui.view.aurumstore.shared.const import TEXT_PADDING, PROGRESS_TRANSITION_TIME, CONTAINER_WIDTH, CONTAINER_WIDTH_LARGE, CONTAINER_WIDTH_SMALL, TOP_PANEL_HEIGHT, TOP_PANEL_HEIGHT_LARGE, TOP_PANEL_HEIGHT_SMALL, MIN_SCREEN_HEIGHT_FOR_LARGE, MIN_SCREEN_HEIGHT_FOR_SMALL, BOTTOM_PANEL_HEIGHT, FRAME_COLOR, EXIT_BUTTON_PADDING, FRAME_WIDTH, STORE_PREVIEW_OVERLAY_HEIGHT
from eve.common.script.sys.eveCfg import IsPreviewable, IsBlueprint
from eve.client.script.ui.view.aurumstore.shared.offerpricing import get_number_of_available_currencies
from eve.client.script.ui.view.aurumstore.shared.util import GetSortedTokens
from eve.client.script.ui.view.aurumstore.vgsOffer import Ribbon, VgsOfferPreview
from eve.client.script.ui.view.aurumstore.vgsUiConst import BACKGROUND_COLOR, BUY_BUTTON_COLOR, HEADER_BG_COLOR, REDEEM_BUTTON_BACKGROUND_COLOR, REDEEM_BUTTON_FILL_COLOR
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import VgsLabelSmall, DetailButton, ExitButton, LazyUrlSprite, VgsLabelMedium
from fastcheckout.const import WINDOW_COLOR, FROM_NES_PRODUCT
from kiring.client.apigateway import KiringPaymentActionID, get_kiring_api_gateway, KiringOrder
from localization import GetByLabel
logger = logging.getLogger(__name__)

class VgsDetailContainer(Container):
    __notifyevents__ = ['OnGiftingPanelActivated', 'OnGiftingPurchasePressed']
    default_name = 'VgsDetailContainer'
    default_state = uiconst.UI_PICKCHILDREN
    frameColor = Color.GRAY9
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        super(VgsDetailContainer, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.vgsUiController = attributes.vgsUiController
        self.offer = attributes.offer
        self.qrCodeCont = None
        fullWidth, fullHeight = self.GetAbsoluteSize()
        self.backgroundBottomContainer = ContainerAutoSize(parent=self, name='backgroundBottomContainer', align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_PICKCHILDREN, width=fullWidth)
        self.backgroundTopContainer = Container(parent=self, name='backgroundTopContainer', align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, height=fullHeight, width=fullWidth)
        if self._doMakeCardLarge(fullHeight):
            self.contWidth = CONTAINER_WIDTH_LARGE
            self.contTopWidth = TOP_PANEL_HEIGHT_LARGE
        elif self._doMakeCardSmall(fullHeight):
            self.contWidth = CONTAINER_WIDTH_SMALL
            self.contTopWidth = TOP_PANEL_HEIGHT_SMALL
        else:
            self.contWidth = CONTAINER_WIDTH
            self.contTopWidth = TOP_PANEL_HEIGHT
        self.offerContainer = Container(parent=self.backgroundTopContainer, name='offerContainer', state=uiconst.UI_NORMAL, align=uiconst.CENTER, width=self.contWidth, height=self.contTopWidth + BOTTOM_PANEL_HEIGHT, bgColor=BACKGROUND_COLOR)
        self.preview_fill = Fill(parent=self.offerContainer, align=uiconst.TOALL, opacity=0, color=WINDOW_COLOR)
        self.loading_wheel = LoadingWheel(parent=self.offerContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0)
        self.main_container = Container(name='MainContainer', parent=self.offerContainer, align=uiconst.TOALL)
        Fill(bgParent=self.main_container, color=FRAME_COLOR, padding=-FRAME_WIDTH)
        previewOverlay = Container(name='previewOverlay', parent=self.main_container, align=uiconst.TOTOP_NOPUSH, height=STORE_PREVIEW_OVERLAY_HEIGHT)
        if self.offer.label is not None:
            Ribbon(parent=previewOverlay, align=uiconst.TOPLEFT, text=self.offer.label.description, texture_path=self.offer.label.url, state=uiconst.UI_DISABLED, idx=0, isBig=True, padding=(-20, -10, 0, 0))
        exitButton = ExitButton(parent=previewOverlay, align=uiconst.TOPRIGHT, onClick=self.CloseOffer, top=EXIT_BUTTON_PADDING, left=EXIT_BUTTON_PADDING)
        GradientSprite(bgParent=previewOverlay, rgbData=[(0.0, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0))], alphaData=[(0.0, 0.5), (1.0, 0.0)], rotation=-math.pi / 2.0)
        self.backButton = HeaderButton(parent=self.main_container, align=uiconst.TOPRIGHT, left=EXIT_BUTTON_PADDING, top=EXIT_BUTTON_PADDING + exitButton.height + 2, texturePath='res:/UI/Texture/Vgs/back.png', hint=GetByLabel('UI/Commands/Back'), onClick=self.OnBackButtonClicked, state=uiconst.UI_HIDDEN)
        self.preview = VgsOfferPreview(parent=self.main_container, align=uiconst.TOTOP, height=self.contTopWidth, offer=self.offer)
        self.CreateBottomLayout(self.offer, attributes.aurumBalance, attributes.gemBalance)
        self.CreateFakeRedeemPanel()
        self.kiringApiGateway = get_kiring_api_gateway()

    def _isPreviewableOffer(self):
        for product in self.offer.productQuantities.itervalues():
            typeID = product.typeId
            if IsBlueprint(typeID) or IsPreviewable(typeID):
                return True
            return False

    def _doMakeCardLarge(self, windowHeight):
        return self._isPreviewableOffer() and MIN_SCREEN_HEIGHT_FOR_LARGE <= windowHeight

    def _doMakeCardSmall(self, windowHeight):
        return MIN_SCREEN_HEIGHT_FOR_SMALL >= windowHeight

    def CreateBottomLayout(self, offer, aurumBalance, gemBalance):
        self.bottomContainer = Container(name='bottomContainer', parent=self.main_container, align=uiconst.TOTOP, clipChildren=True, height=BOTTOM_PANEL_HEIGHT)
        Fill(align=uiconst.TOALL, bgParent=self.bottomContainer, color=HEADER_BG_COLOR)
        GradientSprite(align=uiconst.TOALL, bgParent=self.bottomContainer, rgbData=((0.0, (0.0, 0.0, 0.0)), (1.0, (0.0, 0.0, 0.0))), alphaData=((0.0, 0.8), (0.2, 0.6), (0.6, 0.0)), rotation=math.pi * 0.4)
        self.continueButton = DetailButton(name='ContinueShoppingButton', parent=self.bottomContainer, align=uiconst.CENTERBOTTOM, label=GetByLabel('UI/VirtualGoodsStore/ContinueShopping'), color=BUY_BUTTON_COLOR, state=uiconst.UI_HIDDEN, opacity=0, top=10, onClick=self.CloseOffer)
        currency, price = (None, None)
        if get_number_of_available_currencies(offer) == 1:
            offerPricing = offer.offerPricings[0]
            currency = offerPricing.currency
            price = offerPricing.price
        self.purchaseDetailsPanel = PurchaseDetailsPanel(parent=self.bottomContainer, offer=offer, aurumBalance=aurumBalance, gemBalance=gemBalance, buyOfferCallback=self.vgsUiController.BuyOffer, previewCallback=self.OnPreviewType, kiringPaymentInitiationCallback=self.OnKiringPaymentInitiated, state=uiconst.UI_PICKCHILDREN, width=self.contWidth, buyAurumFunc=lambda : uicore.cmd.CmdBuyPlex(logContext=FROM_NES_PRODUCT), backButton=self.backButton, currency=currency, price=price)
        self.activeBottomPanel = self.purchaseDetailsPanel
        self.purchaseProgressPanel = PurchaseProgressPanel(parent=self.bottomContainer, width=self.contWidth)
        self.purchaseSuccessPanel = PurchaseResultPanel(parent=self.bottomContainer, closeOfferCallback=self.CloseOffer, iconForegroundTexturePath='res:/UI/Texture/vgs/purchase_success_fg.png', iconBackgroundTexturePath='res:/UI/Texture/vgs/purchase_success_bg.png', textTitle=GetByLabel('UI/VirtualGoodsStore/Purchase/Completed'), audioEventName='store_purchase_success', width=self.contWidth)
        self.purchaseFailurePanel = PurchaseResultPanel(parent=self.bottomContainer, closeOfferCallback=self.CloseOffer, iconForegroundTexturePath='res:/UI/Texture/vgs/purchase_fail_fg.png', iconBackgroundTexturePath='res:/UI/Texture/vgs/purchase_fail_bg.png', textTitle=GetByLabel('UI/VirtualGoodsStore/Purchase/Failed'), audioEventName='store_purchase_failure', width=self.contWidth)
        self.purchaseFailureReasonLabel = VgsLabelSmall(parent=self.purchaseFailurePanel, align=uiconst.TOTOP, padding=(TEXT_PADDING,
         TEXT_PADDING,
         TEXT_PADDING,
         0))

    def OnBackButtonClicked(self, *args):
        self.purchaseDetailsPanel.ReconstructPanel(animate=True)

    def fade_in_fill(self, opacity = 1.0):
        animations.FadeIn(self.preview_fill, endVal=opacity, duration=0.5)
        self.preview_fill.Enable()
        animations.FadeIn(self.loading_wheel, duration=0.5)

    def fade_out_fill(self):
        self.open_offer_view()
        animations.FadeOut(self.preview_fill, duration=0.5)
        self.preview_fill.Disable()
        animations.FadeOut(self.loading_wheel, duration=0.3)

    def open_offer_view(self):
        self.bottomContainer.SetState(uiconst.UI_NORMAL)
        self.preview.SetState(uiconst.UI_NORMAL)

    def CreateRedeemPanel(self, offer, offerQuantity):
        self.redeemContainer = StaticRedeemContainer(parent=self.purchaseSuccessPanel, name='offerRedeemQueueContent', align=uiconst.TOTOP, padTop=TEXT_PADDING, redeemTokens=GetSortedTokens(offer.productQuantities), offerQuantity=offerQuantity, clipChildren=False, containerWidth=self.contWidth, dragEnabled=False, minimizeTokens=True)
        self.successDescriptionText = VgsLabelSmall(parent=self.purchaseSuccessPanel, align=uiconst.TOTOP, text='', padding=(TEXT_PADDING,
         TEXT_PADDING,
         TEXT_PADDING,
         0))
        self.successDescriptionText.opacity = 0.0

    def CreateFakeRedeemPanel(self):
        instructionText = '<url=localsvc:method=ShowRedeemUI>%s</url>' % (GetByLabel('UI/RedeemWindow/ClickToInitiateRedeeming'),)
        redeemPanelClass = GetOldRedeemPanel()
        self.fakeRedeemingPanel = redeemPanelClass(parent=self.backgroundBottomContainer, name='fakeRedeemPanel', align=uiconst.TOBOTTOM, dragEnabled=False, redeemButtonBackgroundColor=REDEEM_BUTTON_BACKGROUND_COLOR, redeemButtonFillColor=REDEEM_BUTTON_FILL_COLOR, buttonClick=None, instructionText=instructionText)
        self.fakeRedeemingPanel.UpdateDisplay(animate=False)
        self.fakeRedeemingPanel.HidePanel(animate=False)
        self.vgsUiController.view.storeContainer.redeemingPanel.HidePanel()
        self.vgsUiController.view.storeContainer.redeemingPanel.SetListenToRedeemQueueUpdatedEvents(False)

    def OnPreviewType(self, typeID):
        self.preview.typeID = typeID

    def ConstructPaymentElement(self, paymentMethod, currency, price):
        if self.qrCodeCont:
            self.qrCodeCont.CloseByUser(sleep=True)
        self.qrCodeCont = QRCodeContainer(parent=self, align=uiconst.CENTER, width=350, height=450, idx=0, opacity=0.0, paymentMethod=paymentMethod, currency=currency, price=price, offerName=self.offer.name, account=self.kiringApiGateway.name, onClose=self.OnQRCodeContClose)
        self.fade_in_fill(0.7)

    def OnQRCodeContClose(self):
        self.fade_out_fill()

    def OnKiringPaymentInitiated(self, paymentMethod, currency, price, goodsID, quantity, offerID):
        self.ConstructPaymentElement(paymentMethod, currency, price * quantity)
        unixTimestamp = time.time()
        order = KiringOrder(session.charid, goodsID, quantity, unixTimestamp, on_success=lambda : self.OnKiringPaymentSuccessful(offerID), on_failure=self.OnKiringPaymentFailed)
        try:
            paymentAction = self.kiringApiGateway.place_order(order, paymentMethod)
        except Exception as ex:
            self.OnKiringPaymentFailed(GetByLabel('UI/VirtualGoodsStore/Kiring/CannotConnectToPaymentProvider'))
            raise ex

        if paymentAction is None:
            self.OnKiringPaymentFailed(GetByLabel('UI/VirtualGoodsStore/Kiring/CannotConnectToPaymentProvider'))
            logger.error('No payment action returned from server')
        elif paymentAction.actionID == KiringPaymentActionID.OPEN_WEBSITE:
            self.qrCodeCont.OpenPaymentUrl(paymentAction.url)
        elif paymentAction.actionID == KiringPaymentActionID.SCAN_QR_CODE:
            self.qrCodeCont.ShowQrCode(paymentAction.url, self.kiringApiGateway.name)

    def OnKiringPaymentSuccessful(self, offerID):
        self.qrCodeCont.CloseByUser()
        sm.GetService('vgsService').GetStore().ClearCache()
        self.SwitchToSuccessPanel(self.purchaseDetailsPanel.GetQuantity(), session.charid)
        self.vgsUiController.view.storeContainer.OnOfferPurchase(offerID)

    def OnKiringPaymentFailed(self, reason = None):
        self.qrCodeCont.CloseByUser()
        self.SwitchToFailurePanel(reason)

    def OpenFakeRedeemPanel(self):
        self.fakeRedeemingPanel.ExpandPanel(animate=True, showNewItems=False)

    def SwitchToProgressPanel(self):
        self.SwitchToPanel(self.purchaseProgressPanel)

    def SwitchToSuccessPanel(self, offerQuantity, toCharacterID):
        self.CreateRedeemPanel(self.offer, offerQuantity)
        self.backButton.Hide()
        self.SwitchToPanel(self.purchaseSuccessPanel)
        store = sm.GetService('vgsService').GetStore()
        isGametimeOffer = store.IsGametimeOffer(self.offer)
        isItemOffer = store.IsItemOffer(self.offer)
        isPlexOffer = store.IsPlexOffer(self.offer)
        isGemOffer = store.IsGemOffer(self.offer)
        if toCharacterID:
            if isGametimeOffer:
                self.successDescriptionText.SetText('<center>%s</center>' % GetByLabel('UI/VirtualGoodsStore/Purchase/GiftingGametimeSuccess') + '<br/>')
            if isItemOffer:
                self.successDescriptionText.SetText(self.successDescriptionText.GetText() + '<center>%s</center>' % GetByLabel('UI/VirtualGoodsStore/Purchase/GiftingSuccessSubtext'))
            tokens = self.redeemContainer.GetTokens()
            for tokenInfo, token in tokens.iteritems():
                srcToken = self.redeemContainer.PopToken(token)
                srcToken.AnimateOut(timeOffset=0.6)

        else:
            if isGametimeOffer:
                self.successDescriptionText.SetText(self.successDescriptionText.GetText() + '<center>%s</center>' % GetByLabel('UI/VirtualGoodsStore/Purchase/GameTimePurchaseSuccess') + '<br/>')
            if isPlexOffer:
                self.successDescriptionText.SetText(self.successDescriptionText.GetText() + '<center>%s</center>' % GetByLabel('UI/FastCheckout/PLEXPurchaseSuccessSubText') + '<br/>')
            if isGemOffer:
                self.successDescriptionText.SetText(self.successDescriptionText.GetText() + '<center>%s</center>' % GetByLabel('UI/VirtualGoodsStore/Purchase/GemPurchaseSuccess') + '<br/>')
            if isItemOffer:
                self.successDescriptionText.SetText(self.successDescriptionText.GetText() + '<center>%s</center>' % GetByLabel('UI/VirtualGoodsStore/Purchase/NewPurchaseInstruction') + '<br/>')
                self.OpenFakeRedeemPanel()
                self.fakeRedeemingPanel.AddRedeemContainerContent(self.redeemContainer)
        uicore.animations.MoveOutTop(self.redeemContainer, amount=self.redeemContainer.height, timeOffset=1.0, sleep=True, callback=self.redeemContainer.Close)
        uicore.animations.FadeIn(self.successDescriptionText, duration=1.0, sleep=True)
        self.fakeRedeemingPanel.HidePanel(animate=True)
        self.continueButton.SetState(uiconst.UI_NORMAL)
        animations.FadeIn(self.continueButton)

    def SwitchToFailurePanel(self, reason = None):
        text = reason or GetByLabel('UI/VirtualGoodsStore/Purchase/FailureReasonUnknown')
        self._SetPurchaseFailureReasonText(text)
        self.backButton.Hide()
        self.SwitchToPanel(self.purchaseFailurePanel)

    def _SetPurchaseFailureReasonText(self, text):
        self.purchaseFailureReasonLabel.text = '<center>%s</center>' % text

    def HasSuccessfullyBoughtItem(self):
        return self.activeBottomPanel == self.purchaseSuccessPanel

    def SwitchToPanel(self, newPanel):
        newPanel.OnPanelActivated()
        uicore.animations.MoveOutLeft(self.activeBottomPanel, self.contWidth, duration=PROGRESS_TRANSITION_TIME)
        self.activeBottomPanel = newPanel
        self.activeBottomPanel.state = uiconst.UI_PICKCHILDREN
        uicore.animations.MoveInFromRight(self.activeBottomPanel, self.contWidth, duration=PROGRESS_TRANSITION_TIME, sleep=True)

    def CloseOffer(self, *args):
        uthread.new(sm.GetService('vgsService').GetUiController().CloseOffer)

    def PrepareClose(self):
        self.preview.PrepareClose()

    def _OnResize(self, *args):
        if not hasattr(self, 'backgroundTopContainer'):
            return
        self.backgroundTopContainer.height = self.parent.GetAbsoluteSize()[1]


class QRCodeContainer(Container):
    default_name = 'QRCodeContainer'
    default_bgColor = HEADER_BG_COLOR

    def ApplyAttributes(self, attributes):
        super(QRCodeContainer, self).ApplyAttributes(attributes)
        currency = attributes.currency
        price = attributes.price
        paymentMethod = attributes.paymentMethod
        self.offerName = attributes.offerName
        self.onClose = attributes.onClose
        Fill(bgParent=self, color=FRAME_COLOR, padding=-FRAME_WIDTH)
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=40, bgColor=Color.GRAY2, opacity=0.7)
        self.bottomCont = Container(name='bottomCont', parent=self, align=uiconst.TOBOTTOM, height=60, bgColor=Color.GRAY2, opacity=0.7)
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.TOALL)
        self.ConstructTopCont()
        self.ConstructMainCont(paymentMethod, price, currency)
        self.ConstructBottomCont()
        self.AnimEntry()

    def ConstructTopCont(self):
        VgsLabelMedium(parent=self.topCont, text=u'\u652f\u4ed8', align=uiconst.CENTER)
        ExitButton(parent=self.topCont, align=uiconst.TOPRIGHT, onClick=self.CloseByUser, left=3, top=3)

    def ConstructMainCont(self, paymentMethod, price, currency):
        PriceTagLarge(name='price_tag', parent=self.mainCont, align=uiconst.CENTERTOP, price=price, currency=currency, top=18)
        self.loadingWheel = LoadingWheel(parent=self.mainCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        ProviderElementClass = get_element_for_payment_provider(paymentMethod)
        ProviderElementClass(parent=self.mainCont, align=uiconst.CENTERBOTTOM, top=10)

    def ConstructBottomCont(self):
        VgsLabelSmall(parent=self.bottomCont, align=uiconst.TOPLEFT, text=self.offerName, left=5, top=8)
        self.accountNameLabel = VgsLabelSmall(parent=self.bottomCont, align=uiconst.BOTTOMLEFT, left=5, top=8, bold=True, fontsize=14)

    def CloseByUser(self, sleep = False):
        self.Disable()
        duration = 0.2
        animations.FadeOut(self, duration=duration, callback=self.Close)
        self.onClose()

    def AnimEntry(self):
        duration = 0.4
        animations.FadeIn(self, duration=duration)
        animations.MorphScalar(self, 'top', self.top + 80, self.top, duration=duration)

    def ShowQrCode(self, url, accountName):
        self.loadingWheel.Hide()
        LazyUrlSprite(parent=self.mainCont, align=uiconst.CENTER, pos=(0, 0, 200, 200), imageUrl=url, spriteBgFill=(1.0, 1.0, 1.0, 1.0))
        self.accountNameLabel.text = accountName

    def OpenPaymentUrl(self, url):
        self.loadingWheel.Hide()
        EveLabelMedium(parent=self.mainCont, align=uiconst.CENTER, text=u'\u8bf7\u5728\u6253\u5f00\u7684\u6d4f\u89c8\u5668\u9875\u9762\u4e2d\u5b8c\u6210\u652f\u4ed8')
        blue.os.ShellExecute(url)
