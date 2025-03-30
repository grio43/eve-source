#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\challengetaskprogressbar.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui.shared.infoPanels.const.infoPanelTextureConst import POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH
from eve.client.script.ui.shared.infoPanels.const.infoPanelUIConst import POINT_RIGHT_HEADER_COLOR
from seasons.client.const import get_challenge_progress_counter_label_text, DEFAULT_ANIMATE_PROGRESS
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_REGULAR
PROGRESS_FRAME_CORNER_SIZE = 16
PROGRESS_FRAME_OFFSET = -14
PROGRESS_FRAME_PAD_RIGHT = 7
PROGRESS_BAR_CORNER_SIZE = 24
PROGRESS_BAR_OFFSET = -13
PROGRESS_BAR_PAD_RIGHT = -1
PROGRESS_BAR_UPDATE_ANIMATION_SPEED = 2
PROGRESS_FRAME_OPACITY = 0.2
PROGRESS_BAR_DEFAULT_OPACITY = 0.6
PROGRESS_BAR_HOVER_OPACITY = 1.0
DEFAULT_PROGRESS_LABEL_PAD_LEFT = -2
DEFAULT_ADAPT_TEXT_COLOR_TO_PROGRESS = False
PROGRESS_BAR_COLOR_COMPLETE = (0.259, 0.631, 0.176, 1.0)
PROGRESS_BAR_COLOR_NOT_COMPLETE = POINT_RIGHT_HEADER_COLOR
PROGRESS_LABEL_COLOR_COMPLETE = (0.259, 0.631, 0.176, 1.0)
PROGRESS_LABEL_COLOR_NOT_COMPLETE = SEASON_THEME_TEXT_COLOR_REGULAR
TOOLTIP_WRAP_WIDTH = 200

class ChallengeTaskProgressBar(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.challenge = attributes.challenge
        self.pickState = uiconst.TR2_SPS_ON
        self.adapt_text_color_to_progress = attributes.Get('adapt_text_color_to_progress', DEFAULT_ADAPT_TEXT_COLOR_TO_PROGRESS)
        self.progress_frame_width = attributes.progress_frame_width
        self.progress_frame_width_offset = attributes.progress_frame_width_offset
        self.progress_frame_width_max = attributes.progress_frame_width
        self.progress_label_left = attributes.Get('progress_label_left', DEFAULT_PROGRESS_LABEL_PAD_LEFT)
        self.animate_progress = attributes.Get('animate_progress', DEFAULT_ANIMATE_PROGRESS)
        self.label_type_function = attributes.label_type_function
        self.left_sprite = None
        self.right_sprite = None
        self._construct_progress_label()
        self._construct_progress_bar()
        self.update_progress_bar(self.challenge.progress, suppress_animation=True)

    def _construct_progress_label(self):
        self.challenge_content_container = Container(name='challenge_content_container', parent=self, align=uiconst.ANCH_TOPLEFT, width=self.progress_frame_width, height=self.height, padLeft=6)
        self.challenge_label_container = Container(name='challenge_label_container', parent=self.challenge_content_container, padLeft=self.progress_label_left, align=uiconst.TOLEFT, width=self.progress_frame_width + 10, height=self.height)
        self.challenge_label = self.label_type_function(name='challenge_label', parent=self.challenge_label_container, align=uiconst.CENTERLEFT, padLeft=self.progress_frame_width - 5)
        self._update_counter()

    def _construct_progress_bar(self):
        self.progress_frame_container = Container(name='progress_frame_container', parent=self, align=uiconst.TOLEFT, clipChildren=True)
        self.progress_bar_container = Container(name='progress_bar_container', parent=self.progress_frame_container, align=uiconst.TOLEFT, clipChildren=True)
        self.progress_bar = Frame(name='progress_bar_fill', texturePath=POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH, cornerSize=PROGRESS_BAR_CORNER_SIZE, offset=PROGRESS_BAR_OFFSET, parent=self.progress_bar_container, color=POINT_RIGHT_HEADER_COLOR, padRight=PROGRESS_BAR_PAD_RIGHT)

    def update_progress_bar(self, new_progress, suppress_animation = False):
        progress_width = self._calculate_progress_width(new_progress)
        self.progress_bar_container.width = progress_width - self.progress_frame_width_offset
        if progress_width > self.progress_frame_width_max - self.progress_frame_width_offset:
            new_width = self.progress_frame_width_max
        else:
            new_width = progress_width - self.progress_frame_width_offset
        if self.animate_progress and not suppress_animation:
            animations.MorphScalar(self.progress_frame_container, 'width', startVal=self.progress_frame_container.width, endVal=new_width, duration=PROGRESS_BAR_UPDATE_ANIMATION_SPEED, callback=self.update_progress_bar_color)
        else:
            self.progress_frame_container.width = new_width
            self.update_progress_bar_color()

    def update_progress_bar_color(self):
        if self.adapt_text_color_to_progress:
            if self._is_challenge_complete():
                self.progress_bar.color = PROGRESS_BAR_COLOR_COMPLETE
                self.challenge_label.color = PROGRESS_LABEL_COLOR_COMPLETE
            else:
                self.progress_bar.color = PROGRESS_BAR_COLOR_NOT_COMPLETE
                self.challenge_label.color = PROGRESS_LABEL_COLOR_NOT_COMPLETE
        else:
            self.progress_bar.color = PROGRESS_BAR_COLOR_NOT_COMPLETE

    def _calculate_progress_width(self, new_progress):
        progress = float(new_progress) / float(self.challenge.max_progress)
        return float(self.progress_frame_width_max) * progress

    def update_challenge(self, new_progress):
        self.challenge.progress = new_progress
        self.update_progress_bar(new_progress)
        self._update_counter()

    def _is_challenge_not_started(self):
        return self.challenge.progress == 0

    def _is_challenge_complete(self):
        return self.challenge.progress == self.challenge.max_progress

    def _update_counter(self):
        self.challenge_label_container.Flush()
        if self.challenge.has_completion_rewards() and self._is_challenge_complete():
            self.challenge_label = self.label_type_function(name='challenge_label', parent=self.challenge_label_container, align=uiconst.CENTER)
            challenge_progress_counter_text = get_challenge_progress_counter_label_text(self.challenge)
            self.challenge_label = self.label_type_function(name='challenge_label', parent=self.challenge_label_container, align=uiconst.CENTERLEFT, padLeft=self.progress_frame_width - 5)
            self.challenge_label.SetText(challenge_progress_counter_text)
        else:
            challenge_progress_counter_text = get_challenge_progress_counter_label_text(self.challenge)
            self.challenge_label = self.label_type_function(name='challenge_label', parent=self.challenge_label_container, align=uiconst.CENTERLEFT, padLeft=self.progress_frame_width - 5)
            self.challenge_label.SetText(challenge_progress_counter_text)

    def GetHint(self):
        return None

    def OnMouseHover(self, *args):
        animations.StopAllAnimations(self)
        if self.challenge.reward_date:
            animations.MorphScalar(self.progress_bar, 'opacity', self.progress_bar.opacity, PROGRESS_BAR_HOVER_OPACITY, duration=0.2, curveType=uiconst.ANIM_OVERSHOT5)

    def OnMouseExit(self, *args):
        animations.StopAllAnimations(self)
        if self.challenge.reward_date:
            animations.MorphScalar(self.progress_bar, 'opacity', self.progress_bar.opacity, PROGRESS_BAR_DEFAULT_OPACITY, duration=0.2)
