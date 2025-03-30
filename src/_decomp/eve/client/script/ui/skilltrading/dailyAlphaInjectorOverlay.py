#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\dailyAlphaInjectorOverlay.py
from carbonui import AxisAlignment, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.utilButtons.marketDetailsButton import ShowMarketDetailsButton
from eve.client.script.ui.shared.vgs.button import BuyButtonAur
from eve.client.script.ui.shared.vgs.const import COLOR_PLEX
from eve.common.script.util.eveFormat import RoundISK
from inventorycommon import const as invconst
from inventorycommon.typeHelpers import GetAveragePrice
import clonegrade
import evetypes
import localization

class DailyAlphaInjectorOverlay(Container):
    default_align = uiconst.TOALL
    default_clipChildren = True
    default_state = uiconst.UI_HIDDEN
    CONTENT_LEFT = 140
    SPLASH_LEFT = -180

    def ApplyAttributes(self, attributes):
        super(DailyAlphaInjectorOverlay, self).ApplyAttributes(attributes)
        self.compactMode = False

    def Display(self, message):
        self.Layout()
        self.Load(message)
        self.Enable()
        self.AnimShow()

    def Layout(self):
        if self.children:
            return
        Frame(bgParent=self, texturePath='res:/UI/Texture/classes/Monetization/vignette.png', cornerSize=150)
        self.splash = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, left=self.SPLASH_LEFT, top=10, texturePath='res:/UI/Texture/classes/skilltrading/AlphaInjectorSplash.png', width=400, height=400)
        self.content = ContainerAutoSize(parent=self, align=uiconst.CENTER, left=self.CONTENT_LEFT, width=340)
        self.messageLabel = eveLabel.EveLabelLargeBold(parent=self.content, align=uiconst.TOTOP, color=COLOR_PLEX)
        eveLabel.EveLabelMedium(parent=self.content, align=uiconst.TOTOP, top=12, text=localization.GetByLabel('UI/SkillTrading/AlphaInjectorOverlayMainMessage', limit=clonegrade.CLONE_STATE_ALPHA_MAX_TRAINING_SP, points=sm.GetService('skills').GetSkillPointAmountFromInjectors(invconst.typeAlphaTrainingInjector, quantity=1)))
        itemCont = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, top=12)
        itemIconCont = ContainerAutoSize(parent=itemCont, align=uiconst.TOLEFT, padding=(0, 8, 0, 8))
        Icon(parent=itemIconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, size=64, typeID=invconst.typeAlphaTrainingInjector)
        Sprite(parent=itemIconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgNormal.png', width=64, height=64)
        eveLabel.EveLabelLargeBold(parent=itemCont, align=uiconst.TOTOP, padding=(8, 8, 24, 0), text=evetypes.GetName(invconst.typeAlphaTrainingInjector))
        infoBtnCont = ContainerAutoSize(parent=itemCont, align=uiconst.TOPRIGHT, top=8)
        InfoIcon(parent=infoBtnCont, align=uiconst.TOPLEFT, typeID=invconst.typeAlphaTrainingInjector)
        ShowMarketDetailsButton(parent=infoBtnCont, align=uiconst.TOPLEFT, left=24, width=16, height=16, typeID=invconst.typeAlphaTrainingInjector)
        self.estimatePriceLabel = eveLabel.EveLabelMedium(parent=itemCont, align=uiconst.TOTOP, padding=(8, 0, 8, 6), color=Color.GRAY5)
        buyButtonCont = FlowContainer(parent=itemCont, align=uiconst.TOTOP, padding=(8, 0, 8, 8), contentSpacing=(8, 0))
        BuyButtonAur(parent=buyButtonCont, align=uiconst.NOALIGN, types=[invconst.typeAlphaTrainingInjector])
        dismissCont = FlowContainer(parent=self.content, align=uiconst.TOTOP, padding=(8, 24, 8, 0), contentAlignment=AxisAlignment.CENTER, contentSpacing=(8, 4))
        Button(parent=dismissCont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/Dismiss'), func=lambda *args: self.Dismiss())

    def Load(self, message):
        self.messageLabel.SetText(message)
        self.UpdateEstimatedPrice()

    def Dismiss(self):
        self.Disable()
        self.AnimHide()

    def UpdateEstimatedPrice(self):
        try:
            tokenAveragePrice = GetAveragePrice(invconst.typeAlphaTrainingInjector)
        except KeyError:
            tokenAveragePrice = None

        if not tokenAveragePrice:
            text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/EstimatedPriceUnknown')
        else:
            amount = RoundISK(tokenAveragePrice)
            text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/EstimatedPrice', amount=amount)
        self.estimatePriceLabel.SetText(text)

    def AnimShow(self):
        self.Show()
        animations.FadeTo(self, duration=0.4)
        if not self.compactMode:
            animations.FadeTo(self.splash, timeOffset=0.3)
        animations.FadeTo(self.content, timeOffset=0.3)

    def AnimHide(self):
        animations.FadeOut(self, duration=0.3, callback=self.Hide)

    def EnterCompactMode(self):
        if self.compactMode:
            return
        self.compactMode = True
        animations.FadeOut(self.splash, duration=0.2)
        animations.MorphScalar(self.splash, 'left', startVal=self.splash.left, endVal=self.SPLASH_LEFT - 60, duration=0.3)
        animations.MorphScalar(self.content, 'left', startVal=self.content.left, endVal=0, duration=0.3)

    def ExitCompactMode(self):
        if not self.compactMode:
            return
        self.compactMode = False
        animations.FadeIn(self.splash, duration=0.2)
        animations.MorphScalar(self.splash, 'left', startVal=self.splash.left, endVal=self.SPLASH_LEFT, duration=0.3)
        animations.MorphScalar(self.content, 'left', startVal=self.content.left, endVal=self.CONTENT_LEFT, duration=0.3)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        if budgetWidth < 640:
            self.EnterCompactMode()
        else:
            self.ExitCompactMode()
        return super(DailyAlphaInjectorOverlay, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
