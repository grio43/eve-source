#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\bottomCont.py
import math
import gametime
import uthread2
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui import uiconst, fontconst
from carbonui.primitives.sprite import Sprite
from clonegrade import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.eveColor import WHITE
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
from localization import GetByLabel
from loginrewards.common.const import CLAIM_STATE_CLAIMABLE

class ClaimButton(Button):

    def OnMouseEnter(self, *args):
        super(ClaimButton, self).OnMouseEnter(*args)
        sm.ScatterEvent('OnClaimRewardBtnHover', True)

    def OnMouseExit(self, *args):
        super(ClaimButton, self).OnMouseExit(*args)
        sm.ScatterEvent('OnClaimRewardBtnHover', False)


class RewardBottomCont(Container):
    default_align = uiconst.TOBOTTOM

    def ApplyAttributes(self, attributes):
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.default_height = pConst.CENTER_BOTTOM_HEIGHT
        Container.ApplyAttributes(self, attributes)
        self.rewardInfo = None
        self.nextRewardTime = None
        self.leftCont = Container(parent=self, align=uiconst.TOLEFT, width=pConst.LEFT_WIDTH)
        buttonCont = Container(parent=self, padLeft=pConst.SECTION_DIVIDER)
        self.claimBtn = ClaimButton(parent=buttonCont, align=uiconst.CENTER, label=GetByLabel('UI/LoginRewards/ClaimButtonText'), func=self.OnClaimBtnClicked)
        self.closeBtn = Button(parent=buttonCont, align=uiconst.CENTER, label=GetByLabel('UI/LoginRewards/CloseText'), func=self.OnCloseClicked)
        self.closeBtn.display = False
        self.closeBtn.GetHint = self.GetCloseBtnHint
        self.closeBtn.GetTooltipPointer = lambda *args: uiconst.POINT_TOP_2

    def OnClaimBtnClicked(self, *args):
        pass

    def OnCloseClicked(self, *args):
        self.CloseWnd()

    def LoadRewardInfo(self, claimState, next_reward_time, withTransition = False):
        self.nextRewardTime = next_reward_time
        if claimState == CLAIM_STATE_CLAIMABLE:
            self.SetBtnClaimable(withTransition)
        else:
            self.SetButtonUnclaimable(withTransition)

    def SetButtonUnclaimable(self, withTransition = False):
        self.claimBtn.display = False
        self.closeBtn.display = True
        if withTransition:
            self.closeBtn.Disable()
            uthread2.call_after_wallclocktime_delay(self.SetButtonUnclaimable, 0.5)
        else:
            self.closeBtn.Enable()

    def SetBtnClaimable(self, withTransition = False):
        self.claimBtn.display = True
        self.closeBtn.display = False

    def GetCloseBtnHint(self):
        pass

    def CloseWnd(self):
        pass


class OneTrackRewardBottomCont(RewardBottomCont):

    def ApplyAttributes(self, attributes):
        self.rewardInfo = None
        self.nextRewardTime = None
        RewardBottomCont.ApplyAttributes(self, attributes)
        if not self.panelController.IsOmega() and not self.panelController.IsRookieCampaign():
            UpgradeBtnCont(parent=self, align=uiconst.CENTERLEFT, left=30, isOmega=self.panelController.IsOmega())
            EveLabelMedium(name='upSellText', parent=self, align=uiconst.CENTERLEFT, left=220, color=WHITE, text=GetByLabel('UI/LoginRewards/EverGreenOmegaUpSell'))

    def OnClaimBtnClicked(self, *args):
        self.panelController.ClaimReward()

    def LoadRewardInfo(self, rewardInfo, next_reward_time, withTransition = False):
        self.rewardInfo = rewardInfo
        claimState = rewardInfo.claimState if rewardInfo else None
        RewardBottomCont.LoadRewardInfo(self, claimState, next_reward_time, withTransition)

    def GetCloseBtnHint(self):
        if self.rewardInfo is None:
            return ''
        if self.rewardInfo and self.rewardInfo.claimState == CLAIM_STATE_CLAIMABLE or not self.nextRewardTime:
            return ''
        now = gametime.GetWallclockTime()
        return GetByLabel('UI/LoginRewards/CloseWindowButtonText', time=self.nextRewardTime - now)

    def CloseWnd(self, *args):
        from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
        wnd = DailyLoginRewardsWnd.GetIfOpen()
        if wnd:
            wnd.CloseByUser()


class TwoTrackRewardBottomCont(RewardBottomCont):
    default_align = uiconst.TOBOTTOM
    default_width = 200

    def ApplyAttributes(self, attributes):
        RewardBottomCont.ApplyAttributes(self, attributes)
        if not self.panelController.IsOmega():
            UpgradeBtnCont(parent=self, align=uiconst.CENTERLEFT, left=30, padTop=20, isOmega=self.panelController.IsOmega())
            EveLabelMedium(name='upSellText', parent=self, align=uiconst.CENTERLEFT, left=220, padTop=20, color=WHITE, text=GetByLabel('UI/LoginRewards/eventOmegaUpSell'))

    def OnClaimBtnClicked(self, *args):
        self.panelController.ClaimReward()

    def CloseWnd(self, *args):
        from eve.client.script.ui.shared.loginRewards.loginRewardsWnd import DailyLoginRewardsWnd
        wnd = DailyLoginRewardsWnd.GetIfOpen()
        if wnd:
            wnd.CloseByUser()


class UpgradeBtnCont(Container):
    default_name = 'upgradeBtnCont'
    default_align = uiconst.TOPLEFT
    default_width = 148
    default_height = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        isOmega = attributes.isOmega
        self.upSellSprite = Sprite(name='upSellSprite', parent=self, align=uiconst.CENTERLEFT, width=33, height=29, texturePath='res:/UI/Texture/Classes/LoginCampaign/upsellBanner_icon.png')
        text = GetByLabel('UI/CloneState/AddOmegaTime') if isOmega else GetByLabel('UI/CloneState/UpgradeToOmega')
        upgradeButton = UpgradeButton(parent=self, align=uiconst.CENTERLEFT, text=text, onClick=sm.GetService('loginCampaignService').open_vgs_to_buy_omega_time_from_DLI, onMouseEnterCallback=self.OmegaShineStart, onMouseExitCallback=self.OmegaShineEnd, fontSize=fontconst.EVE_SMALL_FONTSIZE, upperCase=False, pos=(self.upSellSprite.width - 2,
         0,
         120,
         24), labelColor=COLOR_OMEGA_ORANGE, fillColor=COLOR_OMEGA_ORANGE, stretchTexturePath='res:/UI/Texture/Classes/LoginCampaign/upsellBanner_button.png', hiliteTexturePath='res:/UI/Texture/Classes/LoginCampaign/upsellBanner_buttonRollover.png', textureEdgeSize=8)
        upgradeButton.bg.rotation = math.pi
        upgradeButton.hilite.rotation = math.pi
        upgradeButton.width = max(self.width, upgradeButton.label.textwidth + 35)
        self.width = max(self.width, upgradeButton.width + 28)

    def OmegaShineStart(self):
        self.upSellSprite.opacity = 1.5

    def OmegaShineEnd(self):
        self.upSellSprite.opacity = 1.0
