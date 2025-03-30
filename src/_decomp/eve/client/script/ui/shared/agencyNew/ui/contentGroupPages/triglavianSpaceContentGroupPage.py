#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupPages\triglavianSpaceContentGroupPage.py
from carbonui.control.scrollContainer import ScrollContainer
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsNPCCorporation
from localization import GetByLabel
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.moreIcon import DescriptionIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderLarge
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.shared.standings.standingData import StandingData
from eve.client.script.ui.shared.standings.standingEntries import StandingsEntryOneWay
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards import contentGroupCardConstants
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.horizontalContentGroupCard import HorizontalContentGroupCard
from carbonui.control.section import Section, SectionAutoSize, SubSection
from evestations.standingsrestriction import get_all_station_standings_restrictions, get_station_standings_restriction_label

class TriglavianSpaceContentGroupPage(BaseContentGroupPage):
    default_name = 'TriglavianSpaceContentGroupPage'
    contentGroupID = contentGroupConst.contentGroupTriglavianSpace
    default_alignMode = uiconst.CENTER

    def ConstructLayout(self):
        self.mainCont = Container(name='mainContainer', parent=self, align=uiconst.CENTER, width=agencyUIConst.CONTENT_PAGE_WIDTH, height=agencyUIConst.CONTENT_PAGE_HEIGHT)
        left = Container(name='LeftMainContainer', parent=self.mainCont, align=uiconst.TOLEFT_PROP, width=0.5)
        right = Container(name='RightMainContainer', parent=self.mainCont, align=uiconst.TOALL, left=10)
        self.ConstructLeft(left)
        self.ConstructRight(right)

    def ConstructLeft(self, container):
        stationAccess = Section(name='StationAccessSection', parent=container, align=uiconst.TOBOTTOM, height=260, headerText=GetByLabel('UI/Agency/TriglavianSpace/StationAccessSection'))
        standingsSection = SubSection(parent=stationAccess, align=uiconst.TOBOTTOM, headerText=GetByLabel('UI/InfoWindow/TabNames/Standings'), insidePadding=(6, 10, 6, 10), padRight=36, padTop=12, height=62)
        self.ConstructStandingEntry(standingsSection, session.charid)
        if not IsNPCCorporation(session.corpid):
            standingsSection.height = 96
            self.ConstructStandingEntry(standingsSection, session.corpid, 12)
        DescriptionIcon(parent=stationAccess, align=uiconst.BOTTOMRIGHT, top=standingsSection.height - 45, tooltipPanelClassInfo=StandingsRestrictionTooltip())
        stationAccessScroll = ScrollContainer(name='labelScroll', parent=stationAccess, align=uiconst.TOALL)
        EveLabelMedium(name='StationAccessDescription', parent=stationAccessScroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/StationAccessDescription'))
        overview = Section(name='OverviewSection', parent=container, align=uiconst.TOALL, headerText=GetByLabel('UI/Overview/Overview'))
        scroll = ScrollContainer(name='labelScroll', parent=overview, align=uiconst.TOALL)
        EveLabelMedium(name='OverviewDescription', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/OverviewDescription'), state=uiconst.UI_NORMAL)

    def ConstructStandingEntry(self, container, ownerID, padTop = 0):
        standingData = StandingData(ownerID1=ownerID, ownerID2=appConst.factionTriglavian, standing2to1=sm.GetService('standing').GetStandingWithSkillBonus(appConst.factionTriglavian, ownerID))
        standingEntry = StandingsEntryOneWay(parent=container, align=uiconst.TOTOP, height=22, padTop=padTop, standingData=standingData, commonOwnerID=ownerID, hideName=True)
        OwnerIcon(parent=standingEntry, align=uiconst.CENTERLEFT, iconAlign=uiconst.TOLEFT, ownerID=ownerID, iconSize=28, height=28, width=28)

    def ConstructRight(self, container):
        self.cardsContainer = SectionAutoSize(name='cardsContainer', parent=container, align=uiconst.TOBOTTOM, headerText=GetByLabel('UI/Agency/takeMeTo'))
        travelSection = Section(name='TravelSection', parent=container, align=uiconst.TOALL, headerText=GetByLabel('UI/Agency/TriglavianSpace/TravelSection'))
        scroll = ScrollContainer(parent=travelSection, align=uiconst.TOALL)
        EveHeaderLarge(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/ConduitLoopTitle'))
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/ConduitLoopDescription'))
        EveHeaderLarge(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/WormholesTitle'), padTop=8)
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/WormholesDescription'))
        EveHeaderLarge(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/FilamentsTitle'), padTop=8)
        EveLabelMedium(parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/TriglavianSpace/FilamentsDescription'))

    def _ConstructContentGroupCard(self, contentGroup, index):
        cardContainer = Container(name='cardContainer', parent=self.cardsContainer, align=uiconst.TOTOP, height=contentGroupCardConstants.HORIZONTAL_CARD_HEIGHT, top=10 if index > 0 else 0)
        self.cards.append(HorizontalContentGroupCard(parent=cardContainer, align=uiconst.CENTER, state=uiconst.UI_NORMAL, contentGroup=contentGroup, contentGroupID=self.contentGroupID))


class StandingsRestrictionTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric5ColumnTemplate()
        self.tooltipPanel.margin = 12
        self.tooltipPanel.cellSpacing = 4
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/TriglavianSpace/StationAccessSection'), wrapWidth=300, colSpan=5, padBottom=4, bold=True)
        restrictions = sorted(get_all_station_standings_restrictions(appConst.factionTriglavian).items(), key=lambda x: x[1])
        for serviceID, standingsValue in restrictions:
            self.tooltipPanel.AddLabelMedium(text='{:6.2f}'.format(standingsValue), colSpan=2, padRight=4)
            self.tooltipPanel.AddLabelMedium(text=GetByLabel(get_station_standings_restriction_label(serviceID)), colSpan=3)

        return self.tooltipPanel
