#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\careerPortal\progressBar.py
import appConst
import evetypes
import trinity
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from careergoals.client.career_goal_svc import get_career_goals_svc
from careergoals.client.signal import on_goal_progress_changed, on_goal_completed, on_definitions_loaded
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveCaptionSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.infoIcon import CheckMarkGlyphIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
from eve.client.script.ui.util.uix import QtyPopup
from localization import GetByLabel
ICON_SIZE = 24
GAUGE_CONT_HEIGHT = 30
GAUGE_HEIGHT = 4
GAUGE_PADDING = 1
MARKER_HEIGHT = 10
CRATE_SIZE = 86

class ProgressBar(Gauge):
    default_state = uiconst.UI_NORMAL
    default_backgroundColor = eveColor.BLACK
    default_gaugeHeight = 10
    default_height = 10
    default_width = 0
    default_color = eveColor.CRYO_BLUE
    default_labelClass = EveCaptionSmall
    normalGaugeColor = eveColor.CRYO_BLUE
    fullGaugeColor = eveColor.SUCCESS_GREEN

    def GetMenu(self):
        if session and session.role & ROLE_GML:
            menu = [['QA: Progress', self._Debug_ProgressGoal]]
            return menu

    def _Debug_ProgressGoal(self):
        ret = QtyPopup(minvalue=0, setvalue=1)
        if ret and 'qty' in ret:
            for goal in get_career_goals_svc().get_goal_data_controller().get_overall_goals():
                get_career_goals_svc().get_goal_data_controller().admin_progress_goal(goal.goal_id, ret['qty'])

    def ApplyAttributes(self, attributes):
        super(ProgressBar, self).ApplyAttributes(attributes)
        self.markerByGoalID = {}
        self.progressHint = None
        self.frame = Frame(parent=self.gaugeCont, opacity=1.2, color=self.normalGaugeColor, idx=0)
        self.bgGauge = Container(parent=self.gaugeCont, name='bgGauge', align=uiconst.TOPLEFT_PROP, clipChildren=True, width=0.0, height=self.default_gaugeHeight, state=uiconst.UI_DISABLED)
        self.bgGaugeGradient = self._CreateGradient(parent=self.bgGauge, color=eveColor.LEAFY_GREEN)
        self.gauge.opacity = 0.8
        self.gaugeCont.clipChildren = False
        self.gaugeCont.state = uiconst.UI_PICKCHILDREN
        self._InitGaugeWithGoalData()
        on_goal_progress_changed.connect(self.OnGoalProgressChanged)
        on_goal_completed.connect(self.OnGoalCompleted)
        on_definitions_loaded.connect(self._InitGaugeWithGoalData)

    def _CreateGradient(self, parent, color):
        gradient = super(ProgressBar, self)._CreateGradient(parent, color)
        gradient.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
        gradient.glowBrightness = 0.3
        return gradient

    def _InitGaugeWithGoalData(self):
        goal_data_controller = get_career_goals_svc().get_goal_data_controller()
        self.currentProgress = goal_data_controller.get_overall_progress()
        color = self.fullGaugeColor if goal_data_controller.are_all_overall_goals_completed() else self.normalGaugeColor
        self.SetColor(color)
        self.frame.color = color
        max_target = goal_data_controller.get_max_overall_target()
        self.CreateMarkers(goal_data_controller.get_overall_goals(), max_target)
        self.SetValue(self.currentProgress / float(max_target), animate=False)
        self.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=self._GetProgressBarTitle(), description=self._GetProgressBarDescription())

    def CreateMarkers(self, overall_goals, max_target):
        if not max_target:
            return
        for i, goal in enumerate(overall_goals):
            percentValue = float(goal.definition.target_value) / float(max_target)
            goal_rewards = goal.definition.rewards
            if not goal_rewards:
                continue
            reward = goal_rewards[0]
            typeID = reward.type_id
            color = self.fullGaugeColor if goal.is_completed() else self.normalGaugeColor
            self.ShowMarker(percentValue, width=RewardMarker.default_width, color=color, rewardTypeID=typeID, completed=goal.is_completed(), goalID=goal.goal_id, index=i)

    def SetValue(self, value, frequency = 10.0, animate = True, timeOffset = 0.0, duration = 0.6, flash = True):
        if animate:
            animations.MorphScalar(self.bgGauge, 'width', self.bgGauge.width, value, duration=duration, curveSet=self._GetCorrectCurveSet(), callback=lambda : animations.FadeOut(self.progressHint, duration=0.4, callback=self.progressHint.Close))
        super(ProgressBar, self).SetValue(value, frequency, animate, timeOffset + 1.0, duration, flash=False)

    def Close(self):
        on_goal_progress_changed.disconnect(self.OnGoalProgressChanged)
        on_goal_completed.disconnect(self.OnGoalCompleted)
        on_definitions_loaded.disconnect(self._InitGaugeWithGoalData)
        super(ProgressBar, self).Close()

    def _CreateBackgroundFill(self, backgroundColor):
        super(ProgressBar, self)._CreateBackgroundFill(backgroundColor)
        StretchSpriteHorizontal(name='backgroundGlowSprite', parent=self, align=uiconst.TOTOP_NOPUSH, height=18, rightEdgeSize=6, leftEdgeSize=6, top=-14, padding=(-4, 0, -4, 0), texturePath='res:/UI/Texture/classes/careerPortal/progressBarBackgroundGlow.png', outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, color=self.normalGaugeColor)

    def _CreateMarker(self, color, value, width, **kwargs):
        marker = RewardMarker(parent=self, top=0.5, left=value, width=width, state=uiconst.UI_NORMAL, color=color, idx=0, opacity=0, **kwargs)
        animations.FadeIn(marker, duration=1.0, timeOffset=kwargs.get('index', 0) / 4 + 0.1, curveType=uiconst.ANIM_OVERSHOT2)
        self.markerByGoalID[kwargs.get('goalID', None)] = marker
        return marker

    def SetText(self, text):
        super(ProgressBar, self).SetText(text)
        self.label.align = uiconst.TOPLEFT
        self.label.top = -28
        self.label.width = self.label.MeasureTextSize(self.label.text)[0]

    def GetTooltipPosition(self):
        l, t = self.gauge.GetCurrentAbsolutePosition()
        w, h = self.gauge.GetCurrentAbsoluteSize()
        return (l + w,
         t,
         10,
         10)

    def OnGoalProgressChanged(self, goal_id, progress_value):
        goal_data_controller = get_career_goals_svc().get_goal_data_controller()
        if not goal_data_controller.is_overall_goal(goal_id):
            return
        self._ShowProgressHint(progress_value)
        self.currentProgress = goal_data_controller.get_overall_progress()
        self.SetValue(self.currentProgress / float(goal_data_controller.get_max_overall_target()))
        self.SetColor(self.fullGaugeColor if goal_data_controller.are_all_overall_goals_completed() else self.normalGaugeColor)
        self.tooltipPanelClassInfo.headerText = self._GetProgressBarTitle()

    def _ShowProgressHint(self, newProgress):
        if self.progressHint:
            self.progressHint.Close()
        l, t = self.gauge.GetCurrentAbsolutePosition()
        w, h = self.gauge.GetCurrentAbsoluteSize()
        self.progressHint = ContainerAutoSize(name='careerPortalProgressHint', parent=uicore.layer.hint, pos=(l + w,
         t - 20,
         0,
         16))
        Sprite(parent=self.progressHint, align=uiconst.TOLEFT, texturePath='res:/UI/Texture/classes/careerPortal/career_point_icon.png', width=16, height=16, color=eveColor.LEAFY_GREEN)
        EveLabelMedium(parent=self.progressHint, align=uiconst.TOLEFT, text='+%s' % (newProgress - self.currentProgress), color=eveColor.LEAFY_GREEN, left=4)

    def OnGoalCompleted(self, goal_id):
        if not get_career_goals_svc().get_goal_data_controller().is_overall_goal(goal_id):
            return
        marker = self.markerByGoalID.get(goal_id, None)
        if not marker:
            return
        marker.MarkCompleted()

    def _GetProgressBarTitle(self):
        goal_data_controller = get_career_goals_svc().get_goal_data_controller()
        title = GetByLabel('UI/CareerPortal/OverallCareerPoints', currentPoints=goal_data_controller.get_overall_progress(), totalPoints=goal_data_controller.get_max_overall_target())
        return title

    def _GetProgressBarDescription(self):
        overall_goals = get_career_goals_svc().get_goal_data_controller().get_overall_goals()
        description = GetByLabel('UI/CareerPortal/TotalCareerPointsTooltip')
        for goal in overall_goals:
            goal_rewards = goal.definition.rewards
            if goal_rewards and len(goal_rewards) > 0:
                goalReward = evetypes.GetName(goal_rewards[0].type_id)
                description += '<br>%s' % GetByLabel('UI/CareerPortal/OverallGoalInfo', goalCp=goal.definition.target_value, goalReward=goalReward)

        return description


class RewardMarker(Container):
    default_name = 'CareerRewardMarker'
    default_align = uiconst.TOPLEFT_PROP
    default_height = 48
    default_width = 36
    default_rewardTypeID = appConst.typeSkillInjector

    def __init__(self, *args, **kwargs):
        super(RewardMarker, self).__init__(*args, **kwargs)
        self.rewardTypeID = kwargs.get('rewardTypeID', self.default_rewardTypeID)
        self.color = kwargs.get('color', eveColor.CRYO_BLUE)
        self.ConstructLayout()
        if kwargs.get('completed', False):
            self.MarkCompleted()

    def ConstructLayout(self):
        self.successIcon = CheckMarkGlyphIcon(parent=self, align=uiconst.CENTER, pos=(0, 0, 16, 16), opacity=0, state=uiconst.UI_HIDDEN)
        self.itemIcon = ItemIcon(parent=self, align=uiconst.CENTER, pos=(0, 0, 22, 22), typeID=self.rewardTypeID)
        self.itemIcon.techIcon.Hide()
        self.GetHint = self.itemIcon.GetHint
        self.hexagon = Sprite(name='hexagon', parent=self, align=uiconst.CENTER, pos=(0, 0, 58, 58), texturePath='res:/UI/Texture/classes/careerPortal/hexagon.png', textureSecondaryPath=self._GetMaskTexturePath(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.8, spriteEffect=trinity.TR2_SFX_MODULATE, color=self.color, state=uiconst.UI_DISABLED)

    def _GetMaskTexturePath(self):
        if self.left == 1:
            return 'res:/UI/Texture/classes/careerPortal/hexagon_mask_right.png'
        else:
            return 'res:/UI/Texture/classes/careerPortal/hexagon_mask.png'

    def MarkCompleted(self):
        self.successIcon.state = uiconst.UI_DISABLED
        self.successIcon.opacity = 1
        self.itemIcon.opacity = 0.4
        self.hexagon.spriteEffect = Sprite.default_spriteEffect
