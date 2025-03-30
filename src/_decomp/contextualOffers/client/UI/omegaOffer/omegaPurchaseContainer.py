#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\UI\omegaOffer\omegaPurchaseContainer.py
from carbonui import uiconst, fontconst
from carbonui.primitives.gradientSprite import GradientSprite
from contextualOffers.client.UI.offerContentContainer import OfferContentContainer
from contextualOffers.client.UI.timeRemaining import TimeRemaining
from contextualOffers.client.UI.offerInfoTooltip import OfferInfoTooltip
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from newFeatures.newFeatureNotifyButton import NewFeatureButton
from clonegrade.const import COLOR_OMEGA_GOLD
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.base import ScaleDpi
from carbonui.uianimations import animations
from carbonui.uicore import uicore
import math
BLINK_DURATION = 8
BLINK_ROTATION = math.pi * 1.08
BLINK_END_POS = (20.0, 0.0)
BLINK_OPACITY = 0.8
END_OPACITY = 1.0
MOVE_AMOUNT = 20
MOVE_DURATION = 0.45
FADE_IN_DURATION = 0.6
FADE_OFFSET_DIFF = 0.15
OFFSET_INCREMENT = 0.14
INITIAL_OFFSET = 0
TOOLTIP_ICON_SIZE = 20
OFFERS_IDS_WITHOUT_GRADIENT = [1, 2]
OFFER_ID_HIDDEN_TIMER_THRESHOLD = 100000

class OmegaPurchaseContainer(OfferContentContainer):
    default_name = 'omegaPurchaseContainer'

    def ApplyAttributes(self, attributes):
        OfferContentContainer.ApplyAttributes(self, attributes)
        self.ConstructLayout()
        self.ConstructText()
        self.ConstructButtons()
        self.ConstructGradient()

    def ConstructLayout(self):
        textLayer = Container(name='textLayer', parent=self, align=uiconst.TOALL)
        self.topCont = Container(name='topRightCont', parent=textLayer, align=uiconst.CENTERTOP, height=25, width=self.width, padding=(20, 20, 20, 0), clipChildren=False, idx=0)
        self.timerCont = Container(name='timerContainer', parent=textLayer, align=uiconst.TOPRIGHT, height=80, width=300, top=20, left=30, opacity=0)
        self.timeRemaining = TimeRemaining(parent=self.timerCont)
        self.priceContainer = Container(name='priceCont', parent=textLayer, padding=(30, 0, 30, 20), height=50, align=uiconst.TOBOTTOM)
        self.descriptionCont = ContainerAutoSize(name='descriptionCont', parent=textLayer, padding=(30, 0, 20, 10), height=int(35 * fontconst.fontSizeFactor), opacity=0, align=uiconst.TOBOTTOM)
        self.titleCont = Container(name='titleCont', parent=textLayer, padding=(30, 0, 20, 0), height=int(40 * fontconst.fontSizeFactor), opacity=0, align=uiconst.TOBOTTOM)
        self.newPriceCont = ContainerAutoSize(name='newPriceCont', parent=self.priceContainer, opacity=0, align=uiconst.TOLEFT)
        self.oldPriceCont = ContainerAutoSize(name='oldPriceCont', parent=self.priceContainer, padding=(10, 0, 0, 0), top=11, opacity=0, align=uiconst.TOLEFT)
        self.discountCont = Container(name='discountCont', parent=self.topCont, align=uiconst.TOPLEFT, left=10, top=10, opacity=0, height=55, width=110)

    def ConstructGradient(self):
        gradientLayer = Container(name='gradientLayer', parent=self, align=uiconst.TOALL)
        gradientContainer = Container(name='gradientContainer', parent=gradientLayer, align=uiconst.TOBOTTOM, height=200)
        self.gradient = GradientSprite(name='gradient', bgParent=gradientContainer, state=uiconst.UI_HIDDEN, rgbData=((0, (0.0, 0.0, 0.0)),), alphaData=((0.0, 0.7), (0.8, 0.4), (1.0, 0.0)), rotation=math.pi / 2)

    def ConstructText(self):
        basic_text_color = (1, 1, 1, 1)
        self.discountBackground = Frame(name='discountBackground', parent=self.discountCont, aling=uiconst.TOALL, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/mask_Window770.png', cornerSize=12, color=(0.74, 0.008, 0.008, 1))
        self.discountFrame = Frame(name='discountFrame', parent=self.discountCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Shared/BracketBorderWindow/frame_Window.png', cornerSize=12, color=(0, 0, 0, 0.5), idx=0)
        self.discountText = Label(name='discountText', parent=self.discountCont, align=uiconst.CENTER, fontsize=32, bold=True, color=basic_text_color, idx=0)
        self.newPriceText = Label(name='newPriceText', parent=self.newPriceCont, fontsize=32, bold=True, color=COLOR_OMEGA_GOLD)
        self.oldPriceText = Label(name='oldPriceText', parent=self.oldPriceCont, fontsize=20, bold=True, color=(0.5, 0.5, 0.5, 1))
        self.strikeThrough = Sprite(name='strikeThrough', parent=self.oldPriceCont, texturePath='res:/UI/Texture/Vgs/strikethrough.png', height=18, top=int(35 * fontconst.fontSizeFactor - 33), color=(0.5, 0.5, 0.5, 0.85))
        self.descriptionText = Label(name='descriptionText', parent=self.descriptionCont, fontsize=20, align=uiconst.TOTOP, color=basic_text_color)
        self.titleText = Label(name='titleText', parent=self.titleCont, fontsize=32, bold=True, align=uiconst.TOLEFT, color=basic_text_color, maxLines=1)
        self.infoIconCont = Container(name='infoIconCont', parent=self.titleCont, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, width=TOOLTIP_ICON_SIZE, opacity=0, top=8)
        self.offerInfoIcon = MoreInfoIcon(name='offerInfoButton', parent=self.infoIconCont, align=uiconst.TOPRIGHT)

    def ConstructButtons(self):
        self.buyButtonCont = Container(name='buyButtonCont', parent=self.priceContainer, align=uiconst.BOTTOMRIGHT, left=10, top=10, height=42, width=150, opacity=0)
        self.buyButton = NewFeatureButton(name='buyButton', parent=self.buyButtonCont, align=uiconst.TOALL, stretchTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180yellow.png', hiliteTexturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180.png', state=uiconst.UI_DISABLED, buttonColor=(1, 1, 1, 1), mouseLeaveColor=(1, 1, 1, 0), hoverColor=(1, 1, 1, 0.15), fillColor=(1, 1, 1, 0.5), onClick=self.OnButtonClick)
        self.blinkSprite = Sprite(parent=self.buyButtonCont, name='blinkSprite', texturePath='res:/UI/Texture/Shared/BracketBorderWindow/button180blink.png', align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=0, idx=0)
        self.buyButtonText = Label(parent=self.buyButtonCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, fontsize=20, bold=True, color=(0, 0, 0, 1), idx=0)

    def SetTitleText(self, title):
        self.titleText.SetText(title)
        availableWidth = ReverseScaleDpi(self.titleCont.displayWidth)
        fullTextWidth = self.titleText.width
        self.titleText.width = min(availableWidth - TOOLTIP_ICON_SIZE, fullTextWidth)

    def LoadOffer(self, offerID, title, description, offerPrice, originalPrice, discount, buttonText, remainingText, tooltipHeader, tooltipDescription):
        if discount:
            self.discountCont.Show()
            self.discountText.SetText(discount)
            self.discountCont.SetSize(ReverseScaleDpi(self.discountText.actualTextWidth) + 32, ReverseScaleDpi(self.discountText.actualTextHeight) + 8)
        else:
            self.discountText.SetText('')
            self.discountCont.Hide()
        if offerID > OFFER_ID_HIDDEN_TIMER_THRESHOLD:
            self.timerCont.Hide()
        else:
            self.timerCont.Show()
            self.timeRemaining.SetRemainingText(remainingText)
        self.SetTitleText(title)
        self.descriptionText.SetText(description)
        if tooltipHeader or tooltipDescription:
            self.offerInfoIcon.Show()
            self.offerInfoIcon.tooltipPanelClassInfo = OfferInfoTooltip(header=tooltipHeader, description=tooltipDescription, wrapWidth=400)
        else:
            self.offerInfoIcon.Hide()
        self.newPriceText.SetText(offerPrice)
        self.oldPriceText.SetText(originalPrice)
        self.strikeThrough.width = self.oldPriceText.width
        if buttonText:
            self.buyButtonCont.Show()
            self.buyButtonText.SetText(buttonText)
        else:
            self.buyButtonText.SetText('')
            self.buyButtonCont.Hide()
        if offerID not in OFFERS_IDS_WITHOUT_GRADIENT:
            self.gradient.Show()

    def OnTimerUpdated(self, time):
        self.timeRemaining.UpdateTimeRemaining(time)

    def AnimateIn(self):
        self.FadeFromLeft()
        self.FadeFromRight()
        self.FadeIn()

    def FadeFromLeft(self):
        fadeFromLeft = [self.titleCont,
         self.descriptionCont,
         self.oldPriceCont,
         self.newPriceCont]
        offset = INITIAL_OFFSET
        for obj in fadeFromLeft:
            animations.FadeIn(obj=obj, endVal=END_OPACITY, duration=FADE_IN_DURATION, timeOffset=offset + FADE_OFFSET_DIFF)
            animations.MoveInFromLeft(obj=obj, amount=MOVE_AMOUNT, duration=MOVE_DURATION, timeOffset=offset)
            offset += OFFSET_INCREMENT

        animations.FadeIn(obj=self.infoIconCont, endVal=END_OPACITY, duration=FADE_IN_DURATION, timeOffset=len(fadeFromLeft) * OFFSET_INCREMENT + INITIAL_OFFSET, callback=self.EnableInfoIcon)

    def FadeFromRight(self):
        animations.FadeIn(obj=self.timerCont, endVal=END_OPACITY, duration=FADE_IN_DURATION, timeOffset=INITIAL_OFFSET + FADE_OFFSET_DIFF)
        animations.MoveInFromLeft(obj=self.timerCont, amount=MOVE_AMOUNT, duration=MOVE_DURATION, timeOffset=INITIAL_OFFSET)

    def FadeIn(self):
        animations.FadeIn(obj=self.buyButtonCont, endVal=END_OPACITY, duration=FADE_IN_DURATION, timeOffset=INITIAL_OFFSET + 0.5 + FADE_OFFSET_DIFF, callback=self.EnableBuyButton)
        animations.FadeIn(obj=self.discountCont, endVal=END_OPACITY, duration=FADE_IN_DURATION, timeOffset=INITIAL_OFFSET + FADE_OFFSET_DIFF)

    def EnableInfoIcon(self):
        self.infoIconCont.SetState(uiconst.UI_NORMAL)

    def EnableBuyButton(self):
        self.buyButton.SetState(uiconst.UI_NORMAL)
        uicore.animations.SpSwoopBlink(obj=self.blinkSprite, loops=uiconst.ANIM_REPEAT, endVal=BLINK_END_POS, rotation=BLINK_ROTATION, duration=BLINK_DURATION)
        self.blinkSprite.opacity = BLINK_OPACITY
