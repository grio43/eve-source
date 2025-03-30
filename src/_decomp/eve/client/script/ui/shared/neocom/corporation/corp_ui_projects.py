#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corp_ui_projects.py
from carbonui import uiconst, ButtonVariant
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from corporation.client.goals import goalSignals
from corporation.client.goals.goalDetailsCont import GoalDetailsCont
from corporation.client.goals.goalDetailsWnd import GoalDetailsWnd
from eve.client.script.ui.shared.neocom.corporation.corp_goals.goalsBrowser import GoalsBrowser
from jobboard.client.feature_flag import is_job_board_available, are_goals_in_job_board_available
from localization import GetByLabel
from signals import Signal

class OverlayCont(Container):

    def ApplyAttributes(self, attributes):
        super(OverlayCont, self).ApplyAttributes(attributes)
        self.on_back = Signal('on_back')
        self.topCont = ContainerAutoSize(name='topCont', parent=self, align=uiconst.TOTOP, height=20, padTop=8)
        Button(name='backBtn', parent=self.topCont, func=self.on_back, label=GetByLabel('UI/Commands/Back'), variant=ButtonVariant.GHOST, align=uiconst.TOPLEFT)
        self.content = Container(name='content', parent=self, padTop=16)

    def Hide(self, *args):
        super(OverlayCont, self).Hide(*args)
        self.content.Flush()

    def OnBack(self, *args):
        self.on_back()


class CorpUIProjects(Container):
    is_loaded = False

    def Load(self, panel_id, job_id = None, *args):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
        if job_id:
            self.ShowSelectedDetails(job_id)

    def construct_layout(self):
        self.on_display_changed.connect(self.UnloadPanel)
        goalSignals.on_view_details.connect(self.OnViewGoalDetails)
        self.selectedGoalOverlay = None
        self.overlay = OverlayCont(name='overlay', state=uiconst.UI_HIDDEN, parent=self)
        self.overlay.on_back.connect(self.OnOverlayBackBtn)
        self.goalsBrowser = GoalsBrowser(parent=self)

    def OnViewGoalDetails(self, job_id):
        self.ShowSelectedDetails(job_id)

    def ShowSelectedDetails(self, job_id):
        if not is_job_board_available() or not are_goals_in_job_board_available():
            uicore.Message('ServiceUnavailable')
            return
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            GoalDetailsWnd.Open(job_id=job_id, windowInstanceID=job_id)
        else:
            self.overlay.state = uiconst.UI_PICKCHILDREN
            self.overlay.content.Flush()
            detailsCont = GoalDetailsCont(parent=self.overlay.content, job_id=job_id)
            self.goalsBrowser.Hide()
            detailsCont.on_close.connect(self.HideOverlayPanel)

    def OnOverlayBackBtn(self, *args):
        self.HideOverlayPanel()

    def HideOverlayPanel(self, *args):
        self.goalsBrowser.Show()
        self.overlay.Hide()

    def UnloadPanel(self, *args):
        self.HideOverlayPanel()
