#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardItem.py
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from clonegrade import COLOR_OMEGA_GOLD
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.loginRewards.itemTierCont import ItemTierCont
from eve.client.script.ui.shared.loginRewards.rewardUiConst import GREEN_CHECKMARK
from localization import GetByLabel
from loginrewards.common.const import CLAIM_STATE_CLAIMED, TIER1
from loginrewards.common.rewardUtils import GetTierColor, ShouldShowQty
COLOR_ITEM_CLAIMED_BG = (0.5, 0.5, 0.5, 0.15)
COLOR_ITEM_NOT_CLAIMED_BG = (1.0, 1.0, 1.0, 0.1)
COLOR_ITEM_TODAY_BG = (1.0, 1.0, 1.0, 0.05)
OVERLAY_ICON_SIZE = 96

class RewardItem(Container):
    default_name = 'rewardItem'

    def ApplyAttributes(self, attributes):
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.default_width = pConst.DAY_WIDTH
        self.default_height = pConst.DAY_HEIGHT
        self.selectedFill = None
        Container.ApplyAttributes(self, attributes)
        self.rewardInfo = attributes.rewardInfo
        self.tierLineCont = ItemTierCont(parent=self, top=pConst.DAY_HEIGHT / 4)
        self.bgFrame = Frame(name='smallRewardBracket_bg', bgParent=self, texturePath='res:/UI/Texture/classes/LoginCampaign/smallRewardBracket_bg.png', cornerSize=16)
        self.selectedFrame = Frame(bgParent=self, name='rewardFrame', texturePath='res:/UI/Texture/classes/LoginCampaign/smallRewardBracket_stroke.png', cornerSize=16)
        self.selectedFrame.fullOpacity = self.selectedFrame.opacity
        self.selectedFrame.opacity = 0.0
        self.bgFrame.display = False
        self.claimedIcon = Sprite(name='claimedIcon', parent=self, align=uiconst.CENTER, pos=(0, 0, 64, 64), texturePath='res:/ui/Texture/classes/LoginCampaign/claimedCheckNew.png', hint=GetByLabel('UI/LoginRewards/HasBeenClaimed'), color=GREEN_CHECKMARK)
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE), state=uiconst.UI_DISABLED)
        self.overlaySprite = Sprite(name='overlaySprite', parent=self.iconCont, align=uiconst.CENTER, pos=(0,
         0,
         OVERLAY_ICON_SIZE,
         OVERLAY_ICON_SIZE))
        self.qtypar = ContainerAutoSize(parent=self.iconCont, name='qtypar', align=uiconst.BOTTOMRIGHT, bgColor=(0, 0, 0, 0.9))
        self.quantityLabel = Label(parent=self.qtypar, maxLines=1, bold=True, fontsize=fontconst.EVE_SMALL_FONTSIZE, opacity=1.0, padding=(4, 1, 4, 0))
        self.itemIcon = Icon(parent=self.iconCont, align=uiconst.CENTER, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE))
        self.LoadRewardInfo(self.rewardInfo)

    def ConstructSelectedFill(self):
        if self.selectedFill is None:
            self.selectedFill = Frame(name='selectedFill', bgParent=self, texturePath='res:/UI/Texture/classes/LoginCampaign/smallRewardBracket_bg.png', cornerSize=16, color=COLOR_ITEM_TODAY_BG)
            self.selectedFill.fullOpacity = self.selectedFill.opacity

    def LoadRewardInfo(self, rewardInfo):
        if not rewardInfo:
            return
        self.bgFrame.display = True
        qty = rewardInfo.qty
        tier = rewardInfo.tier
        typeID = rewardInfo.typeID
        texturePath = rewardInfo.texturePath
        overlayTexturePath = rewardInfo.overlayTexturePath
        if tier:
            color = GetTierColor(tier)
            if tier == TIER1:
                self.tierLineCont.display = False
            else:
                self.tierLineCont.display = True
                self.tierLineCont.SetColor(color)
            self.selectedFrame.color = color
        else:
            self.tierLineCont.display = False
        self.ModifyLayout(rewardInfo)
        if texturePath:
            self.itemIcon.LoadIcon(texturePath)
        else:
            self.itemIcon.LoadIconByTypeID(typeID=typeID, isCopy=True)
        if overlayTexturePath:
            self.overlaySprite.LoadTexture(overlayTexturePath)
            self.overlaySprite.display = True
        else:
            self.overlaySprite.display = False
        self.qtypar.display = False
        if ShouldShowQty(rewardInfo):
            self.qtypar.display = True
            self.quantityLabel.text = FmtAmt(qty)

    def ModifyLayout(self, rewardInfo):
        isClaimed = rewardInfo.claimState == CLAIM_STATE_CLAIMED
        self.ModifyClaimedState(isClaimed)

    def ModifyClaimedState(self, isClaimed):
        pConst = self.panelController.GetPanelConstants()
        showAsClaimed = isClaimed and pConst.SHOW_CLAIMED
        if showAsClaimed:
            self.claimedIcon.display = True
            self.bgFrame.SetRGBA(*COLOR_ITEM_CLAIMED_BG)
        else:
            self.claimedIcon.display = False
            self.bgFrame.SetRGBA(*COLOR_ITEM_NOT_CLAIMED_BG)
        self.ModifyFadedState(showAsClaimed)

    def ModifyFadedState(self, isFaded):
        if isFaded:
            self.tierLineCont.SetTierLineOpacity(0.2)
            self.iconCont.opacity = 0.5 if self.itemIcon.spriteEffect == trinity.TR2_SFX_SOFTLIGHT else 0.25
        else:
            self.tierLineCont.SetTierLineOpacity(1.0)
            self.iconCont.opacity = 1.0

    def SetSelectedState(self, isOn, animateTime = 0):
        self.ConstructSelectedFill()
        if self.selectedFill:
            endValue = self.selectedFill.fullOpacity if isOn else 0.0
            if animateTime:
                animations.FadeIn(self.selectedFill, endVal=endValue, duration=animateTime)
                animations.FadeIn(self.selectedFrame, endVal=endValue, duration=animateTime)
            else:
                self.selectedFill.opacity = endValue
                self.selectedFrame.opacity = endValue
        if self.selectedFrame:
            self.tierLineCont.display = self.rewardInfo.tier != TIER1 or isOn
            endValue = self.selectedFrame.fullOpacity if isOn else 0.0
            if animateTime:
                animations.FadeIn(self.selectedFrame, endVal=endValue, duration=animateTime)
            else:
                self.selectedFrame.opacity = endValue

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        claimedDays = updateKeyVal.claimedDays
        isClaimed = entryIdx in claimedDays
        self.ModifyClaimedState(isClaimed)


class TwoTrackRewardItem(RewardItem):

    def ModifyLayout(self, rewardInfo):
        return RewardItem.ModifyLayout(self, rewardInfo)

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        RewardItem.UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal)
        claimedDays = updateKeyVal.claimedDays
        isClaimed = entryIdx in claimedDays
        if isClaimed:
            return
        availableRewardsDays = updateKeyVal.availableRewardsDays
        itemCanStillBeClaimed = entryIdx in availableRewardsDays
        if not itemCanStillBeClaimed and entryIdx > selectedIdx:
            SetSaturation(self.iconCont, self.itemIcon, 0.0)
        if self.IsOmegaRestricted():
            self.ModifyFadedState(True)

    def IsOmegaRestricted(self):
        return False


class OmegaRewardItem(TwoTrackRewardItem):

    def ModifyLayout(self, rewardInfo):
        isClaimed = rewardInfo.claimState == CLAIM_STATE_CLAIMED
        self.SetOmegaState(isClaimed)
        return TwoTrackRewardItem.ModifyLayout(self, rewardInfo)

    def LoadRewardInfo(self, rewardInfo):
        if not rewardInfo:
            return
        TwoTrackRewardItem.LoadRewardInfo(self, rewardInfo)
        isClaimed = rewardInfo.claimState == CLAIM_STATE_CLAIMED
        self.SetOmegaState(isClaimed)

    def SetOmegaState(self, isClaimed):
        if isClaimed:
            return
        if self.panelController.IsOmega():
            newFrameColor = COLOR_OMEGA_GOLD[:3] + (0.45,)
            self.bgFrame.SetRGBA(*newFrameColor)
        else:
            self.bgFrame.SetRGBA(*COLOR_ITEM_NOT_CLAIMED_BG)

    def IsOmegaRestricted(self):
        return not self.panelController.IsOmega()

    def ModifyClaimedState(self, isClaimed):
        TwoTrackRewardItem.ModifyClaimedState(self, isClaimed)
        self.SetOmegaState(isClaimed)


def SetSaturation(cont, sprite, saturation = 1.0):
    if saturation < 1.0:
        sprite.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
        cont.opacity = 0.5
    else:
        sprite.spriteEffect = trinity.TR2_SFX_COPY
    sprite.saturation = saturation
