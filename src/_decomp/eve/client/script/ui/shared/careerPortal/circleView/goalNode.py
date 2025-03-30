#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\circleView\goalNode.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorarc import VectorArc
from carbonui.util.dpi import ScaleDpi
from careergoals.client.career_goal_svc import get_career_goals_svc
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.careerPortal import careerConst
from eve.client.script.ui.shared.careerPortal.careerControllerUI import get_career_portal_controller_svc
from eve.client.script.ui.shared.careerPortal.circleView.circleNode import CircleNodeWithText
from eve.client.script.ui.shared.careerPortal.cpSignals import on_cp_goal_tracking_removed, on_cp_goal_tracking_added
from eve.client.script.ui.shared.careerPortal.link.dragData import NodeDragData
from eve.client.script.ui.util.uix import QtyPopup
from careergoals.client.goal import Goal
from localization import GetByLabel
GLOW_SPRITE_WIDTH = 64
GOAL_NODE_RADIUS = 24
DEFAULT_GLOW_OPACITY = 0.8
HIGHLIGHT_GLOW_OPACITY = 1.0

class GoalNode(CircleNodeWithText):
    default_width = 48
    default_height = 48
    isTracked = False

    def ApplyAttributes(self, attributes):
        self.goal = attributes.goal
        super(GoalNode, self).ApplyAttributes(attributes)
        self.UpdateNode()

    def PrepareUI(self):
        super(GoalNode, self).PrepareUI()
        self.centerDot = Sprite(name='centerDot', parent=self.iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0, 0, 6, 6), texturePath='res:/UI/Texture/Shared/smallDot.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)

    def ConstructIcon(self):
        self.bgSprite = Sprite(name='bgSprite', parent=self.iconCont, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/node_glow.png', state=uiconst.UI_DISABLED, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.2, opacity=DEFAULT_GLOW_OPACITY)
        self.checkmarkSprite = Sprite(name='checkmarkSprite', parent=self.iconCont, pos=(0, 0, 20, 20), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/circleView/goalCompleted.png', state=uiconst.UI_DISABLED, color=eveColor.LEAFY_GREEN)
        self.checkmarkSprite.display = False
        self.trackedSprite = Sprite(name='trackedSprite', parent=self.iconCont, pos=(0, 0, 32, 32), align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/careerPortal/circleView/eye_open_32.png', state=uiconst.UI_DISABLED, color=eveColor.WHITE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)
        self.trackedSprite.Hide()

    def ConstructFrame(self):
        self.frame = VectorArc(name='frame', parent=self.iconCont, align=uiconst.CENTER, radius=ScaleDpi(ScaleDpi(GOAL_NODE_RADIUS)), lineWidth=ScaleDpi(2), fill=False, opacity=0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0)

    def GetSignals(self):
        signals = super(GoalNode, self).GetSignals()
        signals.append((careerConst.SELECTED_GOAL_SETTING.on_change, self.OnSelectedGoalChanged))
        signals.append((on_cp_goal_tracking_removed, self.OnGoalUntracked))
        signals.append((on_cp_goal_tracking_added, self.OnGoalTracked))
        return signals

    def GetNameLabel(self):
        if not self.goal:
            return ''
        return self.goal.definition.name

    def GetProgressLabel(self):
        if not self.goal:
            return ''
        totalPoints = self.goal.definition.target_value
        currentPoints = min(self.goal.progress, totalPoints)
        return GetByLabel('UI/CareerPortal/ActivityProgressCount', currentPoints=currentPoints, totalPoints=totalPoints)

    def UpdateAnchorPointsAndSize(self, contSize):
        super(GoalNode, self).UpdateAnchorPointsAndSize(contSize)
        scaledWidth = self.width + ScaleDpi(GLOW_SPRITE_WIDTH)
        self.bgSprite.SetSize(scaledWidth, scaledWidth)

    def OnSelectedGoalChanged(self, goalID):
        self.UpdateNode()

    def OnGoalTracked(self, goalID):
        isTracked = get_career_portal_controller_svc().is_goal_tracked(self.goal.goal_id)
        self.isTracked = True if isTracked and not self.IsCompleted() else False
        self.UpdateTrackedState()

    def OnGoalUntracked(self, goalID):
        if goalID != self.goal.goal_id:
            return
        self.isTracked = False
        self.UpdateTrackedState()

    def OnGoalUpdated(self, goalID, value):
        if goalID != self.goal.goal_id:
            return
        self.UpdateNode()

    def OnGoalCompleted(self, goalID):
        if goalID != self.goal.goal_id:
            return
        self.UpdateNode()

    def IsCompleted(self):
        return self.goal.is_completed()

    def IsSelected(self):
        return careerConst.SELECTED_GOAL_SETTING.get() == self.goal.goal_id

    def UpdateNode(self):
        super(GoalNode, self).UpdateNode()
        if self.IsSelected():
            self.SetSelectedState()
        if get_career_portal_controller_svc().is_goal_tracked(self.goal.goal_id) and not self.IsCompleted():
            self.isTracked = True
        else:
            self.isTracked = False
        self.UpdateTrackedState()

    def SetSelectedState(self):
        self.frame.color = eveColor.CRYO_BLUE
        self.bgSprite.color = eveColor.Color(eveColor.CRYO_BLUE).SetOpacity(HIGHLIGHT_GLOW_OPACITY).GetRGBA()
        if self.IsCompleted():
            return
        self.centerDot.color = eveColor.WHITE
        self.centerDot.glowBrightness = 0.5
        self.trackedSprite.color = eveColor.WHITE
        if self.isTracked:
            self.trackedSprite.glowBrightness = 0.6

    def SetNormalState(self):
        super(GoalNode, self).SetNormalState()
        if self.IsCompleted():
            self.SetCompletedState()
            return
        if self.isTracked:
            self.trackedSprite.color = eveColor.WHITE
        if self.IsSelected():
            return
        self.frame.color = eveColor.WHITE
        self.trackedSprite.glowBrightness = 0
        self.centerDot.color = eveColor.WHITE
        self.centerDot.glowBrightness = 0
        self.bgSprite.color = eveColor.Color(eveColor.WHITE).SetOpacity(DEFAULT_GLOW_OPACITY).GetRGBA()

    def SetHoverState(self):
        super(GoalNode, self).SetHoverState()
        PlaySound('career_portal_mission_hover_play')
        if self.IsCompleted():
            return
        if not self.IsSelected():
            self.centerDot.color = eveColor.CRYO_BLUE
        self.frame.color = eveColor.CRYO_BLUE
        self.centerDot.glowBrightness = 0.5
        self.bgSprite.color = eveColor.Color(eveColor.CRYO_BLUE).SetOpacity(HIGHLIGHT_GLOW_OPACITY).GetRGBA()
        if self.isTracked:
            self.trackedSprite.color = eveColor.CRYO_BLUE

    def SetCompletedState(self):
        super(GoalNode, self).SetCompletedState()
        self.checkmarkSprite.Show()
        self.centerDot.opacity = 0
        if self.IsSelected():
            return
        self.frame.color = eveColor.LEAFY_GREEN
        self.bgSprite.color = eveColor.Color(eveColor.LEAFY_GREEN).SetOpacity(DEFAULT_GLOW_OPACITY).GetRGBA()

    def UpdateTrackedState(self):
        if not self.isTracked:
            self.trackedSprite.Hide()
            self.centerDot.Show()
            return
        self.trackedSprite.Show()
        self.centerDot.Hide()

    def OnClick(self, *args):
        get_career_portal_controller_svc().select_goal(self.goal.goal_id)

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [['Goal ID: {}'.format(self.goal.goal_id), self._CopyGoalID], ['QA: Complete', self._Debug_CompleteGoal], ['QA: Progress', self._Debug_ProgressGoal]]
            return menu

    def GetDragData(self):
        if not self.goal:
            return
        return NodeDragData(self.goal.definition.career, self.goal.definition.group_id, self.goal.goal_id, self.goal.definition.name)

    def _Debug_CompleteGoal(self):
        get_career_goals_svc().get_goal_data_controller().admin_complete_goal(self.goal.goal_id)

    def _Debug_ProgressGoal(self):
        ret = QtyPopup(minvalue=0, setvalue=1, maxvalue=self.goal.definition.target_value)
        if ret and 'qty' in ret:
            get_career_goals_svc().get_goal_data_controller().admin_progress_goal(self.goal.goal_id, ret['qty'])

    def _CopyGoalID(self):
        import blue
        blue.pyos.SetClipboardData(unicode(self.goal.goal_id))
