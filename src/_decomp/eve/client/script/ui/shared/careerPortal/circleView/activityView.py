#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\activityView.py
import carbonui.const as uiconst
import eve.client.script.ui.shared.careerPortal.careerConst as careerConst
import careergoals.client.const as careerGoalsConst
import telemetry
from carbonui.uianimations import animations
from carbonui.util.dpi import ScaleDpi
from eve.client.script.ui.shared.careerPortal import cpSignals
from eve.client.script.ui.shared.careerPortal.circleView.activityNode import ActivityNodeObject, ActivityNode
from eve.client.script.ui.shared.careerPortal.circleView.circleView import CircleView, CircleViewContainer
OUTSIDE_SCALE = (1.3, 1.3)
MAXIMIZED_SCALE = (1.0, 1.0)
MINIMIZED_SCALE = (0.65, 0.65)
OPACITY_BY_STATE = {careerConst.ActivitiesViewState.IN_FOCUS: 1,
 careerConst.ActivitiesViewState.ONE_DOWN: 0.5,
 careerConst.ActivitiesViewState.HIDDEN: 0.0}
CIRCLE_HOVER_OPACITY = 1.0
NODE_SIZE = 48

class ActivityView(CircleViewContainer):
    default_name = 'ActivityView'
    currentState = None

    def CreateCircleView(self, *args, **kwargs):
        return ActivityCircleView(parent=self, *args, **kwargs)

    def GetSignals(self):
        signals = super(ActivityView, self).GetSignals()
        signals.extend([(careerConst.CAREER_WINDOW_STATE_SETTING.on_change, self.OnCareerWindowStateChanged), (cpSignals.on_career_node_hover_on, self.OnCareerNodeHoverOn), (cpSignals.on_career_node_hover_off, self.OnCareerNodeHoverOff)])
        return signals

    def OnCareerWindowStateChanged(self, state, animate = True):
        if state == careerConst.CareerWindowState.CAREERS_VIEW:
            self.AnimateOut()
            self.circleView.innerCircles.ScaleUp()
        elif state == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self.LoadActivities()
            if self.currentState == careerConst.CareerWindowState.GOALS_VIEW:
                self.Maximize()
            else:
                self.AnimateIn()
        elif state == careerConst.CareerWindowState.GOALS_VIEW:
            self.LoadActivities()
            self.Minimize()
            animations.FadeOut(self.circleView.innerCircles, duration=0.4)
            animations.FadeOut(self.circleView.fill, duration=0.4)
            animations.FadeIn(self, duration=0.4)
        self.currentState = state

    def OnCareerNodeHoverOn(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self.circleView.innerCircles.ScaleDown()
            animations.FadeOut(self.circleView.fill, duration=0.4)
            animations.FadeTo(self, startVal=self.opacity, endVal=0.3, duration=0.4)
        elif currentState == careerConst.CareerWindowState.GOALS_VIEW:
            animations.FadeIn(self.circleView.innerCircles, duration=0.4)
            animations.FadeIn(self.circleView.outerCircle, duration=0.4)
            animations.FadeIn(self.circleView.fill, endVal=0.5, duration=0.4)

    def OnCareerNodeHoverOff(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self.circleView.innerCircles.ScaleUp()
            animations.FadeTo(self.circleView.fill, startVal=0, endVal=0.4, duration=0.4)
            animations.FadeIn(self, duration=0.4)
        elif currentState == careerConst.CareerWindowState.GOALS_VIEW:
            animations.FadeOut(self.circleView.innerCircles, duration=0.4)
            animations.FadeTo(self.circleView.outerCircle, startVal=self.circleView.outerCircle.opacity, endVal=0.25, duration=0.4)
            animations.FadeOut(self.circleView.fill, duration=0.4)

    def Minimize(self):
        animations.Tr2DScaleTo(self.circleView, startScale=self.circleView.scale, endScale=MINIMIZED_SCALE)
        self.circleView.outerCircle.outputMode = uiconst.OUTPUT_COLOR
        animations.FadeTo(self.circleView.outerCircle, startVal=1, endVal=0.25, duration=0.5, curveType=uiconst.ANIM_SMOOTH)

    def Maximize(self):
        animations.Tr2DScaleTo(self.circleView, startScale=self.circleView.scale, endScale=MAXIMIZED_SCALE)
        self.circleView.outerCircle.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
        animations.FadeTo(self.circleView.outerCircle, startVal=0.25, endVal=1, duration=0.5, curveType=uiconst.ANIM_SMOOTH)
        animations.FadeTo(self.circleView.fill, startVal=0, endVal=0.25, duration=1.5, timeOffset=0.4, curveType=uiconst.ANIM_OVERSHOT3)

    def AnimateIn(self):
        self.Show()
        animations.FadeIn(self, duration=1)
        animations.Tr2DScaleTo(self.circleView, startScale=(1.3, 1.3), endScale=MAXIMIZED_SCALE)
        animations.FadeTo(self.circleView.outerCircle, startVal=0.5, endVal=1, duration=0.5, curveType=uiconst.ANIM_SMOOTH, timeOffset=0.6)
        animations.FadeTo(self.circleView.fill, startVal=0, endVal=0.25, duration=1.5, timeOffset=0.4, curveType=uiconst.ANIM_OVERSHOT3)
        self.circleView.outerCircle.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW

    def AnimateOut(self):
        animations.FadeOut(self, callback=self.Hide)
        animations.Tr2DScaleTo(self.circleView, startScale=MAXIMIZED_SCALE, endScale=OUTSIDE_SCALE)

    @telemetry.ZONE_METHOD
    def LoadActivities(self):
        selectedPath = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        activities = careerGoalsConst.CAREER_PATH_GROUPS.get(selectedPath, [])
        if not activities:
            return
        if set(activities.values()) == set(self.nodesByID.keys()):
            return
        self.circleView.Reset()
        self.nodesByID.clear()
        windowState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        for idx, activityID in enumerate(activities.itervalues()):
            nodeObject = ActivityNodeObject(selectedPath, activityID)
            node = ActivityNode(name='activityNode_%s' % activityID, nodeObject=nodeObject, highlight=activityID in careerConst.HIGHLIGHTED_ACTIVITIES[selectedPath], initialState=windowState)
            self.circleView.AddNode(node)
            self.nodesByID[activityID] = node

        self.circleView.UpdateCircle()


class ActivityCircleView(CircleView):

    def GetNodeSize(self):
        return ScaleDpi(NODE_SIZE)
