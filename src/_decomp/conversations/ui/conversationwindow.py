#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\ui\conversationwindow.py
from math import pi
import time
import blue
import carbonui.const as uiconst
import uthread
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.fontconst import DEFAULT_FONTSIZE
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite, StreamingVideoSprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from conversations.animatedtransmissionwindow import AnimatedTransmissionWindow
from conversations.const import CONVERSATION_WINDOW_ID
from conversations.ui.completedconversationui import CompletedConversationUi
from conversations.ui.conversationwindowstyle import ConversationWindowStyle, AGENT_ID_TO_STYLE
from conversations.ui.conversationwindowunderlay import ConversationWindowUnderlay
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.themeColored import SpriteThemeColored, LineThemeColored
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_NEOCOM
from eve.client.script.ui.util.uix import GetTextWidth
from globalConfig import GetConversationLine3dPortraitEnabled
from localization import GetByMessageID, GetByLabel, IsPrimaryLanguage
from trinity import TR2_SBM_ADD, TR2_SBM_NONE
from uihider import get_ui_hider, UiHiderMixin
from uthread2 import call_after_wallclocktime_delay
import logging
logger = logging.getLogger(__name__)
COLOR_LABEL = Color.HextoRGBA('#e5f1ff')
DEFAULT_WIDTH = 580
DEFAULT_HEIGHT = 640
MAIN_CONTAINER_PADDING_WINDOW = 0
MAIN_CONTAINER_PADDING_TOP = 0
MAIN_CONTAINER_PADDING = (MAIN_CONTAINER_PADDING_WINDOW,
 MAIN_CONTAINER_PADDING_WINDOW + MAIN_CONTAINER_PADDING_TOP,
 MAIN_CONTAINER_PADDING_WINDOW,
 MAIN_CONTAINER_PADDING_WINDOW)
CONTENT_WIDTH = DEFAULT_WIDTH - 2 * MAIN_CONTAINER_PADDING_WINDOW
CONTENT_HORIZONTAL_PADDING = 20
CONTENT_VERTICAL_PADDING = 12
AGENT_PORTRAIT_SIZE = 320
AGENT_PORTRAIT_VERTICAL_PADDING = 1
AGENT_CONTAINER_GRADIENT = 'res:/UI/Texture/classes/Seasons/lineBreakGradient.png'
AGENT_CONTAINER_GRADIENT_OPACITY = 1.0
AGENT_CONTAINER_SIDE_TEXTURE = 'res:/UI/Texture/classes/ConversationUI/sideDecoration.png'
AGENT_CONTAINER_SIDE_GLOW_TEXTURE = 'res:/UI/Texture/classes/ConversationUI/sideDecorationGlow.png'
AGENT_CONTAINER_SIDE_TEXTURE_WIDTH = 3
AGENT_CONTAINER_SIDE_TEXTURE_HEIGHT = 36
AGENT_CONTAINER_SIDE_GLOW_TEXTURE_WIDTH = 23
AGENT_CONTAINER_SIDE_GLOW_TEXTURE_HEIGHT = 56
AGENT_CONTAINER_SIDE_OPACITY = 0.8
LINE_HEIGHT = 1
TITLE_LINE_PADDING = 16
TITLE_LINE_OPACITY = 0.3
TITLE_CONTAINER_BOT_PADDING = 4
TITLE_OPACITY = 1.0
TITLE_TO_EXPAND_OPTION_PADDING = 4
EXPAND_OPTION_ICON_SIZE = 12
TEXT_TOP_PADDING = 16
TEXT_BOTTOM_PADDING = 6
TEXT_OPACITY = 1.0
HINTS_CONTAINER_TOP_PADDING = 16
HINTS_TO_BUTTONS_PADDING = 16
HINT_CELL_PADDING = 2
HINTS_COLUMN_NUMBER = 2
HINT_TEXT_OPACITY = 1.0
HINT_TEXT_SEPARATION = 4
NEXT_CONVERSATION_LINE_LABEL = 'UI/Conversations/UI/NextConversationLine'
PREVIOUS_CONVERSATION_LINE_LABEL = 'UI/Conversations/UI/PreviousConversationLine'
CONTINUE_BUTTON_LABEL = 'UI/Conversations/UI/Close'
NAVIGATION_BUTTON_LABEL_PADDING = 16
NAVIGATION_BUTTON_HEIGHT = 24
NAVIGATION_BUTTON_PADDING_TOP = 4
NAVIGATION_BUTTON_PADDING_BOTTOM = 4
MAIN_CONTAINER_MIN_HEIGHT = AGENT_PORTRAIT_SIZE + 2 * AGENT_PORTRAIT_VERTICAL_PADDING
AUDIO_ACTIVATION_DELAY_SECONDS = 1.0
ICON_TEXT_EXPAND = 'res:/UI/Texture/classes/ConversationUI/iconTextExpand.png'
ICON_TEXT_COLLAPSE = 'res:/UI/Texture/classes/ConversationUI/iconTextCollapse.png'
WINDOW_TITLE_LABEL = 'UI/Conversations/UI/ConversationWindowTitle'
SETTING_CONVERSATION_WINDOW_TEXT_EXPAND = 'conversation_window_text_expand'
COMPLETED_UI_HEIGHT = 26
COMPLETED_UI_PADDING = 8
MAX_TEXT_SCROLL_HEIGHT = 400
DEFAULT_HINT_ICON_SIZE = 32

def get_total_container_height(container):
    return container.height + container.padTop + container.padBottom


def is_line_3d_portrait_enabled():
    return GetConversationLine3dPortraitEnabled(sm.GetService('machoNet'))


class ConversationWindow(AnimatedTransmissionWindow, UiHiderMixin):
    __notifyevents__ = ['OnAudioActivated',
     'OnAudioDeactivated',
     'OnUIScalingChange',
     'OnHideUI',
     'OnShowUI',
     'OnSetDevice']
    default_windowID = CONVERSATION_WINDOW_ID
    default_iconNum = 'res:/UI/Texture/WindowIcons/tutorial.png'
    default_isCollapseable = False
    default_isStackable = False
    default_isLightBackgroundConfigurable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isMinimizable = True
    default_fixedWidth = DEFAULT_WIDTH
    default_fixedHeight = DEFAULT_HEIGHT
    default_left = 385
    default_top = 75
    default_hideHeaderIcons = False
    default_is_content_expandable = False
    default_is_decoration_on_sides = True
    default_are_hints_visible = True
    default_are_navigation_buttons_enabled = True
    default_show_warning_on_first_close_setting = None
    default_show_warning_on_first_close_dialog = None
    default_close_on_audio_end = False
    default_is_close_button_visible = False
    default_style = ConversationWindowStyle
    current_sound_id = None
    default_conversation_id = None
    default_is_completed = False
    default_delay_seconds_between_audio_ended_and_show_next = 0
    default_should_close_on_continue = False
    default_should_autoprogress = True

    def ApplyAttributes(self, attributes):
        self.is_content_expandable = attributes.Get('is_content_expandable', self.default_is_content_expandable)
        self.is_decoration_on_sides = attributes.Get('is_decoration_on_sides', self.default_is_decoration_on_sides)
        self.are_hints_visible = attributes.Get('are_hints_visible', self.default_are_hints_visible)
        self.are_navigation_buttons_enabled = attributes.Get('are_navigation_buttons_enabled', self.default_are_navigation_buttons_enabled)
        self.show_warning_on_first_close_setting = attributes.Get('show_warning_on_first_close_setting', self.default_show_warning_on_first_close_setting)
        self.show_warning_on_first_close_dialog = attributes.Get('show_warning_on_first_close_dialog', self.default_show_warning_on_first_close_dialog)
        self.close_on_audio_end = attributes.Get('close_on_audio_end', self.default_close_on_audio_end)
        self.is_close_button_visible = attributes.Get('is_close_button_visible', self.default_is_close_button_visible)
        self.delay_seconds_between_audio_ended_and_show_next = attributes.Get('delay_seconds_between_audio_ended_and_show_next', self.default_delay_seconds_between_audio_ended_and_show_next)
        self.conversation_id = attributes.Get('conversation_id', self.default_conversation_id)
        self.is_completed = attributes.Get('is_completed', self.default_is_completed)
        self.should_close_on_continue = attributes.Get('should_close_on_continue', self.default_should_close_on_continue)
        self.should_autoprogress = attributes.Get('should_autoprogress', self.default_should_autoprogress)
        self.style = None
        self.styled_backgrounds_container = None
        self.background_gradient_container = None
        self.portrait_side_line_left_container = None
        self.portrait_side_line_right_container = None
        self.portrait_side_line_glow_left_container = None
        self.portrait_side_line_glow_right_container = None
        self.window_top_line_container = None
        self.window_top_line_glow_container = None
        self.is_waiting_for_delay_to_show_next_conversation = False
        self.next_conversation_tasklet = None
        self.showing_next = False
        self.title_line_container = None
        self.title_line = None
        self.expand_option_container = None
        self.expand_option_sprite = None
        self.text = None
        self.text_container = None
        self.text_label = None
        self.hints_line = None
        self.hints_container = None
        self.navigation_button_container = None
        self.completed_ui_container = None
        self.paragraph_labels = []
        self.hint_labels = []
        self.agent_portrait_intro_3d_container = None
        self.agent_portrait_intro_video_container = None
        self.agent_portrait_image_sprite = None
        self.current_agent_id = None
        self.current_line = None
        self._is_portrait_loaded = False
        super(ConversationWindow, self).ApplyAttributes(attributes)
        self.MakeUnResizeable()
        self.SetCaption(GetByLabel(WINDOW_TITLE_LABEL))
        sm.RegisterNotify(self)
        self._conversation_svc = sm.GetService('conversationService')
        self._audio_svc = sm.GetService('audio')
        self._audio_svc.SubscribeToEventCallback(self._on_sound_event_completed)
        self.is_audio_activated = self._audio_svc.IsActivated()
        self.sound_playing = False
        self.sound_start_time = 0
        self.manual_expanded_setting = self._get_expand_setting()
        content_container_alignment = self._get_content_container_alignment()
        self.main_container = Container(name='main_conversation_container', parent=self.sr.main, align=uiconst.TOTOP, height=DEFAULT_HEIGHT, padding=MAIN_CONTAINER_PADDING)
        self.portrait_container = Container(name='portrait_container', parent=self.main_container, align=self._get_portrait_container_alignment(), width=self._get_portrait_container_width(), height=self._get_portrait_container_height())
        self.portrait_wrapper_container = None
        content_horizontal_padding = self._get_content_horizontal_padding()
        content_top_padding = self._get_content_top_padding()
        content_bottom_padding = self._get_content_bottom_padding()
        content_width = self._get_content_width() - content_horizontal_padding
        self.content_container = Container(name='conversation_content_container', parent=self.main_container, align=content_container_alignment, width=content_width, height=0, padding=(content_horizontal_padding,
         content_top_padding,
         0,
         content_bottom_padding))
        self._add_title()
        has_incoming_transmission_sound = self._transmission_sound_effect is not None
        self.show_next_conversation(play_incoming_transmission_sound=has_incoming_transmission_sound)
        self.SetParent(uicore.layer.alwaysvisible)
        if self.is_neocom_hidden():
            self.MakeUnMinimizable()

    def is_neocom_hidden(self):
        return get_ui_hider().is_ui_element_hidden(UNIQUE_NAME_NEOCOM)

    def OnEndMinimize_(self, *args):
        super(ConversationWindow, self).OnEndMinimize_(*args)
        self.SetParent(uicore.layer.alwaysvisible)

    def OnEndMaximize_(self, *args):
        super(ConversationWindow, self).OnEndMaximize_(*args)
        self.SetParent(uicore.layer.alwaysvisible)

    def InitializeStatesAndPosition(self, *args, **kwds):
        super(ConversationWindow, self).InitializeStatesAndPosition(*args, **kwds)
        self._correct_height(style_changed=True)
        self.SetParent(uicore.layer.alwaysvisible)

    def animate_text_portrait_in(self):
        timeOffset = 0.6
        portrait_offset = 0.5
        portrait_duration = 0.5
        for label in self.paragraph_labels:
            timeOffset += self._FadeInLabel(label, timeOffset, TEXT_OPACITY)

        if self._should_show_hints():
            if self.hints_line:
                animations.FadeIn(self.hints_container, duration=0.6, timeOffset=timeOffset)
            for label in self.hint_labels:
                timeOffset += self._FadeInLabel(label, timeOffset, HINT_TEXT_OPACITY)

        if self._should_show_navigation_buttons():
            self.navigation_button_container.SetState(uiconst.UI_DISABLED)
            animations.FadeIn(self.navigation_button_container, 1.0, duration=0.6, timeOffset=timeOffset, callback=lambda : self.navigation_button_container.SetState(uiconst.UI_NORMAL))
            timeOffset += 0.6
        blue.synchro.SleepWallclock(1000 * portrait_offset)
        if self.agent_portrait_intro_3d_container is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.opacity = 0.0
            self.agent_portrait_intro_3d_container.avatarscenecontainer.fade_in_duration = portrait_duration
            self.agent_portrait_intro_3d_container.avatarscenecontainer.fade_out_duration = 0.3
            self.agent_portrait_intro_3d_container.avatarscenecontainer.fade_out_offset = 0.0
        self.notify_of_open()

    def _FadeInLabel(self, label, timeOffset, opacity):
        animations.FadeIn(label, opacity, duration=0.6, timeOffset=timeOffset)
        animations.MorphScalar(label, 'left', 8, 0, duration=0.4, timeOffset=timeOffset)
        return self._GetTimeOffsetByTextLength(label.text)

    def _GetTimeOffsetByTextLength(self, text):
        numLetters = len(text)
        return max(1.2, numLetters / 100.0)

    def _clear_container(self, container):
        if self._is_ui_element_available(container):
            container.Flush()
            container.Close()

    def _is_ui_element_available(self, ui_element):
        return ui_element and not ui_element.destroyed

    def _get_content_container_alignment(self):
        return uiconst.TOTOP

    def _get_main_container_width(self):
        return DEFAULT_WIDTH

    def _get_main_container_height(self):
        content_container_height_with_padding = self.content_container.height + self.content_container.padTop + self.content_container.padBottom
        vertical_height = MAIN_CONTAINER_MIN_HEIGHT + content_container_height_with_padding
        return vertical_height

    def _get_content_width(self):
        return CONTENT_WIDTH

    def _get_content_horizontal_padding(self):
        return CONTENT_HORIZONTAL_PADDING

    def _get_content_top_padding(self):
        return CONTENT_VERTICAL_PADDING

    def _get_content_bottom_padding(self):
        return CONTENT_VERTICAL_PADDING

    def _get_portrait_container_width(self):
        return self._get_content_width()

    def _get_portrait_container_height(self):
        return AGENT_PORTRAIT_SIZE + 2 * AGENT_PORTRAIT_VERTICAL_PADDING

    def _get_portrait_container_alignment(self):
        return uiconst.TOTOP

    def _get_agent_portrait_size(self):
        return (AGENT_PORTRAIT_SIZE, AGENT_PORTRAIT_SIZE)

    def _get_text_scroll_height(self):
        try:
            return min(self.text_paragraphs_container.height, MAX_TEXT_SCROLL_HEIGHT)
        except AttributeError:
            return MAX_TEXT_SCROLL_HEIGHT

    def _load_portrait(self, agent_data, next_line):
        self._clear_container(self.portrait_wrapper_container)
        self.portrait_wrapper_container = Container(name='portrait_wrapper_container', parent=self.portrait_container, align=uiconst.TOTOP, width=self.portrait_container.width, height=self.portrait_container.height)
        if self.is_decoration_on_sides:
            self._load_portrait_side_lines()
            self._load_portrait_side_lines_glow()
        self._load_agent_portrait(agent_data, next_line)
        if next_line.scene_path is not None or agent_data.scene_path is not None:
            pass

    def _load_agent_container_bg(self):
        agent_portrait_width, agent_portrait_height = self._get_agent_portrait_size()
        self.background_gradient = Sprite(name='agent_portrait_bg', parent=self.portrait_wrapper_container, align=uiconst.CENTER, width=agent_portrait_width, height=agent_portrait_height, texturePath=AGENT_CONTAINER_GRADIENT, opacity=AGENT_CONTAINER_GRADIENT_OPACITY)
        self._set_sprite_color(self.background_gradient, glow=True)

    def _is_using_low_quality_characters(self):
        from avatardisplay.avatardisplay import IsUsingLowQualityCharacters
        return IsUsingLowQualityCharacters()

    def _load_agent_portrait(self, agent_data, next_line, restart_audio = False):
        self._load_agent_portrait_3d(agent_data, next_line, restart_audio=restart_audio)
        self._load_agent_portrait_videos(agent_data)
        self._load_agent_portrait_image(agent_data, restart_audio=restart_audio)

    def _load_agent_portrait_3d(self, agent_data, next_line, restart_audio = False):
        if self._is_using_low_quality_characters():
            return
        if self._is_portrait_loaded or next_line.scene_path is None and agent_data.scene_path is None:
            return
        from avatardisplay.avatardisplay import PlaybackScene
        from avatardisplay.errors import FailedToPlaybackScene
        agent_portrait_width, agent_portrait_height = self._get_agent_portrait_size()
        self.agent_portrait_intro_3d_container = Container(parent=self.portrait_wrapper_container, name='agent_portrait_intro_3d_container', align=uiconst.CENTER, width=agent_portrait_width, height=agent_portrait_height, display=True)
        scene_dir = None
        if is_line_3d_portrait_enabled() and next_line.scene_path is not None:
            scene_dir = next_line.scene_path
        elif agent_data.scene_path is not None:
            scene_dir = agent_data.scene_path
        if scene_dir is not None:
            try:
                PlaybackScene(scene_dir=scene_dir, parent=self.agent_portrait_intro_3d_container, hide=True, sound_start_time=self.sound_start_time if not restart_audio else 0)
                self._is_portrait_loaded = True
            except FailedToPlaybackScene as exc:
                logger.exception(exc)

    def _load_agent_portrait_image(self, agent_data, restart_audio = False):
        if self._is_portrait_loaded:
            return
        agent_portrait_width, agent_portrait_height = self._get_agent_portrait_size()
        self.agent_portrait_image_sprite = Sprite(name='agent_portrait', parent=self.portrait_wrapper_container, align=uiconst.CENTER, width=agent_portrait_width, height=agent_portrait_height, texturePath=agent_data.image_path)
        self._is_portrait_loaded = True
        if restart_audio:
            self._start_playing_audio()

    def _load_agent_portrait_videos(self, agent_data):
        if self._is_portrait_loaded or not agent_data.use_video:
            return
        agent_portrait_size = self._get_agent_portrait_size()[0]
        has_intro_video = agent_data.use_intro_video
        if has_intro_video:
            self.agent_portrait_intro_video_container = Container(parent=self.portrait_wrapper_container, name='agent_portrait_intro_video_container', align=uiconst.TOTOP_NOPUSH, width=self.portrait_container.width, height=self.portrait_container.height, display=False)
            self.agent_portrait_intro_video = StreamingVideoSprite(parent=self.agent_portrait_intro_video_container, name='agent_portrait_intro_video', videoPath=agent_data.intro_video_path, videoLoop=False, align=uiconst.CENTER, width=agent_portrait_size, height=agent_portrait_size, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_NONE, disableAudio=True)
            self.agent_portrait_intro_video.Pause()
            self.agent_portrait_intro_video_container.display = False
        self.agent_portrait_loop_video_container = Container(parent=self.portrait_wrapper_container, name='agent_portrait_loop_video_container', align=uiconst.TOTOP_NOPUSH, width=self.portrait_container.width, height=self.portrait_container.height, display=False)
        self.agent_portrait_loop_video = StreamingVideoSprite(parent=self.agent_portrait_loop_video_container, name='agent_portrait_loop_video', videoPath=agent_data.loop_video_path, videoLoop=True, align=uiconst.CENTER, width=agent_portrait_size, height=agent_portrait_size, state=uiconst.UI_DISABLED, blendMode=TR2_SBM_NONE, disableAudio=True)
        self.agent_portrait_loop_video_container.display = False
        if has_intro_video:
            self.agent_portrait_intro_video.OnVideoFinished = self._play_agent_portrait_loop_video
            self._play_agent_portrait_intro_video()
        else:
            self.agent_portrait_intro_video = None
            self.agent_portrait_intro_video_container = None
            self._play_agent_portrait_loop_video()
        self._is_portrait_loaded = True

    def _play_agent_portrait_intro_video(self):
        self.agent_portrait_intro_video_container.display = True
        self.agent_portrait_intro_video.Play()

    def _play_agent_portrait_loop_video(self):
        if self.agent_portrait_intro_video:
            self.agent_portrait_intro_video_container.display = False
        self.agent_portrait_loop_video_container.display = True
        self.agent_portrait_loop_video.Play()

    def _get_sprite_class(self):
        if self.style.style_color:
            return Sprite
        return SpriteThemeColored

    def _set_sprite_color(self, sprite, glow = True):
        if not sprite:
            return
        if self.style.style_color:
            sprite.color = self.style.style_color
            return
        if glow:
            sprite.colorType = uiconst.COLORTYPE_UIHILIGHTGLOW
        else:
            sprite.colorType = uiconst.COLORTYPE_UIHILIGHT

    def _load_portrait_side_lines(self):
        position_top = (self.portrait_container.height - AGENT_CONTAINER_SIDE_TEXTURE_HEIGHT) / 2
        sprite_class = self._get_sprite_class()
        self._clear_container(self.portrait_side_line_left_container)
        self._clear_container(self.portrait_side_line_right_container)
        self.portrait_side_line_left_container = Container(name='portrait_side_line_left_container', parent=self.portrait_container, align=uiconst.ANCH_TOPLEFT, width=self.portrait_container.width, height=self.portrait_container.height)
        portrait_side_line_left = sprite_class(name='portrait_side_line_left', parent=self.portrait_side_line_left_container, texturePath=AGENT_CONTAINER_SIDE_TEXTURE, align=uiconst.ANCH_TOPLEFT, useSizeFromTexture=True, top=position_top, rotation=pi, opacity=AGENT_CONTAINER_SIDE_OPACITY, blendMode=TR2_SBM_ADD)
        self._set_sprite_color(portrait_side_line_left, glow=True)
        self.portrait_side_line_right_container = Container(name='portrait_side_line_right_container', parent=self.portrait_container, align=uiconst.ANCH_TOPRIGHT, width=self.portrait_container.width, height=self.portrait_container.height)
        portrait_side_line_right = sprite_class(name='portrait_side_line_right', parent=self.portrait_side_line_right_container, texturePath=AGENT_CONTAINER_SIDE_TEXTURE, align=uiconst.ANCH_TOPRIGHT, useSizeFromTexture=True, top=position_top + AGENT_CONTAINER_SIDE_TEXTURE_HEIGHT, left=AGENT_CONTAINER_SIDE_TEXTURE_WIDTH, opacity=AGENT_CONTAINER_SIDE_OPACITY, blendMode=TR2_SBM_ADD)
        self._set_sprite_color(portrait_side_line_right, glow=True)

    def _load_portrait_side_lines_glow(self):
        position_top_glow = (self.portrait_container.height - AGENT_CONTAINER_SIDE_GLOW_TEXTURE_HEIGHT) / 2
        sprite_class = self._get_sprite_class()
        self._clear_container(self.portrait_side_line_glow_left_container)
        self._clear_container(self.portrait_side_line_glow_right_container)
        self.portrait_side_line_glow_left_container = Container(name='portrait_side_line_glow_left_container', parent=self.portrait_container, align=uiconst.ANCH_TOPLEFT, width=self.portrait_container.width, height=self.portrait_container.height)
        portrait_side_line_glow_left = sprite_class(name='portrait_side_line_glow_left', parent=self.portrait_side_line_glow_left_container, texturePath=AGENT_CONTAINER_SIDE_GLOW_TEXTURE, align=uiconst.ANCH_TOPLEFT, useSizeFromTexture=True, top=position_top_glow, left=-AGENT_CONTAINER_SIDE_GLOW_TEXTURE_WIDTH / 2, blendMode=TR2_SBM_ADD, rotation=pi)
        self._set_sprite_color(portrait_side_line_glow_left, glow=False)
        self.portrait_side_line_glow_right_container = Container(name='portrait_side_line_glow_right_container', parent=self.portrait_container, align=uiconst.ANCH_TOPRIGHT, width=self.portrait_container.width, height=self.portrait_container.height)
        portrait_side_line_glow_right = sprite_class(name='portrait_side_line_glow_right', parent=self.portrait_side_line_glow_right_container, texturePath=AGENT_CONTAINER_SIDE_GLOW_TEXTURE, align=uiconst.ANCH_TOPRIGHT, useSizeFromTexture=True, top=position_top_glow + AGENT_CONTAINER_SIDE_GLOW_TEXTURE_HEIGHT, left=AGENT_CONTAINER_SIDE_GLOW_TEXTURE_WIDTH / 2, blendMode=TR2_SBM_ADD)
        self._set_sprite_color(portrait_side_line_glow_right, glow=False)

    def _add_title(self):
        self.title_container = Container(name='title_container', parent=self.content_container, align=uiconst.TOTOP, width=self.content_container.width, height=0, padBottom=TITLE_CONTAINER_BOT_PADDING)
        title_text_width = self.content_container.width
        if self.is_content_expandable:
            self.expand_option_container = Container(name='expand_option_container', parent=self.title_container, align=uiconst.TORIGHT, width=EXPAND_OPTION_ICON_SIZE, height=EXPAND_OPTION_ICON_SIZE)
            title_text_width = title_text_width - EXPAND_OPTION_ICON_SIZE - TITLE_TO_EXPAND_OPTION_PADDING
        self.title_text_container = Container(name='title_text_container', parent=self.title_container, align=uiconst.TOLEFT, width=title_text_width, height=0)
        self.title_label = EveLabelLarge(name='title_label', parent=self.title_text_container, text='', width=title_text_width, align=uiconst.TOTOP, opacity=TITLE_OPACITY, blendMode=TR2_SBM_NONE)

    def _load_expand_option_sprite(self, expand):
        if not self.is_content_expandable or not self.is_audio_activated:
            return
        expand_sprite_texture = ICON_TEXT_COLLAPSE if expand else ICON_TEXT_EXPAND
        if self._is_ui_element_available(self.expand_option_sprite):
            self.expand_option_sprite.Close()
        self.expand_option_sprite = Sprite(name='expand_option', parent=self.expand_option_container, align=uiconst.CENTER, width=EXPAND_OPTION_ICON_SIZE, height=EXPAND_OPTION_ICON_SIZE, texturePath=expand_sprite_texture)
        self.expand_option_sprite.OnClick = self._expand_content

    def _load_title(self, title):
        self.title_label.text = title

    def _load_title_line(self, expand = True):
        self._clear_container(self.title_line_container)
        if expand or not self.is_content_expandable:
            self.title_line_container = Container(name='title_line_container', parent=self.content_container, align=uiconst.TOTOP, width=self.content_container.width, height=LINE_HEIGHT)
            self.title_line = LineThemeColored(name='title_line', parent=self.title_line_container, align=uiconst.TOTOP, weight=LINE_HEIGHT)
            if self.style:
                self.style_line(self.title_line)

    def _should_collapse_content(self, expand):
        return self.is_content_expandable and not expand

    def _should_show_text(self):
        return self.text

    def _should_show_hints(self):
        return self.are_hints_visible and self.hints

    def _should_show_hints_line(self):
        return self._should_show_text() and self._should_show_hints()

    def _get_scroll_bar_color(self):
        if self.style is not None:
            return self.style.scroll_bar_color
        else:
            return

    def _load_text(self, expand = True):
        self._clear_container(self.text_container)
        if not self._should_show_text() or self._should_collapse_content(expand):
            return
        self.text_container = Container(name='text_container', parent=self.content_container, align=uiconst.TOTOP, width=self.content_container.width, height=0, padTop=TEXT_TOP_PADDING, padBottom=TEXT_BOTTOM_PADDING)
        scroll = ScrollContainer(align=uiconst.TOTOP, parent=self.text_container, height=self._get_text_scroll_height(), scrollBarColor=self._get_scroll_bar_color())
        self.text_paragraphs_container = ContainerAutoSize(parent=scroll, align=uiconst.TOTOP)
        self.paragraph_labels = []
        paragraphList = self.GetTextByParagraphs(self.text)
        for text in paragraphList:
            label = EveLabelLarge(name='text_label', parent=self.text_paragraphs_container, text=text, align=uiconst.TOTOP, opacity=0.0, color=COLOR_LABEL, padBottom=12)
            self.paragraph_labels.append(label)

        self.text_paragraphs_container.SetSizeAutomatically()
        scroll.height = self._get_text_scroll_height()

    def GetTextByParagraphs(self, text):
        paragraphList = text.split('\r\n\r\n')
        return paragraphList

    def _load_hints(self, expand = True):
        self._clear_container(self.hints_container)
        if not self._should_show_hints() or self._should_collapse_content(expand):
            return
        self.hints_container = ContainerAutoSize(name='hints_container', parent=self.content_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, opacity=0.0)
        if self._should_show_hints_line():
            self._load_hints_line()
        self.hint_labels = []
        for hint in self.hints:
            paragraph_list = self.GetTextByParagraphs(GetByMessageID(hint.text))
            hint_container = ContainerAutoSize(name='hint_container', parent=self.hints_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padBottom=12 if paragraph_list else 0)
            hint_sprite = self._check_create_hint_sprite(hint, hint_container)
            hint_labels_container = ContainerAutoSize(name='hint_labels_container', parent=hint_container, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=hint_sprite.height if hint_sprite else 0)
            text_height = 0
            for text in paragraph_list:
                pad_top = 12 if self.hint_labels else 0
                label = EveLabelLarge(name='hint_text_label', parent=hint_labels_container, text=text, align=uiconst.TOTOP, color=(1, 1, 1, 1), opacity=0.0, padTop=pad_top)
                text_height += label.height + pad_top
                self.hint_labels.append(label)

            hint_labels_container.SetSizeAutomatically()
            if hint_sprite and text_height < hint_sprite.height:
                hint_labels_container.padTop += max(0, (hint_sprite.height - text_height) / 2)

        self.hints_container.SetSizeAutomatically()
        self.hints_container.UpdateAlignment()

    def _load_hints_line(self):
        self.hints_line = LineThemeColored(name='hints_line', parent=self.hints_container, align=uiconst.TOTOP, weight=LINE_HEIGHT, padBottom=12)
        if self.style:
            self.style_line(self.hints_line)

    def _check_create_hint_sprite(self, hint, parent):
        if not hint.iconID:
            return
        hint_image = self._conversation_svc.get_line_hint_image(hint.iconID)
        hint_image_path = hint_image.image_path
        hint_image_size = hint.image_size or DEFAULT_HINT_ICON_SIZE
        pad_right = 6
        hint_sprite_container = Container(name='hint_sprite_container', parent=parent, width=hint_image_size + pad_right, height=hint_image_size, padLeft=-HINT_CELL_PADDING, align=uiconst.TOLEFT)
        hint_sprite = Sprite(name='hint_image_icon', parent=hint_sprite_container, width=hint_image_size, height=hint_image_size, texturePath=hint_image_path, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)
        if hint_sprite and hint.image_color:
            hint_sprite.SetRGBA(*hint.image_color)
        return hint_sprite

    def _should_expand_content(self):
        language = getattr(session, 'languageID', None)
        is_client_localized = not IsPrimaryLanguage(language) if language else True
        is_audio_enabled = self.is_audio_activated
        return is_client_localized or not is_audio_enabled

    def _is_content_expanded(self):
        return self.text_container is not None and not self.text_container.destroyed

    def _expand_content(self):
        expand = not self._is_content_expanded()
        settings.char.ui.Set(SETTING_CONVERSATION_WINDOW_TEXT_EXPAND, expand)
        self.manual_expanded_setting = expand
        self._clear_container(self.navigation_button_container)
        self._show_expanded_content(expand)
        self._load_navigation_buttons()
        self._correct_height(style_changed=False)

    def _should_show_navigation_buttons(self):
        return self._should_show_next_button() or self._should_show_previous_button() or self._should_show_close_button()

    def _should_show_next_button(self):
        return self.are_navigation_buttons_enabled and self._conversation_svc.are_any_conversation_lines_left()

    def _should_show_previous_button(self):
        return self.are_navigation_buttons_enabled and self._conversation_svc.are_any_previous_conversation_lines_available()

    def _should_show_close_button(self):
        return self.is_close_button_visible and not self._conversation_svc.are_any_conversation_lines_left()

    def _load_navigation_buttons(self):
        if not self._should_show_navigation_buttons():
            return
        self._clear_container(self.navigation_button_container)
        self.navigation_button_container = Container(name='navigation_button_container', align=uiconst.TOBOTTOM, parent=self.content_container, height=NAVIGATION_BUTTON_HEIGHT, padTop=NAVIGATION_BUTTON_PADDING_TOP, opacity=0.0)
        if self._should_show_hints_line():
            self.navigation_button_container.padTop += HINTS_TO_BUTTONS_PADDING
        if self._should_show_next_button():
            label_text = GetByLabel(NEXT_CONVERSATION_LINE_LABEL)
            label_text_width = GetTextWidth(strng=label_text, fontsize=DEFAULT_FONTSIZE)
            button_width = label_text_width + 2 * NAVIGATION_BUTTON_LABEL_PADDING
            next_button = Button(name='next_button', parent=self.navigation_button_container, align=uiconst.TORIGHT, fixedwidth=button_width, label=label_text, func=self.show_next_conversation, args=())
            self.style_button(next_button)
        if self._should_show_previous_button():
            label_text = GetByLabel(PREVIOUS_CONVERSATION_LINE_LABEL)
            label_text_width = GetTextWidth(strng=label_text, fontsize=DEFAULT_FONTSIZE)
            button_width = label_text_width + 2 * NAVIGATION_BUTTON_LABEL_PADDING
            previous_button = Button(name='previous_button', parent=self.navigation_button_container, align=uiconst.TOLEFT, fixedwidth=button_width, label=label_text, func=self.show_previous_conversation, args=())
            self.style_button(previous_button)
        if self._should_show_close_button():
            label_text = GetByLabel(CONTINUE_BUTTON_LABEL)
            label_text_width = GetTextWidth(strng=label_text, fontsize=DEFAULT_FONTSIZE)
            button_width = label_text_width + 2 * NAVIGATION_BUTTON_LABEL_PADDING
            close_button = Button(name='close_button', parent=self.navigation_button_container, align=uiconst.TORIGHT, fixedwidth=button_width, label=label_text, func=self._on_continue_button, args=())
            self.style_button(close_button)

    def _on_continue_button(self, *args):
        sm.ScatterEvent('OnClientEvent_ConversationContinueButtonClicked', self.conversation_id)
        if self.should_close_on_continue:
            self._close_if_open()

    def _clear_navigation_buttons(self):
        self._clear_container(self.navigation_button_container)
        self.navigation_button_container = None

    def show_completed_ui(self):
        self.is_completed = True
        if self._is_ui_element_available(self.completed_ui_container):
            return
        self._load_completed_ui()
        self._correct_height()

    def _load_completed_ui(self):
        self._clear_container(self.completed_ui_container)
        if not self.is_completed:
            return
        self.completed_ui_container = CompletedConversationUi(name='completed_ui_container', align=uiconst.TOBOTTOM, parent=self.content_container, width=self.content_container.width, height=COMPLETED_UI_HEIGHT, padTop=COMPLETED_UI_PADDING)

    def _clear_completed_ui(self):
        self._clear_container(self.completed_ui_container)
        self.completed_ui_container = None

    def style_button(self, button):
        if self.style.style_color:
            button.SetColor(self.style.style_color)
        if self.style.label_color:
            button.SetLabelColor(self.style.label_color)

    def _correct_height(self, style_changed = False):
        title_height = self.title_label.height
        self.title_container.height = title_height
        self.title_text_container = title_height
        title_height = get_total_container_height(self.title_container)
        title_line_height = 0
        text_height = 0
        hints_height = 0
        if self._is_ui_element_available(self.title_line_container):
            title_line_height = get_total_container_height(self.title_line_container)
        if self._is_ui_element_available(self.text_container):
            self.text_container.height = self._get_text_scroll_height()
            text_height = get_total_container_height(self.text_container)
        if self._is_ui_element_available(self.hints_container):
            hints_height = get_total_container_height(self.hints_container)
        self.content_container.height = title_height + title_line_height + text_height + hints_height
        if self._should_show_navigation_buttons() and self._is_ui_element_available(self.navigation_button_container):
            navigation_button_height = get_total_container_height(self.navigation_button_container)
            self.content_container.height = self.content_container.height + navigation_button_height
        if self.is_completed and self._is_ui_element_available(self.completed_ui_container):
            completed_ui_height = get_total_container_height(self.completed_ui_container)
            self.content_container.height = self.content_container.height + completed_ui_height
        self.main_container.height = self._get_main_container_height()
        self._apply_fixed_size()
        if style_changed:
            self._apply_style()
        self.style_backgrounds()

    def _apply_fixed_size(self):
        height = self.main_container.height + 2 * MAIN_CONTAINER_PADDING_WINDOW + MAIN_CONTAINER_PADDING_TOP
        width = self._get_main_container_width()
        width, height = self.GetWindowSizeForContentSize(width=width, height=height)
        self.SetFixedWidth(width)
        self.SetFixedHeight(height)

    def _on_sound_event_completed(self, event_str):
        if self.agent_portrait_intro_3d_container is not None:
            avatar_context = self.agent_portrait_intro_3d_container.avatarscenecontainer.context
            avatar_scene_play_event = avatar_context.GetSceneAudioPlayingEvent() if avatar_context else None
        else:
            avatar_scene_play_event = None
        if not self.sound_playing and not avatar_scene_play_event:
            return
        if event_str is None or not self.is_audio_activated:
            return
        current_play_event = self._conversation_svc.get_play_event(self.current_sound_id)
        if event_str == current_play_event or event_str == avatar_scene_play_event:
            self.sound_playing = False
            if self.should_autoprogress:
                self.show_next_conversation(delay=True, play_incoming_transmission_sound=False)

    def _stop_playing_audio(self):
        self.sound_playing = False
        if self.current_sound_id is None:
            return
        stop_event = self._conversation_svc.get_stop_event(self.current_sound_id)
        if stop_event:
            self._audio_svc.SendUIEvent(stop_event)

    def _start_playing_audio(self):
        if self.destroyed or session.languageID.lower() not in ('en', 'ko', 'es'):
            return
        if uicore.layer.systemmenu.isopen:
            return
        play_event = self._conversation_svc.get_play_event(self.current_sound_id)
        if play_event and self.is_audio_activated:
            self.sound_playing = True
            self.sound_start_time = time.time()
            self._audio_svc.SendUIEventWithCallback(play_event)

    def OnAudioActivated(self):
        self.is_audio_activated = True
        call_after_wallclocktime_delay(self._activate_audio, AUDIO_ACTIVATION_DELAY_SECONDS)

    def _activate_audio(self):
        if self.destroyed:
            return
        if not uicore.layer.systemmenu.isopen:
            self._start_playing_audio()
        if not self._should_show_navigation_buttons() and self.navigation_button_container:
            self._clear_navigation_buttons()
            self._correct_height()
        expand = self._get_expand_setting()
        self._load_expand_option_sprite(expand)

    def OnAudioDeactivated(self):
        self.is_audio_activated = False
        self._stop_playing_audio()
        if self.agent_portrait_intro_3d_container is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.context.StopAudio()
        did_content_change = False
        if self._should_expand_content() and not self._is_content_expanded():
            self._show_expanded_content(expand=True)
            did_content_change = True
        if self._should_show_navigation_buttons() and not self.navigation_button_container:
            self._load_navigation_buttons()
            did_content_change = True
        if did_content_change:
            self._correct_height()
        if self._is_ui_element_available(self.expand_option_sprite):
            self.expand_option_sprite.Close()

    def OnHideUI(self):
        self._stop_playing_audio()
        if self.agent_portrait_intro_3d_container is not None and self.agent_portrait_intro_3d_container.avatarscenecontainer.context is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.context.StopAudio()

    def OnShowUI(self):
        if self.agent_portrait_intro_3d_container is not None:
            if self._is_using_low_quality_characters():
                if self.current_agent_id is not None and self.current_line is not None:
                    logger.info('avatardisplay: Replacing 3D agent with 2D agent')
                    self.agent_portrait_intro_3d_container.display = False
                    self.agent_portrait_intro_3d_container.Close()
                    self.agent_portrait_intro_3d_container = None
                    self._is_portrait_loaded = False
                    self._load_agent_portrait(self._conversation_svc.get_agent(self.current_agent_id), self.current_line, restart_audio=True)
            else:
                logger.info('avatardisplay: Reloading in OnShowUI')
                self.agent_portrait_intro_3d_container.avatarscenecontainer.Reload()
        elif self._is_portrait_loaded:
            if not self._is_using_low_quality_characters():
                logger.info('avatardisplay: Replacing 2D agent with 3D agent')
                self._is_portrait_loaded = False
                if self.agent_portrait_intro_video_container:
                    self.agent_portrait_intro_video_container.Close()
                    logger.info('avatardisplay: closing video container')
                if self.agent_portrait_image_sprite:
                    self.agent_portrait_image_sprite.Close()
                    logger.info('avatardisplay: closing sprite')
                self._load_agent_portrait(self._conversation_svc.get_agent(self.current_agent_id), self.current_line, restart_audio=True)
                self.agent_portrait_intro_3d_container.display = False
                blue.synchro.Sleep(100)
                self.agent_portrait_intro_3d_container.display = True

    def OnSetDevice(self):
        self._stop_playing_audio()

    def show_next_conversation(self, delay = False, play_incoming_transmission_sound = True):
        if self.showing_next:
            return
        self.showing_next = True
        self.kill_next_conversation_tasklet()
        next_line = None
        if self._conversation_svc.are_any_conversation_lines_left():
            next_line = self._conversation_svc.get_next_conversation_line()
        delay_seconds = self.delay_seconds_between_audio_ended_and_show_next
        apply_delay = delay and self.is_audio_activated and delay_seconds > 0
        self._stop_playing_audio()
        if next_line:
            if apply_delay:
                self.next_conversation_tasklet = call_after_wallclocktime_delay(self._show_content, delay_seconds, next_line, play_incoming_transmission_sound)
            else:
                self._show_content(next_line, play_incoming_transmission_sound)
            return
        self.close_on_conversation_end(apply_delay, delay_seconds)
        self.showing_next = False

    def show_previous_conversation(self):
        if self.showing_next:
            return
        self.showing_next = True
        self.kill_next_conversation_tasklet()
        if not self._conversation_svc.are_any_previous_conversation_lines_available():
            return
        self._stop_playing_audio()
        previous_line = self._conversation_svc.get_previous_conversation_line()
        self._show_content(previous_line)

    def kill_next_conversation_tasklet(self):
        if self.next_conversation_tasklet:
            self.next_conversation_tasklet.Kill()
            self.next_conversation_tasklet = None
            if not self._conversation_svc.are_any_previous_conversation_lines_available():
                return
            self._conversation_svc.get_previous_conversation_line()

    def close_on_conversation_end(self, apply_delay, delay_seconds):
        is_audio_active = self.is_audio_activated
        should_close_on_audio_end_with_delay = is_audio_active and self.close_on_audio_end and apply_delay
        should_close_on_audio_end_with_no_delay = is_audio_active and self.close_on_audio_end and not apply_delay
        if should_close_on_audio_end_with_delay:
            call_after_wallclocktime_delay(self._close_if_open, delay_seconds)
        elif should_close_on_audio_end_with_no_delay or not is_audio_active:
            self._close_if_open()

    def _close_if_open(self):
        self.CloseIfOpen()

    def _show_content(self, next_line, play_incoming_transmission_sound = False, play_audio = True):
        if self.destroyed:
            return
        self.next_conversation_tasklet = None
        self._is_portrait_loaded = False
        self.text = next_line.get_text()
        self.hints = next_line.hints
        sound_id = next_line.sound_id
        agent_id = next_line.agent_id
        self.current_agent_id = agent_id
        self.current_line = next_line
        agent_data = self._conversation_svc.get_agent(agent_id)
        agent_name = GetByMessageID(agent_data.name)
        previous_style = self.style
        new_style = self._get_style_by_agent_id(agent_id)
        style_changed = previous_style != new_style
        if style_changed:
            self.style = new_style
        self.current_sound_id = sound_id
        if play_audio:
            self._start_playing_audio()
        self._load_portrait(agent_data, next_line)
        self._load_title(agent_name)
        self._clear_navigation_buttons()
        self._clear_completed_ui()
        expand = self._get_expand_setting()
        self._show_expanded_content(expand)
        self._load_navigation_buttons()
        self._load_completed_ui()
        self._correct_height(style_changed)
        uthread.new(self.animate_text_portrait_in)
        self.showing_next = False

    def _get_expand_setting(self):
        if not self.is_content_expandable or not self.is_audio_activated:
            return True
        manual_expanded_setting = settings.char.ui.Get(SETTING_CONVERSATION_WINDOW_TEXT_EXPAND, None)
        if manual_expanded_setting is not None:
            return manual_expanded_setting
        return self._should_expand_content()

    def _show_expanded_content(self, expand):
        self._load_expand_option_sprite(expand)
        self._load_title_line(expand)
        self._load_text(expand)
        self._load_hints(expand)

    def _get_style_by_agent_id(self, agent_id):
        return AGENT_ID_TO_STYLE.get(agent_id, self.default_style)

    def _apply_style(self):
        self.style_line(self.title_line)
        self.style_line(self.hints_line)
        is_transparent = self.style.style_color is not None
        self.style_window_transparency(is_transparent)

    def style_line(self, line):
        if line:
            line.SetFixedColor(self.style.style_color)
            line.opacity = TITLE_LINE_OPACITY

    def style_window_transparency(self, is_transparent):
        pass

    def Prepare_Background_(self):
        self.sr.underlay = ConversationWindowUnderlay(name='styledBackgroundsContainer', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)

    def style_backgrounds(self):
        if not self.style:
            return
        self.sr.underlay.ApplyStyle(self.style)

    def close_window(self):
        self._stop_playing_audio()
        AnimatedTransmissionWindow.close_window(self)

    def Close(self, *args, **kwargs):
        if self.agent_portrait_intro_3d_container is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.Close()
        self._stop_playing_audio()
        self._audio_svc.UnsubscribeFromEventCallback(self._on_sound_event_completed)
        AnimatedTransmissionWindow.Close(self, *args, **kwargs)

    def CloseByUser(self, *args, **kwargs):
        should_close = self.show_warning_on_first_close()
        if not should_close:
            return
        if not self.destroyed:
            AnimatedTransmissionWindow.CloseByUser(self, *args)

    def Minimize(self, *args, **kwargs):
        if self.is_neocom_hidden():
            return
        if self.agent_portrait_intro_3d_container is not None and self.agent_portrait_intro_3d_container.avatarscenecontainer.context is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.FadeOutOpacity(duration=0.5)
            self.agent_portrait_intro_3d_container.avatarscenecontainer.context.StopAudio()
            self.agent_portrait_intro_3d_container.avatarscenecontainer.context.SetMinimized()
        self._stop_playing_audio()
        self._audio_svc.UnsubscribeFromEventCallback(self._on_sound_event_completed)
        super(ConversationWindow, self).Minimize(*args, **kwargs)
        self.notify_of_minimization()

    def Maximize(self, *args, **kwargs):
        if self.agent_portrait_intro_3d_container is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.opacity = 0.0
        self._audio_svc.SubscribeToEventCallback(self._on_sound_event_completed)
        self._start_playing_audio()
        super(ConversationWindow, self).Maximize(*args, **kwargs)
        self._correct_height(style_changed=False)
        self.notify_of_maximization()
        if self.agent_portrait_intro_3d_container is not None and self.agent_portrait_intro_3d_container.avatarscenecontainer.context is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.context.SetMaximized()
            self.agent_portrait_intro_3d_container.avatarscenecontainer.Reload(self.sound_start_time)

    def notify_of_open(self):
        if self.conversation_id is not None:
            self._conversation_svc.notify_of_conversation_start(self.conversation_id)

    def notify_of_close(self):
        if self.conversation_id is not None:
            self._conversation_svc.clear_conversation(self.conversation_id)

    def notify_of_minimization(self):
        if self.conversation_id is not None:
            self._conversation_svc.notify_of_conversation_minimized(self.conversation_id)

    def notify_of_maximization(self):
        if self.conversation_id is not None:
            self._conversation_svc.notify_of_conversation_maximized(self.conversation_id)

    def show_warning_on_first_close(self):
        if self.destroyed:
            return False
        if not self.show_warning_on_first_close_setting or not self.show_warning_on_first_close_dialog:
            return True
        have_conversations_ever_been_closed = settings.char.ui.Get(self.show_warning_on_first_close_setting, False)
        if have_conversations_ever_been_closed:
            return True
        eve.Message(self.show_warning_on_first_close_dialog)
        settings.char.ui.Set(self.show_warning_on_first_close_setting, True)
        return True

    def OnUIScalingChange(self, *args):
        if self.destroyed:
            return
        if self.agent_portrait_intro_3d_container is not None:
            self.agent_portrait_intro_3d_container.avatarscenecontainer.Reload()
