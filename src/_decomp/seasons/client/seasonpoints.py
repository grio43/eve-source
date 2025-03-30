#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\seasonpoints.py
import carbonui.const as uiconst
import localization
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmallBold
from seasons.client.const import POINTS_ICON_PATH_18, POINTS_ICON_PATH_64, get_points_label_text
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
DEFAULT_SEASON_POINTS_SIZE = 18
DEFAULT_REWARD_LABEL_CLASS = EveLabelSmallBold
DEFAULT_REWARD_LABEL_PADLEFT = 2
DEFAULT_ON_CLICK_FUNCTION = None
REWARD_LABEL_WIDTH = 50

class SeasonPoints(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        reward_label_class = attributes.Get('reward_label_class', DEFAULT_REWARD_LABEL_CLASS)
        reward_label_fontsize = attributes.Get('reward_label_fontsize', None)
        reward_label_padLeft = attributes.Get('reward_label_padLeft', DEFAULT_REWARD_LABEL_PADLEFT)
        season_points_size = attributes.Get('season_points_size', DEFAULT_SEASON_POINTS_SIZE)
        on_click_function = attributes.Get('on_click_function', DEFAULT_ON_CLICK_FUNCTION)
        is_reward_track_points_label = attributes.Get('is_reward_track_points_label', False)
        points_hint = attributes.Get('hint', 'UI/Seasons/RewardPoints')
        self.compact = attributes.get('compact', None)
        if is_reward_track_points_label:
            reward_label_container_left = season_points_size
            reward_icon_container_left = 0
        else:
            reward_label_container_left = 0
            reward_icon_container_left = season_points_size
        reward_label_container = Container(name='reward_label_container', parent=self, align=uiconst.CENTERLEFT, width=REWARD_LABEL_WIDTH, height=season_points_size, left=reward_label_container_left)
        self.reward_label = reward_label_class(name='reward_label', text='', bold=True, parent=reward_label_container, align=uiconst.CENTERLEFT, padLeft=reward_label_padLeft, left=4)
        self.reward_icon_container = Container(name='reward_icon_container', parent=self, align=uiconst.CENTERLEFT, width=season_points_size, height=season_points_size, left=reward_icon_container_left if attributes.points > 9 else reward_icon_container_left / 1.7)
        reward_icon = Sprite(name='reward_icon', parent=self.reward_icon_container, align=uiconst.TOALL, padTop=1, texturePath=POINTS_ICON_PATH_64 if is_reward_track_points_label else POINTS_ICON_PATH_18)
        reward_icon.hint = localization.GetByLabel(points_hint)
        self.reward_label.color = SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
        if reward_label_fontsize:
            self.reward_label.fontsize = reward_label_fontsize
        self.update_points(attributes.points)
        if on_click_function:
            reward_icon.onClick = on_click_function
            self.reward_label.onClick = on_click_function

    def update_points(self, points):
        self.points = points
        if self.compact:
            self.reward_label.text = FmtAmt(self.points)
        else:
            self.reward_label.text = get_points_label_text(self.points)
        self.width = self.reward_icon_container.width + self.reward_label.width
