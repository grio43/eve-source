#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\client\goals\goalDetailsCont.py
import eveicon
from carbonui import ButtonVariant, AxisAlignment
from carbonui.button.group import ButtonGroup
from carbonui.control.scroll import Scroll
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.container import Container
from eveformat import currency
from corporation.client.goals import goalSignals
from corporation.client.goals import goalsUtil
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.neocom.corporation.corp_goals.forms import goalForms
from jobboard.client import get_job_board_service
from jobboard.client.features.corporation_goals.page import CorporationGoalPage
from localization import GetByLabel
from signals import Signal

class GoalDetailsCont(Container):

    def ApplyAttributes(self, attributes):
        super(GoalDetailsCont, self).ApplyAttributes(attributes)
        job_id = attributes.job_id
        self.job = get_job_board_service().get_job(job_id)
        self.goalsController = CorpGoalsController.get_instance()
        self.buttonGroup = ButtonGroup(parent=self, button_alignment=AxisAlignment.END, padTop=16)
        self.ConstructTabs()
        self.ConstructButtons()
        self.on_close = Signal('on_close')
        goalSignals.on_deleted.connect(self._CheckClose)
        goalSignals.on_closed.connect(self._CheckClose)
        goalSignals.on_expired.connect(self._CheckClose)

    def Close(self):
        super(GoalDetailsCont, self).Close()
        goalSignals.on_deleted.disconnect(self._CheckClose)
        goalSignals.on_closed.disconnect(self._CheckClose)
        goalSignals.on_expired.disconnect(self._CheckClose)

    def _CheckClose(self, goal_id):
        if goal_id == self.job.goal_id:
            self.on_close()

    def ConstructButtons(self):
        if goalsUtil.CanAuthorGoals():
            self.buttonGroup.AddButton(GetByLabel('UI/Corporations/Goals/CloneProject'), lambda button: self._clone_goal(button), texturePath=eveicon.copy, variant=ButtonVariant.GHOST)
            if not self.job.goal.get_current_progress():
                self.buttonGroup.AddButton(GetByLabel('UI/Corporations/Goals/DeleteProject'), lambda button: self._delete_goal(button), texturePath=eveicon.trashcan, variant=ButtonVariant.GHOST)
            if self.job.goal.is_active():
                self.buttonGroup.AddButton(GetByLabel('UI/Corporations/Goals/CloseProject'), lambda button: self._close_goal(button), texturePath=eveicon.close, variant=ButtonVariant.GHOST)
                if self.job.goal.is_manual():
                    self.buttonGroup.AddButton(GetByLabel('UI/Corporations/Goals/SetProgress'), lambda *args: goalForms.OpenSetGoalProgressFormWindow(self.job.goal))

    def _close_goal(self, button):
        button.Disable()
        button.busy = True
        try:
            self.goalsController.close_goal(self.job.goal_id)
        finally:
            button.Enable()
            button.busy = False

    def _delete_goal(self, button):
        button.Disable()
        button.busy = True
        try:
            self.goalsController.delete_goal(self.job.goal_id)
        finally:
            button.Enable()
            button.busy = False

    def _clone_goal(self, button):
        button.Disable()
        button.busy = True
        try:
            goalForms.OpenDuplicateGoalFormWindow(self.job.goal)
        finally:
            button.Enable()
            button.busy = False

    def ConstructTabs(self):
        self.tabGroup = TabGroup(parent=self)
        detailsPanel = CorporationGoalPage(self.job, show_related=False, parent=self)
        participantsPanel = ParticipantsPanel(parent=self, goal=self.job.goal)
        self.tabGroup.AddTab(GetByLabel('UI/Corporations/Goals/ProjectDetails'), panel=detailsPanel)
        self.tabGroup.AddTab(GetByLabel('UI/Corporations/Goals/Contributions'), panel=participantsPanel)
        self.tabGroup.AutoSelect()


class ParticipantEntry(Generic):
    isDragObject = True

    def Load(self, node):
        super(ParticipantEntry, self).Load(node)
        self.contributor_id = node.contributor_id

    def GetDragData(self):
        from carbonui.control.dragdrop.dragdata import OwnerDragData
        return [OwnerDragData(self.contributor_id)]

    def GetMenu(self):
        return sm.GetService('menu').GetMenuForOwner(self.contributor_id)


class ParticipantsPanel(Container):

    def ApplyAttributes(self, attributes):
        super(ParticipantsPanel, self).ApplyAttributes(attributes)
        self.goal = attributes.goal

    def LoadPanel(self):
        self.Flush()
        self.scroll = Scroll(parent=self, id='project_participants')
        if self.goal.get_participation_limit():
            self.ConstructLimitedEntries()
        else:
            self.ConstructEntries()

    def ConstructEntries(self):
        self.scroll.Clear()
        entries = []
        summaries = CorpGoalsController.get_instance().get_all_goal_contributor_summaries(self.goal.get_id())
        desired_progress = self.goal.get_desired_progress()
        total_isk = self.goal.get_total_isk()
        for contributor_id, contribution_amount in summaries:
            contributor_name = cfg.eveowners.Get(contributor_id).ownerName
            progress_ratio = float(contribution_amount) / desired_progress
            payout = currency.isk(progress_ratio * total_isk)
            data = {'label': u'{}<t>{}<t>{:.1f}%<t>{}'.format(contributor_name, contribution_amount, progress_ratio * 100, payout),
             'sortValues': (contributor_name, contribution_amount),
             'contributor_id': contributor_id}
            entry = GetFromClass(ParticipantEntry, data)
            entries.append(entry)

        self.scroll.LoadContent(contentList=entries, headers=(GetByLabel('UI/Corporations/Goals/Contributor'),
         GetByLabel('UI/Corporations/Goals/TotalAmount'),
         GetByLabel('UI/Corporations/Goals/OfTargetValue'),
         GetByLabel('UI/Corporations/Goals/ISKPayout')), noContentHint=GetByLabel('UI/Corporations/Goals/NoContributionsFound'))

    def ConstructLimitedEntries(self):
        self.scroll.Clear()
        entries = []
        summaries = CorpGoalsController.get_instance().get_all_goal_contributor_summaries(self.goal.get_id())
        desired_progress = self.goal.get_desired_progress()
        participation_limit = self.goal.get_participation_limit()
        total_isk = self.goal.get_total_isk()
        for contributor_id, contribution_amount in summaries:
            contributor_name = cfg.eveowners.Get(contributor_id).ownerName
            progress_ratio = float(contribution_amount) / desired_progress
            personal_progress_ratio = float(contribution_amount) / participation_limit
            payout = currency.isk(progress_ratio * total_isk)
            data = {'label': u'{}<t>{}<t>{:.1f}%<t>{:.1f}%<t>{}'.format(contributor_name, contribution_amount, progress_ratio * 100, personal_progress_ratio * 100, payout),
             'sortValues': (contributor_name, contribution_amount),
             'contributor_id': contributor_id}
            entry = GetFromClass(ParticipantEntry, data)
            entries.append(entry)

        self.scroll.LoadContent(contentList=entries, headers=(GetByLabel('UI/Corporations/Goals/Contributor'),
         GetByLabel('UI/Corporations/Goals/TotalAmount'),
         GetByLabel('UI/Corporations/Goals/OfTargetValue'),
         GetByLabel('UI/Corporations/Goals/OfPersonalTarget'),
         GetByLabel('UI/Corporations/Goals/ISKPayout')), noContentHint=GetByLabel('UI/Corporations/Goals/NoContributionsFound'))
