#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\gauges\contestedGauge.py
import eveformat
from carbonui import TextColor, uiconst
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.graphs import GraphSegmentParams
from eve.client.script.ui.graphs.circulargraph import CircularGraph
from eveui import Sprite
from factionwarfare.client.text import GetSystemCaptureStatusText
from fwwarzone.client.dashboard.const import ADJACENCY_STATE_TO_ICON_PATH_SMALL, ADJACENCY_TO_DESC, ADJACENCY_TO_LABEL_SYSTEM_TEXT, BLUE_COLOR, RED_COLOR

class ContestedFWSystemGauge(Transform):
    default_radius = 30
    default_lineWidth = 3.5
    default_defenderColor = RED_COLOR
    default_attackerColor = BLUE_COLOR
    default_animateIn = True
    default_displayAdjacencyIcon = True
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ContestedFWSystemGauge, self).ApplyAttributes(attributes)
        self.adjacencySprite = None
        self.systemId = attributes.get('systemId')
        self.fwSvc = sm.GetService('facwar')
        self.radius = attributes.get('radius', self.default_radius)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.adjacencyState = attributes.get('adjacencyState')
        self.attackerColor = attributes.get('attackerColor', self.default_attackerColor)
        self.defenderColor = attributes.get('defenderColor', self.default_defenderColor)
        self.animateIn = attributes.get('animateIn', self.default_animateIn)
        self.displayAdjacencyIcon = attributes.get('displayAdjacencyIcon', self.default_displayAdjacencyIcon)
        self.victoryPointState = sm.GetService('fwVictoryPointSvc').GetVictoryPointState(self.systemId)
        self.width = self.radius * 2
        self.height = self.radius * 2
        self._ConstructLayout()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        descriptionLabel = EveLabelLarge(text=ADJACENCY_TO_DESC[self.adjacencyState], maxWidth=215)
        iconPath = self.GetAdjencyIconPath()
        sprite = Sprite(texturePath=iconPath, width=32, height=32)
        stateText = GetSystemCaptureStatusText(self.victoryPointState)
        contestedLineLabel = EveLabelLarge(color=TextColor.HIGHLIGHT, text=eveformat.bold(stateText))
        systemLabel = EveLabelLarge(color=TextColor.HIGHLIGHT, text=ADJACENCY_TO_LABEL_SYSTEM_TEXT[self.adjacencyState], bold=True)
        containerGrid = LayoutGrid(rows=2, columns=1, margin=15)
        headerGrid = LayoutGrid(rows=1, columns=2, cellPadding=5)
        headerRightSectionGrid = LayoutGrid(rows=2, columns=1)
        headerRightSectionGrid.AddCell()
        headerRightSectionGrid.AddCell(contestedLineLabel)
        headerRightSectionGrid.AddCell(systemLabel)
        headerGrid.AddCell(sprite)
        headerGrid.AddCell(headerRightSectionGrid)
        containerGrid.AddCell(headerGrid)
        containerGrid.AddCell(descriptionLabel)
        tooltipPanel.AddCell(containerGrid)

    def _ConstructLayout(self):
        containerTransform = Transform(parent=self, width=self.width, height=self.height, align=uiconst.CENTER)
        transform = Transform(parent=containerTransform, width=50, height=50, align=uiconst.TOPLEFT)
        VectorLine(parent=containerTransform, translationFrom=(self.width / 2 + 1, -2), translationTo=(self.width / 2 + 1, 5), colorFrom=eveColor.WHITE, colorTo=eveColor.WHITE, widthFrom=0.3, widthTo=0.3, opacity=8.0)
        iconPath = self.GetAdjencyIconPath()
        self.adjacencySprite = Sprite(parent=transform, align=uiconst.CENTER, texturePath=iconPath, width=32, height=32, top=2, color=TextColor.HIGHLIGHT)
        self.adjacencySprite.display = self.displayAdjacencyIcon
        transform.scalingCenter = (0.5, 0.5)
        self.chart = CircularGraph(parent=containerTransform, radius=self.radius, lineWidth=self.lineWidth, bgLineWidth=self.lineWidth, align=uiconst.CENTER, glow=False, glowBrightness=0.5)
        self.ReloadChart()

    def ReloadChart(self):
        self.UpdateChart(self.victoryPointState.contestedFraction)

    def UpdateAdjacencyState(self, newState):
        self.adjacencyState = newState

    def UpdateVictoryPointsState(self, newState):
        self.victoryPointState = newState
        self.ReloadChart()

    def UpdateChart(self, contestedAmount):
        uncontested = 1.0 - contestedAmount
        graphData = [GraphSegmentParams(0.01, eveColor.BLACK, showMarker=False),
         GraphSegmentParams(contestedAmount, self.attackerColor, showMarker=False),
         GraphSegmentParams(0.01, eveColor.BLACK, showMarker=False),
         GraphSegmentParams(uncontested, self.defenderColor, showMarker=False)]
        self.chart.LoadGraphData(graphData, animateIn=self.animateIn)

    def SetAdjacency(self, adjacencyState):
        self.adjacencyState = adjacencyState
        iconPath = self.GetAdjencyIconPath()
        self.adjacencySprite.SetTexturePath(iconPath)

    def SetGaugeColors(self, attackerColor, defenderColor):
        newColors = self.attackerColor != attackerColor or self.defenderColor != defenderColor
        self.attackerColor = attackerColor
        self.defenderColor = defenderColor
        if newColors:
            self.ReloadChart()

    def GetAdjencyIconPath(self):
        return ADJACENCY_STATE_TO_ICON_PATH_SMALL.get(self.adjacencyState, None)
