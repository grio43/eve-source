#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\gauges\warzoneStatusGauge.py
from carbonui import uiconst
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui import eveColor
from eve.client.script.ui.graphs import GraphSegmentParams
from eve.client.script.ui.graphs.circulargraph import CircularGraph
from eveui import Sprite
from fwwarzone.client.dashboard.const import RED_COLOR, BLUE_COLOR, FACTION_ID_TO_COLOR
from localization import GetByLabel
from eve.common.script.util.facwarCommon import GetOccupationEnemyFaction

class WarzoneStatusGauge(Transform):
    default_radius = 30
    default_lineWidth = 3.5
    default_defenderColor = RED_COLOR
    default_attackerColor = BLUE_COLOR
    default_animateIn = True
    default_iconSize = 65
    default_name = 'WarzoneStatusGauge'

    def ApplyAttributes(self, attributes):
        super(WarzoneStatusGauge, self).ApplyAttributes(attributes)
        self.radius = attributes.get('radius', self.default_radius)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.animateIn = attributes.get('animateIn', self.default_animateIn)
        self.warzoneId = attributes.get('warzoneId')
        self.viewingFactionId = attributes.get('viewingFactionId')
        self.width = self.radius * 2
        self.height = self.radius * 2
        self.opposingFactionId = GetOccupationEnemyFaction(self.viewingFactionId)
        self.friendlySystemCount, self.opposingSystemCount, overallCount = self._GetFactionSystemCount(self.viewingFactionId, self.opposingFactionId)
        if overallCount == 0:
            self.fractionFriendlySystems = 0.0
            self.fractionOpposingSystems = 0.0
        else:
            self.fractionFriendlySystems = self.friendlySystemCount / float(overallCount)
            self.fractionOpposingSystems = self.opposingSystemCount / float(overallCount)
        self._ConstructLayout()

    def _ConstructLayout(self):
        containerTransform = Transform(parent=self, width=self.width, height=self.height, align=uiconst.CENTER)
        VectorLine(parent=containerTransform, translationFrom=(self.width / 2 + 1, -15), translationTo=(self.width / 2 + 1, 20), colorFrom=eveColor.ICE_WHITE, colorTo=eveColor.ICE_WHITE, widthFrom=0.08, widthTo=0.08, opacity=32.0)
        Sprite(parent=self, align=uiconst.CENTER, texturePath='res:/ui/Texture/classes/frontlines/factionalwarfare_icon.png', width=self.iconSize, height=self.iconSize)
        chart = CircularGraph(parent=containerTransform, radius=self.radius, lineWidth=self.lineWidth, bgLineWidth=self.lineWidth, align=uiconst.CENTER, glow=True, glowBrightness=0.5)
        graphData = [GraphSegmentParams(self.fractionFriendlySystems, FACTION_ID_TO_COLOR[self.viewingFactionId], GetByLabel('UI/FactionWarfare/frontlinesDashboard/nSystemsOccupiedBy', systems=self.friendlySystemCount, factionName=cfg.eveowners.Get(self.viewingFactionId).name)), GraphSegmentParams(0.01, eveColor.MATTE_BLACK, showMarker=False), GraphSegmentParams(self.fractionOpposingSystems, self.GetOpposingFactionColor(), GetByLabel('UI/FactionWarfare/frontlinesDashboard/nSystemsOccupiedBy', systems=self.opposingSystemCount, factionName=cfg.eveowners.Get(self.opposingFactionId).name))]
        chart.LoadGraphData(graphData, animateIn=self.animateIn)

    def GetOpposingFactionColor(self):
        return FACTION_ID_TO_COLOR[self.opposingFactionId]

    def _GetFactionSystemCount(self, factionAID, factionBID):
        occupationStates = sm.GetService('fwWarzoneSvc').GetAllOccupationStates()[self.warzoneId]
        aCount = 0
        bCount = 0
        for systemId, occupationState in occupationStates.iteritems():
            if occupationState.occupierID == factionAID:
                aCount += 1
            elif occupationState.occupierID == factionBID:
                bCount += 1

        return (aCount, bCount, len(occupationStates))


class WarzoneStatusGaugeFaintOpponent(WarzoneStatusGauge):

    def GetOpposingFactionColor(self):
        color = FACTION_ID_TO_COLOR[self.opposingFactionId]
        color = color[:3] + (0.1,)
        return color
