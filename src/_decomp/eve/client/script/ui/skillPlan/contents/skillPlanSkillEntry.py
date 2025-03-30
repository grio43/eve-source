#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\contents\skillPlanSkillEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.skillPlan.scrollContEntry import ScrollContEntry
from eve.client.script.ui.skillPlan.skillPlanConst import REQUIRED_FOR, IS_PREREQ, NO_REQ
from skills.client.skillController import SkillController

class SkillPlanSkillEntry(ScrollContEntry):
    default_name = 'SkillPlanSkillEntry'
    default_height = 32
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(SkillPlanSkillEntry, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.level = attributes.level
        self.controller = SkillController(self.typeID)
        self.reqState = NO_REQ
        self.skillBar = SkillBar(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=8, skillID=self.typeID, requiredLevel=self.level)
        labelCont = Container(parent=self, padLeft=75)
        EveLabelLarge(parent=labelCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=self.controller.GetRequiredSkillNameAndLevelComparedToTrainedLevel(self.level), autoFadeSides=True, top=-1)
        trainingTimeLabelParent = ContainerAutoSize(parent=self, align=uiconst.TORIGHT, padding=(12, 0, 12, 0), idx=0)
        self.trainingTimeLabel = EveLabelLarge(parent=trainingTimeLabelParent, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, top=-1, text=self.controller.GetTrainingTimeForLevelText(self.level), opacity=0.35, idx=-1)

    def UpdateReqState(self, reqState):
        if reqState in (IS_PREREQ, REQUIRED_FOR):
            self.underlay.is_dependency_or_requirement = True
        else:
            self.underlay.is_dependency_or_requirement = False
        self.reqState = reqState

    def ConstructUnderlay(self):
        self.underlay = SkillEntryUnderlay(bgParent=self, padRight=42, padBottom=0)

    def GetDragData(self):
        return self.skillBar.GetDragData()

    def GetHint(self):
        return self.skillBar.GetHint()

    def GetMenu(self):
        return self.skillBar.GetMenu()

    def Refresh(self):
        self.skillBar.Refresh()

    def OnDblClick(self):
        sm.GetService('info').ShowInfo(self.typeID)


class SkillEntryUnderlay(ListEntryUnderlay):
    _is_dependency_or_requirement = False

    @property
    def is_dependency_or_requirement(self):
        return self._is_dependency_or_requirement

    @is_dependency_or_requirement.setter
    def is_dependency_or_requirement(self, value):
        if self._is_dependency_or_requirement != value:
            self._is_dependency_or_requirement = value
            self._update_color(animate=True)
            self._update_opacity(animate=True)

    def _get_opacity(self):
        if self._is_dependency_or_requirement:
            return self.OPACITY_HOVER
        else:
            return super(SkillEntryUnderlay, self)._get_opacity()
