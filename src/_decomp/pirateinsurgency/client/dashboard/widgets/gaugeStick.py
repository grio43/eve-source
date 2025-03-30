#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\client\dashboard\widgets\gaugeStick.py
import math
import carbonui
import eveicon
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.vectorarc import VectorArc
from eve.client.script.ui import eveColor
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.services.insurgenceDashboardSvc import WrapCallbackWithErrorHandling
from eveui import Sprite
from localization import GetByLabel, GetByMessageID
from pirateinsurgency.client.dashboard.widgets.gauge import SuppressionGauge, CorruptionGauge
from pirateinsurgency.client.utils import CalculateCurrentStageFromFraction

class GaugeOnAStick(Container):
    __notifyevents__ = ['OnCorruptionValueChanged_Local', 'OnSuppressionValueChanged_Local']
    default_width = 64
    default_gaugeHeight = 64
    default_gaugeWidth = 64

    def ApplyAttributes(self, attributes):
        super(GaugeOnAStick, self).ApplyAttributes(attributes)
        self.wholeHeight = attributes.get('height')
        self.lineHeight = attributes.get('lineHeight')
        self.solarSystemID = attributes.get('solarSystemID')
        self.dashboardSvc = attributes.get('dashboardSvc')
        self.gaugeHeight = attributes.get('gaugeHeight', self.default_gaugeHeight)
        self.gaugeWidth = attributes.get('gaugeWidth', self.default_gaugeWidth)
        self.corruptionStage = attributes.get('corruptionStage')
        self.suppressionStage = attributes.get('suppressionStage')
        self.iceHeist = attributes.get('iceHeist', None)
        self.suppressionStages = None
        self.corruptionStages = None
        sm.RegisterNotify(self)
        self.ConstructLayout()

    def ConstructLayout(self):
        circle = VectorArc(name='circle', parent=self, align=uiconst.CENTERTOP, endAngle=math.pi * 2, fill=False, top=self.gaugeHeight / 2)
        lineOffset = -self.lineHeight - self.gaugeHeight / 2 + circle.radius * 2 + circle.lineWidth * 2 + 1
        Container(parent=self, align=uiconst.TOLEFT_NOPUSH, bgColor=eveColor.WHITE, width=2, left=6, padTop=self.wholeHeight - -lineOffset)
        contWidth = 200
        labelsCont = ContainerAutoSize(name='labelsCont', parent=self, width=contWidth, align=uiconst.CENTERTOP, left=contWidth / 2 + self.gaugeWidth / 2, top=-5, alignMode=uiconst.TOTOP, padLeft=10)
        carbonui.TextHeadline(parent=labelsCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/corruption'), color=eveColor.SAND_YELLOW)
        self.corruptionStageLabel = carbonui.TextBody(parent=labelsCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage=self.corruptionStage))
        carbonui.TextHeadline(parent=labelsCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/suppression'))
        self.suppressionStageLabel = carbonui.TextBody(parent=labelsCont, align=uiconst.TOTOP, text=GetByLabel('UI/PirateInsurgencies/stageLabel', stage=self.suppressionStage))
        if self.iceHeist:
            iceHiestCont = Container(parent=self, align=uiconst.TOTOP_NOPUSH, height=32, width=200, top=-30, left=-50)
            dungeonName = GetByMessageID(self.iceHeist[0].dungeonNameID)
            Sprite(parent=iceHiestCont, width=32, height=32, texturePath=eveicon.tow, align=uiconst.TOLEFT, top=-10)
            carbonui.TextBody(parent=iceHiestCont, text=dungeonName, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, padLeft=4)
        self.dashboardSvc.RequestSuppressionStages(WrapCallbackWithErrorHandling(self.suppressionStagesCallback, parentContainer=None))
        self.dashboardSvc.RequestCorruptionStages(WrapCallbackWithErrorHandling(self.corruptionStagesCallback, parentContainer=None))

    def OnSuppressionValueChanged_Local(self, systemID, data):
        if systemID != self.solarSystemID:
            return
        if self.suppressionStages is None:
            return
        if self.suppressionStageLabel is None:
            return
        stageText = GetByLabel('UI/PirateInsurgencies/stageLabel', stage=data.stage)
        self.suppressionStageLabel.SetText(stageText)

    def OnCorruptionValueChanged_Local(self, systemID, data):
        if systemID != self.solarSystemID:
            return
        if self.corruptionStages is None:
            return
        if self.corruptionStageLabel is None:
            return
        stageText = GetByLabel('UI/PirateInsurgencies/stageLabel', stage=data.stage)
        self.corruptionStageLabel.SetText(stageText)

    def corruptionStagesCallback(self, stages):
        self.corruptionStages = stages
        CorruptionGauge(parent=self, name='CorruptionGauge', align=uiconst.TOTOP_NOPUSH, width=self.gaugeWidth, height=self.gaugeHeight, systemID=self.solarSystemID, stages=stages, dashboardSvc=self.dashboardSvc, drawSprite=False, fullErrorBox=False)

    def suppressionStagesCallback(self, stages):
        self.suppressionStages = stages
        width = self.gaugeWidth * 0.75
        height = self.gaugeHeight * 0.75
        SuppressionGauge(parent=self, name='SuppressionGauge', align=uiconst.TOTOP_NOPUSH, width=width, height=height, systemID=self.solarSystemID, stages=stages, dashboardSvc=self.dashboardSvc, drawSprite=False, top=height / 6, fullErrorBox=False, errorReportingEnabled=False)
