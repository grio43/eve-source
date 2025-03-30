#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\overview.py
from carbonui import TextColor, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.util.uix import GetMappedRankBase
from fwwarzone.client.dashboard.collapsingSections import CollapsableSectionsContainer
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR
from localization import GetByLabel

class FWOverviewPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.factionId = attributes.get('factionId')
        self.ConstructLayout()

    def ConstructProgressCont(self, progressionCont):
        factionMilitiaId = sm.StartService('facwar').GetFactionMilitiaCorporation(self.factionId)
        standing = sm.GetService('standing').GetStandingWithSkillBonus(factionMilitiaId, session.charid)
        currentRank = 1
        currRank = sm.GetService('facwar').GetCharacterRankInfo(session.charid)
        if currRank:
            currentRank = currRank.currentRank
        standingFloatingPointPart = standing - int(standing)
        icon = GetMappedRankBase(currentRank, self.factionId, align=uiconst.CENTER)
        rankRowCont = Container(name='rankRowCont', parent=progressionCont, align=uiconst.TOTOP, height=128, width=500, padLeft=50, padRight=50, padTop=10)
        rankCont = Transform(parent=rankRowCont, align=uiconst.TOLEFT, width=128, height=128)
        icon.SetParent(rankCont)
        rankName, rankDescription = sm.GetService('facwar').GetRankLabel(session.warfactionid, currentRank)
        rankDescriptionCont = Container(name='rankDescriptionCont', align=uiconst.TOLEFT, width=300, parent=rankRowCont)
        EveLabelMedium(parent=rankDescriptionCont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/tellRankName', rankName=rankName), align=uiconst.TOTOP)
        descLabel = EveLabelSmall(padTop=5, parent=rankDescriptionCont, text=rankDescription, align=uiconst.TOTOP)
        newHeight = descLabel.actualTextHeight
        if newHeight > rankRowCont.height:
            rankRowCont.height = newHeight
        gaugeRowCont = Container(name='gaugeRowCont', parent=progressionCont, height=100, padTop=10, align=uiconst.TOTOP)
        gaugeCont = ContainerAutoSize(name='gaugeCont', parent=gaugeRowCont, align=uiconst.TOLEFT, height=100)
        standingsGauge = Gauge(name='standingsGauge', parent=gaugeCont, gaugeHeight=20, align=uiconst.TOLEFT, value=standingFloatingPointPart, color=FACTION_ID_TO_COLOR[self.factionId], opacity=0.75, width=500)
        standingsGauge.SetText(GetByLabel('UI/FactionWarfare/frontlinesDashboard/nextRankProgress'))
        standingsGauge.hint = GetByLabel('UI/Standings/StandingsBarHint', owner=self.factionId, standing=round(standing, 1))
        if currentRank < 9:
            standingsGauge.SetSubText(GetByLabel('UI/FactionWarfare/frontlinesDashboard/nextRankAt', standingLevel=int(standing) + 1.0))
            nextRankIcon = GetMappedRankBase(currentRank + 1, self.factionId, align=uiconst.TORIGHT)
            nextRankCont = Transform(parent=gaugeRowCont, align=uiconst.TOLEFT, left=20, top=-25, width=128, height=128)
            nextRankIcon.SetParent(nextRankCont)
            rankName, _ = sm.GetService('facwar').GetRankLabel(session.warfactionid, currentRank + 1)
            nextRankIcon.hint = GetByLabel('UI/FactionWarfare/frontlinesDashboard/nextRankName', rankName=rankName)
            standingsGauge.ShowArrow(1.0)
            EveLabelSmall(parent=standingsGauge, text=int(standing) + 1.0, align=uiconst.BOTTOMRIGHT, top=40, left=-6)
        else:
            standingsGauge.SetSubText(GetByLabel('UI/FactionWarfare/frontlinesDashboard/highestRankReached'))
            standingsGauge.SetValue(1.0)
            standingsGauge.opacity = 0.2

    def ConstructLayout(self):
        rulesCont = ScrollContainer(align=uiconst.TOALL)
        eveLabel.Label(parent=rulesCont, align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/RulesOfEngagementText'))
        progressionCont = ScrollContainer(align=uiconst.TOALL)
        if session.warfactionid:
            self.ConstructProgressCont(progressionCont)
        else:
            EveCaptionLarge(parent=progressionCont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/notEngagedInFW'), align=uiconst.CENTER, color=TextColor.SECONDARY)
        sections = [(progressionCont, GetByLabel('UI/FactionWarfare/frontlinesDashboard/Progression'), False), (rulesCont, GetByLabel('UI/FactionWarfare/frontlinesDashboard/rulesOfEngagement'), True)]
        collapsingSections = CollapsableSectionsContainer(parent=self, padding=80, sections=sections, layoutRoom=0.8)
        collapsingSections.ToggleSectionCollapse(1)
