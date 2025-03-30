#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\skillPlanProgressGauge.py
import math
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.skillPlan.milestone.milestoneConst import START_ANGLE, GAUGE_ANGLE
from eve.client.script.ui.skillPlan.milestone.milestoneProgressGauge import MilestoneProgressGauge
from eve.client.script.ui.skillPlan.milestone.milestoneUtil import GetMissingSkillsColor

class SkillPlanProgressGauge(MilestoneProgressGauge):
    startAngle = START_ANGLE
    angle = GAUGE_ANGLE
    gaugeTexturePath = 'res:/UI/Texture/classes/SkillPlan/milestones/gaugeBG.png'

    def ApplyAttributes(self, attributes):
        super(SkillPlanProgressGauge, self).ApplyAttributes(attributes)
        self.UpdateSpritePositions()

    def UpdateSpriteColors(self, animate = True):
        if not self.controller:
            return
        trainedRatio = self.controller.GetProgressRatio()
        inTrainingRatio = self.controller.GetInTrainingRatio()
        startColor = self._GetStartSpriteColor(trainedRatio)
        endColor = self._GetEndSpriteColor(inTrainingRatio, trainedRatio)
        if animate:
            duration = 1.0
            animations.SpColorMorphTo(self.startSprite, self.startSprite.GetRGB(), startColor, duration=duration)
            animations.SpColorMorphTo(self.endSprite, self.endSprite.GetRGB(), endColor, duration=duration)
        else:
            self.startSprite.SetRGBA(*startColor)
            self.endSprite.SetRGBA(*endColor)

    def _GetStartSpriteColor(self, trainedRatio):
        if trainedRatio > 0.0:
            color = eveColor.WHITE
        else:
            color = GetMissingSkillsColor(self.highlightNotInTraining)
        return color

    def _GetEndSpriteColor(self, inTrainingRatio, trainedRatio):
        if trainedRatio >= 1.0:
            color = eveColor.WHITE
        elif trainedRatio + inTrainingRatio >= 1.0:
            color = eveColor.CRYO_BLUE
        else:
            color = GetMissingSkillsColor(self.highlightNotInTraining)
        return color

    def UpdateProgress(self, animate = True):
        super(SkillPlanProgressGauge, self).UpdateProgress(animate)
        self.UpdateSpriteColors(animate)

    def UpdateSpritePositions(self):
        radius = self.radius * 0.94
        left = radius * math.cos(math.pi - self.startAngle)
        top = radius * math.sin(math.pi - self.startAngle)
        self.startSprite.left = -left
        self.startSprite.top = top
        self.endSprite.left = left
        self.endSprite.top = top

    def SetRadius(self, radius):
        super(SkillPlanProgressGauge, self).SetRadius(radius)
        self.UpdateSpritePositions()

    def _ApplyNewRadius(self):
        super(SkillPlanProgressGauge, self)._ApplyNewRadius()
        self.UpdateSpritePositions()

    def ConstructLayout(self):
        self.startSprite = Sprite(name='startSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 30, 30), texturePath='res:/UI/Texture/classes/SkillPlan/milestones/gaugeStartEnd.png')
        self.endSprite = Sprite(name='endSprite', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 30, 30), texturePath='res:/UI/Texture/classes/SkillPlan/milestones/gaugeStartEnd.png')
        super(SkillPlanProgressGauge, self).ConstructLayout()

    def GetLineWidth(self, radius):
        return 0.22 * radius
