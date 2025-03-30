#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\milestoneProgressGauge.py
import math
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.skillPlan.milestone import milestoneConst
from eve.client.script.ui.skillPlan.milestone.milestoneConst import TRANSFORM_RADIUS
from eve.client.script.ui.skillPlan.milestone.milestoneSegment import ProgressSegment, InTrainingSegment, SkillsMissingSegment
from eve.client.script.ui.skillPlan.milestone.milestoneUtil import GetMissingSkillsColor
from signals import Signal
SEGMENT_HINT_SCALE = 0.12
MIN_GAUGE_RATIO_TRAINED = 0.01
MIN_GAUGE_RATIO = 0.03

class MilestoneProgressGauge(Container):
    default_highlightNotInTraining = False
    gaugeTexturePath = 'res:/UI/Texture/classes/SkillPlan/milestones/thinGaugeBG.png'
    startAngle = -math.pi / 2
    angle = 2 * math.pi

    def ApplyAttributes(self, attributes):
        super(MilestoneProgressGauge, self).ApplyAttributes(attributes)
        self._radius = attributes.radius
        self.controller = attributes.controller
        self.highlightNotInTraining = attributes.get('highlightNotInTraining', self.default_highlightNotInTraining)
        self.ConstructLayout()

    def ConstructLayout(self):
        self.gaugeTransform = Transform(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         TRANSFORM_RADIUS * 2,
         TRANSFORM_RADIUS * 2), scalingCenter=(0.5, 0.5), scale=self._GetTransformScale(self.radius))
        self.progressGauge = ProgressSegment(parent=self.gaugeTransform, align=uiconst.CENTER, lineWidth=self.GetLineWidth(TRANSFORM_RADIUS), startAngle=self.startAngle, angle=self.angle, texturePath=self.gaugeTexturePath)
        self.inTrainingGauge = InTrainingSegment(parent=self.gaugeTransform, align=uiconst.CENTER, lineWidth=self.GetLineWidth(TRANSFORM_RADIUS), startAngle=self.startAngle, angle=self.angle, texturePath=self.gaugeTexturePath)
        self.missingGauge = SkillsMissingSegment(parent=self.gaugeTransform, align=uiconst.CENTER, lineWidth=self.GetLineWidth(TRANSFORM_RADIUS), startAngle=self.startAngle, angle=self.angle, texturePath=self.gaugeTexturePath, highlightNotInTraining=self.highlightNotInTraining, color=GetMissingSkillsColor(self.highlightNotInTraining))

    def SetController(self, controller):
        self.controller = controller

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._ApplyNewRadius()

    def _ApplyNewRadius(self):
        self._ApplyTransformScaling()
        self.pickRadius = self.radius

    def SetRadius(self, radius):
        self.radius = radius

    def _ApplyTransformScaling(self, animate = False):
        scale = self._GetTransformScale(self.radius)
        if animate:
            animations.MorphVector2(self.gaugeTransform, 'scale', self.gaugeTransform.scale, scale, duration=milestoneConst.SCALE_ANIMATION_DURATION)
        else:
            self.gaugeTransform.scale = scale

    def _GetTransformScale(self, radius):
        scale = float(radius) / TRANSFORM_RADIUS
        return (scale, scale)

    def UpdateProgress(self, animate = True):
        if not self.controller:
            for gauge in (self.progressGauge, self.inTrainingGauge, self.missingGauge):
                gauge.SetStartEnd(0.0, 0.0, animate)

            return
        progressRatio = self.controller.GetProgressRatio()
        if progressRatio:
            progressRatio = min(max(progressRatio, MIN_GAUGE_RATIO_TRAINED), 0.999)
        inTrainingRatio = self.controller.GetInTrainingRatio()
        if inTrainingRatio:
            inTrainingRatio = min(max(inTrainingRatio, MIN_GAUGE_RATIO), 0.999)
        remainingRatio = 0.0 if self.controller.IsCompleted() else 1.0 - progressRatio - inTrainingRatio
        self.progressGauge.SetStartEnd(None, progressRatio, animate)
        self.inTrainingGauge.SetStartEnd(progressRatio, progressRatio + inTrainingRatio, animate)
        self.missingGauge.SetStartEnd(1.0 - remainingRatio, None, animate)

    def GetLineWidth(self, radius):
        return 0.75 * radius
