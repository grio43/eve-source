#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\milestoneSegment.py
import trinity
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.donutSegment import DonutSegment
from eve.client.script.ui.skillPlan.milestone.milestoneConst import TRANSFORM_RADIUS

class MilestoneSegment(DonutSegment):
    default_textureWidth = 43.0
    default_spriteEffect = trinity.TR2_SFX_COPY
    default_radius = TRANSFORM_RADIUS
    default_state = uiconst.UI_DISABLED
    default_colorEnd = eveColor.WHITE

    def ApplyAttributes(self, attributes):
        super(MilestoneSegment, self).ApplyAttributes(attributes)

    def GetColor(self):
        return self.color

    def SetStartEnd(self, start = None, end = None, animate = False):
        duration = 1.0
        if start is not None:
            if animate:
                animations.MorphScalar(self, 'start', self.start, start, duration=duration)
            else:
                self.start = start
        if end is not None:
            if animate:
                animations.MorphScalar(self, 'end', self.end, end, duration=duration)
            else:
                self.end = end


class ProgressSegment(MilestoneSegment):
    default_color = eveColor.WHITE


class InTrainingSegment(MilestoneSegment):
    default_color = eveColor.CRYO_BLUE


class SkillsMissingSegment(MilestoneSegment):

    def ApplyAttributes(self, attributes):
        self.highlightNotInTraining = attributes.highlightNotInTraining
        super(SkillsMissingSegment, self).ApplyAttributes(attributes)
