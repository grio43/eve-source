#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\trainingOverviewPanel\trainingOverviewPanel.py
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveicon
import uthread2
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.skillPlan import skillPlanUISignals
from eve.client.script.ui.skillPlan.controls.milestoneIndicatorHeader import MilestoneIndicatorHeader
from eve.client.script.ui.skillPlan.milestone.skillPlanProgressIndicator import SkillPlanProgressIndicator
from eve.client.script.ui.skillPlan.skillQueuePanel.skillQueuePanelNew import SkillQueuePanelNew
from localization import GetByLabel
from skills.skillplan import skillPlanSignals
from skills.skillplan.skillPlanService import GetSkillPlanSvc

class TrainingOverviewPanel(Container):

    def ApplyAttributes(self, attributes):
        super(TrainingOverviewPanel, self).ApplyAttributes(attributes)
        self.skillPlan = None
        skillPlanSignals.on_tracked_plan_changed.connect(self.OnTrackedPlanChanged)
        skillPlanSignals.on_deleted.connect(self.OnSkillPlanDeleted)
        self.trackedCont = Container(name='trackedCont', parent=self, align=uiconst.TOTOP_PROP, height=0.4)
        self.skillPlanProgressIndicator = None
        self.skillQueue = SkillQueuePanelNew(parent=self, align=uiconst.TOALL, uniqueUiName=pConst.UNIQUE_NAME_SKILLQUEUE)
        uthread2.start_tasklet(self.InitializeTrackedPlan)

    def OnSkillPlanDeleted(self, skillPlanID):
        if self.skillPlan and self.skillPlan.GetID() == skillPlanID:
            self.SetSkillPlan(None)

    def InitializeTrackedPlan(self):
        skillPlan = GetSkillPlanSvc().GetTrackedSkillPlan()
        if skillPlan:
            self.trackedCont.Show()
            uthread2.start_tasklet(self.SetSkillPlan, skillPlan)
        else:
            self.trackedCont.Hide()

    def CheckConstructTrackedCont(self):
        if not self.skillPlanProgressIndicator:
            self.headerCont = MilestoneIndicatorHeader(parent=self.trackedCont, align=uiconst.TOTOP, captionText=GetByLabel('UI/SkillPlan/TrackedSkillPlan'), highlightNotInTraining=True)
            self.headerCont.OnClick = self.OnSkillPlanNameClicked
            untrackButtonCont = Container(parent=self.trackedCont, name='untrackButtonCont', align=uiconst.TOBOTTOM, height=36, padBottom=4)
            self.untrackButton = Button(name='untrackButton', parent=untrackButtonCont, align=uiconst.CENTER, texturePath=eveicon.camera_untrack, iconSize=20, hint=GetByLabel('UI/SkillPlan/UntrackPlanHint'), func=self._OnUntrackButtonClicked)
            self.skillPlanProgressIndicator = SkillPlanProgressIndicator(parent=self.trackedCont, align=uiconst.TOALL, highlightNotInTraining=True, tooltipDirection=uiconst.POINT_LEFT_2, padBottom=10)

    def _OnUntrackButtonClicked(self, *args):
        if self.skillPlan:
            if GetSkillPlanSvc().IsSkillPlanTracked(self.skillPlan.GetID()):
                if uicore.Message('AskUntrackPlan', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                    GetSkillPlanSvc().SetTrackedSkillPlanID(None)

    def OnSkillPlanNameClicked(self, *args):
        if self.skillPlan:
            skillPlanUISignals.on_selected(self.skillPlan)

    def OnTrackedPlanChanged(self, _, skillPlan):
        if self.destroyed:
            return
        self.SetSkillPlan(skillPlan)
        animations.FadeTo(self.trackedCont, 0.0, 1.0, duration=0.6)

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan
        if skillPlan is not None:
            self.CheckConstructTrackedCont()
            self.trackedCont.Show()
            self.skillPlanProgressIndicator.SetSkillPlan(skillPlan)
            self.headerCont.SetSkillPlanName(skillPlan.GetName())
        elif self.trackedCont:
            self.trackedCont.Hide()
            self.skillPlanProgressIndicator.ClearSkillPlan()
