#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\warzoneInfoSideCont.py
from collections import deque
from evePathfinder.core import IsUnreachableJumpCount
import eveformat
import evelink.client
from carbonui import TextAlign, uiconst, TextColor, Density
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.skillPlan.skillPlanInfoIcon import SkillPlanInfoIcon
from eve.common.script.util.facwarCommon import GetOccupationEnemyFaction
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.collapsingSection import CollapsingSection
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_TEXT, ADVANTAGE_CONTENT_DATA, FACTION_ID_TO_COLOR
from fwwarzone.client.dashboard.gauges.advantageWidget import AdvantageWidget
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge
from fwwarzone.client.dashboard.shipCasterVisualization import _ShipCasterVisualization
from localization import GetByLabel
RESIZE_DURATION = 0.5
FADE_OUT_DURATION = 0.25
FADE_OFFSET = 0.25
NOT_FW_SOLARSYSTEM = -1

class WarzoneInfoSideCont(Container):
    default_name = 'WarzoneInfoSideCont'
    default_align = uiconst.TORIGHT
    default_width = 350

    def ApplyAttributes(self, attributes):
        super(WarzoneInfoSideCont, self).ApplyAttributes(attributes)
        self.fullWidth = self.width
        self.currentSolarsystemID = None
        self.attackerGauge = None
        self.defenderGauge = None
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.fwAdvantageSvc = sm.GetService('fwAdvantageSvc')
        self.isShowing = False
        self.viewingFactionId = attributes.get('viewingFactionId')
        self.contentCont = Container(name='contentCont', parent=self)
        self.hasLoaded = False
        self.interstellarShipCasterFactionFocusSignal = attributes.get('interstellarShipCasterFactionFocusSignal')
        self.sections = {}
        self.lastOpenedSectionNames = deque([])

    def EnsureEnoughSpaceForSectionToExpand(self, section):
        if not section.collapsed:
            return
        totalHeightOfOpenedSections = 0
        for name, eachSection in self.sections.iteritems():
            if not eachSection.collapsed:
                totalHeightOfOpenedSections += eachSection.expandedSectionHeightWithHeader

        heightDifference = self.displayHeight - totalHeightOfOpenedSections - section.expandedSectionHeightWithHeader
        while heightDifference < 0 and len(self.lastOpenedSectionNames) > 0:
            poppedSectionName = self.lastOpenedSectionNames.pop()
            poppedSection = self.sections[poppedSectionName]
            if not poppedSection.collapsed:
                poppedSection.Toggle(callCallback=False)
                heightDifference += poppedSection.expandedSectionHeight

        self.lastOpenedSectionNames.appendleft(section.name)

    def ConstructNotPartOfWarzoneSystem(self, systemId):
        hqSystems = sm.GetService('fwWarzoneSvc').GetAllHQSystems()
        cont = Container(parent=self.selectedSystemCont, align=uiconst.TOALL, padding=(41, 10, 41, 0), opacity=0)
        systemHeaderLineCont = Container(parent=cont, align=uiconst.TOTOP, height=42, padBottom=16)
        if systemId in hqSystems.values():
            solarSystem = cfg.mapSystemCache.get(systemId, None)
            if not solarSystem:
                return
            factionId = getattr(solarSystem, 'factionID', None)
            spriteTransform = Transform(parent=systemHeaderLineCont, width=32, height=32, align=uiconst.TOLEFT, padRight=8)
            Sprite(parent=spriteTransform, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/shipcaster_icon_32.png', useSizeFromTexture=True)
            EveLabelLarge(parent=cont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/FactionHQSystem', factionID=factionId), align=uiconst.TOTOP, padBottom=8)
        secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(systemId))
        EveCaptionLarge(parent=systemHeaderLineCont, align=uiconst.TOLEFT, text=u'{} {}'.format(cfg.evelocations.Get(systemId).name, secStatusText))
        if systemId in hqSystems.values():
            SkillPlanInfoIcon(parent=systemHeaderLineCont, align=uiconst.TOLEFT, top=-4, padLeft=8, hint=GetByLabel('UI/FactionWarfare/frontlinesDashboard/factionShipcasterHereTooltip', factionID=factionId))
        EveLabelLarge(parent=cont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/systemNotPartOfWarzone'), align=uiconst.TOTOP, color=TextColor.SECONDARY)
        animations.FadeIn(cont, duration=0.25)

    def SelectSystem(self, systemId, gateLinks, forceExpanded = False):
        self.selectedSystemCont.Flush()
        if systemId == self.currentSolarsystemID and not forceExpanded:
            self.FadeOut()
            return False
        if self.selecetedSystemSection.collapsed:
            self.selecetedSystemSection.Toggle()
        self.currentSolarsystemID = systemId or NOT_FW_SOLARSYSTEM
        occupationState = sm.GetService('fwWarzoneSvc').GetOccupationState(systemId)
        if occupationState is None:
            self.ConstructNotPartOfWarzoneSystem(systemId)
            return True
        padLeft = 41
        padTop = 0
        headlineCont = Container(parent=self.selectedSystemCont, align=uiconst.TOTOP, height=62, padTop=padTop, padLeft=padLeft)
        adjacencyState = occupationState.adjacencyState
        occupierID = occupationState.occupierID
        attackerID = occupationState.attackerID
        ContestedFWSystemGauge(parent=headlineCont, align=uiconst.TOLEFT, systemId=systemId, radius=25, attackerColor=FACTION_ID_TO_COLOR[attackerID], defenderColor=FACTION_ID_TO_COLOR[occupierID], adjacencyState=adjacencyState)
        secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(systemId))
        systemNameLabel = EveCaptionLarge(parent=Container(parent=headlineCont, align=uiconst.TOLEFT, width=1, padLeft=10), align=uiconst.CENTERLEFT, text=u'{} {}'.format(cfg.evelocations.Get(systemId).name, secStatusText), opacity=0.0, state=uiconst.UI_NORMAL)
        victoryPointsState = sm.GetService('fwVictoryPointSvc').GetVictoryPointState(systemId)
        stateText = GetSystemCaptureStatusText(victoryPointsState)
        EveLabelLarge(padTop=14, padLeft=padLeft, parent=self.selectedSystemCont, align=uiconst.TOTOP, text=cfg.eveowners.Get(occupierID).name + u': {}'.format(stateText))
        EveLabelLarge(parent=self.selectedSystemCont, align=uiconst.TOTOP, padLeft=padLeft, padTop=5, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/jumps', numJumps=self._GetNumJumpsString(systemId)))
        EveLabelMedium(parent=self.selectedSystemCont, align=uiconst.TOTOP, padTop=10, padLeft=padLeft, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/thisSystemIsAdjacencyLabel', adjacencyState=ADJACENCY_TO_LABEL_TEXT[adjacencyState]))
        if gateLinks:
            for gate in gateLinks:
                empireSolarSystemId = gate.empireSolarSystemId
                nonFWSolarSystem = cfg.mapSystemCache.get(empireSolarSystemId, None)
                empireFaction = getattr(nonFWSolarSystem, 'factionID', None)
                if occupierID != empireFaction:
                    continue
                solarSystemName = evelink.location_link(empireSolarSystemId)
                text = GetByLabel('UI/FactionWarfare/frontlinesDashboard/GateLeadsToSystem', solarSystemLink=solarSystemName)
                EveLabelMedium(name='gateLinkLabel', parent=self.selectedSystemCont, align=uiconst.TOTOP, padTop=10, padLeft=padLeft, text=text, state=uiconst.UI_NORMAL)

        advantageTitleCont = Container(parent=self.selectedSystemCont, height=19, align=uiconst.TOTOP, padTop=20, padLeft=padLeft)
        EveLabelLarge(parent=advantageTitleCont, align=uiconst.TOLEFT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel'), bold=True)
        SkillPlanInfoIcon(parent=advantageTitleCont, align=uiconst.TOLEFT, padLeft=5, hint=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/advantageTrackerDescription'))
        systemAdvantageWidget = AdvantageWidget(systemId=systemId, name='AdvantageWidget', parent=self.selectedSystemCont, align=uiconst.TOTOP, padLeft=padLeft, padRight=40)
        animations.FadeIn(systemNameLabel, duration=0.25)
        animations.FadeIn(systemAdvantageWidget, duration=0.25)
        return True

    def LoadPanel(self, fadeIn = True):
        self.contentCont.Flush()
        self.sections = {}
        self.selectedSystemCont = Container(height=295, clipChildren=True)
        self.selecetedSystemSection = CollapsingSection(name='selecetedSystemSection', sectionId=1, parent=self.contentCont, section=self.selectedSystemCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/FactionWarfare/frontlinesDashboard/selectedSystemSectionHeader'), collapsed=False, showDividerLine=False, preToggleCallback=self.EnsureEnoughSpaceForSectionToExpand)
        self.sections[self.selecetedSystemSection.name] = self.selecetedSystemSection
        self.lastOpenedSectionNames.appendleft(self.selecetedSystemSection.name)
        advantageMechanicsCont = Container(height=300, clipChildren=True)
        objectivesSection = CollapsingSection(name='objectivesSection', parent=self.contentCont, section=advantageMechanicsCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/FactionWarfare/frontlinesDashboard/AdvantageObjectivesSectionHeader'), collapsed=True, preToggleCallback=self.EnsureEnoughSpaceForSectionToExpand)
        self.sections[objectivesSection.name] = objectivesSection
        infoTextCont = ContainerAutoSize(parent=self.selectedSystemCont, name='systemInfo', align=uiconst.TOTOP, padLeft=25, padRight=25)
        EveCaptionLarge(parent=infoTextCont, padTop=28, name='systemStateLabel', align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/systemState'), textAlign=TextAlign.CENTER)
        EveLabelLarge(padTop=15, parent=infoTextCont, name='systemStateInstructionLabel', align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/systemStateInstructionLabel'), textAlign=TextAlign.CENTER)
        padLeft = 41
        EveLabelLarge(parent=advantageMechanicsCont, align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageObjectivesTitle'), padLeft=padLeft, padRight=padLeft, padTop=10)
        objectivesDetailsCont = ContainerAutoSize(parent=advantageMechanicsCont, align=uiconst.TOTOP, padding=(padLeft,
         10,
         0,
         0))
        for obj in ADVANTAGE_CONTENT_DATA:
            _ObjectiveRow(parent=objectivesDetailsCont, align=uiconst.TOTOP, iconTexturePath=obj.iconTexturePath, text=obj.text, tooltipText=obj.tooltipText)

        link = evelink.local_service_link(method='OpenFWInfoTab', text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/moreInfo'))
        EveLabelLarge(parent=objectivesDetailsCont, align=uiconst.TOTOP, text=link, padTop=10, state=uiconst.UI_NORMAL)
        self.shipCasterInfoCont = Container(height=160, clipChildren=True)
        shipCasterSection = CollapsingSection(name='shipCasterSection', parent=self.contentCont, section=self.shipCasterInfoCont, align=uiconst.TOTOP, headerText=GetByLabel('UI/FactionWarfare/frontlinesDashboard/shipcasterSectionHeader'), collapsed=False, preToggleCallback=self.EnsureEnoughSpaceForSectionToExpand)
        self.sections[shipCasterSection.name] = shipCasterSection
        self.lastOpenedSectionNames.appendleft(shipCasterSection.name)
        myToggleBtnGroup = ToggleButtonGroup(name='myToggleBtnGroup', parent=self.shipCasterInfoCont, align=uiconst.TOTOP, padding=(30, 10, 30, 0), callback=self.ConstructShipCasterFactionView, density=Density.COMPACT)
        myToggleBtnGroup.height = 24
        myToggleBtnGroup.AddButton(self.viewingFactionId, cfg.eveowners.Get(self.viewingFactionId).name)
        enemyID = GetOccupationEnemyFaction(self.viewingFactionId)
        myToggleBtnGroup.AddButton(enemyID, cfg.eveowners.Get(enemyID).name)
        self.shipCasterCont = ContainerAutoSize(parent=self.shipCasterInfoCont, align=uiconst.TOTOP, padLeft=padLeft)
        myToggleBtnGroup.SelectByID(self.viewingFactionId)
        if fadeIn:
            self.FadeIn()
        return True

    def ConstructShipCasterFactionView(self, factionID, *args):
        self.interstellarShipCasterFactionFocusSignal(factionID)
        self.shipCasterCont.Flush()
        _ShipCasterVisualization(factionID=factionID, parent=self.shipCasterCont, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        landingPads = sm.GetService('shipcaster').GetFactionLandingPads(factionID)
        unlinkedLandingPadsCont = Container(parent=self.shipCasterCont, align=uiconst.TOTOP, height=32)
        disrupted = []
        building = []
        idle = []
        for pad in landingPads:
            if pad.isDisrupted:
                disrupted.append(pad.solarSystemID)
            elif not pad.isBuilt:
                building.append(pad.solarSystemID)
            elif not pad.isLinked and pad.canBeLinked:
                idle.append(pad.solarSystemID)

        if idle or building or disrupted:
            EveLabelLarge(parent=unlinkedLandingPadsCont, align=uiconst.TOLEFT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/otherLandingPadsText'))
        if len(idle) > 0:
            idleSprite = Sprite(parent=unlinkedLandingPadsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/landingpad_32.png', width=32, height=32, top=-5, color=TextColor.NORMAL)
            idleSprite.LoadTooltipPanel = self.GetLoadTooltipFunctionForLandingPadSprite(idle, GetByLabel('UI/FactionWarfare/frontlinesDashboard/idleLandingPadsTooltipHeading'))
        if len(building) > 0:
            buildingLandingPads = Sprite(parent=unlinkedLandingPadsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/landingpad_32.png', width=32, height=32, top=-5, color=TextColor.SECONDARY)
            buildingLandingPads.LoadTooltipPanel = self.GetLoadTooltipFunctionForLandingPadSprite(building, GetByLabel('UI/FactionWarfare/frontlinesDashboard/underConstructionLandingPadsTooltipHeading'))
        if len(disrupted):
            disruptedSprite = Sprite(parent=unlinkedLandingPadsCont, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/landingpad_32.png', width=32, height=32, top=-5, color=eveColor.WARNING_ORANGE)
            disruptedSprite.LoadTooltipPanel = self.GetLoadTooltipFunctionForLandingPadSprite(disrupted, GetByLabel('UI/FactionWarfare/frontlinesDashboard/disruptedLandingPadsTooltipHeading'))

    def GetLoadTooltipFunctionForLandingPadSprite(self, systemIds, title):

        def fun(tooltipPanel, owner):
            tooltipPanel.LoadGeneric1ColumnTemplate()
            tooltipPanel.cellSpacing = 3
            tooltipPanel.AddLabelLarge(text=title)
            for id in systemIds:
                nameText = cfg.evelocations.Get(id).name
                secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(id))
                tooltipPanel.AddLabelMedium(text=u'{} {}'.format(nameText, secStatusText), padding=0)

        return fun

    def _GetNumJumpsString(self, systemID):
        numJumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(systemID)
        if IsUnreachableJumpCount(numJumps):
            return '-'
        else:
            return numJumps

    def FadeIn(self, animate = True):
        self.Show()
        animations.FadeIn(self, duration=RESIZE_DURATION, timeOffset=FADE_OFFSET)
        self.isShowing = True
        if animate:
            animations.MorphScalar(self, 'width', startVal=self.width, endVal=self.fullWidth, duration=RESIZE_DURATION)
        else:
            self.width = self.fullWidth

    def FadeOut(self, animate = True):
        self.currentSolarsystemID = None
        animations.FadeOut(self, duration=FADE_OUT_DURATION)
        self.isShowing = False
        if animate:
            animations.MorphScalar(self, 'width', startVal=self.width, endVal=0, duration=RESIZE_DURATION, callback=self.Hide)
        else:
            self.width = 0


class _ObjectiveRow(Container):
    default_height = 25

    def ApplyAttributes(self, attributes):
        super(_ObjectiveRow, self).ApplyAttributes(attributes)
        self.iconTexturePath = attributes.get('iconTexturePath')
        self.text = attributes.get('text')
        self.tooltipText = attributes.get('tooltipText')
        self.ConstructLayout()

    def ConstructLayout(self):
        Sprite(parent=self, align=uiconst.CENTERLEFT, top=-5, width=16, height=16, texturePath=self.iconTexturePath)
        EveLabelLarge(parent=self, align=uiconst.TOLEFT, padLeft=20, text=self.text)
        SkillPlanInfoIcon(parent=self, align=uiconst.TOLEFT, top=-2, padLeft=5, hint=self.tooltipText)
