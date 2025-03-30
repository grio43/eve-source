#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\widgets\gauge.py
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui import eveColor
from eve.client.script.ui.graphs import GraphSegmentParams
from eve.client.script.ui.graphs.circulargraph import CircularGraph
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from pirateinsurgency.client.dashboard.const import GetPirateFactionIDFromWarzoneID, GetFactionColorFromPerspectiveOfMilitia, GetSuppressionColor, GetGenericCorruptionColor
NORMAL_SIZE_FACTOR = 1.0
HIGHLIGHT_SIZE_FACTOR = 1.5
SEPERATOR_SIZE = 0.02

class AbstractIncursionStageGauge(Transform):

    def ApplyAttributes(self, attributes):
        super(AbstractIncursionStageGauge, self).ApplyAttributes(attributes)
        self.containerWidth = attributes.get('width')
        self.systemID = attributes.get('systemID')
        self.stages = attributes.get('stages')
        self.dashboardSvc = attributes.get('dashboardSvc')
        self.totalProportion = 0.0
        self.vanguardProportion = 0.0
        self.fullErrorBox = attributes.get('fullErrorBox', True)
        self.errorReportingEnabled = attributes.get('errorReportingEnabled', True)
        sm.RegisterNotify(self)
        self.icon = None
        self.ConstructLayout()

    def ConstructLayout(self):
        self.chart = CircularGraph(name='chart', parent=self, radius=self.containerWidth / 2, lineWidth=3, bgLineWidth=3, align=uiconst.CENTER, glow=True, glowBrightness=0.5)
        self.backgroundChart = CircularGraph(name='backgroundChart', parent=self, radius=self.containerWidth / 2, lineWidth=3, bgLineWidth=3, align=uiconst.CENTER, colorBg=(0.0, 0.0, 0.0, 0.1))

    def OnDataLoaded(self, data):
        currentValue = data.numerator
        maxValue = data.denominator
        self.vanguardProportion = 0
        if data.vanguardNumerator and data.vanguardDenominator and data.vanguardDenominator > 0:
            self.vanguardProportion = float(data.vanguardNumerator) / float(data.vanguardDenominator)
        self.totalProportion = float(currentValue) / float(maxValue)
        if maxValue == 0:
            self.LoadGaugeData(0, 0)
        else:
            self.LoadGaugeData(self.totalProportion, self.vanguardProportion)

    def SetIcon(self, texturePath):
        if self.icon:
            self.icon.SetTexturePath(texturePath)

    def LoadGaugeData(self, currentProportion, extraVanguardProportion):
        graphData = []
        backgroundGraphData = []
        capsuleerProportion = currentProportion - extraVanguardProportion
        separatorColor = (0, 0, 0, 0)
        prevThreshold = 0.0
        for idx, currentThreshold in enumerate(self.stages):
            thicknessSizeFactor = NORMAL_SIZE_FACTOR
            if currentProportion >= prevThreshold:
                if currentProportion < currentThreshold:
                    thicknessSizeFactor = HIGHLIGHT_SIZE_FACTOR
                thisSegmentCapsuleerProportion = max(0, min(capsuleerProportion, currentThreshold) - prevThreshold - SEPERATOR_SIZE)
                if thisSegmentCapsuleerProportion > 0:
                    graphData.append(GraphSegmentParams(thisSegmentCapsuleerProportion, self.gaugeColor, sizeFactor=thicknessSizeFactor))
                if capsuleerProportion < currentThreshold and currentProportion >= currentThreshold:
                    thisSegmentVanguardProportion = min(currentProportion, currentThreshold) - (thisSegmentCapsuleerProportion + prevThreshold + SEPERATOR_SIZE)
                    graphData.append(GraphSegmentParams(thisSegmentVanguardProportion, self.vanguardColor, sizeFactor=thicknessSizeFactor))
                graphData.append(GraphSegmentParams(SEPERATOR_SIZE, separatorColor))
            backgroundProportion = currentThreshold - prevThreshold - SEPERATOR_SIZE
            backgroundGraphData.append(GraphSegmentParams(backgroundProportion, eveColor.GUNMETAL_GREY, sizeFactor=thicknessSizeFactor))
            backgroundGraphData.append(GraphSegmentParams(SEPERATOR_SIZE, separatorColor))
            prevThreshold = currentThreshold

        self.backgroundChart.LoadGraphData(backgroundGraphData, animateIn=False)
        self.chart.LoadGraphData(graphData, animateIn=True)


class SuppressionGauge(AbstractIncursionStageGauge):
    default_badgeTexturePath = 'res:/UI/Texture/classes/pirateinsurgencies/faction_badges/suppression.png'
    default_drawSprite = True
    __notifyevents__ = ['OnSuppressionValueChanged_Local']

    def ApplyAttributes(self, attributes):
        super(SuppressionGauge, self).ApplyAttributes(attributes)
        self.gaugeColor = GetSuppressionColor(fill=False)
        self.vanguardColor = eveColor.FOCUS_BLUE
        drawSprite = attributes.get('drawSprite', SuppressionGauge.default_drawSprite)
        if drawSprite:
            self.icon = Sprite(name='icon', parent=self, texturePath=SuppressionGauge.default_badgeTexturePath, width=44, height=44, align=uiconst.CENTER)
        errorParent = None
        if self.errorReportingEnabled:
            errorParent = self
        wrappedCallback = WrapCallbackWithErrorHandling(self.OnDataLoaded, parentContainer=errorParent, onErrorCallback=self.Flush, fullErrorBox=self.fullErrorBox)
        if self.systemID == session.solarsystemid2:
            self.dashboardSvc.RequestLocalSystemSuppression(wrappedCallback)
        else:
            self.dashboardSvc.RequestSystemSuppression(self.systemID, wrappedCallback)

    def OnSuppressionValueChanged_Local(self, systemID, data):
        if systemID == self.systemID:
            numerator = data.numerator
            denominator = data.denominator
            vanguardNumerator = data.vanguardNumerator
            vanguardDenominator = data.vanguardDenominator
            self.totalProportion = float(numerator) / float(denominator)
            self.vanguardProportion = float(vanguardNumerator) / float(vanguardDenominator)
            self.LoadGaugeData(self.totalProportion, self.vanguardProportion)


class CorruptionGauge(AbstractIncursionStageGauge):
    default_badgeTexturePath = 'res:/UI/Texture/classes/pirateinsurgencies/faction_badges/corruption.png'
    default_drawSprite = True
    __notifyevents__ = ['OnCorruptionValueChanged_Local']

    def ApplyAttributes(self, attributes):
        super(CorruptionGauge, self).ApplyAttributes(attributes)
        self.gaugeColor = GetGenericCorruptionColor(fill=False)
        self.vanguardColor = eveColor.WHITE
        snapshot = self.dashboardSvc.GetCampaignSnapshotForSystem(self.systemID)
        if snapshot is not None:
            pirateFactionID = GetPirateFactionIDFromWarzoneID(snapshot.warzoneID)
            self.gaugeColor = GetFactionColorFromPerspectiveOfMilitia(session.warfactionid, pirateFactionID, fill=False)
        drawSprite = attributes.get('drawSprite', CorruptionGauge.default_drawSprite)
        if drawSprite:
            self.icon = Sprite(name='icon', parent=self, texturePath=CorruptionGauge.default_badgeTexturePath, width=44, height=44, align=uiconst.CENTER)
        errorParent = None
        if self.errorReportingEnabled:
            errorParent = self
        wrappedCallback = WrapCallbackWithErrorHandling(self.OnDataLoaded, parentContainer=errorParent, onErrorCallback=self.Flush, fullErrorBox=self.fullErrorBox)
        if self.systemID == session.solarsystemid2:
            self.dashboardSvc.RequestLocalSystemCorruption(wrappedCallback)
        else:
            self.dashboardSvc.RequestSystemCorruption(self.systemID, wrappedCallback)

    def OnCorruptionValueChanged_Local(self, systemID, data):
        if systemID == self.systemID:
            numerator = data.numerator
            denominator = data.denominator
            vanguardNumerator = data.vanguardNumerator
            vanguardDenominator = data.vanguardDenominator
            self.totalProportion = float(numerator) / float(denominator)
            self.vanguardProportion = float(vanguardNumerator) / float(vanguardDenominator)
            self.LoadGaugeData(self.totalProportion, self.vanguardProportion)
