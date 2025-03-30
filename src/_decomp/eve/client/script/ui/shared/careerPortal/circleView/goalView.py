#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\goalView.py
import carbonui.const as uiconst
import eve.client.script.ui.shared.careerPortal.careerConst as careerConst
import uthread2
from carbonui.uianimations import animations
from carbonui.util.dpi import ScaleDpi
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui.shared.careerPortal import cpSignals
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.circleView.circleView import CircleView, CircleViewContainer
from eve.client.script.ui.shared.careerPortal.circleView.goalNode import GoalNode
BTN_CONT_HEIGHT = 30
EXTRA_TEXT_PADDING = 6
WRAP_BUFFER = EXTRA_TEXT_PADDING + 6
PROP_SIZE_BY_STATE = {careerConst.GoalsViewState.IN_FOCUS: 0.7,
 careerConst.GoalsViewState.HIDDEN: 1.0}
OPACITY_BY_STATE = {careerConst.GoalsViewState.IN_FOCUS: 1,
 careerConst.GoalsViewState.HIDDEN: 0.0}
NODE_SIZE = 48

class GoalView(CircleViewContainer):

    def ApplyAttributes(self, attributes):
        self.currentState = None
        super(GoalView, self).ApplyAttributes(attributes)

    def CreateCircleView(self, *args, **kwargs):
        return GoalCircleView(parent=self, *args, **kwargs)

    def GetSignals(self):
        signals = super(GoalView, self).GetSignals()
        signals.extend([(cpSignals.on_activity_circle_one_down_hover_on, self.OnActivityCircleHoverOn),
         (cpSignals.on_activity_circle_one_down_hover_off, self.OnActivityCircleHoverOff),
         (cpSignals.on_clicked_outside, self.OnClickedOutside),
         (cpSignals.on_career_node_hover_on, self.OnCareerNodeHoverOn),
         (cpSignals.on_career_node_hover_off, self.OnCareerNodeHoverOff)])
        return signals

    def OnCareerNodeHoverOn(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.GOALS_VIEW:
            return
        self.circleView.innerCircles.ScaleDown()
        animations.FadeOut(self.circleView.fill, duration=0.4)
        animations.FadeTo(self, startVal=self.opacity, endVal=0.3, duration=0.4)

    def OnCareerNodeHoverOff(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.GOALS_VIEW:
            return
        self.circleView.innerCircles.ScaleUp()
        animations.FadeIn(self.circleView.fill, endVal=0.5, duration=0.4)
        animations.FadeIn(self, duration=0.4)

    def OnCareerWindowStateChanged(self, state, animate = True):
        if state in [careerConst.CareerWindowState.CAREERS_VIEW, careerConst.CareerWindowState.ACTIVITIES_VIEW]:
            self.AnimateOut()
        elif state == careerConst.CareerWindowState.GOALS_VIEW:
            self.LoadGoals()
            self.AnimateIn()

    def LoadGoals(self):
        selectedPath = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        selectedActivity = careerConst.SELECTED_ACTIVITY_SETTING.get()
        goals = get_career_goals_svc().get_goal_data_controller().get_goals_in_group(selectedPath, selectedActivity)
        self.circleView.Reset()
        for i, goal in enumerate(goals):
            node = GoalNode(goal=goal)
            self.circleView.AddNode(node)

        self.circleView.UpdateCircle()

    def AnimateIn(self):
        self.Show()
        animations.FadeIn(self, duration=1)
        animations.Tr2DScaleTo(self.circleView, startScale=(1.4, 1.4), endScale=(1.0, 1.0))
        animations.FadeTo(self.circleView.fill, startVal=0, endVal=0.5, duration=1.5, timeOffset=0.4, curveType=uiconst.ANIM_OVERSHOT3)

    def AnimateOut(self):
        if self.opacity <= 0:
            self.Hide()
            return
        animations.FadeOut(self, callback=self.Hide)
        animations.Tr2DScaleTo(self.circleView, startScale=(1.0, 1.0), endScale=(1.4, 1.4))

    def OnActivityCircleHoverOn(self):
        self.circleView.SetArcOpacity(1.0, careerConst.HOVER_ANIMATION_DURATION)

    def OnActivityCircleHoverOff(self):
        self.circleView.SetArcOpacity(self.circleView.default_arc_opacity, careerConst.HOVER_ANIMATION_DURATION)

    def OnClickedOutside(self):
        if self.currentState == careerConst.GoalsViewState.IN_FOCUS:
            get_career_portal_controller_svc().select_goal(None)


class GoalCircleView(CircleView):
    flairCircle = None

    def UpdateCircle(self):
        super(GoalCircleView, self).UpdateCircle()

    def GetNodeSize(self):
        return ScaleDpi(NODE_SIZE)

    def ConstructOuterCircle(self, radius):
        super(GoalCircleView, self).ConstructOuterCircle(radius)
        self.outerCircle.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
