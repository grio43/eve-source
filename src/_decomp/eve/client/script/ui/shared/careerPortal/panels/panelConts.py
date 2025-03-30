#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\panels\panelConts.py
import uthread2
from carbonui import uiconst, const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal import careerConst, cpSignals
from eve.client.script.ui.shared.careerPortal.panels.auraCareerAssistancePanel import AuraCareerAssistancePanel
from eve.client.script.ui.shared.careerPortal.panels.auraVideoAssistancePanel import AuraVideoAssistancePanel
from eve.client.script.ui.shared.careerPortal.panels.careerDetailsPanel import CareerDetailsPanel
from eve.client.script.ui.shared.careerPortal.panels.goalDetailsPanel import GoalPanel, AuraGoalPanel
from eveexceptions import EatsExceptions
PANEL_ANIMATION_OFFSET = 100

class BasePanelContainer(ContainerAutoSize):
    default_align = uiconst.TOTOP_NOPUSH
    default_alignMode = uiconst.TOTOP
    panels = []

    def __init__(self, initialState, *args, **kwargs):
        super(BasePanelContainer, self).__init__(*args, **kwargs)
        self.ConnectToSignals()
        self.OnCareerWindowStateChanged(initialState)

    @EatsExceptions('BasePanelContainer::ConnectToSignals')
    def ConnectToSignals(self):
        for signal, callback in self._GetSignals():
            signal.connect(callback)

    @EatsExceptions('BasePanelContainer::DisconnectFromSignals')
    def DisconnectFromSignals(self):
        for signal, callback in self._GetSignals():
            signal.disconnect(callback)

    def Close(self):
        self.DisconnectFromSignals()
        super(BasePanelContainer, self).Close()

    def _ConstructPanels(self):
        raise NotImplementedError

    def _GetSignals(self):
        return [(cpSignals.on_clicked_outside, self.OnClickedOutside), (careerConst.CAREER_WINDOW_STATE_SETTING.on_change, self.OnCareerWindowStateChanged)]

    def OnClickedOutside(self):
        self.AnimateOut()

    def OnCareerWindowStateChanged(self, newState):
        raise NotImplementedError

    def AnimateIn(self):
        timeOffset = 0
        self.parent.parent.parent.Enable()
        for panel in self.panels:
            panel.StopAnimations()
            panel.Show()
            panel.SetState(uiconst.UI_NORMAL)
            animations.FadeIn(panel, duration=0.75)
            animations.MorphScalar(panel, 'left', startVal=PANEL_ANIMATION_OFFSET, endVal=0, duration=0.4, timeOffset=timeOffset, curveType=uiconst.ANIM_SMOOTH)
            timeOffset += 0.2

    def AnimateOut(self, callback = None):
        timeOffset = 0
        for panel in self.panels:
            panel.StopAnimations()
            panel.SetState(uiconst.UI_DISABLED)
            animations.FadeOut(panel, duration=0.5, callback=panel.Hide)
            animations.MorphScalar(panel, 'left', startVal=0, endVal=PANEL_ANIMATION_OFFSET, duration=0.4, timeOffset=timeOffset, curveType=uiconst.ANIM_SMOOTH, callback=callback)
            timeOffset += 0.1


class ActivityViewPanels(BasePanelContainer):
    default_name = 'ActivityViewPanels'

    def _ConstructPanels(self):
        if self.panels:
            return
        careerDetailsPanel = CareerDetailsPanel(parent=self, color=eveColor.Color(eveColor.CRYO_BLUE).SetOpacity(0.8).GetRGBA(), bgColor=eveColor.Color(eveColor.CRYO_BLUE).SetBrightness(0.05).SetOpacity(0.9).GetRGBA())
        auraPanel = AuraCareerAssistancePanel(parent=self, color=eveColor.Color(eveColor.AURA_PURPLE).SetOpacity(0.8).GetRGBA(), bgColor=eveColor.Color(eveColor.AURA_PURPLE).SetBrightness(0.05).SetOpacity(0.9).GetRGBA(), top=32)
        self.panels = [careerDetailsPanel, auraPanel]

    def OnCareerWindowStateChanged(self, newState):
        if newState == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self._ConstructPanels()
            self.AnimateIn()
        else:
            self.AnimateOut()


class GoalViewPanels(BasePanelContainer):
    default_name = 'GoalViewPanels'

    def _GetSignals(self):
        superSignals = super(GoalViewPanels, self)._GetSignals()
        superSignals.extend([(careerConst.SELECTED_GOAL_SETTING.on_change, self.OnGoalSelected)])
        return superSignals

    def _ConstructPanels(self):
        if self.panels:
            return
        self.auraPanel = AuraVideoAssistancePanel(parent=self, color=eveColor.Color(eveColor.AURA_PURPLE).SetOpacity(0.8).GetRGBA(), bgColor=eveColor.Color(eveColor.AURA_PURPLE).SetBrightness(0.05).SetOpacity(0.9).GetRGBA())
        self.panels = [self.auraPanel]

    def OnGoalSelected(self, goalID):
        if not goalID:
            return
        self.AnimateOut()

    def OnCareerWindowStateChanged(self, newState):
        selectedGoal = careerConst.SELECTED_GOAL_SETTING.get()
        goals_in_group = get_career_goals_svc().get_goal_data_controller().get_goals_in_group(careerConst.SELECTED_CAREER_PATH_SETTING.get(), careerConst.SELECTED_ACTIVITY_SETTING.get())
        goal_ids = [ g.goal_id for g in goals_in_group ]
        if newState == careerConst.CareerWindowState.GOALS_VIEW and selectedGoal not in goal_ids:
            self._ConstructPanels()
            self.auraPanel.LoadActivity(careerConst.SELECTED_ACTIVITY_SETTING.get())
            self.AnimateIn()
        else:
            self.AnimateOut()


class GoalDetailPanels(BasePanelContainer):
    default_name = 'GoalDetailPanels'
    _selectedGoal = None
    _loadingThread = None
    visible = False

    def __init__(self, *args, **kwargs):
        super(GoalDetailPanels, self).__init__(*args, **kwargs)
        self.OnGoalSelected(careerConst.SELECTED_GOAL_SETTING.get())

    def _ConstructPanels(self):
        if self.panels:
            return
        self.goalPanel = GoalPanel(parent=self, color=eveColor.Color(eveColor.CRYO_BLUE).SetOpacity(0.8).GetRGBA(), bgColor=eveColor.Color(eveColor.CRYO_BLUE).SetBrightness(0.05).SetOpacity(0.9).GetRGBA())
        self.auraGoalPanel = AuraGoalPanel(parent=self, top=24, color=eveColor.Color(eveColor.AURA_PURPLE).SetOpacity(0.8).GetRGBA(), bgColor=eveColor.Color(eveColor.AURA_PURPLE).SetBrightness(0.05).SetOpacity(0.9).GetRGBA())
        self.panels = [self.goalPanel, self.auraGoalPanel]

    def _GetSignals(self):
        superSignals = super(GoalDetailPanels, self)._GetSignals()
        superSignals.extend([(careerConst.SELECTED_GOAL_SETTING.on_change, self.OnGoalSelected)])
        return superSignals

    def OnCareerWindowStateChanged(self, state):
        if state != careerConst.CareerWindowState.GOALS_VIEW:
            self.AnimateOut()
            self.visible = False

    def OnClickedOutside(self):
        super(GoalDetailPanels, self).OnClickedOutside()
        self.visible = False

    def OnGoalSelected(self, goalID):
        if not goalID or careerConst.CAREER_WINDOW_STATE_SETTING.get() != careerConst.CareerWindowState.GOALS_VIEW:
            return
        self._ConstructPanels()
        if self._loadingThread is not None:
            self._loadingThread.Kill()
        if self.visible:
            self.AnimateOut(callback=lambda : uthread2.StartTasklet(self._SwitchGoal, goalID))
        else:
            self._LoadNewGoal(goalID)

    def _SwitchGoal(self, newGoalID):
        uthread2.Sleep(0.1)
        self._loadingThread = uthread2.StartTasklet(self.LoadDetails_thread, newGoalID)

    def _LoadNewGoal(self, goalID):
        self._loadingThread = uthread2.StartTasklet(self.LoadDetails_thread, goalID)

    def LoadDetails_thread(self, goal_id):
        goal = get_career_goals_svc().get_goal_data_controller().get_goal(goal_id)
        for panel in self.panels:
            panel.LoadGoal(goal)

        self.AnimateIn()
        self.visible = True
