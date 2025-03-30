#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsBar.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control import tooltips
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FillThemeColored, SpriteThemeColored
from eve.client.script.ui.shared.info import infoConst
from eve.client.script.ui.shared.standings import standingsUIUtil, standingUIConst
from eve.client.script.ui.shared.standings.standingData import StandingData
from eve.client.script.ui.shared.standings.standingUIConst import THRESHOLD_ATTACKEDINSPACE
from eve.client.script.ui.shared.standings.standingsUIUtil import GetStandingColor, GetStationServiceRestrictionsForThreshold
from eve.client.script.ui.station.agents import agentUtil
from eve.client.script.ui.station.agents.agentUtil import GetAgentDerivedStanding, GetNPCCorpDerivedStanding
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.lib.appConst import factionTriglavian, factionEDENCOM
from eve.common.script.sys import idCheckers
from eve.common.script.util.standingUtil import OpenStandingsPanelOnOwnerByID
from localization import GetByLabel
from utillib import KeyVal
OPACITY_BAR = 0.5
OPACITY_ARROWSPRITE = 0.3
ICONSIZE_THRESHOLD = 32
PADDING_THRESHOLD_ICON = 2
OPACITY_ICON_ENABLED = 1.0
OPACITY_ICON_DISABLED = 0.2

class StandingsBar(Container):
    default_name = 'StandingBar'
    default_state = uiconst.UI_NORMAL
    default_hasTopThresholdIcons = True
    default_hasBottomLabels = True
    default_hasBarAnimation = True
    default_barHeight = 20

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.hasTopThresholdIcons = attributes.get('hasTopThresholdIcons', self.default_hasTopThresholdIcons)
        self.hasBottomLabels = attributes.get('hasBottomLabels', self.default_hasBottomLabels)
        self.hasBarAnimation = attributes.get('hasBarAnimation', self.default_hasBarAnimation)
        self.barHeight = attributes.get('barHeight', self.default_barHeight)
        self.thresholdIconsByID = {}
        self.hideZeroAxisLabel = False
        self.thresholdIconCont = Container(name='thresholdIconCont', parent=self, padding=(-ICONSIZE_THRESHOLD / 2,
         0,
         -ICONSIZE_THRESHOLD / 2,
         1))
        mainCont = Container(name='mainCont', parent=self)
        self.mainBarCont = Container(name='mainBarCont', parent=mainCont, align=uiconst.TOTOP, top=self.barHeight + 6, height=self.barHeight)
        self.barCont = Container(name='barCont', parent=self.mainBarCont)
        self.barBGCont = Container(name='bgCont', parent=self.mainBarCont)
        self.axisLabelCont = Container(name='axisLabelCont', parent=mainCont, align=uiconst.TOTOP, height=12, padTop=1, opacity=1.0 if self.hasBottomLabels else 0.0)
        self.ConstructBar()
        self.ConstructBarSecondary()
        self.ConstructBarIncrease()
        self.ConstructBackground()
        self.ConstructAxisLabels()

    def ConstructBackground(self):
        FillThemeColored(bgParent=self.barBGCont, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.9)
        opacity = 0.15
        SpriteThemeColored(name='bgArrowSprite', parent=self.barBGCont, align=uiconst.TOLEFT_PROP, colorType=uiconst.COLORTYPE_UIBASE, width=0.5, texturePath='res:/UI/Texture/Classes/Standings/barArrowBG.png', opacity=opacity, tileX=True)
        SpriteThemeColored(name='bgArrowSprite', parent=self.barBGCont, align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIBASE, texturePath='res:/UI/Texture/Classes/Standings/barArrowBG.png', opacity=opacity, tileX=True, rotation=math.pi)

    def ConstructAxisLabels(self):
        opacity = 0.6
        EveLabelSmall(parent=self.axisLabelCont, text='-10.0', align=uiconst.TOPLEFT, opacity=opacity)
        self.zeroAxisLabel = EveLabelSmall(parent=self.axisLabelCont, text='0.0', align=uiconst.CENTERTOP, opacity=opacity)
        EveLabelSmall(parent=self.axisLabelCont, text='10.0', align=uiconst.TOPRIGHT, opacity=opacity)

    def ConstructBar(self):
        self.bar = Container(name='bar', parent=self.barCont, align=uiconst.TOLEFT_PROP, state=uiconst.UI_NORMAL, width=0.0, left=0.5, clipChildren=True)
        self.bar.OnClick = self.OnBarClick
        self.arrowSprite = Sprite(name='arrowSprite', bgParent=self.bar, texturePath='res:/UI/Texture/Classes/Standings/arrows_20.png', opacity=0.2, tileX=True)
        self.barFill = Fill(name='barFill', bgParent=self.bar, opacity=0.7)

    def OnBarClick(self):
        OpenStandingsPanelOnOwnerByID(self.standingData.GetOwnerID2())

    def SetTooltips(self):
        self.bar.tooltipPanelClassInfo = StandingsBarTooltip(text=self.GetBarHint())
        self.barSecondary.tooltipPanelClassInfo = StandingsBarTooltip(text=self.GetSecondaryBarHint())
        self.barIncrease.tooltipPanelClassInfo = StandingsBarTooltip(text=self.GetIncreaseBarHint())

    def GetBarHint(self):
        if idCheckers.IsCorporation(self.standingData.GetOwnerID1()):
            return GetByLabel('UI/Standings/StandingsBarHintToCorp', owner=self.standingData.GetOwnerID2(), corpName=self.standingData.GetOwner1Name(), standing=round(self.standingData.GetStanding2To1(), 2))
        else:
            return GetByLabel('UI/Standings/StandingsBarHint', owner=self.standingData.GetOwnerID2(), standing=round(self.standingData.GetStanding2To1(), 2))

    def GetSecondaryBarHint(self):
        standing, ownerID = self.GetStandingUsed()
        if idCheckers.IsCorporation(self.standingData.GetOwnerID1()):
            return GetByLabel('UI/Standings/StandingsBarHintToCorp', owner=ownerID, corpName=self.standingData.GetOwner1Name(), standing=round(standing, 2))
        else:
            return GetByLabel('UI/Standings/StandingsBarHint', owner=ownerID, standing=round(standing, 2))

    def ConstructBarSecondary(self):
        self.barSecondary = Container(name='barSecondary', parent=self.barCont, align=uiconst.TOLEFT_PROP, state=uiconst.UI_NORMAL, width=0.0, clipChildren=True)
        self.barSecondary.OnClick = self.OnSecondaryBarClick
        self.arrowSpriteSecondary = Sprite(name='arrowSpriteSecondary', bgParent=self.barSecondary, texturePath='res:/UI/Texture/Classes/Standings/arrows_20.png', opacity=0.2, tileX=True)
        self.barFillSecondary = Fill(name='barFillSecondary', bgParent=self.barSecondary, opacity=0.7)

    def OnSecondaryBarClick(self):
        _, ownerID = self.GetStandingUsed()
        OpenStandingsPanelOnOwnerByID(ownerID)

    def ConstructBarIncrease(self):
        self.barIncrease = Container(name='barIncrease', parent=self.barCont, align=uiconst.TOLEFT_PROP, state=uiconst.UI_NORMAL, width=0.0, left=0.5, clipChildren=True)
        self.arrowSpriteIncrease = Sprite(name='arrowSpriteIncrease', bgParent=self.barIncrease, texturePath='res:/UI/Texture/Classes/Standings/arrows_20.png', opacity=0.2, tileX=True)
        self.barFillIncrease = Fill(name='barFillIncrease', bgParent=self.barIncrease, opacity=0.7)

    def GetIncreaseBarHint(self):
        standing, ownerID = self.GetStandingUsed()
        standingsIncrease = self.GetStandingIncrease()
        increment = standingsIncrease - standing
        return GetByLabel('UI/Common/StandingsGain', standing=round(increment, 2))

    def UpdateThresholdIcons(self):
        fromID = self.standingData.GetOwnerID2()
        thresholdIDs = standingsUIUtil.GetStandingThresholdIDs(fromID=fromID, toID=self.standingData.GetOwnerID1())
        self._HideThresholdIconsNotPresent(thresholdIDs)
        self.iconsByStandingValue = {}
        self.hideZeroAxisLabel = False
        for thresholdTypeID, thresholdValueID in thresholdIDs:
            self._UpdateThresholdIcon(fromID, thresholdValueID, thresholdTypeID)

        if self.hideZeroAxisLabel:
            self.zeroAxisLabel.state = uiconst.UI_HIDDEN
        else:
            self.zeroAxisLabel.state = uiconst.UI_DISABLED

    def _UpdateThresholdIcon(self, fromID, thresholdValueID, thresholdTypeID):
        icon = self.GetThresholdIcon(thresholdTypeID, thresholdValueID)
        standingThreshold = self.GetThresholdValue(fromID, thresholdTypeID, thresholdValueID)
        isDuplicate = standingThreshold in self.iconsByStandingValue
        if isDuplicate and standingThreshold == 0:
            self.hideZeroAxisLabel = True
        self.iconsByStandingValue[standingThreshold] = icon
        if icon.standingThreshold != standingThreshold:
            self.AnimateThresholdIconPosition(icon, standingThreshold)
        func = self.GetFunctionByThresholdID(thresholdTypeID, fromID, thresholdValueID)
        standing, _ = self.GetStandingUsed()
        icon.Update(standing=standing, ownerID=fromID, standingThreshold=standingThreshold, func=func, isDuplicate=isDuplicate)

    def GetThresholdValue(self, fromID, thresholdTypeID, thresholdValueID):
        if idCheckers.IsNPCCharacter(fromID) and thresholdTypeID == standingUIConst.THRESHOLD_AGENTOFFERSMISSIONS:
            return self._GetThresholdValueForAgent(fromID)
        elif thresholdTypeID == standingUIConst.THRESHOLD_EPICARCUNLOCK:
            thresholdValue = self._GetThresholdValueForAgent(thresholdValueID)
            return max(thresholdValue, 0.0)
        elif thresholdTypeID == THRESHOLD_ATTACKEDINSPACE and fromID in (factionTriglavian, factionEDENCOM):
            return 0.0
        elif thresholdTypeID in (standingUIConst.THRESHOLD_STATIONSERVICE, standingUIConst.THRESHOLD_STATIONSERVICE_CORPORATION):
            return thresholdValueID
        else:
            return standingUIConst.THRESHOLD_VALUES_BY_THRESHOLDTYPE.get(thresholdTypeID)

    def _GetThresholdValueForAgent(self, agentID):
        agent = sm.GetService('agents').GetAgentByID(agentID)
        return agentUtil.GetAgentStandingThreshold(agent.level)

    def _HideThresholdIconsNotPresent(self, thresholdIDs):
        for thresholdID, icon in self.thresholdIconsByID.iteritems():
            if thresholdID not in thresholdIDs:
                icon.StopAnimations()
                icon.FadeOut()

    def AnimateThresholdIconPosition(self, icon, standingThreshold):
        left = self._GetIconLeftValue(standingThreshold)
        if icon.opacity > 0.1:
            animations.MorphScalar(icon, 'left', icon.left, left, duration=0.6)
        else:
            icon.StopAnimations()
            icon.left = left

    def GetStandingUsed(self):
        ownerID = self.standingData.GetOwnerID2()
        if idCheckers.IsNPCCharacter(ownerID):
            return GetAgentDerivedStanding(ownerID)
        if idCheckers.IsNPCCorporation(ownerID):
            if not standingsUIUtil.IsResourceWarsCorporation(ownerID):
                return GetNPCCorpDerivedStanding(ownerID)
            else:
                return (sm.GetService('standing').GetStandingWithSkillBonus(ownerID, session.charid), ownerID)
        else:
            return (self.standingData.GetStanding2To1(), ownerID)

    def GetStandingIncrease(self):
        return self.standingData.GetStandingIncrease()

    def _ConstructThresholdIcon(self, thresholdID):
        return ThresholdIcon(parent=self.thresholdIconCont, align=uiconst.TOPLEFT_PROP, width=ICONSIZE_THRESHOLD, height=ICONSIZE_THRESHOLD, thresholdID=thresholdID, padTop=-0.1, hasTopThresholdIcons=self.hasTopThresholdIcons, lineHeight=self.barHeight)

    def GetThresholdIcon(self, thresholdTypeID, thresholdValueID):
        thresholdID = (thresholdTypeID, thresholdValueID)
        if thresholdID not in self.thresholdIconsByID:
            icon = self._ConstructThresholdIcon(thresholdID)
            self.thresholdIconsByID[thresholdID] = icon
        return self.thresholdIconsByID[thresholdID]

    def _GetIconLeftValue(self, standingThreshold):
        return (standingThreshold + 10.0) / 20.0

    def GetFunctionByThresholdID(self, thresholdTypeID, fromID, thresholdValueID):
        if thresholdTypeID == standingUIConst.THRESHOLD_ATTACKEDINSPACE:
            return self.OnThresholdAttackedInSpace
        if thresholdTypeID == standingUIConst.THRESHOLD_NOACCESSTOAGENTS:
            return self.OnThresholdNoAccessToAgents
        if thresholdTypeID == standingUIConst.THRESHOLD_EPICARCUNLOCK:
            return lambda : self.OnThresholdEpicArcUnlock(thresholdValueID)
        if thresholdTypeID == standingUIConst.THRESHOLD_FACTIONALWARFARE:
            return self.OnThresholdFactionalWarfare
        if thresholdTypeID == standingUIConst.THRESHOLD_AGENTOFFERSMISSIONS:
            return self.OnThresholdAgentOffersMissions
        if thresholdTypeID == standingUIConst.THRESHOLD_NOACCESSTOAGENT:
            return self.OnThresholdNoAccessToAgent
        if thresholdTypeID in (standingUIConst.THRESHOLD_AGENTSLVL2,
         standingUIConst.THRESHOLD_AGENTSLVL3,
         standingUIConst.THRESHOLD_AGENTSLVL4,
         standingUIConst.THRESHOLD_AGENTSLVL5):
            if idCheckers.IsFaction(fromID):
                return self.OnThresholdFactionAgents
            else:
                return lambda : self.OnThresholdCorpAgents(standingUIConst.AGENT_LEVEL_BY_THRESHOLD_ID[thresholdTypeID])
        elif thresholdTypeID in standingUIConst.THRESHOLDS_RESOURCE_WARS:
            if standingsUIUtil.IsResourceWarsCorporation(fromID):
                return self.OnThresholdResourceWars
        elif thresholdTypeID == standingUIConst.THRESHOLD_STATIONSERVICE:
            return self.OnThresholdStationService

    def OnThresholdNoAccessToAgent(self):
        self._ShowInfoForThisOwner(infoConst.TAB_AGENTINFO)

    def OnThresholdAgentOffersMissions(self):
        self._ShowInfoForThisOwner(infoConst.TAB_AGENTINFO)

    def OnThresholdFactionAgents(self):
        self._ShowInfoForThisOwner(infoConst.TAB_MEMBERS)

    def OnThresholdCorpAgents(self, agentLvl):
        self._ShowInfoForThisOwner(infoConst.TAB_AGENTS, abstractinfo=KeyVal(selectedLevel=agentLvl))

    def OnThresholdFactionalWarfare(self):
        factionID = self.standingData.GetOwnerID2() if session.warfactionid is None else None
        uicore.cmd.OpenMilitia(factionID=factionID)

    def OnThresholdEpicArcUnlock(self, agentID):
        sm.GetService('agents').OpenDialogueWindow(agentID)

    def OnThresholdNoAccessToAgents(self):
        if idCheckers.IsFaction(self.standingData.GetOwnerID2()):
            self._ShowInfoForThisOwner(infoConst.TAB_MEMBEROFCORPS)
        else:
            self._ShowInfoForThisOwner(infoConst.TAB_AGENTS)

    def OnThresholdAttackedInSpace(self):
        self._ShowInfoForThisOwner(infoConst.TAB_SYSTEMS)

    def OnThresholdResourceWars(self):
        self._ShowInfoForThisOwner(infoConst.TAB_STANDINGS)

    def OnThresholdStationService(self):
        self._ShowInfoForThisOwner(infoConst.TAB_STATIONS)

    def _ShowInfoForThisOwner(self, tabID = None, abstractinfo = None):
        sm.GetService('info').ShowInfo(self.standingData.GetOwner2TypeID(), self.standingData.GetOwnerID2(), selectTabType=tabID, abstractinfo=abstractinfo)

    def Update(self, fromID, toID = None):
        if toID is None:
            toID = session.charid
        standing = sm.GetService('standing').GetStanding(fromID, toID)
        self.UpdateWithStandings(fromID, toID, standing)

    def UpdateWithStandings(self, fromID, toID, standing, increase = None):
        self.standingData = StandingData(toID, fromID, standing2to1=standing, standingIncrease=increase)
        self.UpdateThresholdIcons()
        self.Animate()
        self.SetTooltips()

    def Animate(self):
        standing = self.standingData.GetStanding2To1()
        duration = 0.3
        derivedStanding, _ = self.GetStandingUsed()
        self.AnimateBar(duration, standing, derivedStanding)
        if derivedStanding != standing and derivedStanding > 0.0:
            self.barSecondary.Show()
            self.AnimateSecondaryBar(duration, standing, derivedStanding)
        else:
            self.AnimateBarHide(self.barSecondary, duration)
        standingsIncrease = self.GetStandingIncrease()
        if standingsIncrease > standing:
            self.barIncrease.Show()
            self.AnimateIncreaseBar(standing, standingsIncrease, duration)
        else:
            self.AnimateBarHide(self.barIncrease, duration)

    def AnimateBarHide(self, bar, duration):
        if self.hasBarAnimation:
            animations.MorphScalar(bar, 'width', bar.width, 0.0, duration=duration)
        else:
            bar.width = 0.0

    def AnimateSecondaryBar(self, duration, standing, standingSecondary):
        width = self.GetSecondaryBarWidth(standing, standingSecondary)
        color = self.GetSecondaryBarColor(standingSecondary)
        if self.hasBarAnimation:
            animations.MorphScalar(self.barSecondary, 'width', self.barSecondary.width, width, duration=duration)
            animations.FadeTo(self.barSecondary, 1.0, OPACITY_BAR, curveType=uiconst.ANIM_WAVE, duration=duration * 2)
            animations.SpColorMorphTo(self.barFillSecondary, endColor=color[:3], duration=duration)
            animations.FadeTo(self.arrowSpriteSecondary, 0.0, OPACITY_ARROWSPRITE, duration=duration * 2, curveType=uiconst.ANIM_OVERSHOT2, timeOffset=duration / 2.0)
        else:
            self.barSecondary.width = width
            self.barSecondary.opacity = OPACITY_BAR
            self.barFillSecondary.color = color[:3]
            self.arrowSpriteSecondary.opacity = OPACITY_ARROWSPRITE

    def AnimateIncreaseBar(self, standing, standingsIncrease, duration):
        left, width = self.GetIncreaseBarLeftWidth(standing, standingsIncrease)
        color = standingUIConst.COLOR_INCREASE
        self.barIncrease.left = left
        animations.MorphScalar(self.barIncrease, 'width', self.barIncrease.width, width, duration=duration)
        animations.FadeTo(self.barIncrease, 1.0, OPACITY_BAR, curveType=uiconst.ANIM_WAVE, duration=duration * 2)
        animations.SpColorMorphTo(self.barFillIncrease, endColor=color[:3], duration=duration)
        animations.FadeTo(self.arrowSpriteIncrease, 0.0, OPACITY_ARROWSPRITE, duration=duration * 2, curveType=uiconst.ANIM_OVERSHOT2, timeOffset=duration / 2.0)

    def GetSecondaryBarColor(self, standingSecondary):
        return standingsUIUtil.GetStandingColor(standingSecondary)

    def GetBarColor(self, standing, standingSecondary):
        if standingSecondary and standingSecondary > standing:
            return Color.GRAY5
        else:
            return standingsUIUtil.GetStandingColor(standing)

    def GetSecondaryBarWidth(self, standing, standingSecondary):
        if standing < 0.0:
            return (standingSecondary + 10.0) / 40.0
        else:
            return (standingSecondary - standing) / 20.0

    def GetIncreaseBarLeftWidth(self, standing, standingsIncrease):
        left, width = self.GetBarLeftWidth(standing)
        increaseWidth = standingsIncrease / 20.0 if standingsIncrease > 0.05 else 0.0
        return (left, max(0.0, increaseWidth - width))

    def AnimateBar(self, duration, standing, standingSecondary):
        left, width = self.GetBarLeftWidth(standing)
        color = self.GetBarColor(standing, standingSecondary)
        self.arrowSprite.rotation = 0.0 if standing > 0.0 else math.pi
        if self.hasBarAnimation:
            animations.MorphScalar(self.bar, 'width', self.bar.width, width, duration=duration)
            animations.MorphScalar(self.bar, 'left', self.bar.left, left, duration=duration)
            animations.FadeTo(self.bar, 1.0, OPACITY_BAR, curveType=uiconst.ANIM_WAVE, duration=duration * 2)
            animations.SpColorMorphTo(self.barFill, endColor=color[:3], duration=duration)
            animations.FadeTo(self.arrowSprite, 0.0, OPACITY_ARROWSPRITE, duration=duration * 2, curveType=uiconst.ANIM_OVERSHOT4, timeOffset=duration / 2.0)
        else:
            self.bar.width = width
            self.bar.left = left
            self.bar.opacity = OPACITY_BAR
            self.barFill.color = color[:3]
            self.arrowSprite.opacity = OPACITY_ARROWSPRITE

    def GetBarLeftWidth(self, standing):
        width = standing / 20.0
        if width != 0.0:
            width = math.fabs(width)
        else:
            width = 1e-17
        left = 0.5 if standing > 0.0 else 0.5 - width
        return (left, width)


class ThresholdIcon(Container):
    default_name = 'ThresholdIcon'
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_hasTopThresholdIcons = True
    default_lineHeight = 20

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        thresholdID = attributes.thresholdID
        self.thresholdTypeID = thresholdID[0]
        self.hasTopThresholdIcons = attributes.get('hasTopThresholdIcons', self.default_hasTopThresholdIcons)
        self.lineHeight = attributes.get('lineHeight', self.default_lineHeight)
        self.standingThreshold = None
        self.ownerID = None
        self.func = None
        self.texturePath = standingsUIUtil.GetStandingThresholdIcon(thresholdID)
        self.glowSprite = GlowSprite(name='icon', parent=self, align=uiconst.TOALL, texturePath=self.texturePath, iconClass=Sprite)
        if not self.hasTopThresholdIcons:
            self.glowSprite.Hide()
            self.Disable()
        self.lineContainer = Container(name='DashedLineContainer', parent=self, align=uiconst.TOBOTTOM, left=-1, top=-self.lineHeight + 2, height=self.lineHeight)
        self.line = Sprite(name='DashedLine', parent=self.lineContainer, align=uiconst.CENTER, texturePath='res:/UI/Texture/Classes/Standings/thresholdLine.png', width=3, height=self.lineHeight, opacity=0.7, state=uiconst.UI_DISABLED)

    def Update(self, standing, ownerID, standingThreshold = None, func = None, isDuplicate = False):
        if standingThreshold is not None:
            self.standingThreshold = standingThreshold
        self.ownerID = ownerID
        self.func = func
        color, opacity = self.GetColorAndOpacity(standing)
        self.Enable()
        if self.hasTopThresholdIcons or isDuplicate:
            self.glowSprite.OnClick = self.func
            self.glowSprite.tooltipPanelClassInfo = self._BuildTooltip(color)
            animations.SpColorMorphTo(self.glowSprite.icon, endColor=color, duration=0.3)
        else:
            self.lineContainer.OnClick = self.func
            self.lineContainer.tooltipPanelClassInfo = self._BuildTooltip(color)
            self.SetState(uiconst.UI_PICKCHILDREN)
            self.lineContainer.SetState(uiconst.UI_NORMAL)
            self.height = ICONSIZE_THRESHOLD + self.lineHeight - PADDING_THRESHOLD_ICON
            self.lineContainer.top = 13
        animations.FadeTo(self, self.opacity, opacity, duration=0.3)
        if isDuplicate:
            self.top = 45
            self.line.Hide()
        else:
            self.top = 0
            self.line.Show()

    def GetColorAndOpacity(self, standing):
        if self.IsUnlocked(standing):
            opacity = OPACITY_ICON_ENABLED
            color = standingsUIUtil.GetStandingColor(standing)
        else:
            opacity = OPACITY_ICON_DISABLED
            color = Color.WHITE
        return (color, opacity)

    def _BuildTooltip(self, color):
        if self.thresholdTypeID in (standingUIConst.THRESHOLD_STATIONSERVICE, standingUIConst.THRESHOLD_STATIONSERVICE_CORPORATION):
            tooltipClass = ThresholdTooltipStationService
        else:
            tooltipClass = ThresholdTooltip
        return tooltipClass(self.texturePath, self.thresholdTypeID, self.ownerID, self.standingThreshold, color)

    def IsUnlocked(self, standing):
        if self.thresholdTypeID not in standingUIConst.THRESHOLDS_ACTIVATE_AT_LESS_THAN:
            isUnlocked = standing >= self.standingThreshold
        else:
            isUnlocked = standing <= self.standingThreshold
        return isUnlocked

    def FadeOut(self):
        self.Disable()
        opacity = 0.0
        animations.FadeTo(self, self.opacity, opacity, duration=0.3)

    def OnClick(self, *args):
        self.func()


class ThresholdTooltip(TooltipBaseWrapper):

    def __init__(self, iconPath, thresholdTypeID, ownerID, standingThreshold, color):
        super(ThresholdTooltip, self).__init__()
        self.iconPath = iconPath
        self.thresholdTypeID = thresholdTypeID
        self.ownerID = ownerID
        self.standingThreshold = standingThreshold
        self.iconColor = color

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.AddSpriteLabel(texturePath=self.iconPath, label=GetByLabel(standingUIConst.LABELS_BY_THRESHOLDTYPEID[self.thresholdTypeID]), colSpan=2, bold=True, iconColor=self.iconColor)
        self.tooltipPanel.AddSpacer(1, 4, 2)
        self.tooltipPanel.AddLabelMedium(text='<b>%s</b>' % self.standingThreshold, color=GetStandingColor(self.standingThreshold), colSpan=2)
        self.tooltipPanel.AddSpacer(1, 4, 2)
        ownerName = cfg.eveowners.Get(self.ownerID).ownerName
        hint = standingUIConst.HINTS_BY_THRESHOLDTYPEID[self.thresholdTypeID]
        text = GetByLabel(hint, ownerName=ownerName)
        self.tooltipPanel.AddLabelMedium(text=text, colSpan=2, wrapWidth=200)
        return self.tooltipPanel


class ThresholdTooltipStationService(ThresholdTooltip):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric4ColumnTemplate()
        self.tooltipPanel.AddSpriteLabel(texturePath=self.iconPath, label=GetByLabel(standingUIConst.LABELS_BY_THRESHOLDTYPEID[self.thresholdTypeID]), colSpan=4, bold=True, iconColor=self.iconColor)
        self.tooltipPanel.AddSpacer(1, 4, 4)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel(standingUIConst.HINTS_BY_THRESHOLDTYPEID[self.thresholdTypeID]), colSpan=4, wrapWidth=200)
        values = GetStationServiceRestrictionsForThreshold(self.ownerID, self.standingThreshold, self.thresholdTypeID)
        for standingsValue, serviceID in values:
            self.tooltipPanel.AddSpacer(1, 4, 4)
            self.tooltipPanel.AddLabelMedium(text='<b>%s</b>' % standingsValue, color=GetStandingColor(standingsValue), colSpan=1)
            self.tooltipPanel.AddLabelMedium(text=standingsUIUtil.GetStationServiceLabel(serviceID), colSpan=3)

        return self.tooltipPanel


class StandingsBarTooltip(TooltipBaseWrapper):

    def __init__(self, text):
        super(StandingsBarTooltip, self).__init__()
        self.text = text

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = tooltips.TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.AddLabelMedium(text=self.text)
        return self.tooltipPanel
