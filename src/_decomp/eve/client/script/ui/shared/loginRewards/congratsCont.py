#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\congratsCont.py
import gametime
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui import uiconst
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold, EveLabelMedium
from eve.client.script.ui.shared.loginRewards.rewardUiConst import GREEN_CHECKMARK, TODAYS_SIDE_PADDING, CAMPAIGN_STATUS_SUCCESSFULLY_COMPLETED
from localization import GetByLabel

class CongratsScreenInEntry(Container):
    default_height = 0
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.innerCont = ContgratsCont(name='innerCont', parent=self, align=uiconst.TOALL, padTop=pConst.CONGRATS_OFFSET)

    def LoadCongratsScreen(self, *args):
        self.innerCont.LoadCongratsElements(self.GetHeaderText, self.GetBodyText)

    def GetHeaderText(self):
        return self.panelController.GetCongratsHeaderText()

    def GetBodyText(self):
        return self.panelController.GetCongratsBodyText()


class TwoTrackCongratsScreen(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.panelController = attributes.panelController
        Sprite(bgParent=self, texturePath='res:/UI/Texture/classes/LoginCampaign/todaysReward_gradient_BG.png', color=(0, 0, 0, 1), padLeft=TODAYS_SIDE_PADDING, padRight=TODAYS_SIDE_PADDING)
        self.innerCont = ContgratsCont(name='innerCont', parent=self, align=uiconst.TOTOP_NOPUSH, top=100, height=150, bgColor=(0.1, 0.1, 0.1, 1.0))

    def LoadCongratsScreen(self):
        self.innerCont.LoadCongratsElements(self.GetHeaderText, self.GetBodyText, True)

    def GetHeaderText(self):
        return self.panelController.GetCongratsHeaderText()

    def GetBodyText(self):
        return self.panelController.GetCongratsBodyText()


class ContgratsCont(Container):

    def LoadCongratsElements(self, headerFunc, textFunc, updateText = True):
        self.updateThread = None
        self.Flush()
        animations.FadeTo(self, 0.0, 1.0, duration=0.5, curveType=uiconst.ANIM_OVERSHOT3, timeOffset=0.2)
        doneIcon = Sprite(name='doneIcon', parent=self, align=uiconst.CENTERTOP, pos=(0, -26, 64, 64), texturePath='res:/ui/Texture/classes/LoginCampaign/claimedCheckNew.png', color=GREEN_CHECKMARK)
        self.gradientCont = Container(name='gradientCont', parent=self, align=uiconst.TOTOP_NOPUSH, height=25, top=-6)
        Sprite(name='headerGradientGlow', parent=self.gradientCont, texturePath='res:/UI/Texture/classes/LoginCampaign/campaignComplete_gradientGlow_2.png', align=uiconst.TOTOP_NOPUSH, height=25, color=GREEN_CHECKMARK)
        Sprite(name='headerGradient', parent=self.gradientCont, texturePath='res:/UI/Texture/classes/LoginCampaign/campaignComplete_gradientGlow_1.png', align=uiconst.TOTOP, top=6, height=13, color=GREEN_CHECKMARK)
        self.headerLabel = EveLabelLargeBold(parent=self, text=GetFormattedText(headerFunc()), align=uiconst.TOTOP, top=40, padding=(10, 0, 10, 0))
        self.textLabel = EveLabelMedium(parent=self, text=GetFormattedText(textFunc()), align=uiconst.TOTOP, top=10, opacity=0.75, padLeft=10, padRight=10)
        lineTexture = 'res:/UI/Texture/classes/LoginCampaign/todaysRewardBracket.png'
        self.todayBracket = StretchSpriteHorizontal(parent=self, align=uiconst.TOBOTTOM_NOPUSH, texturePath=lineTexture, height=12, rightEdgeSize=80, leftEdgeSize=80, opacity=0.1)
        if updateText:
            self.updateThread = AutoTimer(500, self.UpdateText, headerFunc, textFunc)

    def UpdateText(self, headerFunc, textFunc):
        self.headerLabel.text = GetFormattedText(headerFunc())
        self.textLabel.text = GetFormattedText(textFunc())

    def Close(self):
        self.updateThread = None
        Container.Close(self)


def GetFormattedText(text):
    return '<center>%s</center>' % text
