#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardPreviewItemEntry.py
import evetypes
import trinity
import uthread2
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD, ROLE_LEGIONEER
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from clonegrade import COLOR_OMEGA_GOLD
from crates import CratesStaticData
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium, EveLabelSmall
from eve.client.script.ui.shared.loginRewards.congratsCont import CongratsScreenInEntry
from eve.client.script.ui.shared.loginRewards.rewardTooltip import LoadTooltipPanelForReward
from eve.client.script.ui.shared.loginRewards.rewardUiConst import TODAYS_SIDE_PADDING, GREEN_CHECKMARK
from eve.client.script.ui.shared.loginRewards.rewardsCrosshair import RewardCrosshair
from eve.client.script.ui.eveColor import WHITE
from eveexceptions import ExceptionEater
from eveservices.menu import GetMenuService
from inventorycommon.const import categoryBlueprint
from localization import GetByLabel
from loginrewards.client.tooltips import OmegaIconToolTip
from loginrewards.common.const import CLAIM_STATE_CLAIMED
from loginrewards.common.rewardUtils import GetTierName, GetTierColor, GetTierFanfareVideoPath, GetCloneStateVideoPath, ShouldShowQty
import blue
from utillib import KeyVal
OVERLAY_ICON_SIZE = 96

class PreviewItemEntry(Container):
    default_name = 'previewItemEntry'
    default_bgColor = (0.1, 0.1, 0.1, 1.0)
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL
    todayBracketOpacity = 0.1

    def ApplyAttributes(self, attributes):
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.default_height = pConst.TODAY_HEIGHT
        self.currentRewardInfo = None
        Container.ApplyAttributes(self, attributes)
        self.congratsCont = CongratsScreenInEntry(name='congratsCont', parent=self, panelController=self.panelController)
        self.rewardCont = Container(name='rewardCont', parent=self)
        self.ConstructRewardCont()
        self.crosshair = RewardCrosshair(parent=self)
        if session.charid:
            self.GetMenu = self.GetMenuFunc

    def ConstructRewardCont(self):
        pConst = self.panelController.GetPanelConstants()
        self.videoCont = Container(name='videoCont', parent=self.rewardCont, padTop=-2, padBottom=-2, clipChildren=True)
        lineTexture = 'res:/UI/Texture/classes/LoginCampaign/todaysRewardBracket.png'
        self.todayBracket = StretchSpriteHorizontal(parent=self.rewardCont, align=uiconst.TOBOTTOM_NOPUSH, texturePath=lineTexture, height=12, rightEdgeSize=80, leftEdgeSize=80, opacity=self.todayBracketOpacity)
        self.fadeCont = Container(name='fadeCont', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE), state=uiconst.UI_DISABLED)
        self.fadeItem = Icon(name='fadeItem', parent=self.fadeCont, align=uiconst.CENTER, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE), state=uiconst.UI_DISABLED)
        self.fanfareVideo = StreamingVideoSprite(parent=self.videoCont, name='fanfareVideo', videoPath='res:/UI/Texture/classes/LoginCampaign/hexagons_09d_greyscale_03.webm', videoLoop=False, align=uiconst.CENTER, state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, spriteEffect=trinity.TR2_SFX_COPY, opacity=0.0, disableAudio=True, pos=(0, 0, 315, 200))
        self.fanfareVideo.Pause()
        self.itemCont = Container(name='itemCont', parent=self.rewardCont, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE), align=uiconst.CENTER)
        self.overlaySprite = Sprite(name='overlaySprite', parent=self.itemCont, align=uiconst.CENTER, pos=(0,
         0,
         OVERLAY_ICON_SIZE,
         OVERLAY_ICON_SIZE))
        self.qtypar = ContainerAutoSize(parent=self.itemCont, name='qtypar', align=uiconst.BOTTOMRIGHT, bgColor=(0, 0, 0, 0.9))
        self.quantityLabel = Label(parent=self.qtypar, maxLines=1, bold=True, fontsize=fontconst.EVE_SMALL_FONTSIZE, opacity=1.0, padding=(4, 1, 4, 0))
        self.itemIcon = Icon(parent=self.itemCont, align=uiconst.CENTER, pos=(0,
         0,
         pConst.ICON_SIZE,
         pConst.ICON_SIZE), state=uiconst.UI_DISABLED)
        self.typeText = EveLabelMedium(name='typeText', parent=self.rewardCont, align=uiconst.TOTOP_NOPUSH, top=self.height + 6, padLeft=TODAYS_SIDE_PADDING + 4, padRight=TODAYS_SIDE_PADDING + 4, color=WHITE)

    def LoadRewardInfo(self, rewardInfo, fullOpacity = True):
        self._LoadRewardInfo(rewardInfo, fullOpacity)
        self.SetVideoPath(rewardInfo)

    def _LoadRewardInfo(self, rewardInfo, fullOpacity = True):
        pConst = self.panelController.GetPanelConstants()
        self.currentRewardInfo = rewardInfo
        if not rewardInfo:
            self.LoadCompletedScreen(fullOpacity)
            return
        qty = rewardInfo.qty
        typeID = rewardInfo.typeID
        texturePath = rewardInfo.texturePath
        overlayTexturePath = rewardInfo.overlayTexturePath
        iconSize = rewardInfo.iconSize or pConst.ICON_SIZE
        self.SetTypeText(rewardInfo)
        if texturePath:
            self.itemIcon.LoadIcon(texturePath)
        else:
            self.itemIcon.LoadIconByTypeID(typeID=typeID, isCopy=True)
        self.itemIcon.SetSize(iconSize, iconSize)
        if overlayTexturePath:
            self.overlaySprite.LoadTexture(overlayTexturePath)
            self.overlaySprite.display = True
        else:
            self.overlaySprite.display = False
        self.qtypar.display = False
        if ShouldShowQty(rewardInfo):
            self.qtypar.display = True
            self.quantityLabel.text = FmtAmt(qty)

    def _GetTierNamePath(self, tier):
        tierNamePath = GetTierName(tier) if tier else None
        return tierNamePath

    def SetTierCont(self, tier, fullOpacity = True):
        color = GetTierColor(tier)
        if color:
            self.tierLineCont.display = True
            self.tierLineCont.SetColor(color)
            if fullOpacity:
                self.tierLineCont.opacity = 1.0
            else:
                self.tierLineCont.opacity = 0.0
        else:
            self.tierLineCont.display = False

    def SetVideoPath(self, rewardInfo):
        with ExceptionEater('SetVideoPath'):
            if rewardInfo:
                videoPath = self.GetVideoPath(rewardInfo.tier)
                self.fanfareVideo.SetVideoPath(videoPath)
                self.fanfareVideo.Pause()

    def GetVideoPath(self, tier):
        return GetTierFanfareVideoPath(tier)

    def LoadNewReward(self, rewardInfo, sleepTimeSec = 2, delayedEndSec = 0, playVideo = True):
        self.FadeOutAndPlayVideo(sleepTimeSec, playVideo)
        if delayedEndSec:
            uthread2.call_after_wallclocktime_delay(self._EndLoadNewReward, delayedEndSec, rewardInfo)
        else:
            self._EndLoadNewReward(rewardInfo)

    def FadeOutAndPlayVideo(self, sleepTimeSec = 2, playVideo = True):
        self.fadeItem.LoadIcon(self.itemIcon.texturePath)
        fadeTimeInSec = 0.3
        elementsToFade = self.GetElementsToFade()
        for eachElement in elementsToFade:
            animations.FadeOut(eachElement, duration=fadeTimeInSec)

        blue.pyos.synchro.SleepWallclock(fadeTimeInSec * 1000)
        timeOffset = 0.6 * sleepTimeSec
        if playVideo:
            self.fanfareVideo.Play()
            animations.FadeIn(self.fanfareVideo, duration=0.1)
            animations.FadeOut(self.fadeCont, duration=fadeTimeInSec, timeOffset=timeOffset)
            blue.pyos.synchro.SleepWallclock(sleepTimeSec * 1000)
        else:
            animations.FadeOut(self.fadeCont, duration=fadeTimeInSec)

    def _EndLoadNewReward(self, rewardInfo):
        if not self or self.destroyed:
            return
        fadeTimeInSec = 0.3
        self._LoadRewardInfo(rewardInfo, False)
        elementsToFade = self.GetElementsToFade()
        for eachElement in elementsToFade:
            endValue = getattr(eachElement, 'fullOpacity', 1.0)
            animations.FadeTo(eachElement, eachElement.opacity, endValue, duration=fadeTimeInSec)

        uthread2.call_after_wallclocktime_delay(self.SetVideoPath, 2, rewardInfo)

    def GetElementsToFade(self):
        elementsToFade = [self.typeText, self.itemCont, self.crosshair]
        return elementsToFade

    def SetTypeText(self, rewardInfo):
        text = self.GetTypeText(rewardInfo)
        self.typeText.text = text

    def GetTypeText(self, rewardInfo):
        rewardName = rewardInfo.GetRewardName()
        qty = rewardInfo.qty
        if ShouldShowQty(rewardInfo):
            text = '<center><b>%s</b></center>' % GetByLabel('UI/LoginRewards/NumType', qty=qty, typeName=rewardName)
        else:
            text = '<center><b>%s</b></center>' % rewardName
        return text

    def GetMenuFunc(self, *args):
        typeID = self.currentRewardInfo.typeID
        pConst = self.panelController.GetPanelConstants()
        if not pConst.CRATES_HAVE_INFO and CratesStaticData().is_crate(typeID):
            if session.role & (ROLE_GML | ROLE_WORLDMOD | ROLE_LEGIONEER):
                return [('GM / WM Extras', ('isDynamic', GetMenuService().GetGMMenu, (None,
                    None,
                    None,
                    None,
                    None,
                    typeID)))]
            return []
        if evetypes.GetCategoryID(typeID) == categoryBlueprint:
            bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=typeID, runsRemaining=self.currentRewardInfo.qty, original=False)
            abstractInfo = KeyVal(fullBlueprintData=bpData)
        else:
            abstractInfo = None
        return GetMenuService().GetMenuFromItemIDTypeID(None, typeID, includeMarketDetails=True, abstractInfo=abstractInfo)

    def LoadCompletedScreen(self, fullOpacity = True):
        if fullOpacity:
            self.rewardCont.Hide()
        else:
            animations.FadeOut(self.rewardCont, duration=0.2, callback=lambda *args: self.rewardCont.Hide())
        self.crosshair.SetSideSpriteDisplay(False)
        self.congratsCont.LoadCongratsScreen()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if not self.currentRewardInfo:
            return
        LoadTooltipPanelForReward(tooltipPanel, self.currentRewardInfo)


class CompactPreviewItemEntry(PreviewItemEntry):
    cloneTexture = ''
    default_padTop = 4
    default_padBottom = 4
    cloneSpriteColor = (1, 1, 1, 0)
    cloneText = ''
    todayBracketOpacity = 0.4

    def ApplyAttributes(self, attributes):
        PreviewItemEntry.ApplyAttributes(self, attributes)
        wOffest = 60
        hOffset = 10
        w = self.absoluteRight - self.absoluteLeft
        wCenter = w / 2
        wLeft = wCenter + wOffest
        h = self.absoluteBottom - self.absoluteTop
        hCenter = h / 2
        hTop = hCenter + hOffset
        self.cloneSprite = Sprite(name='cloneSprite', parent=self.rewardCont, opacity=1.0, align=uiconst.BOTTOMRIGHT, state=uiconst.UI_DISABLED, texturePath=self.cloneTexture, pos=(wLeft,
         hTop,
         30,
         30), color=self.cloneSpriteColor)
        textColor = self.cloneSpriteColor[:3] + (0.8,)
        self.cloneLabel = EveLabelMedium(parent=self.rewardCont, align=uiconst.TOPRIGHT, pos=(wLeft,
         hTop,
         0,
         0), text=self.cloneText, color=textColor)
        self.typeText.Close()
        maxWidth = w - wLeft
        maxHeight = h - hTop
        self.typeText = EveLabelSmall(parent=self.rewardCont, align=uiconst.TOPLEFT, text='', color=textColor, pos=(wLeft,
         hTop,
         maxWidth,
         0))
        self.typeText.SetBottomAlphaFade(maxHeight - 10, 10)
        self.claimedIcon = Sprite(parent=self.rewardCont, align=uiconst.CENTER, pos=(0, 0, 64, 64), texturePath='res:/ui/Texture/classes/LoginCampaign/claimedCheck.png', hint=GetByLabel('UI/LoginRewards/HasBeenClaimed'), color=GREEN_CHECKMARK, idx=0)
        self.claimedIcon.display = False

    def _LoadRewardInfo(self, rewardInfo, fullOpacity = True):
        PreviewItemEntry._LoadRewardInfo(self, rewardInfo, fullOpacity)
        if not rewardInfo:
            return
        rewardName = rewardInfo.GetRewardName()
        self.typeText.text = rewardName

    def GetElementsToFade(self):
        elements = PreviewItemEntry.GetElementsToFade(self)
        elements += [self.cloneSprite, self.cloneLabel]
        return elements


class TwoTrackPreviewItemEntryAlpha(CompactPreviewItemEntry):
    cloneTexture = 'res:/UI/Texture/classes/LoginCampaign/alpha_Icon.png'
    cloneText = GetByLabel('UI/LoginRewards/CloneAlpha')
    cloneSpriteColor = (1, 1, 1, 1)

    def _LoadRewardInfo(self, rewardInfo, fullOpacity = True):
        if rewardInfo and rewardInfo.claimState == CLAIM_STATE_CLAIMED:
            self.claimedIcon.display = True
            self.itemIcon.opacity = 0.5
        else:
            self.claimedIcon.display = False
        CompactPreviewItemEntry._LoadRewardInfo(self, rewardInfo, fullOpacity)
        if not rewardInfo:
            return

    def GetVideoPath(self, *args):
        return GetCloneStateVideoPath(isOmegaEntry=False)


class TwoTrackPreviewItemEntryOmega(CompactPreviewItemEntry):
    cloneTexture = 'res:/UI/Texture/classes/LoginCampaign/omega_Icon.png'
    cloneSpriteColor = COLOR_OMEGA_GOLD
    cloneText = GetByLabel('UI/LoginRewards/CloneOmega')

    def ApplyAttributes(self, attributes):
        CompactPreviewItemEntry.ApplyAttributes(self, attributes)
        self.omegaLockSprite = Sprite(name='omegaLockSprite', parent=self.rewardCont, texturePath='res:/UI/Texture/classes/LoginCampaign/rewardTrack_omegaLocked.png', pos=(0, -8, 24, 24), align=uiconst.CENTERBOTTOM, state=uiconst.UI_NORMAL, idx=0, color=COLOR_OMEGA_GOLD)
        self.omegaLockSprite.tooltipPanelClassInfo = OmegaIconToolTip(sm.GetService('loginCampaignService').open_vgs_to_buy_omega_time_from_DLI)
        self.SetOmegaState()

    def ConstructHatchPattern(self):
        if getattr(self, 'hatchCont', None) is None:
            self.hatchCont = Container(name='hatchCont', parent=self.rewardCont, align=uiconst.TOALL, clipChildren=True, idx=1, bgColor=(0, 0, 0, 0.55))
            color = COLOR_OMEGA_GOLD[:3] + (0.2,)
            hatchPattern = Sprite(name='hatchPattern', parent=self.hatchCont, texturePath='res:/UI/Texture/Classes/LoginCampaign/itemContainer_negation.png', align=uiconst.CENTERBOTTOM, pos=(0, 0, 372, 198), state=uiconst.UI_DISABLED, color=color)

    def LoadRewardInfo(self, rewardInfo, fullOpacity = True):
        CompactPreviewItemEntry.LoadRewardInfo(self, rewardInfo, fullOpacity)
        if not rewardInfo:
            return
        newCrosshairColor = COLOR_OMEGA_GOLD[:3] + (RewardCrosshair.LINE_OPACITY,)
        self.crosshair.SetRGBA(newCrosshairColor)
        newTodayBracketColor = COLOR_OMEGA_GOLD[:3] + (self.todayBracket.opacity,)
        self.todayBracket.SetRGBA(*newTodayBracketColor)
        self.SetOmegaState()

    def SetOmegaState(self):
        if self.panelController.IsOmega():
            self.omegaLockSprite.display = False
            if getattr(self, 'hatchCont', None):
                self.hatchCont.display = False
        else:
            self.omegaLockSprite.display = True
            self.ConstructHatchPattern()
            self.hatchCont.display = True

    def GetVideoPath(self, *args):
        return GetCloneStateVideoPath(isOmegaEntry=True)


class ReminderPreviewItemEntry(CompactPreviewItemEntry):
    cloneSpriteColor = (1, 1, 1, 0)

    def ApplyAttributes(self, attributes):
        CompactPreviewItemEntry.ApplyAttributes(self, attributes)
