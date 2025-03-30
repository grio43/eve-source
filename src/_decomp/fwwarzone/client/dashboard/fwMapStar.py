#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\fwMapStar.py
import eveformat.client
from carbonui import TextColor, uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_TEXT, FACTION_ID_TO_COLOR, FACTION_ID_TO_FLAT_ICON, SYSTEM_NOT_PART_OF_WARZONE_TEXT
from fwwarzone.client.dashboard.gauges.advantageWidget import AdvantageWidget
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge
from localization import GetByLabel

class FWMapStar(ButtonIcon):

    def ApplyAttributes(self, attributes):
        self.system = attributes.get('system')
        self.systemId = self.system.systemId
        self.warzoneId = attributes.get('warzoneId')
        ButtonIcon.ApplyAttributes(self, attributes)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.system.isNavigationSystem:
            self._ConstructNavigationSystemTooltip(tooltipPanel)
        else:
            self._ConstructWarzoneSystemTooltip(tooltipPanel)

    def _isDefendingFaction(self, factionId, systemId):
        return sm.GetService('fwWarzoneSvc').GetAllOccupationStates()[self.warzoneId][systemId].occupierID == factionId

    def _ConstructNavigationSystemTooltip(self, tooltipPanel):
        solarSystem = cfg.mapSystemCache.get(self.systemId, None)
        if solarSystem:
            factionId = getattr(solarSystem, 'factionID', None)
            secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(self.systemId))
            label = EveLabelLarge(text=u'{} {}'.format(cfg.evelocations.Get(self.systemId).name, secStatusText), bold=True)
            ownerLabel = None
            logo = None
            if factionId:
                ownerLabel = EveLabelLarge(text=cfg.eveowners.Get(factionId).name, opacity=1.0)
                if factionId in FACTION_ID_TO_FLAT_ICON:
                    logo = Sprite(texturePath=FACTION_ID_TO_FLAT_ICON[factionId], align=uiconst.TOPLEFT, width=32, height=32, state=uiconst.UI_DISABLED, color=FACTION_ID_TO_COLOR[factionId])
            infoText = EveLabelLarge(text=SYSTEM_NOT_PART_OF_WARZONE_TEXT)
            infoText.maxWidth = 150
            containerGrid = LayoutGrid(rows=2, columns=1, margin=10, cellSpacing=5)
            topRow = LayoutGrid(columns=2, rows=3, cellSpacing=1, cellPadding=0)
            if factionId:
                topRow.AddCell(logo, rowSpan=2)
            topRow.AddCell(label)
            if factionId:
                topRow.AddCell(ownerLabel)
            bottomRow = LayoutGrid()
            bottomRow.AddCell(infoText)
            containerGrid.AddCell(topRow)
            containerGrid.AddCell(bottomRow)
            tooltipPanel.AddCell(containerGrid)

    def _ConstructWarzoneSystemTooltip(self, tooltipPanel):
        if self.system.occupationState.adjacencyState == -1:
            return
        factionId = self.system.occupationState.occupierID
        attackerFactionID = self.system.occupationState.attackerID
        contestedGaugeTransform = Transform(width=50, height=50)
        secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(self.systemId))
        systemNameLabel = EveLabelLarge(text=u'%s %s' % (cfg.evelocations.Get(self.systemId).name, secStatusText), bold=True)
        victoryPointState = sm.GetService('fwVictoryPointSvc').GetVictoryPointState(self.systemId)
        stateText = GetSystemCaptureStatusText(victoryPointState)
        contestedLabelStatus = EveLabelLarge(text=stateText, bold=True, color=TextColor.HIGHLIGHT)
        occupierLabel = EveLabelLarge(text=cfg.eveowners.Get(factionId).name)
        ContestedFWSystemGauge(parent=contestedGaugeTransform, align=uiconst.TOPLEFT, systemId=self.systemId, radius=25, attackerColor=FACTION_ID_TO_COLOR[attackerFactionID], defenderColor=FACTION_ID_TO_COLOR[factionId], adjacencyState=self.system.occupationState.adjacencyState, animateIn=False)
        informationLabel = EveLabelLarge(text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/thisSystemIsAdjacencyLabel', adjacencyState=ADJACENCY_TO_LABEL_TEXT[self.system.occupationState.adjacencyState]))
        advantageGaugeCont = Transform(height=50, width=200)
        advantageSubheaderLabel = EveLabelLarge(text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel'))
        AdvantageWidget(systemId=self.systemId, name='AdvantageWidget', parent=advantageGaugeCont, align=uiconst.TOTOP, animateIn=False)
        headerLabelGrid = LayoutGrid(rows=3, columns=1, cellPadding=0)
        headerLabelGrid.AddCell(systemNameLabel)
        headerLabelGrid.AddCell(occupierLabel)
        headerLabelGrid.AddCell(contestedLabelStatus)
        headerGrid = LayoutGrid(rows=1, columns=2, cellPadding=5)
        headerGrid.AddCell(contestedGaugeTransform)
        headerGrid.AddCell(headerLabelGrid)
        advantageGrid = LayoutGrid(rows=2, columns=1)
        advantageGrid.AddCell(advantageSubheaderLabel)
        advantageGrid.AddCell(advantageGaugeCont)
        containerGrid = LayoutGrid(rows=3, columns=1, cellPadding=5, margin=10)
        containerGrid.AddCell(headerGrid)
        containerGrid.AddCell(informationLabel)
        containerGrid.AddCell(advantageGrid)
        tooltipPanel.AddCell(containerGrid)

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.systemId)
