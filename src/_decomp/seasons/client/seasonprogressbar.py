#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\seasonprogressbar.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelLarge, Label
from eve.client.script.ui.control.gauge import Gauge
from localization import GetByLabel
from localization.formatters import FormatNumeric
from seasons.client.const import POINTS_ICON_PATH_64
from seasons.client.rewardIcon import Reward
COLOR_GREEN = (0.259, 0.631, 0.176, 1.0)
COLOR_GREY = (0.43, 0.43, 0.43, 1.0)
CURRENT_POINTS_CONTAINER_WIDTH = 185
PADDING_CURRENT_POINTS_LEFT = 12
PADDING_CURRENT_POINTS_TO_BAR = 6
CURRENT_POINTS_ICON_SIZE = 48
PADDING_CURRENT_POINTS_ICON_TO_LABEL = 2
CURRENT_POINTS_LABEL_COLOR = (0.5, 0.5, 0.5, 1.0)
CURRENT_POINTS_ICON_COLOR = (0.8, 0.8, 0.8, 1.0)
CURRENT_POINTS_COLOR = (1.0, 1.0, 1.0, 1.0)
PROGRESS_BAR_HEIGHT = 12
PROGRESS_BAR_TOP = 25
PROGRESS_BAR_COLOR = COLOR_GREEN
PROGRESS_BAR_BG_COLOR = COLOR_GREY
REWARD_UI_ELEMENT_WIDTH = 50
POINTS_MARKER_WIDTH = 1
POINTS_MARKER_HEIGHT = PROGRESS_BAR_HEIGHT + 6
POINTS_MARKER_COLOR = COLOR_GREEN
POINTS_LABEL_FONTSIZE = 24
POINTS_LABEL_FILL_MARGIN_H = 4
POINTS_LABEL_FILL_MARGIN_V = 2
LABEL_PATH_POINTS_EARNED = 'UI/Agency/Seasons/PointsEarned'

class RewardsBar(Container):
    __notifyevents__ = ['OnSeasonalGoalCompletedInClient',
     'OnSeasonalGoalClaimedInClient',
     'OnSeasonalPointsUpdatedInClient',
     'OnSeasonalGoalsResetInClient']

    def ApplyAttributes(self, attributes):
        super(RewardsBar, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.seasons_service = sm.GetService('seasonService')
        self.current_points = float(self.seasons_service.get_points())
        self.max_points = float(self.seasons_service.get_max_points())
        self.bar_left = PADDING_CURRENT_POINTS_LEFT + CURRENT_POINTS_CONTAINER_WIDTH + PADDING_CURRENT_POINTS_TO_BAR
        width, _ = self.GetAbsoluteSize()
        self.bar_width = width - self.bar_left - REWARD_UI_ELEMENT_WIDTH
        self.add_current_points()
        self.add_rewards_container()
        self.add_progress_bar()

    def get_points_position(self, points):
        progress_ratio = min(points / self.max_points, 0.9999)
        return int(progress_ratio * self.bar_width)

    def add_rewards_container(self):
        self.rewards = self.seasons_service.get_rewards()
        self.reward_ui_elements = {}
        self.rewards_container = Container(name='rewards_container', parent=self, align=uiconst.TOTOP_NOPUSH, height=self.height)
        for reward_id, reward_data in self.rewards.items():
            progress_needed = float(reward_data['points_required'])
            self.reward_ui_elements[reward_id] = Reward(parent=self.rewards_container, name='reward_ui', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT, left=REWARD_UI_ELEMENT_WIDTH / 2 + self.get_points_position(progress_needed), width=REWARD_UI_ELEMENT_WIDTH, height=self.rewards_container.height, reward=reward_data, seasonSvc=self.seasons_service, rewardIndex=reward_id, progressBarWidth=self.bar_width, progressBarHeight=PROGRESS_BAR_HEIGHT, progressBarTop=PROGRESS_BAR_TOP, progressBarLeft=REWARD_UI_ELEMENT_WIDTH / 2, pointsLabelTop=-POINTS_LABEL_FILL_MARGIN_V)

    def add_current_points(self):
        current_points_container = Container(name='current_points_container', parent=self, align=uiconst.TOLEFT, width=CURRENT_POINTS_CONTAINER_WIDTH, padLeft=PADDING_CURRENT_POINTS_LEFT, padRight=PADDING_CURRENT_POINTS_TO_BAR)
        top_to_align_with_center_of_bar = PROGRESS_BAR_TOP + PROGRESS_BAR_HEIGHT / 2
        Sprite(name='points_icon', parent=current_points_container, align=uiconst.BOTTOMLEFT, bgColor=(1.0, 0.0, 0.0, 0.1), width=CURRENT_POINTS_ICON_SIZE, height=CURRENT_POINTS_ICON_SIZE, texturePath=POINTS_ICON_PATH_64, top=top_to_align_with_center_of_bar - CURRENT_POINTS_ICON_SIZE / 2, color=CURRENT_POINTS_ICON_COLOR)
        points_earned_label = EveLabelLarge(name='points_earned_label', parent=current_points_container, align=uiconst.TOPLEFT, text=GetByLabel(LABEL_PATH_POINTS_EARNED), left=8, top=46, color=CURRENT_POINTS_LABEL_COLOR)
        points_earned_label.top -= points_earned_label.height / 2
        self.points_label = Label(name='points_label', parent=current_points_container, align=uiconst.BOTTOMLEFT, text=FormatNumeric(int(self.current_points), useGrouping=True), fontsize=POINTS_LABEL_FONTSIZE, left=CURRENT_POINTS_ICON_SIZE + PADDING_CURRENT_POINTS_ICON_TO_LABEL, top=top_to_align_with_center_of_bar, color=CURRENT_POINTS_COLOR)
        self.points_label.top -= self.points_label.height / 2
        self.update_current_points_label()

    def add_progress_bar(self):
        padding_h = REWARD_UI_ELEMENT_WIDTH / 2
        bar_container = Container(name='bar_container', parent=self, align=uiconst.TOTOP_NOPUSH, height=self.height, padding=(padding_h,
         0,
         padding_h,
         0))
        self.bar = Gauge(name='bar_gauge', parent=bar_container, align=uiconst.TOBOTTOM, heigth=PROGRESS_BAR_HEIGHT, gaugeHeight=PROGRESS_BAR_HEIGHT, backgroundColor=PROGRESS_BAR_BG_COLOR, color=PROGRESS_BAR_COLOR, top=PROGRESS_BAR_TOP)
        self.update_progress_bar()

    def update_current_points_label(self):
        self.points_label.text = FormatNumeric(int(self.current_points), useGrouping=True)

    def update_progress_bar(self):
        self.bar.SetValue(self.current_points / self.max_points)

    def update_points(self):
        self.current_points = float(self.seasons_service.get_points())
        self.update_progress_bar()
        self.update_current_points_label()

    def set_points(self, points):
        self.current_points = points
        self.update_progress_bar()
        self.update_current_points_label()

    def update_all_rewards(self):
        self.rewards = self.seasons_service.get_rewards()
        for reward_index, reward_data in self.rewards.items():
            self.update_reward(reward_index, reward_data)

    def update_reward(self, reward_id, reward_data):
        self.rewards[reward_id] = reward_data
        self.reward_ui_elements[reward_id].update_reward(reward_data)

    def update_all(self):
        self.update_points()
        self.update_all_rewards()

    def OnSeasonalGoalsResetInClient(self):
        self.update_all()

    def OnSeasonalGoalCompletedInClient(self, reward_id, reward_data):
        self.update_reward(reward_id, reward_data)

    def OnSeasonalGoalClaimedInClient(self, reward_id, reward_data):
        self.update_reward(reward_id, reward_data)

    def OnSeasonalPointsUpdatedInClient(self, season_points):
        self.set_points(season_points)
