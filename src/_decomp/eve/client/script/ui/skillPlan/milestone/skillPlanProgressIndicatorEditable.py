#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\milestone\skillPlanProgressIndicatorEditable.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.util.color import Color
from carbonui.util.various_unsorted import IsUnder
from eve.client.script.ui import eveColor
from eve.client.script.ui.skillPlan import skillPlanUISignals, skillPlanUtil
from eve.client.script.ui.skillPlan.milestone.milestoneTooltips import AddMilestonesTooltip
from eve.client.script.ui.skillPlan.milestone.milestoneProgressIndicator import MilestoneProgressIndicator
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressIndicator import SkillPlanProgressIndicator
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressGauge import SkillPlanProgressGauge
from eveui import Sprite
from signals import Signal
from skills.skillplan.milestone.milestoneController import MilestoneType
from carbonui.uicore import uicore
OPACITY_IDLE = 0.1
START_ANGLE_BY_NUM_MILESTONES = (0,
 -math.pi / 6,
 0,
 math.pi / 10,
 math.pi / 10)

class SkillPlanProgressIndicatorEditable(SkillPlanProgressIndicator):

    def ApplyAttributes(self, attributes):
        super(SkillPlanProgressIndicatorEditable, self).ApplyAttributes(attributes)
        self.onMilestoneDataDroppedSignal = Signal('onMilestoneDataDroppedSignal')
        skillPlanUISignals.on_milestone_added.connect(self.OnMilestoneAdded)
        skillPlanUISignals.on_milestone_removed.connect(self.OnMilestoneRemoved)
        self.tooltipPanelClassInfo = AddMilestonesTooltip()
        self.ConstructEmptyMilestone()
        self.defaultStateCont = Container()

    def GetTooltipDelay(self):
        return 0

    def OnMilestoneAdded(self, skillPlanID, milestoneID):
        if skillPlanID != self.skillPlan.GetID():
            return
        self.ReconstructMilestones()
        self.UpdateMilestonePositions()

    def OnMilestoneRemoved(self, skillPlanID, milestoneID):
        if skillPlanID != self.skillPlan.GetID():
            return
        self.ReconstructMilestones()
        self.UpdateMilestonePositions()

    def OnMouseEnter(self, *args):
        if self.defaultStateCont.display:
            self.defaultStateCont.OnMouseEnter()

    def OnMouseExit(self, *args):
        if self.plusIcon.display:
            self.plusIcon.OnDragExit()

    def OnDragEnter(self, dragSource, dragData):
        dragData = dragData[0]
        if self.plusIcon.display:
            if self.IsValidDragData(dragData):
                self.plusIcon.OnDragEnter()
            else:
                self.plusIcon.OnDragEnterInvalid()

    def IsValidDragData(self, dragData):
        typeID, level = skillPlanUtil.GetDragDataTypeIDAndLevel(dragData)
        if not skillPlanUtil.IsTypeValidMilestone(typeID):
            return
        if typeID is None:
            return False
        for milestone in self.skillPlan.GetMilestones().values():
            if milestone.GetMilestoneType() == MilestoneType.TYPE_ID_MILESTONE and milestone.GetTypeID() == typeID:
                return False
            if milestone.GetMilestoneType() == MilestoneType.SKILL_REQUIREMENT_MILESTONE and milestone.GetData() == (typeID, level):
                return False

        return True

    def ConstructProgressGauge(self):
        radius = self.GetOuterRadius()
        self.progressGauge = SkillPlanProgressGauge(parent=self.mainCont, align=uiconst.TOALL, radius=radius, highlightNotInTraining=self.highlightNotInTraining, controller=self.skillPlan)

    def OnDragExit(self, dragSource, dragData):
        if IsUnder(uicore.uilib.mouseOver, self):
            return
        if self.plusIcon:
            self.plusIcon.OnDragExit()

    def OnDropData(self, dragSource, dragData):
        return self._OnDataDropped(dragData)

    def _OnDataDropped(self, dragData, milestoneID = None):
        dragData = dragData[0]
        typeID, level = skillPlanUtil.GetDragDataTypeIDAndLevel(dragData)
        if typeID is None or not skillPlanUtil.IsTypeValidMilestone(typeID):
            eve.Message('CantAddAsMilestone')
        elif typeID:
            self.onMilestoneDataDroppedSignal(typeID, level, milestoneID)
        if self.plusIcon:
            self.plusIcon.OnDragExit()

    def OnDataDroppedOnTypeIndicator(self, dragSource, dragData, milestoneID):
        return self._OnDataDropped(dragData, milestoneID)

    def UpdateMilestonePositions(self):
        super(SkillPlanProgressIndicatorEditable, self).UpdateMilestonePositions()
        self.UpdatePlusIconPosition()

    def UpdatePlusIconPosition(self):
        numMilestones = len(self.milestoneIndicators)
        if numMilestones == 5:
            self.plusIcon.Hide()
        elif numMilestones == 0:
            self.plusIcon.top = 0
            self.plusIcon.width = self.plusIcon.height = 114
            self.plusIcon.Show()
        else:
            self.plusIcon.width = self.plusIcon.height = 54
            self.plusIcon.top = self._GetMilestonePositionRadius(5, self.GetOuterRadius())
            self.plusIcon.Show()

    def _GetMilestonePosition(self, i, num, outerRadius):
        if num == 1:
            left = 0
            top = -0.25 * outerRadius
        else:
            if num < 5:
                num += 1
            angle = self._GetMilestoneAngle(i, num)
            posRadius = self._GetMilestonePositionRadius(num, outerRadius)
            left = posRadius * math.cos(angle)
            top = posRadius * math.sin(angle)
        return (left, top)

    def _GetMilestoneAngle(self, i, num):
        startAngle = START_ANGLE_BY_NUM_MILESTONES[num - 2]
        angle = startAngle - 2 * math.pi * i / float(num)
        return angle

    def _GetMilestoneIconRadius(self, num, radius):
        if num < 5:
            num += 1
        return super(SkillPlanProgressIndicatorEditable, self)._GetMilestoneIconRadius(num, radius)

    def AddMilestone(self, milestoneID):
        m = self.GetMilestoneIndicator(milestoneID)
        if m is not None:
            return
        milestone = self.skillPlan.GetMilestone(milestoneID)
        milestoneIndicator = MilestoneProgressIndicator(parent=self, align=uiconst.CENTER, milestone=milestone, skillPlan=self.skillPlan, isEditable=True, highlightNotInTraining=self.highlightNotInTraining)
        milestoneIndicator.on_data_dropped.connect(self.OnDataDroppedOnTypeIndicator)
        self.milestoneIndicators[milestoneID] = milestoneIndicator

    def ConstructEmptyMilestone(self):
        self.plusIcon = EmptySlot(name='plusIcon', parent=self.mainCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED)

    def _GetTrainingTimeLeftText(self):
        return self.skillPlan.GetTotalTrainingTimeText()


class EmptySlot(Container):
    default_width = 54
    default_height = 54

    def ApplyAttributes(self, attributes):
        super(EmptySlot, self).ApplyAttributes(attributes)
        Sprite(name='plusIcon', parent=self, align=uiconst.CENTER, pos=(0, 0, 12, 12), texturePath='res:/UI/Texture/Classes/SkillPlan/milestones/plus.png')
        self.bg = Sprite(name='bg', bgParent=self, texturePath='res:/UI/Texture/Classes/SkillPlan/milestones/plusIconBG.png', color=eveColor.SMOKE_BLUE, opacity=0.6)
        self.frame = Sprite(name='frame', bgParent=self, texturePath='res:/UI/Texture/Classes/SkillPlan/milestones/plusIconFrame.png', color=eveColor.CRYO_BLUE, opacity=1.0)

    def SetRadius(self, radius):
        self.width = self.height = radius

    def OnDragEnter(self):
        duration = 0.3
        animations.SpColorMorphTo(self.frame, self.frame.GetRGBA(), eveColor.WHITE, duration=duration)
        color = Color(*eveColor.CRYO_BLUE).SetOpacity(0.9).GetRGBA()
        animations.SpColorMorphTo(self.bg, self.bg.GetRGBA(), color, duration=duration)

    def OnDragEnterInvalid(self):
        duration = uiconst.TIME_ENTRY
        animations.SpColorMorphTo(self.frame, self.frame.GetRGBA(), eveColor.HOT_RED, duration=duration)
        color = Color(*eveColor.HOT_RED).SetOpacity(0.6).GetRGBA()
        animations.SpColorMorphTo(self.bg, self.bg.GetRGBA(), color, duration=duration)

    def OnDragExit(self):
        animations.SpColorMorphTo(self.frame, self.frame.GetRGBA(), eveColor.CRYO_BLUE, duration=uiconst.TIME_EXIT)
        color = Color(*eveColor.SMOKE_BLUE).SetOpacity(0.6).GetRGBA()
        animations.SpColorMorphTo(self.bg, self.bg.GetRGBA(), color, duration=uiconst.TIME_EXIT)
