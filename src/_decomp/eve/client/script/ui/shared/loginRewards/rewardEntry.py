#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardEntry.py
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD, ROLE_LEGIONEER
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from clonegrade import COLOR_OMEGA_GOLD
from crates import CratesStaticData
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from eve.client.script.ui.eveColor import WHITE
from eve.client.script.ui.shared.loginRewards.rewardItem import RewardItem, OmegaRewardItem, TwoTrackRewardItem
from eve.client.script.ui.shared.loginRewards.rewardTooltip import LoadTooltipPanelForReward
from eve.client.script.ui.shared.loginRewards.rewardUiConst import BLUE_TEXT_COLOR, TODAYS_HEADER_FILL_COLOR
from eveservices.menu import GetMenuService
from inventorycommon.const import categoryBlueprint
from localization import GetByLabel
from loginrewards.client.tooltips import OmegaIconToolTip
from loginrewards.common.const import CLAIM_STATE_CLAIMED
from utillib import KeyVal
import mathext
COLOR_ITEM_TODAY_BG = (1.0, 1.0, 1.0, 0.1)
SEC_PER_PIXEL = 0.07

class RewardEntry(Container):
    default_name = 'rewardEntry'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    rewardItemClass = RewardItem

    def ApplyAttributes(self, attributes):
        self.panelController = attributes.panelController
        pConst = self.panelController.GetPanelConstants()
        self.default_height = pConst.ENTRY_HEIGHT
        self.default_width = pConst.ENTRY_WIDTH
        self.isSelected = False
        Container.ApplyAttributes(self, attributes)
        self.rewardInfo = attributes.rewardInfo
        self.entryCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        self.rewardItemCont = self.rewardItemClass(parent=self, align=uiconst.TOTOP, rewardInfo=self.rewardInfo, panelController=self.panelController)
        if session.charid:
            self.GetMenu = self.GetMenuFunc
        self.labelScrollingCont = AddLabel(self, self.panelController, self.rewardInfo)

    def OnMouseEnter(self, *args):
        self.labelScrollingCont.TriggerOnMouseEnterParent()

    def OnMouseExit(self, *args):
        self.labelScrollingCont.TriggerOnMouseExitParent()

    def SetSelectedState(self, isOn, animateTime = 0):
        self.isSelected = isOn
        self.rewardItemCont.SetSelectedState(isOn, animateTime)

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        self.rewardItemCont.UpdateEntryState(entryIdx, selectedIdx, updateKeyVal)

    def GetMenuFunc(self, *args):
        typeID = self.rewardInfo.typeID
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
            bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=typeID, runsRemaining=self.rewardInfo.qty, original=False)
            abstractInfo = KeyVal(fullBlueprintData=bpData)
        else:
            abstractInfo = None
        return GetMenuService().GetMenuFromItemIDTypeID(None, typeID, includeMarketDetails=True, abstractInfo=abstractInfo)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadTooltipPanelForReward(tooltipPanel, self.rewardInfo)


class RewardEntryWithTodayAndNextText(RewardEntry):
    default_padRight = 8

    def ApplyAttributes(self, attributes):
        self._currentTextColor = None
        RewardEntry.ApplyAttributes(self, attributes)
        pConst = self.panelController.GetPanelConstants()
        dayTextCont = Container(name='dayTextCont', parent=self.entryCont, align=uiconst.TOTOP, height=pConst.DAY_TEXT_BANNER_HEIGHT)
        self.todayLabel = EveLabelMedium(parent=dayTextCont, align=uiconst.CENTER, text=GetByLabel('UI/LoginRewards/TodaysGift'), color=BLUE_TEXT_COLOR, padBottom=20)
        self.todayLabel.fullOpacity = 1.0
        self.nextLabel = EveLabelMedium(parent=dayTextCont, align=uiconst.CENTER, text=GetByLabel('UI/LoginRewards/NextGift'), color=BLUE_TEXT_COLOR, padBottom=20)
        self.nextLabel.fullOpacity = 1.0

    def SetSelectedState(self, isOn, animateTime = 0):
        wasSelected = self.isSelected
        if isOn and wasSelected:
            return
        RewardEntry.SetSelectedState(self, isOn, animateTime)
        todayLabelOpacity, nextLabelOpacity = self.GetTodayAndNextLabelOpacity(isOn)
        if animateTime and (isOn or wasSelected):
            animations.FadeTo(self.todayLabel, self.todayLabel.opacity, todayLabelOpacity, duration=animateTime)
            animations.FadeTo(self.nextLabel, self.nextLabel.opacity, nextLabelOpacity, duration=animateTime)
        else:
            self.todayLabel.opacity = todayLabelOpacity
            self.nextLabel.opacity = nextLabelOpacity

    def GetTodayAndNextLabelOpacity(self, isOn):
        if not isOn:
            return (0.0, 0.0)
        elif self.panelController.CanSomethingBeClaimedNow():
            return (self.todayLabel.fullOpacity, 0.0)
        else:
            return (0.0, self.nextLabel.fullOpacity)


class RewardEntryWithDay(RewardEntry):
    default_padRight = 6

    def ApplyAttributes(self, attributes):
        self._currentTextColor = None
        RewardEntry.ApplyAttributes(self, attributes)
        pConst = self.panelController.GetPanelConstants()
        dayTextCont = Container(name='dayTextCont', parent=self.entryCont, align=uiconst.TOTOP, height=pConst.DAY_TEXT_BANNER_HEIGHT, padBottom=4)
        text = self.GetTextForEntry()
        self.dayLabel = EveLabelMedium(parent=dayTextCont, align=uiconst.CENTER, text=text, padBottom=20)
        self.dayLabel.fullOpacity = 1.0

    def GetTextForEntry(self, isOn = False):
        pConst = self.panelController.GetPanelConstants()
        if pConst.SHOW_DAY_NUM:
            return GetByLabel('UI/LoginRewards/DayText', day=self.rewardInfo.day)
        else:
            return GetByLabel('UI/LoginRewards/TodaysGift')

    def GetTextColor(self, isOn):
        opacity = self.dayLabel.fullOpacity
        if isOn:
            textColor = BLUE_TEXT_COLOR
        else:
            textColor = (1, 1, 1)
            if not self.panelController.GetPanelConstants().SHOW_DAY_NUM:
                opacity = 0
            else:
                textColor = (1, 1, 1)
        return textColor[:3] + (opacity,)

    def SetSelectedState(self, isOn, animateTime = 0):
        wasSelected = self.isSelected
        if isOn and wasSelected:
            return
        RewardEntry.SetSelectedState(self, isOn, animateTime)
        textColor = self.GetTextColor(isOn)
        if animateTime and (isOn or wasSelected):
            self.SetTextColor(textColor)
        else:
            self.dayLabel.SetTextColor(textColor)

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        RewardEntry.UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal)
        claimedDays = updateKeyVal.claimedDays
        isClaimed = entryIdx in claimedDays
        availableRewardsDays = getattr(updateKeyVal, 'availableRewardsDays', None)
        if isClaimed:
            self.dayLabel.fullOpacity = 0.5
        elif availableRewardsDays is not None:
            itemCanStillBeClaimed = self.rewardInfo.day - 1 in availableRewardsDays
            if not itemCanStillBeClaimed:
                self.dayLabel.SetRGBA(0.5, 0.5, 0.5, 0.5)

    def SetTextColor(self, newColor):
        startValue = self.dayLabel.GetRGB()[:3]
        opacity = newColor[3]
        newColor = newColor[:3]
        animations.MorphVector3(self, 'currentTextColor', startVal=startValue, endVal=newColor, curveType=uiconst.ANIM_SMOOTH, duration=0.5, callback=lambda : self.SetCurrentTextColor(newColor))
        animations.FadeTo(self.dayLabel, self.dayLabel.opacity, opacity, duration=0.5)

    def SetCurrentTextColor(self, newColor):
        self._currentBalance = newColor
        if not self.destroyed:
            newLabelColor = newColor + (self.dayLabel.fullOpacity,)
            self.dayLabel.SetTextColor(newLabelColor)

    def GetCurrentTextColor(self):
        return self._currentTextColor

    currentTextColor = property(GetCurrentTextColor, SetCurrentTextColor)


class AlphaRewardEntry(RewardEntry):
    default_padRight = 4
    rewardItemClass = TwoTrackRewardItem


class OmegaRewardEntry(RewardEntry):
    default_padRight = 4
    default_name = 'omgaRewardEntry'
    rewardItemClass = OmegaRewardItem

    def ApplyAttributes(self, attributes):
        RewardEntry.ApplyAttributes(self, attributes)
        pConst = self.panelController.GetPanelConstants()
        self.omegaLockSprite = Sprite(name='omegaLockSprite', parent=self, texturePath='res:/UI/Texture/classes/LoginCampaign/chapter_Locked.png', pos=(0,
         -pConst.DAY_HEIGHT + 24,
         14,
         18), align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL, idx=0, opacity=0.75, color=COLOR_OMEGA_GOLD)
        self.omegaLockSprite.display = False
        self.omegaLockSprite.tooltipPanelClassInfo = OmegaIconToolTip(sm.GetService('loginCampaignService').open_vgs_to_buy_omega_time_from_DLI)

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        self.rewardItemCont.UpdateEntryState(entryIdx, selectedIdx, updateKeyVal)
        availableRewardsDays = updateKeyVal.availableRewardsDays
        itemCanStillBeClaimed = entryIdx in availableRewardsDays
        pastReward = entryIdx < selectedIdx
        self.SetOmegaState(itemCanStillBeClaimed, pastReward)

    def SetOmegaState(self, itemCanStillBeClaimed, pastReward):
        isClaimed = self.rewardInfo.claimState == CLAIM_STATE_CLAIMED
        if self.panelController.IsOmega() or isClaimed:
            self.omegaLockSprite.display = False
            return
        if not itemCanStillBeClaimed and not pastReward:
            self.omegaLockSprite.display = False
        else:
            self.omegaLockSprite.display = True


class DayEntry(Container):
    default_height = 30
    default_width = 98
    default_padRight = 4
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        self._currentTextColor = None
        self.isSelected = False
        Container.ApplyAttributes(self, attributes)
        self.rewardInfo = attributes.rewardInfo
        text = self.GetTextForEntry()
        self.dayLabel = EveLabelMedium(parent=self, align=uiconst.CENTER, text=text)
        self.dayLabel.fullOpacity = 1.0

    def GetTextForEntry(self, isOn = False):
        return GetByLabel('UI/LoginRewards/DayText', day=self.rewardInfo.day)

    def GetTextColor(self, isOn):
        opacity = self.dayLabel.fullOpacity
        if isOn:
            textColor = BLUE_TEXT_COLOR
        else:
            textColor = (1, 1, 1)
        return textColor[:3] + (opacity,)

    def SetDaySelectedState(self, isOn, animateTime = 0):
        wasSelected = self.isSelected
        if isOn and wasSelected:
            return
        textColor = self.GetTextColor(isOn)
        if animateTime and (isOn or wasSelected):
            self.SetTextColor(textColor)
        else:
            self.dayLabel.SetTextColor(textColor)

    def SetTextColor(self, newColor):
        startValue = self.dayLabel.GetRGB()[:3]
        opacity = newColor[3]
        newColor = newColor[:3]
        animations.MorphVector3(self, 'currentTextColor', startVal=startValue, endVal=newColor, curveType=uiconst.ANIM_SMOOTH, duration=0.5, callback=lambda : self.SetCurrentTextColor(newColor))
        animations.FadeTo(self.dayLabel, self.dayLabel.opacity, opacity, duration=0.5)

    def SetCurrentTextColor(self, newColor):
        self._currentBalance = newColor
        if not self.destroyed:
            newLabelColor = newColor + (self.dayLabel.fullOpacity,)
            self.dayLabel.SetTextColor(newLabelColor)

    def GetCurrentTextColor(self):
        return self._currentTextColor

    currentTextColor = property(GetCurrentTextColor, SetCurrentTextColor)

    def UpdateEntryState(self, entryIdx, selectedIdx, updateKeyVal):
        claimedDays = updateKeyVal.claimedDays
        isClaimed = entryIdx in claimedDays
        if isClaimed:
            self.dayLabel.fullOpacity = 0.5


def AddLabel(parent, panelController, rewardInfo):
    labelCont = Container(name='labelCont', parent=parent, align=uiconst.TOALL, clipChildren=True, padding=(2, 4, 2, 4))
    return LabelScrollingCont(parent=labelCont, rewardInfo=rewardInfo, panelController=panelController, align=uiconst.TOTOP_NOPUSH, height=45)


class LabelScrollingCont(Container):
    default_state = uiconst.UI_DISABLED
    fadeHeight = 10

    def ApplyAttributes(self, attributes):
        self._currentFade = None
        Container.ApplyAttributes(self, attributes)
        rewardInfo = attributes.rewardInfo
        panelController = attributes.panelController
        pConst = panelController.GetPanelConstants()
        text = '<center>%s</center>' % rewardInfo.GetRewardName()
        w, h = EveLabelSmall.MeasureTextSize(text, width=pConst.ENTRY_WIDTH)
        self.label = EveLabelSmall(parent=self, align=uiconst.TOTOP_NOPUSH, text=text, width=pConst.ENTRY_WIDTH, color=WHITE)
        self.label.SetBottomAlphaFade(self.height, maxFadeHeight=self.fadeHeight)

    def TriggerOnMouseEnterParent(self, *args):
        diff = self.label.textheight - self.height
        if diff <= 2:
            return
        duration = mathext.clamp(SEC_PER_PIXEL * diff, 0, 2.0)
        animations.MorphScalar(self.label, 'padTop', self.label.padTop, -diff, duration=duration)
        fadeEndValue = (self.label.textheight, self.fadeHeight)
        self.label.SetBottomAlphaFade(*fadeEndValue)

    def TriggerOnMouseExitParent(self, *args):
        self.label.StopAnimations()
        self.label.padTop = 0
        self.label.SetBottomAlphaFade(self.height, self.fadeHeight)
