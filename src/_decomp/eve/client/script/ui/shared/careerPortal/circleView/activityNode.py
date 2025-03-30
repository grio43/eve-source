#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\activityNode.py
import math
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorarc import VectorArc
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.uianimations import animations
from carbonui.util.dpi import ScaleDpi
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal import careerConst, cpSignals
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.circleView.circleNode import CircleNodeWithText
from eve.client.script.ui.shared.careerPortal.link.dragData import NodeDragData
from localization import GetByLabel
ANIM_DURATION = 0.4
TEXT_WIDTH = 200
TEXT_PADDING = 2
DEFAULT_BG_OPACITY = 0.1
GLOW_SPRITE_WIDTH = 64
HIGHLIGHT_BG_OPACITY = 0.3
ACTIVITY_NODE_SIZE = 48

class ActivityNode(CircleNodeWithText):
    default_name = 'ActivityNode'
    default_height = ACTIVITY_NODE_SIZE
    default_width = ACTIVITY_NODE_SIZE

    def ApplyAttributes(self, attributes):
        self.nodeObject = attributes.nodeObject
        self.highlight = attributes.get('highlight', False)
        self.highlightSprite = None
        super(ActivityNode, self).ApplyAttributes(attributes)
        self.highlight = self.highlight and not self.IsCompleted()
        if self.highlight:
            self.highlightSprite = VectorArc(name='highlight', parent=self, align=uiconst.CENTER, radius=ScaleDpi((self.default_width + ScaleDpi(16)) / 2), fill=False, color=eveColor.AURA_PURPLE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, state=uiconst.UI_DISABLED, glowBrightness=0.5)
        animations.FadeIn(self.icon, duration=ANIM_DURATION, timeOffset=0.5)
        goals = get_career_goals_svc().get_goal_data_controller().get_goals_in_group(self.nodeObject.careerID, self.nodeObject.activityID)
        self.goalsInGroup = [ g.goal_id for g in goals ]
        self.OnCareerWindowStateChanged(attributes.initialState)

    def GetSignals(self):
        newSignals = [(cpSignals.on_career_node_hover_on, self.OnCareerNodeHoverOn), (cpSignals.on_career_node_hover_off, self.OnCareerNodeHoverOff)]
        return newSignals + super(ActivityNode, self).GetSignals()

    def ConstructIcon(self):
        self.icon = Sprite(parent=self.iconCont, name='activityIcon', align=uiconst.CENTER, pos=(0, 0, 32, 32), texturePath=self.nodeObject.iconTexturePath, state=uiconst.UI_DISABLED, color=eveColor.LEAFY_GREEN if self.IsCompleted() else eveColor.WHITE, opacity=0)
        super(ActivityNode, self).ConstructIcon()
        if self.IsCompleted():
            bgSpriteColor = eveColor.LEAFY_GREEN
        elif self.highlight:
            bgSpriteColor = eveColor.AURA_PURPLE
        else:
            bgSpriteColor = eveColor.CRYO_BLUE
        self.bgSprite.color = eveColor.Color(bgSpriteColor).SetOpacity(0).GetRGBA()
        self.glowSprite = Sprite(name='glowSprite', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/node_glow.png', state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.2, opacity=0)

    def UpdateAnchorPointsAndSize(self, contSize):
        super(ActivityNode, self).UpdateAnchorPointsAndSize(contSize)
        self.glowSprite.SetSize(self.width + GLOW_SPRITE_WIDTH, self.height + GLOW_SPRITE_WIDTH)

    def ConstructFrame(self):
        radius = ScaleDpi(self.default_width / 2)
        self.dashedFrame = DashedCircle(name='dashedFrame', parent=self.iconCont, align=uiconst.CENTER, radius=radius, lineWidth=2, color=eveColor.LEAFY_GREEN, startAngle=math.radians(-90), range=math.pi * 2, gapEnds=True, dashCount=len(self.nodeObject.GetGoals()), dashSizeFactor=8, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)
        self.bgFrame = DashedCircle(name='dashedFrameBG', parent=self.iconCont, align=uiconst.CENTER, radius=radius, lineWidth=2, color=eveColor.WHITE, startAngle=math.radians(-90), range=math.pi * 2, gapEnds=True, dashCount=len(self.nodeObject.GetGoals()), dashSizeFactor=8, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.4)
        self.dashedFrame.end = 0
        self.frame = VectorArc(name='frame', parent=self.iconCont, align=uiconst.CENTER, radius=radius, fill=False, opacity=0, color=eveColor.LEAFY_GREEN if self.IsCompleted() else eveColor.WHITE)
        self.UpdateDashedCircle()

    def OnCareerNodeHoverOn(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.GOALS_VIEW:
            return
        if self.IsSelected():
            return
        animations.FadeIn(self.icon, duration=ANIM_DURATION)
        animations.FadeIn(self.frame, duration=ANIM_DURATION)
        animations.FadeOut(self.bgSprite, duration=ANIM_DURATION)

    def OnCareerNodeHoverOff(self, *args):
        currentState = careerConst.CAREER_WINDOW_STATE_SETTING.get()
        if currentState != careerConst.CareerWindowState.GOALS_VIEW:
            return
        if self.IsSelected():
            return
        animations.FadeOut(self.frame, duration=ANIM_DURATION)
        animations.FadeOut(self.icon, duration=ANIM_DURATION)
        animations.FadeIn(self.bgSprite, duration=ANIM_DURATION)

    def OnCareerWindowStateChanged(self, state):
        if state == careerConst.CareerWindowState.ACTIVITIES_VIEW:
            self.Enable()
            animations.FadeIn(self.textCont, duration=ANIM_DURATION)
            animations.FadeOut(self.bgSprite, duration=ANIM_DURATION)
            animations.FadeOut(self.frame, duration=ANIM_DURATION)
            animations.FadeIn(self.icon, duration=ANIM_DURATION, timeOffset=0.5)
            animations.FadeIn(self.dashedFrame, duration=ANIM_DURATION)
            animations.FadeIn(self.bgFrame, duration=ANIM_DURATION)
            if self.highlight:
                self.highlightSprite.display = True
        elif state == careerConst.CareerWindowState.GOALS_VIEW:
            self.Disable()
            if not self.IsSelected():
                animations.FadeOut(self.glowSprite, duration=ANIM_DURATION)
                self.frame.color = eveColor.WHITE
                animations.FadeOut(self.frame, duration=ANIM_DURATION)
                animations.FadeOut(self.icon, duration=ANIM_DURATION)
                animations.FadeTo(self.bgSprite, startVal=0, endVal=DEFAULT_BG_OPACITY, duration=ANIM_DURATION)
                endColor = eveColor.LEAFY_GREEN if self.IsCompleted() else eveColor.LED_GREY
                opacity = 0.4 if self.IsCompleted() else 0.6
                animations.SpColorMorphTo(self.bgSprite, startColor=self.bgSprite.rgba, endColor=eveColor.Color(endColor).SetOpacity(opacity).GetRGBA(), duration=ANIM_DURATION)
            else:
                animations.FadeIn(self.glowSprite)
                animations.FadeIn(self.frame, duration=ANIM_DURATION)
                endColor = eveColor.LEAFY_GREEN if self.IsCompleted() else eveColor.CRYO_BLUE
                self.frame.color = endColor
                animations.SpColorMorphTo(self.glowSprite, startColor=self.glowSprite.rgba, endColor=endColor, duration=ANIM_DURATION)
                animations.SpColorMorphTo(self.bgSprite, startColor=self.bgSprite.rgba, endColor=eveColor.Color(endColor).SetOpacity(0.3).GetRGBA(), duration=ANIM_DURATION)
            animations.FadeOut(self.textCont, duration=ANIM_DURATION)
            animations.FadeOut(self.dashedFrame, duration=ANIM_DURATION)
            animations.FadeOut(self.bgFrame, duration=ANIM_DURATION)
            if self.highlight:
                self.highlightSprite.display = False
        else:
            animations.FadeOut(self.icon, duration=ANIM_DURATION)
            animations.FadeTo(self.bgSprite, startVal=0, endVal=DEFAULT_BG_OPACITY, duration=ANIM_DURATION)
        self.UpdateNode()

    def UpdateNode(self):
        super(ActivityNode, self).UpdateNode()
        self.UpdateDashedCircle()

    def UpdateDashedCircle(self):
        goals = self.nodeObject.GetGoals()
        completedGoals = [ goal for goal in goals if goal.is_completed() ]
        self.dashedFrame.SetValue(len(completedGoals) / float(len(goals)))
        self.bgFrame.start = len(completedGoals) / float(len(goals))

    def OnGoalUpdated(self, goalID, value):
        if goalID in self.goalsInGroup:
            self.UpdateNode()

    def OnGoalCompleted(self, goalID):
        if goalID in self.goalsInGroup and self.IsCompleted():
            self.icon.color = eveColor.LEAFY_GREEN

    def IsCompleted(self):
        progress, total = self.nodeObject.points
        return progress >= total

    def IsSelected(self):
        return self.nodeObject.activityID == careerConst.SELECTED_ACTIVITY_SETTING.get()

    def OnClick(self, *args):
        PlaySound('career_portal_select_mission_play')
        get_career_portal_controller_svc().select_activity(self.nodeObject.activityID, self.nodeObject.activityName, self.nodeObject.careerID)

    def SetNormalState(self):
        super(ActivityNode, self).SetNormalState()
        self.bgSprite.opacity = 0.0
        if self.highlight:
            self.highlightSprite.glowBrightness = 0.5

    def SetHoverState(self):
        PlaySound('career_portal_mission_hover_play')
        super(ActivityNode, self).SetHoverState()
        self.bgSprite.opacity = HIGHLIGHT_BG_OPACITY
        if self.highlight:
            self.highlightSprite.glowBrightness = 1.0

    def SetCompletedState(self):
        super(ActivityNode, self).SetCompletedState()
        self.bgSprite.color = eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(HIGHLIGHT_BG_OPACITY).GetRGBA()
        self.glowSprite.color = eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(HIGHLIGHT_BG_OPACITY).GetRGBA()
        if self.highlightSprite:
            self.highlightSprite.display = False

    def GetNameLabel(self):
        return self.nodeObject.activityName

    def GetProgressLabel(self):
        return self.nodeObject.progressLabel

    def GetDragData(self):
        if self.nodeObject:
            return NodeDragData(self.nodeObject.careerID, self.nodeObject.activityID, None, self.nodeObject.activityName)

    def UpdateTextPos(self, angle):
        super(ActivityNode, self).UpdateTextPos(angle)
        if self.highlight:
            self.textCont.top -= 4


class ActivityNodeObject(object):

    def __init__(self, careerID, activityID):
        self.careerID = careerID
        self.activityID = activityID
        self._activityName = None
        self._currentPoints = None
        self._maxPoints = None

    @property
    def iconTexturePath(self):
        return careerConst.ICON_BY_ACTIVITY_ID.get(self.activityID, '')

    @property
    def activityName(self):
        if self._activityName is None:
            self._activityName = careerConst.GetCareerPathGroupName(self.careerID, self.activityID)
        return self._activityName

    def GetGoals(self):
        return get_career_goals_svc().get_goal_data_controller().get_goals_in_group(self.careerID, self.activityID)

    @property
    def points(self):
        goals = self.GetGoals()
        self._maxPoints = len(goals)
        self._currentPoints = len([ g for g in goals if g.is_completed() ])
        return (self._currentPoints, self._maxPoints)

    @property
    def progressLabel(self):
        currentPoints, maxPoints = self.points
        return GetByLabel('UI/CareerPortal/ActivityProgressCount', currentPoints=currentPoints, totalPoints=maxPoints)

    def __repr__(self):
        return '%s - points: %s' % (self.activityName, self.progressLabel)
