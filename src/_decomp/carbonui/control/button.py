#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\button.py
import logging
import math
import weakref
import eveformat
import eveicon
import signals
import telemetry
import threadutils
import trinity
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, fontconst
from carbonui.button import styling
from carbonui.button.const import ButtonFrameType, ButtonStyle, ButtonVariant, HEIGHT_NORMAL, InteractionState
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from carbonui.loggers.buttonLogger import log_button_clicked
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uiconst import Density
from carbonui.util.various_unsorted import GetBrowser
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.menuUtil import DESTRUCTIVEGROUP, RAGEQUITGROUP
log = logging.getLogger(__name__)
OPACITY_LABEL_IDLE = 1.0
OPACITY_LABEL_HOVER = 1.0
OPACITY_LABEL_MOUSEDOWN = 1.2

class Button(Container):
    default_analyticID = None
    default_align = uiconst.RELATIVE
    default_label = ''
    default_func = None
    default_args = None
    default_fixedwidth = None
    default_fixedheight = None
    default_state = uiconst.UI_NORMAL
    default_enabled = True
    default_busy = False
    default_iconSize = 16
    default_texturePath = None
    default_color = None
    default_iconPadding = 0
    default_variant = ButtonVariant.NORMAL
    default_style = ButtonStyle.NORMAL
    default_density = Density.NORMAL
    default_frame_type = ButtonFrameType.CUT_BOTTOM_RIGHT
    default_width = 100
    default_height = HEIGHT_NORMAL
    default_maxWidth = 300
    default_sidePadding = 10
    default_soundHover = uiconst.SOUND_BUTTON_HOVER
    default_soundClick = uiconst.SOUND_BUTTON_CLICK
    default_fontsize = fontconst.EVE_SMALL_FONTSIZE
    default_fontStyle = None
    default_fontFamily = None
    default_fontPath = None
    default_uppercase = False
    default_bold = False
    ICON_SIZE = 16
    ICON_MARGIN = 4
    BUSY_ANIMATION_DURATION = 2.0
    ARROWS_TEXTURE = 'res:/UI/Texture/Classes/Industry/CenterBar/arrows.png'
    ARROWS_TEXTURE_SEGMENT_COUNT = 6
    ARROWS_TEXTURE_MASK = 'res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png'
    __busy_context = None
    __on_enabled_changed = None
    __on_hovered_changed = None
    __ready = False
    _arrows = None
    _icon = None
    _label = None

    def __init__(self, get_menu_entry_data_func = None, **kwargs):
        self._get_menu_entry_data_func = get_menu_entry_data_func
        self._interaction_state = set()
        super(Button, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        self._busy = attributes.get('busy', self.default_busy)
        self._density = attributes.get('density', self.default_density)
        self._texturePath = attributes.get('texturePath', self.default_texturePath)
        self._variant = attributes.get('variant', None) or self.default_variant
        self._style = attributes.get('style', None) or self.default_style
        self._frame_type = attributes.get('frame_type', None) or self.default_frame_type
        self._label_text = self._sanitize_label(attributes.get('label', self.default_label))
        enabled = attributes.get('enabled', self.default_enabled)
        if not enabled:
            self._interaction_state.add(InteractionState.disabled)
        args = attributes.get('args', None)
        if args == 'self':
            attributes.args = self
        self.fixedwidth = attributes.get('fixedwidth', self.default_fixedwidth)
        self.fixedheight = attributes.get('fixedheight', self.default_fixedheight)
        self.func = attributes.get('func', self.default_func)
        self.args = attributes.get('args', self.default_args)
        self.color = attributes.get('color', self.default_color)
        self.fontStyle = attributes.get('fontStyle', self.default_fontStyle)
        self.fontFamily = attributes.get('fontFamily', self.default_fontFamily)
        self.fontPath = attributes.get('fontPath', self.default_fontPath)
        self.fontsize = attributes.get('fontsize', self.default_fontsize)
        self.soundClick = attributes.get('soundClick', self.default_soundClick)
        self.soundHover = attributes.get('soundHover', self.default_soundHover)
        self.minwidth = attributes.get('minwidth', self._GetDefaultMinWidth())
        self.maxwidth = attributes.get('maxwidth', self.default_maxWidth)
        self.sidePadding = attributes.get('sidePadding', self.default_sidePadding)
        self.analyticID = attributes.get('analyticID', self.default_analyticID)
        self.bold = attributes.get('bold', self.default_bold)
        self.color = attributes.get('color', self.default_color)
        self.iconPadding = attributes.get('iconPadding', self.default_iconPadding)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.uppercase = attributes.get('uppercase', self.default_uppercase)
        attributes.pop('fontFamily', None)
        attributes.fontsize = styling.get_fontsize(self.density)
        super(Button, self).ApplyAttributes(attributes)
        if self.default_fontsize is None:
            self.default_fontsize = fontconst.DEFAULT_FONTSIZE
        self.isTabStop = 1
        self.resetTop = None
        self.blinking = 0
        for each in ('btn_modalresult', 'btn_default', 'btn_cancel'):
            if each in attributes:
                attr = attributes.get(each, None)
                setattr(self, each, attr)

        self.Prepare_()
        self.__ready = True
        self._update_busy(animate=False)
        self.Update_Size_()

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if self._density != value:
            self._density = value
            self.Update_Size_()

    @property
    def frame_type(self):
        return self._frame_type

    @frame_type.setter
    def frame_type(self, value):
        if self._frame_type != value:
            self._frame_type = value
            self._update_frame_type()

    @property
    def hovered(self):
        return InteractionState.hovered in self._interaction_state

    @property
    def on_hovered_changed(self):
        if self.__on_hovered_changed is None:
            self.__on_hovered_changed = signals.Signal('{}.on_hovered_changed'.format(self.__class__.__name__))
        return self.__on_hovered_changed

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        if self._variant != value:
            self._variant = value
            self._OnVariantChanged()

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if self._style != value:
            self._style = value
            self._OnStyleChanged()

    @property
    def icon(self):
        return self.texturePath

    @icon.setter
    def icon(self, value):
        self.texturePath = value

    @property
    def label(self):
        return self._label_text

    @label.setter
    def label(self, value):
        if self.destroyed:
            return
        value = self._sanitize_label(value)
        if self._label_text != value:
            self._label_text = value
            if value:
                if self._label is None:
                    self.PrepareLabel()
                self._label.text = value
            elif self._label is not None:
                self._label.Close()
                self._label = None
                self.sr.label = None
            self.Update_Size_()

    @staticmethod
    def _sanitize_label(label):
        if label is not None:
            stripped_label = eveformat.strip_tags(label, tags=['center'])
            if stripped_label != label:
                log.warning("Attempting to assign a button label containing a 'center' tag.")
                return stripped_label
        return label

    @property
    def text(self):
        return self.label

    @property
    def texturePath(self):
        return self._texturePath

    @texturePath.setter
    def texturePath(self, value):
        if value != self._texturePath:
            self._texturePath = value
            self._UpdateIcon()

    @property
    def enabled(self):
        return InteractionState.disabled not in self._interaction_state

    @enabled.setter
    def enabled(self, value):
        if value and InteractionState.disabled in self._interaction_state:
            self._discard_state(InteractionState.disabled)
            self._emit_on_enabled_changed()
        elif not value and InteractionState.disabled not in self._interaction_state:
            self._add_state(InteractionState.disabled)
            self._emit_on_enabled_changed()

    @property
    def disabled(self):
        return InteractionState.disabled in self._interaction_state

    @disabled.setter
    def disabled(self, value):
        if value and InteractionState.disabled not in self._interaction_state:
            self._add_state(InteractionState.disabled)
            self._emit_on_enabled_changed()
        elif not value and InteractionState.disabled in self._interaction_state:
            self._discard_state(InteractionState.disabled)
            self._emit_on_enabled_changed()

    @property
    def on_enabled_changed(self):
        if self.__on_enabled_changed is None:
            self.__on_enabled_changed = signals.Signal()
        return self.__on_enabled_changed

    def _emit_on_enabled_changed(self):
        if self.__on_enabled_changed is not None:
            self.__on_enabled_changed(self)

    @property
    def pressed(self):
        return InteractionState.pressed in self._interaction_state

    @property
    def busy(self):
        return self._busy

    @busy.setter
    def busy(self, value):
        if value != self._busy:
            self._busy = value
            self._update_busy()

    @property
    def busy_context(self):
        if self.__busy_context is None:
            self.__busy_context = BusyContext(self)
        return self.__busy_context

    def enable(self, animate = True):
        if not self.enabled:
            self._discard_state(InteractionState.disabled, animate)

    def disable(self, animate = True):
        if self.enabled:
            self._add_state(InteractionState.disabled, animate)

    def get_menu_entry_data(self):
        if self._get_menu_entry_data_func is not None:
            return self._get_menu_entry_data_func()
        else:
            return ButtonActionMenuEntryData(self)

    def press(self, play_audio = True):
        self._execute(play_audio=play_audio)

    @telemetry.ZONE_METHOD
    def Prepare_(self):
        self.PrepareLabel()
        self.PrepareIcon()
        self.PrepareHilite()
        self.PrepareActiveFrame()
        self.PrepareUnderlay()

    def PrepareLabel(self):
        self._label = EveLabelMedium(name='label', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=self._get_label_color(), shadowSpriteEffect=trinity.TR2_SFX_GLOW, text=self._label_text, idx=0)
        self.sr.label = self._label

    def PrepareIcon(self):
        if self.texturePath is None:
            return
        icon_size = self._get_icon_size()
        self._icon = Sprite(name='icon', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=icon_size, height=icon_size, texturePath=self.texturePath, spriteEffect=self._get_icon_sprite_effect(), color=self._get_icon_color(), idx=0)

    def _UpdateIcon(self):
        if self._texturePath is None:
            if self._icon is not None:
                self._icon.Close()
                self._icon = None
        elif self._icon is not None:
            self._icon.SetTexturePath(self._texturePath)
            self._icon.spriteEffect = self._get_icon_sprite_effect()
        else:
            self.PrepareIcon()
        self.Update_Size_()

    def OnColorThemeChanged(self):
        super(Button, self).OnColorThemeChanged()
        self._OnStateChanged()

    def _OnVariantChanged(self):
        self.underlay.variant = self.variant
        self._OnStateChanged()

    def _OnStyleChanged(self):
        self.underlay.style = self.style
        self._OnStateChanged()

    def _OnStateChanged(self, old_state = None, animate = True):
        if self.destroyed:
            return
        if old_state is None:
            old_state = self._interaction_state
        self.underlay.set_interaction_state(self._interaction_state, animate)
        self._update_label_color(animate)
        self._update_icon_color(animate)
        self._update_arrows_color(animate)

    def _update_frame_type(self):
        if self.underlay:
            self.underlay.frame_type = self._frame_type

    def _get_label_color(self):
        return styling.get_foreground_color(button_variant=self._variant, button_style=self._style, interaction_states=self._interaction_state)

    def _update_label_color(self, animate = True):
        if not self.sr.label:
            return
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self.sr.label, endColor=self._get_label_color(), duration=duration)
        else:
            self.sr.label.color = self._get_label_color()

    def _get_icon_color(self):
        return styling.get_icon_color(button_variant=self._variant, button_style=self._style, interaction_states=self._interaction_state)

    def _update_icon_color(self, animate = True):
        if not self._icon:
            return
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self._icon, endColor=self._get_icon_color(), duration=duration)
        else:
            self._icon.color = self._get_icon_color()

    def _get_icon_size(self):
        if eveicon.is_icon_in_library(self._texturePath):
            return self.ICON_SIZE
        else:
            return min(self.iconSize, styling.get_height(self.density) - self.ICON_MARGIN * 2)

    def _get_icon_sprite_effect(self):
        if eveicon.is_icon_in_library(self._texturePath):
            return trinity.TR2_SFX_COPY
        else:
            return trinity.TR2_SFX_COLOROVERLAY

    def _get_arrows_color(self):
        color = styling.get_stroke_color(self._variant, self._style, self._interaction_state)
        if not self.busy:
            color = color[:3] + (0.0,)
        return color

    def _update_arrows_color(self, animate = True):
        if not self._arrows:
            return
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self._arrows, endColor=self._get_arrows_color(), duration=duration)
        else:
            self._arrows.color = self._get_arrows_color()

    def PrepareHilite(self):
        self.sr.hilite = Fill(name='hilite', bgParent=self, color=(0.7, 0.7, 0.7, 0.5), state=uiconst.UI_HIDDEN)

    def PrepareActiveFrame(self):
        pass

    def PrepareUnderlay(self):
        self.underlay = ButtonUnderlay(name='underlay', parent=self, variant=self._variant, style=self._style, frame_type=self._frame_type, interaction_state=self._interaction_state)

    def PrepareBusyArrows(self):
        if self._arrows is None:
            self._arrows = Sprite(name='arrows', bgParent=self, texturePath=self.ARROWS_TEXTURE_MASK, textureSecondaryPath=self.ARROWS_TEXTURE, spriteEffect=trinity.TR2_SFX_MODULATE, color=self._get_arrows_color(), idx=0)
            self._arrows.tileXSecondary = True
            x_translation = 1.0 / float(self.ARROWS_TEXTURE_SEGMENT_COUNT)
            self._arrows.translationSecondary = (-x_translation, 0)

    def _UpdateContentPosition(self):
        if self._label is not None and self.text and self._icon is not None:
            icon_offset = styling.get_icon_offset(self.density)
            icon_size = self._get_icon_size()
            gap_size = styling.get_icon_gap(self.density)
            half_icon_size = int(round(icon_size / 2.0))
            half_icon_offset = int(round(icon_offset / 2.0))
            half_gap_size = int(round(gap_size / 2.0))
            half_text_width = int(round(self._label.textwidth / 2.0))
            self._label.left = half_icon_size + half_gap_size - half_icon_offset
            self._icon.left = -half_text_width - half_gap_size - half_icon_offset
        elif self._label is not None and self._label.text:
            self._label.left = 0
        elif self._icon is not None:
            self._icon.left = 0

    @telemetry.ZONE_METHOD
    def Update_Size_(self):
        if not self.__ready:
            return
        self._UpdateContentPosition()
        self.width = self.get_intrinsic_width()
        self.height = self.get_intrinsic_height()

    def get_intrinsic_height(self):
        height = styling.get_height(self.density)
        if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
            height += self.padTop + self.padBottom
        return height

    def get_intrinsic_width(self):
        width = styling.get_side_padding(self.density) * 2
        if self._icon is not None and self._label is not None and self.text:
            icon_offset = styling.get_icon_offset(self.density)
            gap_size = styling.get_icon_gap(self.density)
            text_width = self._label.textwidth
            width += self._get_icon_size() + gap_size + text_width - icon_offset
        elif self._icon is not None:
            width = styling.get_height(self.density)
        elif self._label is not None:
            width += self._label.textwidth
        if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
            width += self.padLeft + self.padRight
        return max(styling.get_min_width(self.density), width)

    def SetLabel(self, label):
        self.label = label

    def SetLabel_(self, label):
        self.label = label

    def OnSetFocus(self, *args):
        self._add_state(InteractionState.focused)
        if self.disabled:
            return
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                browser = GetBrowser(self)
                if browser:
                    uthread.new(browser.ShowObject, self)

    def OnKillFocus(self, *etc):
        self._discard_state(InteractionState.focused)

    def OnMouseEnter(self, *args):
        if InteractionState.hovered not in self._interaction_state:
            self._add_state(InteractionState.hovered)
            if self.__on_hovered_changed is not None:
                self.__on_hovered_changed(self)
        self.Blink(False)
        if not self.disabled:
            self.underlay.OnMouseEnter()
            PlaySound(self.soundHover)

    def OnMouseExit(self, *args):
        if InteractionState.hovered in self._interaction_state:
            self._discard_state(InteractionState.hovered)
            if self.__on_hovered_changed is not None:
                self.__on_hovered_changed(self)
        self.underlay.OnMouseExit()

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._add_state(InteractionState.pressed)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._discard_state(InteractionState.pressed)

    def Confirm(self, *args):
        if self.IsVisible():
            uthread.new(self.OnClick, self)

    @telemetry.ZONE_METHOD
    def SetColor(self, color):
        pass

    @telemetry.ZONE_METHOD
    def SetLabelColor(self, color):
        pass

    @telemetry.ZONE_METHOD
    def SetActiveFrameColor(self, color):
        pass

    def Enable(self):
        self.enabled = True

    def Disable(self):
        self.enabled = False

    def Blink(self, on_off = 1, blinks = 1000, time = 800):
        self.blinking = on_off
        if on_off:
            self.underlay.Blink(blinks)
        else:
            self.underlay.StopBlink()

    def GetCursor(self):
        if self.disabled:
            return uiconst.UICURSOR_DEFAULT

    def _add_state(self, state, animate = True):
        old_state = frozenset(self._interaction_state)
        self._interaction_state.add(state)
        self._OnStateChanged(old_state, animate)

    def _discard_state(self, state, animate = True):
        old_state = frozenset(self._interaction_state)
        self._interaction_state.discard(state)
        self._OnStateChanged(old_state, animate)

    def _loop_arrow_animation(self):
        if not self._busy and not self.destroyed:
            return
        x_translation = 1.0 / float(self.ARROWS_TEXTURE_SEGMENT_COUNT)
        animations.MorphVector2(self._arrows, 'translationSecondary', (x_translation, 0.0), (-x_translation, 0.0), duration=self.BUSY_ANIMATION_DURATION, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    @threadutils.threaded
    def _start_arrow_animation(self):
        if self.destroyed:
            return
        self._animate_reset_arrow()
        if self._busy:
            self._loop_arrow_animation()

    @threadutils.threaded
    def _stop_arrow_animation(self):
        if self.destroyed:
            return
        self._animate_reset_arrow()
        if not self._busy:
            animations.StopAnimation(self._arrows, 'translationSecondary')

    def _animate_reset_arrow(self):
        x_translation = 1.0 / float(self.ARROWS_TEXTURE_SEGMENT_COUNT)
        diff = math.fabs(-x_translation - self._arrows.translationSecondary[0])
        if diff > 0.001:
            duration = diff / x_translation / 2.0 * self.BUSY_ANIMATION_DURATION
            animations.MorphVector2(self._arrows, 'translationSecondary', self._arrows.translationSecondary, (-x_translation, 0.0), duration=duration, curveType=uiconst.ANIM_LINEAR, sleep=True)

    def _update_busy(self, animate = True):
        if self.destroyed:
            return
        if self._busy:
            self.PrepareBusyArrows()
            self._start_arrow_animation()
        elif self._arrows is not None:
            self._stop_arrow_animation()
        self._OnStateChanged(animate=animate)

    def IsEnabled(self):
        return not self.disabled

    def SetFunc(self, func):
        self.func = func

    def OnClick(self, *args):
        if self:
            self._execute()

    def _execute(self, play_audio = True):
        if not self.destroyed and self.enabled and self.func:
            if play_audio:
                PlaySound(self.soundClick)
            log_button_clicked(self)
            self._CallFunction()

    def _CallFunction(self):
        if type(self.args) == tuple:
            self.func(*self.args)
        else:
            self.func(self.args or self)

    def Hilite_(self, on):
        if self.disabled:
            return
        if self.sr.hilite:
            if on:
                self.sr.hilite.state = uiconst.UI_DISABLED
            else:
                self.sr.hilite.state = uiconst.UI_HIDDEN

    def _GetDefaultMinWidth(self):
        return styling.get_default_min_width(self.density)

    def OnGlobalFontSizeChanged(self):
        super(Button, self).OnGlobalFontSizeChanged()
        self.Update_Size_()


class ButtonUnderlay(Container):
    BACKGROUND_TEXTURE_BY_FRAME_TYPE = {ButtonFrameType.CUT_BOTTOM_LEFT: 'res:/UI/Texture/classes/Button/background_cut_bottom_left.png',
     ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT: 'res:/UI/Texture/classes/Button/background_cut_bottom_left_right.png',
     ButtonFrameType.CUT_BOTTOM_RIGHT: 'res:/UI/Texture/classes/Button/background_cut_bottom_right.png',
     ButtonFrameType.RECTANGLE: 'res:/UI/Texture/classes/Button/background_rectangle.png'}
    FRAME_TEXTURE_BY_FRAME_TYPE = {ButtonFrameType.CUT_BOTTOM_LEFT: 'res:/UI/Texture/classes/Button/frame_cut_bottom_left.png',
     ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT: 'res:/UI/Texture/classes/Button/frame_cut_bottom_left_right.png',
     ButtonFrameType.CUT_BOTTOM_RIGHT: 'res:/UI/Texture/classes/Button/frame_cut_bottom_right.png',
     ButtonFrameType.RECTANGLE: 'res:/UI/Texture/classes/Button/frame_rectangle.png'}

    def __init__(self, parent = None, name = None, variant = ButtonVariant.NORMAL, style = ButtonStyle.NORMAL, frame_type = ButtonFrameType.CUT_BOTTOM_RIGHT, interaction_state = None):
        self._ready = False
        self._variant = variant
        self._style = style
        self._frame_type = frame_type
        self._glow = None
        self._frame = None
        self._background = None
        self._interaction_state = set()
        if interaction_state is not None:
            self._interaction_state = self._interaction_state.union(interaction_state)
        super(ButtonUnderlay, self).__init__(name=name, parent=parent, align=uiconst.TOALL)
        self._layout()
        self._ready = True

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        if self._variant != value:
            self._variant = value
            self._update()

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if self._style != value:
            self._style = value
            self._update()

    @property
    def frame_type(self):
        return self._frame_type

    @frame_type.setter
    def frame_type(self, value):
        if self._frame_type != value:
            self._frame_type = value
            self._update_frame_type()

    @property
    def interaction_state(self):
        return self._interaction_state

    @interaction_state.setter
    def interaction_state(self, value):
        self.set_interaction_state(value)

    @property
    def hovered(self):
        return InteractionState.hovered in self._interaction_state

    @property
    def pressed(self):
        return InteractionState.pressed in self._interaction_state

    @property
    def focused(self):
        return InteractionState.focused in self._interaction_state

    @property
    def disabled(self):
        return InteractionState.disabled in self._interaction_state

    def set_interaction_state(self, state, animate = True):
        if self._interaction_state != state:
            self._interaction_state = frozenset(state)
            self._update(animate)

    def _layout(self):
        frame_texture = self._get_frame_texture()
        self._glow = Frame(parent=self, align=uiconst.TOALL, texturePath=frame_texture, cornerSize=9, color=self._get_glow_color(), outputMode=trinity.Tr2SpriteTarget.GLOW)
        self._frame = Frame(parent=self, align=uiconst.TOALL, texturePath=frame_texture, cornerSize=9, color=self._get_frame_color())
        self._background = Frame(parent=self, align=uiconst.TOALL, texturePath=self._get_background_texture(), cornerSize=9, color=self._get_background_color(), outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW, glowBrightness=0.3)

    def _update(self, animate = True):
        if not self._ready or self.destroyed:
            return
        self._update_glow_color(animate)
        self._update_background_color(animate)
        self._update_border_color(animate)

    def _get_glow_color(self):
        return styling.get_glow_color(button_variant=self._variant, button_style=self._style, interaction_states=self._interaction_state)

    def _update_glow_color(self, animate = True):
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self._glow, endColor=self._get_glow_color(), duration=duration)
        else:
            self._glow.color = self._get_glow_color()

    def _get_background_color(self):
        return styling.get_background_color(button_variant=self._variant, button_style=self._style, interaction_states=self._interaction_state)

    def _update_background_color(self, animate = True):
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self._background, endColor=self._get_background_color(), duration=duration)
        else:
            self._background.color = self._get_background_color()

    def _get_frame_color(self):
        return styling.get_stroke_color(button_variant=self._variant, button_style=self._style, interaction_states=self._interaction_state)

    def _get_frame_texture(self):
        return self.FRAME_TEXTURE_BY_FRAME_TYPE[self._frame_type]

    def _get_background_texture(self):
        return self.BACKGROUND_TEXTURE_BY_FRAME_TYPE[self._frame_type]

    def _update_frame_type(self):
        frame_texture = self._get_frame_texture()
        if self._glow:
            self._glow.texturePath = frame_texture
        if self._frame:
            self._frame.texturePath = frame_texture
        if self._background:
            self._background.texturePath = self._get_background_texture()

    def _update_border_color(self, animate = True):
        if animate:
            duration = 0.1 if self.pressed or self.hovered else 0.3
            animations.SpColorMorphTo(self._frame, endColor=self._get_frame_color(), duration=duration)
        else:
            self._frame.color = self._get_frame_color()

    def OnMouseEnter(self):
        pass

    def OnMouseExit(self):
        pass

    def OnMouseDown(self):
        pass

    def OnMouseUp(self):
        pass

    def SetFixedColor(self, color):
        pass

    def SetEnabled(self):
        pass

    def SetDisabled(self):
        pass

    def Blink(self, blinkCount = 3):
        pass

    def StopBlink(self):
        pass

    def SetFocused(self):
        pass

    def SetUnfocused(self):
        pass

    def Select(self):
        pass

    def Deselect(self):
        pass

    def OnColorThemeChanged(self):
        self._update()


class BusyContext(object):

    def __init__(self, button):
        self._count = 0
        self._button_ref = weakref.ref(button)

    def __enter__(self):
        self._count += 1
        self._set_busy(True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._count -= 1
        if self._count == 0:
            self._set_busy(False)

    def _set_busy(self, value):
        button = self._button_ref()
        if button:
            button.busy = value


class ButtonActionMenuEntryData(MenuEntryData):

    def __init__(self, button):
        self._button_ref = weakref.ref(button)
        text = button.label or button.hint
        hint = button.hint if button.hint != text else None
        super(ButtonActionMenuEntryData, self).__init__(text=text, hint=hint, func=self._execute, texturePath=button.icon, menuGroupID=get_menu_group_id_from_button_style(button.style), isEnabled=button.enabled)
        button.on_enabled_changed.connect(self._on_button_enabled_changed)

    def _execute(self):
        button = self._button_ref()
        if button:
            button.press(play_audio=False)

    def _on_button_enabled_changed(self, button):
        self.isEnabled = button.enabled


def get_menu_group_id_from_button_style(style):
    if style == ButtonStyle.DANGER:
        return RAGEQUITGROUP
    elif style == ButtonStyle.WARNING:
        return DESTRUCTIVEGROUP
    else:
        return None
