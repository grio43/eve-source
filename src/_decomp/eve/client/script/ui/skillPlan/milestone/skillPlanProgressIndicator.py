#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\skillPlanProgressIndicator.py
import math
from collections import OrderedDict
import uthread2
from carbonui import TextColor, uiconst, fontconst
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.milestone.milestoneProgressIndicator import MilestoneProgressIndicator
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressGauge import SkillPlanProgressGauge
from eve.client.script.ui.skillPlan.skillPlanConst import TRAINING_TIME_EMPTY_LABEL
from skills.skillplan import skillPlanConst, skillPlanSignals
from skills.skillplan.milestone.milestoneController import MilestoneType
START_ANGLE_BY_NUM_MILESTONES = (0,
 0,
 -math.pi / 2,
 math.pi / 4,
 math.pi / 10)

class SkillPlanProgressIndicator(Container):
    default_state = uiconst.UI_NORMAL
    default_alignMode = uiconst.CENTERTOP
    default_highlightNotInTraining = False
    __notifyevents__ = ['OnSkillQueueChanged']

    def ApplyAttributes(self, attributes):
        super(SkillPlanProgressIndicator, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        skillPlanSignals.on_saved.connect(self.OnSkillPlanSaved)
        skillPlan = attributes.skillPlan
        self.highlightNotInTraining = attributes.get('highlightNotInTraining', self.default_highlightNotInTraining)
        self._isInit = False
        self.skillPlan = None
        self.milestoneIndicators = OrderedDict()
        self.updateTrainingTimeThread = None
        self.mainCont = Container(name='mainCont', parent=self, align=uiconst.CENTER)
        self.ConstructTopWedge()
        self.ConstructProgressGauge()
        skillPlanUISignals.on_skill_requirements_changed.connect(self.OnSkillRequirementsChanged)
        skillPlanUISignals.on_milestone_updated.connect(self.OnMilestoneUpdated)
        self._isInit = True
        if skillPlan:
            self.SetSkillPlan(skillPlan)
        uthread2.start_tasklet(self._UpdateProgressThread)

    def ConstructProgressGauge(self):
        radius = self.GetOuterRadius()
        self.progressGauge = SkillPlanProgressGauge(parent=self.mainCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL, radius=radius, highlightNotInTraining=self.highlightNotInTraining, controller=self.skillPlan)

    def ConstructTopWedge(self):
        ratio = 125 / 33.0
        size = 0.09
        self.topWedgeCont = Container(name='topWedgeCont', parent=self.mainCont, align=uiconst.TOPLEFT_PROP, pos=(0.5,
         0.035,
         size * ratio,
         size))
        self.topWedgeBG = Sprite(name='topWedge', bgParent=self.topWedgeCont, texturePath='res:/UI/Texture/classes/SkillPlan/milestones/topWedge.png', opacity=0.6)
        self.completedUnderscore = StretchSpriteHorizontal(name='completedUnderscore', parent=self.topWedgeCont, texturePath='res:/UI/Texture/classes/SkillPlan/milestones/completedUnderscore.png', align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, height=24, top=-18, padding=(-1, 0, -1, 0), color=eveColor.LEAFY_GREEN)
        self.totalTrainingTimeLabel = EveLabelLarge(parent=self.topWedgeCont, name='totalTrainingTimeLabel', align=uiconst.CENTER, text=TRAINING_TIME_EMPTY_LABEL, color=TextColor.HIGHLIGHT)

    def UpdateGaugeProgress(self, animate = True):
        self.progressGauge.UpdateProgress(animate=animate)
        self.UpdateTopWedge()

    def UpdateTopWedge(self):
        if not self.skillPlan:
            return
        inTrainingRatio = self.skillPlan.GetInTrainingRatio()
        trainedRatio = self.skillPlan.GetProgressRatio()
        if self.skillPlan and self.skillPlan.IsCompleted():
            color = eveColor.COPPER_OXIDE_GREEN
        elif inTrainingRatio + trainedRatio == 0.0:
            color = eveColor.LED_GREY
        else:
            color = eveColor.SMOKE_BLUE
        color = Color(*color).SetOpacity(0.6).GetRGBA()
        self.topWedgeBG.SetRGBA(*color)
        if self.skillPlan and self.skillPlan.IsCompleted():
            self.completedUnderscore.Show()
        else:
            self.completedUnderscore.Hide()

    def ClearSkillPlan(self):
        self.ClearMilestones()
        self.totalTrainingTimeLabel.SetText(TRAINING_TIME_EMPTY_LABEL)
        self.skillPlan = None
        self.UpdateGaugeProgress(animate=False)

    def ClearMilestones(self):
        for m in self.milestoneIndicators.values():
            m.Close()

        self.milestoneIndicators.clear()

    def GetMilestoneIndicator(self, milestoneID):
        return self.milestoneIndicators.get(milestoneID, None)

    def AddMilestone(self, milestoneID):
        m = self.GetMilestoneIndicator(milestoneID)
        if m is not None:
            return
        milestone = self.skillPlan.GetMilestone(milestoneID)
        milestoneIndicator = MilestoneProgressIndicator(parent=self, idx=0, align=uiconst.CENTER, milestone=milestone, skillPlan=self.skillPlan, isEditable=False, highlightNotInTraining=self.highlightNotInTraining)
        self.milestoneIndicators[milestoneID] = milestoneIndicator

    def UpdateMilestonePositions(self):
        num = len(self.milestoneIndicators)
        radius = self.GetOuterRadius()
        iconRadius = self._GetMilestoneIconRadius(num, radius)
        for i, milestone in enumerate(self.milestoneIndicators.values()):
            left, top = self._GetMilestonePosition(i, num, radius)
            milestone.left = left
            milestone.top = top
            milestone.SetRadius(iconRadius)

    def _GetMilestoneIconRadius(self, num, radius):
        return radius * 0.45 * (1.0 - 0.085 * num)

    def _GetMilestonePosition(self, i, num, outerRadius):
        if num == 1:
            left = top = 0
        else:
            angle = self._GetMilestoneAngle(i, num)
            r = self._GetMilestonePositionRadius(num, outerRadius)
            left = r * math.cos(angle)
            top = r * math.sin(angle)
        return (left, top)

    def _GetMilestoneAngle(self, i, num):
        startAngle = START_ANGLE_BY_NUM_MILESTONES[num - 1]
        angle = startAngle - 2 * math.pi * i / float(num)
        return angle

    def _GetMilestonePositionRadius(self, num, outerRadius):
        return 0.35 * outerRadius * (1.0 + 0.21 * num / skillPlanConst.MAX_NUM_MILESTONES)

    def GetOuterRadius(self):
        width, height = self.GetAbsoluteSize()
        return min(width / 2, height / 2)

    def SetSkillPlan(self, skillPlan):
        if self.destroyed:
            return
        self.skillPlan = skillPlan
        self.progressGauge.SetController(self.skillPlan)
        self.UpdateGaugeProgress(animate=False)
        if self.skillPlan:
            self.totalTrainingTimeLabel.SetText(self._GetTrainingTimeLeftText())
        self.ReconstructMilestones()
        self.ApplyRadius()

    def ReconstructMilestones(self):
        self.ClearMilestones()
        if not self.skillPlan:
            return
        for m in self.skillPlan.GetMilestones():
            self.AddMilestone(m)

    def OnSkillRequirementsChanged(self, skillPlanID):
        if self.skillPlan and skillPlanID == self.skillPlan.GetID():
            self.UpdateGaugeProgress()
            self.totalTrainingTimeLabel.SetText(self._GetTrainingTimeLeftText())

    def OnMilestoneUpdated(self, milestoneID):
        if not self.skillPlan:
            return
        milestoneIndicator = self.GetMilestoneIndicator(milestoneID)
        if milestoneIndicator is None:
            return
        milestone = self.skillPlan.GetMilestone(milestoneID)
        if milestone.GetMilestoneType() == MilestoneType.SKILL_REQUIREMENT_MILESTONE:
            level = milestone.GetLevel()
            self.skillPlan.AddAllSkillsRequiredFor(milestone.GetTypeID(), level)
            skillPlanUISignals.on_skill_requirements_changed(self.skillPlan.GetID())
        milestoneIndicator.UpdateProgress()

    def _UpdateProgressThread(self):
        while not self.destroyed:
            if self.skillPlan:
                self.totalTrainingTimeLabel.SetText(self._GetTrainingTimeLeftText())
                self.UpdateGaugeProgress(animate=False)
            uthread2.Sleep(1.0)

    def _GetTrainingTimeLeftText(self):
        return self.skillPlan.GetTotalTrainingTimeLeftText()

    def _OnSizeChange_NoBlock(self, *args):
        if self._isInit:
            self.ApplyRadius()

    def ApplyRadius(self):
        radius = self.GetOuterRadius()
        self.mainCont.width = self.mainCont.height = 2 * radius
        self.progressGauge.SetRadius(radius)
        self.UpdateMilestonePositions()
        if radius > 100:
            self.topWedgeBG.Show()
            self.totalTrainingTimeLabel.fontsize = fontconst.EVE_LARGE_FONTSIZE
        else:
            self.topWedgeBG.Hide()
            self.totalTrainingTimeLabel.fontsize = fontconst.EVE_SMALL_FONTSIZE

    def OnSkillQueueChanged(self):
        if self.destroyed:
            return
        self.UpdateGaugeProgress()
        for milestoneIndicator in self.milestoneIndicators.values():
            milestoneIndicator.UpdateProgress()

    def OnSkillPlanSaved(self, skillPlan):
        if self.skillPlan and self.skillPlan.GetID() == skillPlan.GetID():
            self.SetSkillPlan(skillPlan)

    @property
    def maxHeight(self):
        return ReverseScaleDpi(self.parent.displayWidth)
