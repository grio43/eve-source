#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\challengeinfopaneltaskentry.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from seasons.client.challengeinfopanelprogressbar import ChallengeInfoPanelProgressBar
from seasons.client.seasonpoints import DEFAULT_SEASON_POINTS_SIZE
CHALLENGE_CONTAINER_WIDTH = 259
PROGRESS_FRAME_WIDTH_OFFSET = 9
PROGRESS_LABEL_LEFT = 7
HEADER_HEIGHT = 28
HEADER_PAD_TOP = 0
HEADER_PAD_BOTTOM = 0
HEADER_MOUSE_OVER_ANIMATION_SCALE = 2.0
HEADER_MOUSE_OVER_ANIMATION_DURATION = 0.5
HEADER_MOUSE_RESET_ANIMATION_SCALE = 1.0
HEADER_MOUSE_RESET_ANIMATION_DURATION = 0.1
LABEL_CONTAINER_HEIGHT = 25
LABEL_CONTAINER_WIDTH = CHALLENGE_CONTAINER_WIDTH - DEFAULT_SEASON_POINTS_SIZE
DETAILS_INFO_SIZE = 64
CATEGORY_CONTAINER_SIZE = DETAILS_INFO_SIZE - 10
CATEGORY_ICON_PADDING = 5
CATEGORY_ICON_SIZE_OFFSET = 4
CATEGORY_BORDER_WIDTH = 1
DETAILS_SIZE = DETAILS_INFO_SIZE + LABEL_CONTAINER_HEIGHT
DETAILS_PAD_RIGHT = 7
DETAILS_BACKGROUND_COLOR = (0, 0, 0, 0.2)
DETAILS_BLURRED_BACKGROUND_COLOR = (1, 1, 1, 0.9)
DETAILS_PAD_LEFT = 5
CHALLENGE_DESCRIPTION_WIDTH = CHALLENGE_CONTAINER_WIDTH - DETAILS_INFO_SIZE - DETAILS_PAD_RIGHT - DETAILS_PAD_LEFT
CHALLENGE_DESCRIPTION_PADDING = 10
CHALLENGE_DESCRIPTION_COLOR = (1, 1, 1, 0.5)
CHALLENGE_DESCRIPTION_PAD_SIDES = 5
FINISHED_CHECK_WIDTH = 14
FINISHED_CHECK_HEIGHT = 14
FINISHED_CHECK_ANIMATION_GLOW_COLOR = (1, 1, 1, 0.25)
FINISHED_CHECK_ANIMATION_GLOW_EXPAND = 2
FINISHED_CHECK_ANIMATION_DURATION = 0.5
COMPLETED_BACKGROUND_HIGHLIGHT_COLOR = (0.196, 1.0, 0.137, 0.5)
COMPLETED_CHECK_RES_PATH = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesCheck.png'
EXPIRED_BACKGROUND_HIGHLIGHT_COLOR = (1, 0.75, 0, 0.5)
DEFAULT_SHOW_DETAILS = True

class ChallengeInfoPanelTaskEntry(ContainerAutoSize):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 4
    default_padBottom = 0
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    tooltipPointer = uiconst.POINT_LEFT_2
    callbackTaskExpanded = None
    counter_background = None
    progress_bar = None

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.challenge = attributes.challenge
        self.open_challenges = attributes.open_challenges_function
        self._construct_progress_bar()
        self.objects_for_animations = []

    def _construct_progress_bar(self):
        self.progress_bar = ChallengeInfoPanelProgressBar(name='header_container', parent=self, align=uiconst.TOTOP, challenge=self.challenge, height=HEADER_HEIGHT, padTop=HEADER_PAD_TOP, padBottom=HEADER_PAD_BOTTOM, state=uiconst.UI_NORMAL, show_expiration_timer=True, progress_label_left=PROGRESS_LABEL_LEFT, opacity=0.0)
        animations.FadeIn(self.progress_bar)

    def GetHint(self):
        return None

    def update_challenge_progress(self, new_progress):
        self.challenge.progress = new_progress
        self.progress_bar.update_challenge(new_progress)

    def show_dormant(self):
        self.progress_bar.show_dormant()

    def complete_challenge(self):
        self.update_challenge_progress(self.challenge.max_progress)

    def _is_completed(self):
        return self.challenge.progress >= self.challenge.max_progress

    def Close(self):
        if self.progress_bar is not None:
            animations.StopAllAnimations(self.progress_bar)
            self.progress_bar.Close()
        self.progress_bar = None
        Container.Close(self)
