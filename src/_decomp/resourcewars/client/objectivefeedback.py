#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\objectivefeedback.py
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from carbonui.fontconst import STYLE_DEFAULT
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.buttons import TextButtonWithBackgrounds, ButtonTextBoldness
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.util.uix import GetTextWidth
from eve.common.lib.appConst import factionAmarrEmpire, factionCaldariState, factionGallenteFederation, factionMinmatarRepublic
from gametime import SEC, MSEC
from localization import GetByLabel
import log
from resourcewars.client.rewardsfeedback import RewardsFeedbackWindow
from uthread2 import Sleep, StartTasklet, call_after_wallclocktime_delay
ICON_WIDTH = 72
ICON_HEIGHT = 82
ICON_STROKE_WIDTH = 80
ICON_STROKE_HEIGHT = 92
ICON_BG_WIDTH = 103
ICON_BG_HEIGHT = 119
MESSAGE_WIDTH = 188
MESSAGE_HEIGHT = 30
ACTION_WIDTH = 100
ACTION_HEIGHT = 23
ACTION_TOP = 4
VIEW_TOP = 260
VIEW_LEFT = -2
VIEW_WIDTH = max(ICON_BG_WIDTH, MESSAGE_WIDTH, ACTION_WIDTH)
VIEW_HEIGHT = ICON_BG_HEIGHT + MESSAGE_HEIGHT + ACTION_TOP + ACTION_HEIGHT
SMALL_SCREEN_HEIGHT = 768
MESSAGE_FONTSIZE = 17
ACTION_FONTSIZE = 11
MIN_TEXT_PADDING = 20
ACTION_BUTTON_WIDTH = 100
ACTION_BUTTON_TOP = 10
VICTORY_ICON_BY_FACTION = {factionAmarrEmpire: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Amarr.png',
 factionCaldariState: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Caldari.png',
 factionGallenteFederation: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Gallente.png',
 factionMinmatarRepublic: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Minmatar.png'}
DEFEAT_ICON_BY_FACTION = {factionAmarrEmpire: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Failed_Amarr.png',
 factionCaldariState: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Failed_Caldari.png',
 factionGallenteFederation: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Failed_Gallente.png',
 factionMinmatarRepublic: 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Failed_Minmatar.png'}
ICON_STROKE = 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_Stroke.png'
ICON_BG = 'res:/UI/Texture/Classes/ResourceWars/missionFeedback_backGround.png'
ICON_OPACITY = 0.85
ICON_STROKE_OPACITY = 0.45
ICON_BG_OPACITY = 0.15
MESSAGE_FRAME = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Objective_Button_bg.png'
MESSAGE_FRAME_OPACITY = 0.45
ICON_FADE_IN_DURATION_SEC = 0.1
ICON_BG_FADE_IN_DURATION_SEC = 0.1
MESSAGE_DELAY_SEC = 0.1
MESSAGE_FADE_IN_DURATION_SEC = 0.1
MESSAGE_EXPAND_DURATION_SEC = 0.25
MESSAGE_TEXT_FADE_IN_DURATION_SEC = 0.1
ACTION_FADE_IN_DURATION_SEC = 0.1
ACTION_EXPAND_DURATION_SEC = 0.25
ACTION_TEXT_FADE_IN_DURATION_SEC = 0.1
BLINK_DURATION_SHOW = 0.045
BLINK_DURATION_HIDE = 0.045
BLINK_LOOPS = 2
INITIAL_WIDTH_TEXT = 10
TOTAL_ICON_IN_DURATION = ICON_FADE_IN_DURATION_SEC + ICON_BG_FADE_IN_DURATION_SEC
TOTAL_MESSAGE_IN_DURATION = MESSAGE_DELAY_SEC + MESSAGE_FADE_IN_DURATION_SEC + MESSAGE_EXPAND_DURATION_SEC + MESSAGE_TEXT_FADE_IN_DURATION_SEC
TOTAL_ACTION_IN_DURATION = ACTION_FADE_IN_DURATION_SEC + ACTION_EXPAND_DURATION_SEC + ACTION_TEXT_FADE_IN_DURATION_SEC
TOTAL_BLINK_DURATION = (BLINK_DURATION_SHOW + BLINK_DURATION_HIDE) * BLINK_LOOPS
TOTAL_IN_DURATION = TOTAL_ICON_IN_DURATION + TOTAL_MESSAGE_IN_DURATION + TOTAL_ACTION_IN_DURATION + TOTAL_BLINK_DURATION
ACTION_TEXT_FADE_OUT_DURATION_SEC = 0.1
ACTION_COLLAPSE_DURATION_SEC = 0.25
MESSAGE_TEXT_FADE_OUT_DURATION_SEC = 0.1
MESSAGE_COLLAPSE_DURATION_SEC = 0.25
ICON_BG_FADE_OUT_DURATION_SEC = 0.1
ICON_FADE_OUT_DURATION_SEC = 0.1
TOTAL_ACTION_OUT_DURATION = ACTION_TEXT_FADE_OUT_DURATION_SEC + ACTION_COLLAPSE_DURATION_SEC
TOTAL_MESSAGE_OUT_DURATION = MESSAGE_TEXT_FADE_OUT_DURATION_SEC + MESSAGE_COLLAPSE_DURATION_SEC
TOTAL_ICON_OUT_DURATION = ICON_BG_FADE_OUT_DURATION_SEC + ICON_FADE_OUT_DURATION_SEC
TOTAL_OUT_DURATION = TOTAL_ACTION_OUT_DURATION + TOTAL_MESSAGE_OUT_DURATION + TOTAL_ICON_OUT_DURATION
CLOSE_VIEW_TIMER_MSEC = max(30000, TOTAL_IN_DURATION * SEC / MSEC)
SHOW_REWARDS_DELAY_MSEC = 100

def get_scale():
    return float(uicore.desktop.height) / float(SMALL_SCREEN_HEIGHT)


class ObjectiveFeedback(object):

    def __init__(self):
        self.view = None
        self.rewards = None
        self.data = None
        self.close_view_thread = None
        self.show_rewards_thread = None

    def show_view(self, is_victory, is_rewarded, data):
        self.close_view()
        self.close_rewards()
        self.data = data
        view_class = VictoryFeedbackContainer if is_victory else DefeatFeedbackContainer
        self.view = view_class(name='objectiveFeedbackView', parent=uicore.layer.main, align=uiconst.TOALL, faction=data['faction'], func=self.accept_victory if is_victory and is_rewarded else self.accept_defeat)
        self.close_view_thread = AutoTimer(CLOSE_VIEW_TIMER_MSEC, self.close_view_animating)

    def close_view(self):
        try:
            if self.view and not self.view.destroyed:
                self.view.Close()
        finally:
            self.close_view_thread = None

    def close_view_animating(self, should_check_hover = True, should_blink = False):
        if self.view and not self.view.destroyed:
            if should_check_hover and self.view.is_action_hovered:
                self.close_view_thread = AutoTimer(CLOSE_VIEW_TIMER_MSEC, self.close_view_animating)
            else:
                msecs_until_close = TOTAL_OUT_DURATION * SEC / MSEC
                self.view.animate_out(should_blink)
                self.close_view_thread = AutoTimer(msecs_until_close, self.close_view)

    def accept_victory(self):
        if self.view and not self.view.destroyed:
            msecs_until_close = TOTAL_OUT_DURATION * SEC / MSEC
            self.close_view_animating(should_check_hover=False, should_blink=True)
            self.show_rewards_thread = AutoTimer(msecs_until_close + SHOW_REWARDS_DELAY_MSEC, self.show_rewards)
        else:
            self.show_rewards()

    def accept_defeat(self):
        self.close_view_animating(should_check_hover=False, should_blink=True)

    def show_rewards(self):
        try:
            self.close_view()
            self.close_rewards()
            if self.data:
                self.rewards = RewardsFeedbackWindow(func=self.close_rewards, data=self.data)
                sm.GetService('audio').SendUIEvent('res_wars_reward_play')
        finally:
            self.show_rewards_thread = None

    def close_rewards(self):
        if self.rewards and not self.rewards.destroyed:
            self.rewards.Close()


class DefeatFeedbackContainer(Container):
    ICON_BY_FACTION = DEFEAT_ICON_BY_FACTION
    MESSAGE_LABEL = 'UI/ResourceWars/ObjectiveFailed'
    ACTION_LABEL = 'UI/ResourceWars/ObjectiveCompletedAction'
    HINT_LABEL = 'UI/ResourceWars/ObjectiveFailedHint'

    def ApplyAttributes(self, attributes):
        self.is_ready = False
        self.faction = attributes.get('faction', None)
        self.func = attributes.get('func', None)
        self.is_action_hovered = False
        Container.ApplyAttributes(self, attributes)
        self.update_scale()
        if self.faction not in self.ICON_BY_FACTION:
            log.LogWarn('Failed to build feedback view. Icon not available for faction', self.faction)
            return
        self.build_base()
        self.build_icon_stroke()
        self.build_icon()
        self.build_icon_bg()
        self.build_message()
        self.build_action()
        self.should_resize = False
        self.blink_thread = call_after_wallclocktime_delay(self.animate_blink, TOTAL_IN_DURATION - TOTAL_BLINK_DURATION)
        self.finalize_thread = call_after_wallclocktime_delay(self.finalize_view, TOTAL_IN_DURATION)

    def Close(self):
        self.stop_content_animations()
        Container.Close(self)

    def stop_content_animations(self):
        self.blink_thread = None
        self.blink_out_thread = None
        uicore.animations.StopAllAnimations(self.icon)
        uicore.animations.StopAllAnimations(self.icon_bg)
        uicore.animations.StopAllAnimations(self.message_frame)
        uicore.animations.StopAllAnimations(self.message)
        uicore.animations.StopAllAnimations(self.action)
        uicore.animations.StopAllAnimations(self.action.textContainer)

    def finalize_view(self):
        self.finalize_thread = None
        self.is_ready = True
        self.resize_view()

    def update_scale(self):
        self.scale = get_scale()

    def build_base(self):
        self.base = Container(name='objectiveFeedbackCenter', parent=self, align=uiconst.TOTOP, width=VIEW_WIDTH * self.scale, height=VIEW_HEIGHT * self.scale, state=uiconst.UI_PICKCHILDREN, top=VIEW_TOP * self.scale, left=VIEW_LEFT * self.scale)

    def build_icon(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        icon_width, icon_height = self.get_icon_size()
        self.icon_container = Container(name='objectiveFeedbackCenter_iconContainer', parent=self.base, align=uiconst.TOTOP_NOPUSH, width=icon_bg_width, height=icon_bg_height, state=uiconst.UI_DISABLED)
        self.icon = Sprite(name='objectiveFeedbackCenter_icon', parent=self.icon_container, align=uiconst.CENTER, width=icon_width, height=icon_height, texturePath=self.ICON_BY_FACTION[self.faction], opacity=0.0)
        self.animate_icon_in()

    def build_icon_bg(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        self.icon_bg_container = Container(name='objectiveFeedbackCenter_iconBgContainer', parent=self.base, align=uiconst.TOTOP, width=icon_bg_width, height=icon_bg_height, state=uiconst.UI_DISABLED)
        self.icon_bg = Sprite(name='objectiveFeedbackCenter_iconBg', parent=self.icon_bg_container, align=uiconst.CENTER, width=icon_bg_width, height=icon_bg_height, texturePath=ICON_BG, opacity=0.0)
        self.animate_icon_bg_in()

    def build_icon_stroke(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        icon_stroke_width, icon_stroke_height = self.get_icon_stroke_size()
        self.icon_stroke_container = Container(name='objectiveFeedbackCenter_iconStrokeContainer', parent=self.base, align=uiconst.TOTOP_NOPUSH, width=icon_bg_width, height=icon_bg_height, state=uiconst.UI_PICKCHILDREN)
        self.icon_stroke = Sprite(name='objectiveFeedbackCenter_iconStroke', parent=self.icon_stroke_container, align=uiconst.CENTER, width=icon_stroke_width, height=icon_stroke_height, texturePath=ICON_STROKE, opacity=0.0)
        if self.HINT_LABEL:
            self.icon_stroke.hint = GetByLabel(self.HINT_LABEL)
        self.animate_icon_stroke_in()

    def build_message(self):
        text = GetByLabel(self.MESSAGE_LABEL)
        text = text.upper()
        message_width, message_height = self.get_message_size()
        self.message_container = Container(name='objectiveFeedbackCenter_messageContainer', parent=self.base, align=uiconst.TOTOP, width=message_width, height=message_height, state=uiconst.UI_PICKCHILDREN)
        fontsize = self.get_message_fontsize()
        self.message = Label(name='objectiveFeedbackCenter_message', parent=self.message_container, align=uiconst.CENTER, text=text, fontsize=fontsize, opacity=0.0, fontstyle=STYLE_DEFAULT)
        frame_width, frame_height, frame_left = self.get_message_frame_size(text, fontsize, message_width, message_height)
        self.message_frame = Frame(name='objectiveFeedbackCenter_messageFrame', parent=self.message_container, texturePath=MESSAGE_FRAME, state=uiconst.UI_NORMAL, align=uiconst.CENTER, width=INITIAL_WIDTH_TEXT, height=frame_height, left=frame_left, opacity=0.0)
        if self.HINT_LABEL:
            self.message_frame.hint = GetByLabel(self.HINT_LABEL)
        self.animate_message_in(frame_width)

    def build_action(self):
        action_width, action_height, action_top = self.get_action_size()
        self.action_container = Container(name='objectiveFeedbackCenter_actionContainer', parent=self.base, align=uiconst.TOTOP, width=action_width, height=action_height, opacity=0.0, top=action_top)
        self.action = None
        self.rebuild_action_button(action_height, shouldAnimate=True)

    def rebuild_action_button(self, action_height, shouldAnimate = False):
        button_text = GetByLabel(self.ACTION_LABEL)
        button_fontsize = self.get_action_fontsize()
        button_width, button_height = self.get_action_button_size(button_text, button_fontsize, action_height)
        if self.action and not self.action.destroyed:
            self.action.Close()
        self.action = ActionButton(name='objectiveFeedbackCenter_action', parent=self.action_container, align=uiconst.CENTERBOTTOM, width=INITIAL_WIDTH_TEXT if shouldAnimate else button_width, height=button_height, func=self.func, text=button_text, fontsize=button_fontsize, textContainerOpacity=0.0 if shouldAnimate else 1.0, onMouseEventFunc=self.set_action_hover_state)
        if shouldAnimate:
            self.animate_action_in(button_width)

    def animate_icon_in(self):
        uicore.animations.FadeIn(self.icon, endVal=ICON_OPACITY, duration=ICON_FADE_IN_DURATION_SEC)

    def animate_icon_bg_in(self):
        uicore.animations.FadeIn(self.icon_bg, endVal=ICON_BG_OPACITY, duration=ICON_BG_FADE_IN_DURATION_SEC, timeOffset=ICON_FADE_IN_DURATION_SEC)

    def animate_icon_stroke_in(self):
        uicore.animations.FadeIn(self.icon_stroke, endVal=ICON_STROKE_OPACITY, duration=ICON_FADE_IN_DURATION_SEC)

    def animate_message_in(self, frame_width):
        offset = TOTAL_ICON_IN_DURATION + MESSAGE_DELAY_SEC
        uicore.animations.FadeIn(self.message_frame, endVal=MESSAGE_FRAME_OPACITY, duration=MESSAGE_FADE_IN_DURATION_SEC, timeOffset=offset)
        offset += MESSAGE_FADE_IN_DURATION_SEC
        uicore.animations.MorphScalar(obj=self.message_frame, attrName='width', startVal=self.message_frame.width, endVal=frame_width, duration=MESSAGE_EXPAND_DURATION_SEC, timeOffset=offset)
        offset += MESSAGE_EXPAND_DURATION_SEC
        uicore.animations.FadeIn(self.message, duration=MESSAGE_TEXT_FADE_IN_DURATION_SEC, timeOffset=offset)

    def animate_action_in(self, button_width):
        offset = TOTAL_ICON_IN_DURATION + TOTAL_MESSAGE_IN_DURATION
        uicore.animations.FadeIn(self.action_container, duration=ACTION_FADE_IN_DURATION_SEC, timeOffset=offset)
        offset += ACTION_FADE_IN_DURATION_SEC
        uicore.animations.MorphScalar(obj=self.action, attrName='width', startVal=self.action.width, endVal=button_width, duration=ACTION_EXPAND_DURATION_SEC, timeOffset=offset)
        offset += ACTION_EXPAND_DURATION_SEC
        uicore.animations.FadeIn(self.action.textContainer, duration=ACTION_TEXT_FADE_IN_DURATION_SEC, timeOffset=offset)

    def animate_blink(self):
        try:
            for loop in xrange(0, BLINK_LOOPS):
                self.message_container.opacity = 0.0
                self.action_container.opacity = 0.0
                Sleep(BLINK_DURATION_HIDE)
                self.message_container.opacity = 1.0
                self.action_container.opacity = 1.0
                if loop < BLINK_LOOPS - 1:
                    Sleep(BLINK_DURATION_SHOW)

        finally:
            self.blink_thread = None

    def animate_out(self, should_blink):
        self.finalize_view()
        initial_offset = 0
        if should_blink:
            self.blink_out_thread = StartTasklet(self.animate_blink_out)
            initial_offset += TOTAL_BLINK_DURATION
        self.animate_action_out(initial_offset)
        self.animate_message_out(initial_offset)
        self.animate_icon_out(initial_offset)

    def animate_blink_out(self):
        try:
            for loop in xrange(0, BLINK_LOOPS):
                self.message_container.opacity = 0.0
                self.action_container.opacity = 0.0
                Sleep(BLINK_DURATION_HIDE)
                self.message_container.opacity = 1.0
                self.action_container.opacity = 1.0
                if loop < BLINK_LOOPS - 1:
                    Sleep(BLINK_DURATION_SHOW)

        finally:
            self.blink_out_thread = None

    def animate_action_out(self, initial_offset):
        offset = initial_offset
        uicore.animations.FadeOut(self.action.textContainer, duration=ACTION_TEXT_FADE_OUT_DURATION_SEC, timeOffset=offset)
        offset += ACTION_TEXT_FADE_OUT_DURATION_SEC
        uicore.animations.MorphScalar(obj=self.action, attrName='width', startVal=self.action.width, endVal=0.0, duration=ACTION_COLLAPSE_DURATION_SEC, timeOffset=offset, callback=self.hide_action)

    def animate_message_out(self, initial_offset):
        offset = initial_offset + ACTION_TEXT_FADE_OUT_DURATION_SEC + ACTION_COLLAPSE_DURATION_SEC
        uicore.animations.FadeOut(self.message, duration=MESSAGE_TEXT_FADE_OUT_DURATION_SEC, timeOffset=offset)
        offset += MESSAGE_TEXT_FADE_OUT_DURATION_SEC
        uicore.animations.MorphScalar(obj=self.message_frame, attrName='width', startVal=self.message_frame.width, endVal=0.0, duration=MESSAGE_COLLAPSE_DURATION_SEC, timeOffset=offset, callback=self.hide_message)

    def animate_icon_out(self, initial_offset):
        offset = initial_offset + ACTION_TEXT_FADE_OUT_DURATION_SEC + ACTION_COLLAPSE_DURATION_SEC + MESSAGE_TEXT_FADE_OUT_DURATION_SEC + MESSAGE_COLLAPSE_DURATION_SEC
        uicore.animations.FadeOut(self.icon_bg, duration=ICON_BG_FADE_OUT_DURATION_SEC, timeOffset=offset)
        offset += ICON_BG_FADE_OUT_DURATION_SEC
        uicore.animations.FadeOut(self.icon, duration=ICON_FADE_OUT_DURATION_SEC, timeOffset=offset)
        uicore.animations.FadeOut(self.icon_stroke, duration=ICON_FADE_OUT_DURATION_SEC, timeOffset=offset)

    def hide_action(self):
        self.action_container.opacity = 0.0

    def hide_message(self):
        self.message_container.opacity = 0.0

    def _OnResize(self, *args):
        new_scale = get_scale()
        self.should_resize = new_scale != self.scale
        Container._OnResize(self, *args)
        if not self.destroyed and self.is_ready:
            self.resize_view()

    def resize_view(self):
        self.blink_thread = None
        self.blink_out_thread = None
        try:
            if self.should_resize:
                self.update_scale()
                self.resize_base()
                self.resize_icon()
                self.resize_icon_bg()
                self.resize_icon_stroke()
                self.resize_message()
                self.resize_action()
        finally:
            self.should_resize = False

    def resize_base(self):
        self.base.width = VIEW_WIDTH * self.scale
        self.base.height = VIEW_HEIGHT * self.scale
        self.base.top = VIEW_TOP * self.scale
        self.base.left = VIEW_LEFT * self.scale

    def resize_icon(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        icon_width, icon_height = self.get_icon_size()
        self.icon_container.width = icon_bg_width
        self.icon_container.height = icon_bg_height
        self.icon.width = icon_width
        self.icon.height = icon_height

    def resize_icon_bg(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        self.icon_bg_container.width = icon_bg_width
        self.icon_bg_container.height = icon_bg_height
        self.icon_bg.width = icon_bg_width
        self.icon_bg.height = icon_bg_height

    def resize_icon_stroke(self):
        icon_bg_width, icon_bg_height = self.get_icon_bg_size()
        icon_stroke_width, icon_stroke_height = self.get_icon_stroke_size()
        self.icon_stroke_container.width = icon_bg_width
        self.icon_stroke_container.height = icon_bg_height
        self.icon_stroke.width = icon_stroke_width
        self.icon_stroke.height = icon_stroke_height

    def resize_message(self):
        message_width, message_height = self.get_message_size()
        self.message_container.width = message_width
        self.message_container.height = message_height
        fontsize = self.get_message_fontsize()
        self.message.fontsize = fontsize
        text = GetByLabel(self.MESSAGE_LABEL)
        frame_width, frame_height, frame_left = self.get_message_frame_size(text, fontsize, message_width, message_height)
        self.message_frame.width = frame_width
        self.message_frame.height = frame_height
        self.message_frame.left = float(message_width - frame_width) / 2

    def resize_action(self):
        action_width, action_height, action_top = self.get_action_size()
        self.action_container.width = action_width
        self.action_container.height = action_height
        self.action_container.top = action_top
        self.rebuild_action_button(action_height)

    def get_icon_size(self):
        return (ICON_WIDTH * self.scale, ICON_HEIGHT * self.scale)

    def get_icon_bg_size(self):
        return (ICON_BG_WIDTH * self.scale, ICON_BG_HEIGHT * self.scale)

    def get_icon_stroke_size(self):
        return (ICON_STROKE_WIDTH * self.scale, ICON_STROKE_HEIGHT * self.scale)

    def get_message_size(self):
        return (MESSAGE_WIDTH * self.scale, MESSAGE_HEIGHT * self.scale)

    def get_message_frame_size(self, text, fontsize, message_width, message_height):
        text_width = GetTextWidth(strng=text, fontsize=fontsize, fontStyle=STYLE_DEFAULT, uppercase=1)
        min_text_padding = self.get_min_text_padding()
        frame_width = max(message_width, text_width + min_text_padding)
        frame_height = message_height
        frame_left = float(message_width - frame_width) / 2
        return (frame_width, frame_height, frame_left)

    def get_action_size(self):
        return (ACTION_WIDTH * self.scale, ACTION_HEIGHT * self.scale, ACTION_TOP * self.scale)

    def get_action_button_size(self, text, fontsize, action_height):
        width = ACTION_BUTTON_WIDTH * self.scale
        text_width = GetTextWidth(strng=text, fontsize=fontsize, fontStyle=STYLE_DEFAULT)
        min_text_padding = self.get_min_text_padding()
        width = max(width, text_width + min_text_padding)
        height = action_height
        return (width, height)

    def get_min_text_padding(self):
        return MIN_TEXT_PADDING * self.scale

    def get_message_fontsize(self):
        return MESSAGE_FONTSIZE * self.scale

    def get_action_fontsize(self):
        return ACTION_FONTSIZE * self.scale

    def set_action_hover_state(self, state):
        self.is_action_hovered = state


class VictoryFeedbackContainer(DefeatFeedbackContainer):
    ICON_BY_FACTION = VICTORY_ICON_BY_FACTION
    MESSAGE_LABEL = 'UI/ResourceWars/ObjectiveCompleted'
    ACTION_LABEL = 'UI/ResourceWars/ObjectiveCompletedAction'
    HINT_LABEL = None


class ActionButton(TextButtonWithBackgrounds):
    default_mouseUpBGTexture = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Accept_Button_bg.png'
    default_mouseEnterBGTexture = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Accept_Button_Highlight.png'
    default_mouseDownBGTexture = 'res:/UI/Texture/Classes/ResourceWars/resourceWars_Accept_Button_Highlight.png'
    default_mouseUpBGOpacity = 0.5
    default_mouseEnterBGOpacity = 0.75
    default_mouseDownBGOpacity = 0.9
    default_frameCornerSize = 7
    default_hoverSound = None
    default_selectSound = None
    default_mouseUpTextColor = (1.0, 1.0, 1.0, 0.75)
    default_mouseEnterTextColor = (0.0, 0.0, 0.0, 0.8)
    default_mouseDownTextColor = (0.0, 0.0, 0.0, 1.0)
    default_boldText = ButtonTextBoldness.BOLD_ON_MOUSEOVER

    def ApplyAttributes(self, attributes):
        TextButtonWithBackgrounds.ApplyAttributes(self, attributes)
        self.onMouseEventFunc = attributes.get('onMouseEventFunc')

    def OnMouseEnter(self, *args):
        self.onMouseEventFunc(True)
        TextButtonWithBackgrounds.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        self.onMouseEventFunc(False)
        TextButtonWithBackgrounds.OnMouseExit(self, *args)
