#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\careerView.py
import math
import eve.client.script.ui.shared.careerPortal.careerConst as careerConst
import eveicon
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import TextAlign, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from characterdata import careerpathconst
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.shared.careerPortal import cpSignals
from eve.client.script.ui.shared.careerPortal.careerPointsLabel import CareerPointsLabel
from eve.client.script.ui.shared.careerPortal.circleView.careerNode import CareerNode, CareerNodeObject, NODE_MAX_SIZE
from eve.client.script.ui.shared.careerPortal.circleView.circleView import CircleView, CircleViewContainer
from eveui import Sprite
from localization import GetByLabel
CIRCLE_HOVER_OPACITY = 1.0
CENTRAL_ICON_BASE_WIDTH = 516
CENTRAL_ICON_BASE_HEIGHT = 360
SMALL_FONTSIZE = 18

class CareerView(CircleViewContainer):
    default_name = 'CareerView'
    default_opacity = 1
    activityViewCareerInfoTop = 0.67
    goalViewCareerInfoTop = 0.7

    def __init__(self, *args, **kwargs):
        self.careerInfoTop = 0.5
        super(CareerView, self).__init__(*args, **kwargs)
        self.circleView.OnCareerWindowStateChanged(self.initialState)

    def CreateCircleView(self, *args, **kwargs):
        return CareerCircleView(parent=self, *args, **kwargs)

    def GetSignals(self):
        signals = super(CareerView, self).GetSignals()
        signals.extend([(careerConst.CAREER_WINDOW_STATE_SETTING.on_change, self.OnCareerWindowStateChanged), (cpSignals.on_career_node_hover_on, self.OnCareerNodeHoverOn), (cpSignals.on_career_node_hover_off, self.OnCareerNodeHoverOff)])
        return signals

    def OnEndScale(self, wnd):
        super(CareerView, self).OnEndScale(wnd)
        w, _ = wnd.GetAbsoluteSize()
        if w < 1200:
            self.careerNameLabel.fontsize = SMALL_FONTSIZE
            self.activityNameLabel.fontsize = SMALL_FONTSIZE
            self.backLabel.fontsize = SMALL_FONTSIZE
        else:
            self.careerNameLabel.fontsize = self.careerNameLabel.default_fontsize
            self.activityNameLabel.fontsize = self.activityNameLabel.default_fontsize
            self.backLabel.fontsize = self.backLabel.default_fontsize
        self._UpdateCareerInfoTop()

    def OnCareerWindowStateChanged(self, newState, animate = True):
        selectedCareer = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        careerNode = self.nodesByID.get(selectedCareer, None)
        if newState == careerConst.CareerWindowState.CAREERS_VIEW:
            self._GoToCareerViewState()
            animations.FadeOut(self.backLabelCont, duration=0.4, callback=self.backLabelCont.Hide)
            return
        if careerNode:
            self.careerPointsLabel.careerNodeObject = careerNode.nodeObject
        self.careerNameLabel.text = careerConst.GetCareerPathName(selectedCareer)
        if newState == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            if not careerNode:
                return
            self.backLabel.text = GetByLabel('UI/CareerPortal/GoToCareerOverview')
            self._GoToActivityViewState(careerNode, animate)
        elif newState == careerConst.CareerWindowState.GOALS_VIEW:
            self.backLabel.text = GetByLabel('UI/CareerPortal/GoToActivities')
            self._GoToGoalViewState(animate, selectedCareer)
        else:
            return

    def _GoToCareerViewState(self):
        animations.FadeOut(self.careerInfoContainer, duration=0.2)

    def _GoToGoalViewState(self, animate, selectedCareer):
        selectedActivity = careerConst.SELECTED_ACTIVITY_SETTING.get()
        activityName = careerConst.GetCareerPathGroupName(selectedCareer, selectedActivity)
        self.careerNameLabel.bold = False
        self.activityNameLabel.text = activityName
        self._UpdateCareerInfoTop()
        if animate:
            if self.backLabelCont.IsHidden():
                self._UpdateCareerInfoContainer()
            animations.MorphScalar(self.activityNameLabel, 'top', startVal=self.activityNameLabel.top, endVal=0, duration=0.5)
            animations.FadeIn(self.activityNameLabel, duration=0.75)
        else:
            self.careerInfoContainer.opacity = 1
            self.activityNameLabel.top = 0
            self.activityNameLabel.opacity = 1

    def _UpdateCareerInfoContainer(self):
        self._UpdateCareerInfoTop()
        animations.MorphScalar(self.careerInfoContainer, 'top', startVal=self.careerInfoContainer.top, endVal=self.careerInfoTop, duration=0.5)
        animations.FadeIn(self.careerInfoContainer, duration=1.0)

    def _UpdateCareerInfoTop(self):
        windowState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if windowState == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self.careerInfoTop = self.activityViewCareerInfoTop
        elif windowState == careerConst.CareerWindowState.GOALS_VIEW:
            self.careerInfoTop = self.goalViewCareerInfoTop

    def _GoToActivityViewState(self, careerNode, animate):
        self.careerNameLabel.bold = True
        self.careerNameLabel.text = careerNode.nodeObject.careerPathName
        self._UpdateCareerInfoTop()
        if animate:
            if self.backLabelCont.IsHidden():
                self._UpdateCareerInfoContainer()
            animations.MorphScalar(self.activityNameLabel, 'top', startVal=self.activityNameLabel.top, endVal=-30, duration=0.5)
            animations.FadeOut(self.activityNameLabel, duration=0.5)
        else:
            self.careerInfoContainer.top = 0.61
            self.activityNameLabel.top = -30
            self.activityNameLabel.opacity = 0
            self.careerInfoContainer.opacity = 1

    def OnCareerNodeHoverOn(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState == careerConst.CareerWindowState.CAREERS_VIEW:
            return
        self._ShowBackLabel()

    def OnCareerNodeHoverOff(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState == careerConst.CareerWindowState.CAREERS_VIEW:
            return
        self._HideBackLabel()

    def _ShowBackLabel(self):
        animations.MorphScalar(self.careerInfoContainer, 'top', startVal=self.careerInfoContainer.top, endVal=self.careerInfoTop - 0.05, duration=0.4)
        animations.FadeOut(self.careerInfoContainer, duration=0.4)
        animations.MorphScalar(self.backLabelCont, 'top', startVal=self.backLabelCont.top, endVal=0.65, duration=0.4)
        animations.FadeIn(self.backLabelCont, duration=0.4)
        self.backLabelCont.Show()

    def _HideBackLabel(self):
        animations.MorphScalar(self.careerInfoContainer, 'top', startVal=self.careerInfoContainer.top, endVal=self.careerInfoTop, duration=0.4)
        animations.FadeIn(self.careerInfoContainer, duration=0.4)
        animations.MorphScalar(self.backLabelCont, 'top', startVal=self.backLabelCont.top, endVal=0.725, duration=0.4)
        animations.FadeOut(self.backLabelCont, duration=0.4, callback=self.backLabelCont.Hide)

    def PrepareUI(self):
        super(CareerView, self).PrepareUI()
        self.careerInfoContainer = ContainerAutoSize(name='careerInfoContainer', parent=self, align=uiconst.TOPLEFT_PROP, left=0.5, top=0.67, state=uiconst.UI_DISABLED, width=CENTRAL_ICON_BASE_WIDTH, opacity=0)
        self.careerNameLabel = EveCaptionLarge(name='careerNameLabel', parent=self.careerInfoContainer, textAlign=TextAlign.CENTER, align=uiconst.TOTOP, bold=True)
        self.activityNameLabel = EveCaptionLarge(name='activityNameLabel', parent=self.careerInfoContainer, textAlign=TextAlign.CENTER, align=uiconst.TOTOP, opacity=0, maxWidth=100, bold=True, text='---', top=-30)
        pointsContainer = Container(name='pointsContainer', parent=self.careerInfoContainer, align=uiconst.TOTOP, height=20)
        self.careerPointsLabel = CareerPointsLabel(parent=pointsContainer, careerNode=None, top=4)
        self.backLabelCont = ContainerAutoSize(name='backLabelCont', parent=self, align=uiconst.TOPLEFT_PROP, left=0.5, top=0.67, height=30, opacity=0)
        self.backLabelCont.Hide()
        Sprite(name='leftArrow', parent=Container(parent=self.backLabelCont, align=uiconst.TOLEFT, width=16, height=16), align=uiconst.CENTER, pos=(0, 0, 16, 16), texturePath=eveicon.chevron_left)
        self.backLabel = EveCaptionLarge(parent=ContainerAutoSize(parent=self.backLabelCont, align=uiconst.TOLEFT), name='backLabel', align=uiconst.CENTERLEFT, left=4, text='placeholder', state=uiconst.UI_DISABLED, bold=True)
        self._CreateCareerNodes()

    def _CreateCareerNodes(self):
        for idx, careerPathID in enumerate(careerConst.GetSortedCareerPaths()):
            nodeObject = CareerNodeObject(careerPathID)
            node = CareerNode(name='careerNode_%s' % careerPathID, nodeObject=nodeObject, initialState=self.initialState)
            self.circleView.AddNode(node)
            self.nodesByID[careerPathID] = node

        self.circleView.UpdateCircle()


class CareerCircleView(CircleView):
    default_arc_opacity = 1.0
    innerCircleTexturePath = 'res:/UI/Texture/classes/careerPortal/career_hover_inner_2px.png'

    def ApplyAttributes(self, attributes):
        super(CareerCircleView, self).ApplyAttributes(attributes)
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.connect(self.OnCareerWindowStateChanged)
        cpSignals.on_career_node_hover_on.connect(self.OnCareerNodeHoverOn)
        cpSignals.on_career_node_hover_off.connect(self.OnCareerNodeHoverOff)
        self.innerCircles.opacity = 0
        self.fill.opacity = 0

    def _GetViewColor(self):
        return eveColor.Color(eveColor.WHITE).SetOpacity(0.4).GetRGBA()

    def ConstructInnerCircles(self):
        super(CareerCircleView, self).ConstructInnerCircles()
        self.innerCircles.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW

    def _GetInnerCircleScale(self):
        return (0.8, 0.8)

    def _GetNodeMask(self):
        selectedCareerPath = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        if selectedCareerPath in (careerpathconst.career_path_enforcer, careerpathconst.career_path_explorer):
            return 'res:/UI/Texture/classes/careerPortal/nodeMasks/career_inner_mask_down.png'
        else:
            return 'res:/UI/Texture/classes/careerPortal/nodeMasks/career_inner_mask_up.png'

    def Close(self):
        careerConst.CAREER_WINDOW_STATE_SETTING.on_change.disconnect(self.OnCareerWindowStateChanged)
        cpSignals.on_career_node_hover_on.disconnect(self.OnCareerNodeHoverOn)
        cpSignals.on_career_node_hover_off.disconnect(self.OnCareerNodeHoverOff)
        super(CircleView, self).Close()

    def GetNodeSize(self):
        return min(NODE_MAX_SIZE, self.width * 0.215)

    def _GetAngleOffset(self):
        return -math.pi / 4

    def OnCareerNodeHoverOn(self, *args):
        if careerConst.CAREER_WINDOW_STATE_SETTING.get() != careerConst.CareerWindowState.ACTIVITIES_VIEW:
            return
        PlaySound('career_portal_go_to_activities_play')
        animations.FadeIn(self.innerCircles, endVal=0.4, duration=0.4)

    def OnCareerNodeHoverOff(self, *args):
        if careerConst.CAREER_WINDOW_STATE_SETTING.get() != careerConst.CareerWindowState.ACTIVITIES_VIEW:
            return
        animations.FadeOut(self.innerCircles, duration=0.4)

    def OnCareerWindowStateChanged(self, state, animate = True):
        careerID = careerConst.SELECTED_CAREER_PATH_SETTING.get()
        if animate:
            animations.FadeOut(self.innerCircles, duration=0.4)
        else:
            self.innerCircles.opacity = 0
        self.innerCircles.SetSecondaryTexturePath(self._GetNodeMask())
        if state in (careerConst.CareerWindowState.ACTIVITIES_VIEW, careerConst.CareerWindowState.GOALS_VIEW):
            self._GoToAlternateState(animate, careerID)
        elif state == careerConst.CareerWindowState.CAREERS_VIEW:
            self._GoToCareerState(animate)
        else:
            return

    def _GoToCareerState(self, animate):
        if animate:
            animations.FadeIn(self.outerCircle, endVal=0.4, duration=0.5)
            animations.Tr2DScaleTo(self, startScale=self.scale, endScale=(1.0, 1.0))
            animations.Tr2DRotateTo(self, startAngle=self.rotation, endAngle=0)
        else:
            self.outerCircle.opacity = 0.4
            self.scale = (1, 1)
            self.rotation = 0

    def _GoToAlternateState(self, animate, careerID):
        if animate:
            animations.FadeOut(self.outerCircle, duration=0.5)
            animations.Tr2DScaleTo(self, startScale=self.scale, endScale=(0.6, 0.6))
            animations.Tr2DRotateTo(self, startAngle=self.rotation, endAngle=math.radians(careerConst.CIRCLE_ROTATION_BY_CAREER[careerID]))
            animations.SpSecondaryTextureRotate(self.innerCircles, startVal=self.rotation, endVal=-math.radians(careerConst.CIRCLE_ROTATION_BY_CAREER[careerID]), duration=0.5)
        else:
            if self.outerCircle:
                self.outerCircle.opacity = 0
            self.scale = (0.6, 0.6)
            self.rotation = math.radians(careerConst.CIRCLE_ROTATION_BY_CAREER[careerID])
            self.innerCircles.rotationSecondary = -math.radians(careerConst.CIRCLE_ROTATION_BY_CAREER[careerID])
