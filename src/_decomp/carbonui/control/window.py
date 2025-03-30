#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\window.py
import math
import sys
import weakref
import blue
import eveicon
import gametime
import localization
import log
import signals
import telemetry
import types
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.animatedsprite import AnimSprite
from carbonui.control.button import Button
from carbonui.button.const import ButtonVariant
from carbonui.control.contextMenu.menuData import MenuData, MenuEntryData
from carbonui.window.resizer import Resizer, Side
from carbonui.window.snap import find_sibling_windows, SNAP_DISTANCE, WINDOW_SNAP_DISTANCE
from carbonui.window.underlay import WindowUnderlay
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import GetWindowAbove, Transplant
from carbonui.window.header.base import WindowHeaderBase
from carbonui.window.settings import GetRegisteredState, RegisterState, WindowCompactModeSetting, WindowMarginMode, window_compact_mode_default_setting, window_margin_mode
from carbonui.window.util import is_blocked
from eve.client.script.ui import eveThemeColor
from carbonui.button.group import ButtonGroup, ButtonSizeMode
from carbonui.loggers.message_bus.windowMessenger import WindowMessenger
from carbonui.window.control.default import DefaultWindowControls
from carbonui.window.control.action import CloseWindowAction, CollapseWindowAction, CompactModeWindowAction, LightBackgroundWindowAction, LockWindowAction, MinimizeWindowAction, OverlayWindowAction
from carbonui.window.header.default import DefaultWindowHeader
from eveexceptions import EatsExceptions, UserError
from menu import MenuLabel
POSOVERLAPSHIFT = 11
LEGACY_SIDE_NAME_BY_SIDE = {Side.LEFT: 'left',
 Side.TOP: 'top',
 Side.RIGHT: 'right',
 Side.BOTTOM: 'bottom'}

class Window(Container):
    __guid__ = 'uicontrols.Window'
    isDragObject = True
    isTopLevelWindow = True
    default_width = 256
    default_height = 128
    default_minSize = (default_width, default_height)
    default_maxSize = (None, None)
    default_fixedHeight = None
    default_fixedWidth = None
    default_left = '__center__'
    default_top = '__center__'
    default_name = 'window'
    default_idx = 0
    default_state = uiconst.UI_HIDDEN
    default_isLightBackground = False
    default_isLightBackgroundConfigurable = True
    default_isOverlayed = False
    default_isOverlayable = True
    default_iconNum = 'res:/UI/Texture/WindowIcons/other.png'
    default_scope = uiconst.SCOPE_INGAME
    default_soundOpen = None
    default_extend_content_into_header = False
    default_apply_content_padding = True
    default_windowInstanceID = None
    default_stackID = None
    default_caption = None
    default_captionLabelPath = None
    default_descriptionLabelPath = None
    default_align = uiconst.RELATIVE
    default_openMinimized = False
    default_isKillable = True
    default_isMinimizable = True
    default_isStackable = True
    default_isCompactable = False
    default_isLockable = True
    default_useDefaultPos = False
    default_analyticID = None
    default_isCollapseable = True
    default_isCompact = None
    default_windowID = None
    WINDOW_NEVER_OFFSCREEN_BUFFER = 20
    COLLAPSE_AREA_HEIGHT = 25
    __active = False
    __active_snap_grid = None
    __caption = None
    __closing = False
    __collapsed = False
    __drag_started = False
    __focused_at_timestamp = None
    __header = None
    __header_has_sufficient_bottom_padding = False
    __header_inset = (0, 0)
    __hide_loading_indicator_requested = False
    __hovered = False
    __modal_result = None
    __on_active_changed = None
    __on_caption_changed = None
    __on_collapsed_changed = None
    __on_collapsible_changed = None
    __on_compact_mode_changed = None
    __on_content_padding_changed = None
    __on_end_scale = None
    __on_fixed_height_changed = None
    __on_fixed_width_changed = None
    __on_header_height_changed = None
    __on_header_inset_changed = None
    __on_icon_changed = None
    __on_killable_changed = None
    __on_light_background_changed = None
    __on_lockable_changed = None
    __on_locked_changed = None
    __on_margin_mode_changed = None
    __on_minimizable_changed = None
    __on_stacked_changed = None
    __on_start_scale = None
    __on_window_state_changed = None
    __opened_at_timestamp = None
    __previous_content_padding = None
    __previous_header_height = None
    __ready = False
    __resizer = None
    __scale_sides = None
    __stack = None
    __window_controls = None
    __window_controls_cont = None

    @staticmethod
    def __get_default_compact(window_ref):
        window = window_ref()
        if not window or window.closing:
            return False
        elif window.compactable and window.default_isCompact is None:
            return window_compact_mode_default_setting.get()
        else:
            return window.default_isCompact

    @classmethod
    def Reload(cls, instance):
        attributes = instance.attributesBunch
        state = instance.state
        if instance.isDialog:
            instance.Close()
            return
        attributes.openMinimized = instance.IsMinimized()
        instance.Close()
        wnd = cls.Open(**attributes)
        wnd.SetState(state)

    def __init__(self, show_window_controls = True, **kwargs):
        self.default_parent = uicore.layer.main
        self.__apply_content_padding = kwargs.get('apply_content_padding', self.default_apply_content_padding)
        self.__collapsible = self.default_isCollapseable
        self.__compact_mode_setting = WindowCompactModeSetting(window_id=kwargs.get('windowID', self.default_windowID), default_value=lambda _window_ref = weakref.ref(self): Window.__get_default_compact(_window_ref))
        self.__compactable = self.default_isCompactable
        self.__extend_content_into_header = kwargs.get('extend_content_into_header', self.default_extend_content_into_header)
        self.__icon = kwargs.get('iconNum', self.GetDefaultWndIcon())
        self.__killable = self.default_isKillable
        self.__lockable = self.default_isLockable
        self.__minimizable = kwargs.get('isMinimizable', self.default_isMinimizable)
        self.__scene_containers = set()
        self.__show_window_controls = show_window_controls
        self.__stackable = self.default_isStackable
        self._changing = False
        self._fixedHeight = self.default_fixedHeight
        self._fixedWidth = self.default_fixedWidth
        self._resizeable = True
        self._scaling = False
        self.preDragAbs = None
        self.preDragCursorPos = None
        self.stackID = kwargs.get('stackID', self.default_stackID)
        self.sortedScaleWindows = None
        self.minmaxScale = None
        self.dragMousePosition = None
        self.isBlinking = False
        self.isDialog = False
        self.isModal = False
        self.maxsize = kwargs.get('maxSize', self.default_maxSize)
        self.minsize = kwargs.get('minSize', self.default_minSize)
        self.scope = kwargs.get('scope', self.default_scope)
        self.windowID = kwargs.get('windowID', self.default_windowID)
        self.windowInstanceID = kwargs.get('windowInstanceID', self.default_windowInstanceID)
        super(Window, self).__init__(**kwargs)
        attributesBunch = Bunch(**kwargs)
        self.PostApplyAttributes(attributesBunch)
        window_margin_mode.on_changed.connect(self.__on_global_window_margin_mode_changed)
        notifyevents = getattr(self, '__notifyevents__', None)
        if not notifyevents:
            notifyevents = ['OnUIRefresh']
        elif 'OnUIRefresh' not in notifyevents:
            notifyevents.append('OnUIRefresh')
        self.__notifyevents__ = notifyevents
        sm.RegisterNotify(self)

    def ApplyAttributes(self, attributes):
        self.attributesBunch = attributes
        self.sr.tab = None
        self.sr.modalParent = None
        self.sr.loadingParent = None
        self.sr.underlay = None
        self.sr.headerParent = None
        self.sr.loadingIndicator = None
        self._CheckCallableDefaults()
        uicore.registry.RegisterWindow(self)
        left, top, _, _ = self.GetDefaultSizeAndPosition()
        attributes['left'] = left
        attributes['top'] = top
        if self.windowID:
            try:
                attributes.name = str(self.windowID)
            except Exception:
                attributes.name = repr(self.windowID)

        super(Window, self).ApplyAttributes(attributes)
        self.sr.maincontainer = Container(name='content', parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.cacheContents = True
        self.InitializeSize(useDefaultPos=attributes.get('useDefaultPos', self.default_useDefaultPos))
        self.Prepare_()
        self._UpdateHeaderInset(silent=True)
        self._UpdateBorderPadding()
        self.__compact_mode_setting.on_change.connect(self.__on_compact_mode_setting_changed)
        self._analyticID = attributes.Get('analyticID', self.default_analyticID)
        self.__opened_at_timestamp = gametime.GetWallclockTime()
        sm.ScatterEvent('OnWindowOpened', self)
        self._LogWindowEventOpened()
        soundOpen = attributes.get('soundOpen', self.default_soundOpen)
        if soundOpen:
            PlaySound(soundOpen)

    @property
    def active(self):
        return self.__active

    @property
    def on_active_changed(self):
        if self.__on_active_changed is None:
            self.__on_active_changed = signals.Signal('{}.on_active_changed'.format(self.__class__.__name__))
        return self.__on_active_changed

    def _emit_on_active_changed(self):
        if not self.closing and self.__on_active_changed is not None:
            self.__on_active_changed(self)

    @property
    def analyticID(self):
        return self._analyticID

    @property
    def caption(self):
        return self.__caption

    @caption.setter
    def caption(self, value):
        if self.__caption != value:
            self.__caption = value
            self._emit_on_caption_changed()

    @property
    def on_caption_changed(self):
        if self.__on_caption_changed is None:
            self.__on_caption_changed = signals.Signal('Window.on_caption_changed')
        return self.__on_caption_changed

    def _emit_on_caption_changed(self):
        if not self.closing:
            self._OnCaptionChanged()
            if self.__on_caption_changed is not None:
                self.__on_caption_changed(self)

    @property
    def content(self):
        return self.sr.main

    @property
    def content_padding(self):
        if self.compact or self.margin_mode == WindowMarginMode.COMPACT:
            padding = 8
        else:
            padding = 16
        should_apply_top_padding = self.__extend_content_into_header or not self.__header_has_sufficient_bottom_padding
        top_padding = padding if should_apply_top_padding else 0
        return (padding,
         top_padding,
         padding,
         padding)

    @property
    def on_content_padding_changed(self):
        if self.__on_content_padding_changed is None:
            self.__on_content_padding_changed = signals.Signal('Window.on_content_padding_changed')
        return self.__on_content_padding_changed

    def _emit_on_content_padding_changed(self):
        if not self.closing and self.__on_content_padding_changed is not None:
            self.__on_content_padding_changed(self)

    @property
    def apply_content_padding(self):
        return self.__apply_content_padding

    @apply_content_padding.setter
    def apply_content_padding(self, value):
        value = bool(value)
        if value != self.__apply_content_padding:
            self.__apply_content_padding = value
            self._UpdateContentPadding()

    @property
    def closing(self):
        return self.__closing or self.stacked and self.stack.closing

    @property
    def collapsed(self):
        if self.stacked:
            return self.stack.collapsed
        return self.__collapsed

    @property
    def on_collapsed_changed(self):
        if self.__on_collapsed_changed is None:
            self.__on_collapsed_changed = signals.Signal('Window.on_collapsed_changed')
        return self.__on_collapsed_changed

    def _emit_on_collapsed_changed(self):
        if not self.closing and self.__on_collapsed_changed is not None:
            self.__on_collapsed_changed(self)

    @collapsed.setter
    def collapsed(self, value):
        if value:
            self.Collapse()
        else:
            self.Expand()

    @property
    def collapsible(self):
        return self.__collapsible

    @collapsible.setter
    def collapsible(self, value):
        if self.__collapsible != value:
            if value:
                self.__collapsible = True
            else:
                self.__collapsible = False
            self._emit_on_collapsible_changed()

    @property
    def on_collapsible_changed(self):
        if self.__on_collapsible_changed is None:
            self.__on_collapsible_changed = signals.Signal('{}.on_collapsible_changed'.format(self.__class__.__name__))
        return self.__on_collapsible_changed

    def _emit_on_collapsible_changed(self):
        if self.__on_collapsible_changed is not None:
            self.__on_collapsible_changed(self)

    @property
    def compact(self):
        if self.compactable:
            return self.__compact_mode_setting.get()
        else:
            return self.__compact_mode_setting.get_default()

    @compact.setter
    def compact(self, value):
        action = 'compact' if value else 'uncompact'
        if self.compactable and not is_blocked(action, self.windowID):
            self.__compact_mode_setting.set(value)

    @property
    def on_compact_mode_changed(self):
        if self.__on_compact_mode_changed is None:
            self.__on_compact_mode_changed = signals.Signal('Window.on_compact_mode_changed')
        return self.__on_compact_mode_changed

    def _emit_on_compact_mode_changed(self):
        if not self.closing:
            if self.compact:
                self.OnCompactModeEnabled()
            else:
                self.OnCompactModeDisabled()
            self._UpdateContentPadding()
            self._update_window_controls()
            if self.__on_compact_mode_changed is not None:
                self.__on_compact_mode_changed(self)

    def __on_compact_mode_setting_changed(self, value):
        if not self.closing:
            self._emit_on_compact_mode_changed()

    @property
    def compactable(self):
        return self.__compactable

    @property
    def displayRect(self):
        return (self._displayX,
         self._displayY,
         self._displayWidth,
         self._displayHeight)

    @displayRect.setter
    def displayRect(self, value):
        displayX, displayY, displayWidth, displayHeight = value
        self._displayX = int(round(displayX))
        self._displayY = int(round(displayY))
        self._displayWidth = int(round(displayWidth))
        self._displayHeight = int(round(displayHeight))
        ro = self.renderObject
        if ro:
            ro.displayX = self._displayX
            ro.displayY = self._displayY
            ro.displayWidth = self._displayWidth
            ro.displayHeight = self._displayHeight

    @property
    def extend_content_into_header(self):
        return self.__extend_content_into_header

    @extend_content_into_header.setter
    def extend_content_into_header(self, value):
        if self.__extend_content_into_header != value:
            self.__extend_content_into_header = value
            self._UpdateHeaderAlignment()
            self._UpdateContentPadding()

    @property
    def fixed_height(self):
        return self._fixedHeight

    @fixed_height.setter
    def fixed_height(self, value):
        self.SetFixedHeight(value)

    @property
    def on_fixed_height_changed(self):
        if self.__on_fixed_height_changed is None:
            self.__on_fixed_height_changed = signals.Signal('{}.on_fixed_height_changed'.format(self.__class__.__name__))
        return self.__on_fixed_height_changed

    def _emit_fixed_height_changed(self):
        if not self.closing and self.__on_fixed_height_changed is not None:
            self.__on_fixed_height_changed(self)

    @property
    def fixed_width(self):
        return self._fixedWidth

    @fixed_width.setter
    def fixed_width(self, value):
        self.SetFixedWidth(value)

    @property
    def on_fixed_width_changed(self):
        if self.__on_fixed_width_changed is None:
            self.__on_fixed_width_changed = signals.Signal('{}.on_fixed_width_changed'.format(self.__class__.__name__))
        return self.__on_fixed_width_changed

    def _emit_fixed_width_changed(self):
        if not self.closing and self.__on_fixed_width_changed is not None:
            self.__on_fixed_width_changed(self)

    @property
    def header(self):
        if self.closing:
            raise RuntimeError('Attempting to manipulate a window header while the window is closing or already closed.')
        elif self.__header is not None and self.__header.destroyed:
            raise RuntimeError("The window's header has been destroyed, even though the window has not been closed yet")
        return self.__header

    @header.setter
    def header(self, value):
        if not self.closing:
            if value is None:
                value = DefaultWindowHeader()
            self._SetHeader(value)

    @property
    def header_height(self):
        if self.__header is not None:
            _, height = self.__header.GetAbsoluteSize()
            return height + self.__header.padTop + self.__header.padBottom
        return 0

    @property
    def on_header_height_changed(self):
        if self.__on_header_height_changed is None:
            self.__on_header_height_changed = signals.Signal('{}.on_header_height_changed'.format(self.__class__.__name__))
        return self.__on_header_height_changed

    def _emit_on_header_height_changed(self):
        if not self.closing and self.__on_header_height_changed is not None:
            self.__on_header_height_changed(self)

    @property
    def header_inset(self):
        return self.__header_inset

    @property
    def on_header_inset_changed(self):
        if self.__on_header_inset_changed is None:
            self.__on_header_inset_changed = signals.Signal('Window.on_header_inset_changed')
        return self.__on_header_inset_changed

    def _emit_on_header_inset_changed(self):
        if not self.closing and self.__on_header_inset_changed is not None:
            self.__on_header_inset_changed(self)

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, value):
        if self.__icon != value:
            self.__icon = value
            self._emit_on_icon_changed()

    @property
    def on_icon_changed(self):
        if self.__on_icon_changed is None:
            self.__on_icon_changed = signals.Signal('Window.on_icon_changed')
        return self.__on_icon_changed

    def _emit_on_icon_changed(self):
        if not self.closing and self.__on_icon_changed is not None:
            self.__on_icon_changed(self)

    @property
    def is_stack(self):
        return False

    @property
    def killable(self):
        return self.__killable

    @killable.setter
    def killable(self, value):
        if self.__killable != value:
            self.__killable = value
            self._emit_on_killable_changed()

    @property
    def on_killable_changed(self):
        if self.__on_killable_changed is None:
            self.__on_killable_changed = signals.Signal('Window.on_killable_changed')
        return self.__on_killable_changed

    def _emit_on_killable_changed(self):
        if not self.closing and self.__on_killable_changed is not None:
            self.__on_killable_changed(self)

    @property
    def light_background_enabled(self):
        return self.IsLightBackgroundEnabled()

    @light_background_enabled.setter
    def light_background_enabled(self, value):
        if value == self.light_background_enabled:
            return
        if value:
            self.EnableLightBackground()
        else:
            self.DisableLightBackground()

    @property
    def on_light_background_changed(self):
        if self.__on_light_background_changed is None:
            self.__on_light_background_changed = signals.Signal('Window.on_light_background_changed')
        return self.__on_light_background_changed

    def _emit_on_light_background_changed(self):
        if not self.closing:
            self.UpdateIntersectionBackground()
            if self.__on_light_background_changed is not None:
                self.__on_light_background_changed(self)

    @property
    def locked(self):
        return self.GetRegisteredState('locked', False)

    @locked.setter
    def locked(self, value):
        action = 'lock' if value else 'unlock'
        if is_blocked(action, self.windowID):
            return
        if self.locked != value:
            self.RegisterState('locked', bool(value))
            self._emit_on_locked_changed()

    @property
    def on_locked_changed(self):
        if self.__on_locked_changed is None:
            self.__on_locked_changed = signals.Signal('Window.on_locked_changed')
        return self.__on_locked_changed

    def _emit_on_locked_changed(self):
        if not self.closing:
            self.Prepare_ScaleAreas_()
            if self.__on_locked_changed is not None:
                self.__on_locked_changed(self)

    @property
    def lockable(self):
        return self.default_isLockable

    @lockable.setter
    def lockable(self, value):
        if self.__lockable != value:
            self.__lockable = value
            self._emit_on_lockable_changed()

    @property
    def on_lockable_changed(self):
        if self.__on_lockable_changed is None:
            self.__on_lockable_changed = signals.Signal('{}.on_lockable_changed'.format(self.__class__.__name__))
        return self.__on_lockable_changed

    def _emit_on_lockable_changed(self):
        if self.__on_lockable_changed is not None:
            self.__on_lockable_changed(self)

    @property
    def margin_mode(self):
        return window_margin_mode.value

    @property
    def on_margin_mode_changed(self):
        if self.__on_margin_mode_changed is None:
            self.__on_margin_mode_changed = signals.Signal('{}.on_margin_mode_changed'.format(self.__class__.__name__))
        return self.__on_margin_mode_changed

    @property
    def minimizable(self):
        return self.__minimizable

    @minimizable.setter
    def minimizable(self, value):
        if self.__minimizable != value:
            self.__minimizable = value
            self._emit_on_minimizable_changed()

    @property
    def on_minimizable_changed(self):
        if self.__on_minimizable_changed is None:
            self.__on_minimizable_changed = signals.Signal('{}.on_minimizable_changed'.format(self.__class__.__name__))
        return self.__on_minimizable_changed

    def _emit_on_minimizable_changed(self):
        if not self.closing and self.__on_minimizable_changed is not None:
            self.__on_minimizable_changed(self)

    @property
    def minimized(self):
        return self.IsMinimized()

    @minimized.setter
    def minimized(self, value):
        if value:
            self.Minimize()
        else:
            self.Maximize()

    @property
    def overlayable(self):
        return self.default_isOverlayable

    @property
    def show_window_controls(self):
        return self.__show_window_controls

    @show_window_controls.setter
    def show_window_controls(self, value):
        if self.__show_window_controls != value:
            self.__show_window_controls = value
            self._update_window_controls_visibility()

    @property
    def stack(self):
        return self.__stack

    @property
    def stacked(self):
        return self.__stack is not None

    @property
    def on_stacked_changed(self):
        if self.__on_stacked_changed is None:
            self.__on_stacked_changed = signals.Signal('Window.on_stacked_changed')
        return self.__on_stacked_changed

    def _emit_on_stacked_changed(self):
        if not self.closing and self.__on_stacked_changed is not None:
            self.__on_stacked_changed(self)

    @property
    def on_start_scale(self):
        if self.__on_start_scale is None:
            self.__on_start_scale = signals.Signal('Window.on_start_scale')
        return self.__on_start_scale

    def _emit_on_start_scale(self):
        if not self.closing and self.__on_start_scale is not None:
            self.__on_start_scale(self)

    @property
    def on_end_scale(self):
        if self.__on_end_scale is None:
            self.__on_end_scale = signals.Signal('Window.on_end_scale')
        return self.__on_end_scale

    def _emit_on_end_scale(self):
        if not self.closing and self.__on_end_scale is not None:
            self.__on_end_scale(self)

    def OnUIRefresh(self):
        self.Reload(self)

    @telemetry.ZONE_METHOD
    def PostApplyAttributes(self, attributes):
        self.RegisterSize()
        if attributes.get('ignoreStack', False):
            self.RegisterStackID(None)
        self.InitializeCaption(attributes)
        if attributes.get('openDragging', False) and uicore.uilib.leftbtn:
            self.RegisterStackID(None)
            self._SetOpen(True)
            uthread.new(self._OpenDraggingThread)
        else:
            self.InitializeStatesAndPosition(showIfInStack=attributes.get('showIfInStack', True), useDefaultPos=attributes.get('useDefaultPos', self.default_useDefaultPos))
        if attributes.get('openMinimized', self.default_openMinimized):
            self.Minimize(animate=False)
        uicore.registry.SetFocus(self)
        self.__ready = True

    def InitializeCaption(self, attributes):
        if self.__caption is not None:
            return
        caption = attributes.get('caption', self.default_caption)
        if caption is not None:
            self.SetCaption(caption)
        else:
            captionLabelPath = attributes.get('captionLabelPath', self.default_captionLabelPath)
            if captionLabelPath:
                self.SetCaption(localization.GetByLabel(captionLabelPath))

    def Show(self, *args):
        self.Maximize(*args)

    def _OpenDraggingThread(self):
        self.state = uiconst.UI_NORMAL
        if self.IsLocked():
            return
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)
        self.left = uicore.uilib.x - 5
        self.top = uicore.uilib.y - 5
        uicore.uilib.SetMouseCapture(self)
        compact = self.GetRegisteredState('compact', False)
        if compact:
            self.Compact()
        self._BeginDrag()

    def GetAbsolutePosition(self):
        stack = self.stack
        if stack:
            return stack.contentCont.GetAbsolutePosition()
        return (self.left, self.top)

    def _CheckCallableDefaults(self):
        if callable(self.default_left):
            self.default_left = self.default_left()
        if callable(self.default_top):
            self.default_top = self.default_top()
        if callable(self.default_width):
            self.default_width = self.default_width()
        if callable(self.default_height):
            self.default_height = self.default_height()

    def Prepare_(self):
        self.Prepare_Layout()
        self._create_window_controls()
        self.Prepare_Header_()
        self.Prepare_LoadingIndicator_()
        self.Prepare_Background_()
        self.Prepare_ScaleAreas_()

    def Prepare_Layout(self):
        self.ConstructHeaderParent()
        self.sr.main = self.construct_content_cont()

    def construct_content_cont(self):
        return Container(parent=self.sr.maincontainer, name='main', align=uiconst.TOALL, padding=self.content_padding)

    def ConstructHeaderParent(self):
        self.sr.headerParent = ContainerAutoSize(parent=self.sr.maincontainer, name='headerParent', align=self._GetHeaderAlignment(), alignMode=uiconst.TOTOP, callback=self.__on_header_parent_size_changed, only_use_callback_when_size_changes=True)
        index = 0
        if self.__resizer is not None:
            index = self.__resizer.GetOrder()
        self.__window_controls_cont = Container(name='window_controls_cont', parent=self, align=uiconst.TOTOP_NOPUSH, padding=self._get_window_controls_cont_padding(), idx=index)

    def _get_window_controls_cont_padding(self):
        pad_left, pad_top, pad_right, pad_bottom = self.GetWindowBorderPadding()
        size_left, size_top, size_right, size_bottom = self.GetWindowBorderSize()
        return (pad_left + size_left,
         pad_top + size_top,
         pad_right + size_right,
         pad_bottom + size_bottom)

    def Prepare_Header_(self):
        self._SetHeader(DefaultWindowHeader())

    def _create_window_controls(self):
        actions = self._get_window_actions()
        self.__window_controls = DefaultWindowControls(window=self, parent=self.__window_controls_cont, actions=actions, get_menu=self.GetMenuMoreOptions, get_link_data=self.GetWindowLinkData, menu_unique_name=self.get_wnd_menu_unique_name(), on_reserved_width_changed=self._UpdateHeaderInset, display=self._get_window_controls_visible())

    def update_window_controls(self):
        self.__window_controls.update()

    def _get_window_actions(self):
        actions = [CloseWindowAction(self),
         MinimizeWindowAction(self),
         LockWindowAction(self),
         OverlayWindowAction(self),
         CompactModeWindowAction(self),
         LightBackgroundWindowAction(self),
         CollapseWindowAction(self)]
        actions.extend(self.GetCustomHeaderButtons())
        return actions

    def get_wnd_menu_unique_name(self):
        return None

    def _update_window_controls(self):
        self._destroy_window_controls()
        self._create_window_controls()

    def _destroy_window_controls(self):
        if self.__window_controls is not None:
            self.__window_controls.Close()
            self.__window_controls = None

    def _get_window_controls_visible(self):
        return self.__show_window_controls and not self.stacked

    def _update_window_controls_visibility(self):
        if self.__window_controls is not None:
            self.__window_controls.display = self._get_window_controls_visible()

    def GetCustomHeaderButtons(self):
        return []

    def GetMenuMoreOptions(self):
        return MenuData()

    def GetWindowLinkData(self):
        return None

    def Prepare_Background_(self):
        self.sr.underlay = WindowUnderlay(parent=self, padding=self.GetWindowBorderPadding())

    def GetDefaultWndIcon(self):
        return self.default_iconNum

    def GetNeocomGroupIcon(self):
        return self.icon

    def GetNeocomGroupLabel(self):
        return self.GetCaption()

    def EnableLightBackground(self):
        self.sr.underlay.EnableLightBackground()
        self._SetLightBackground(True)

    def DisableLightBackground(self):
        self.sr.underlay.DisableLightBackground()
        self._SetLightBackground(False)

    def IsLightBackgroundConfigurable(self, *args):
        return self.default_isLightBackgroundConfigurable

    def IsLightBackgroundEnabled(self):
        default = self.default_isLightBackground
        if callable(self.default_isLightBackground):
            default = default()
        return self.GetRegisteredState('isLightBackground', default)

    def _SetLightBackground(self, isLightBackground):
        self.RegisterState('isLightBackground', isLightBackground)
        self._emit_on_light_background_changed()

    def IsOverlayed(self):
        return self.GetRegisteredState('isOverlayed', self.default_isOverlayed)

    def SetOverlayed(self):
        self.RegisterState('isOverlayed', True)

    def SetNotOverlayed(self):
        self.RegisterState('isOverlayed', False)

    def IsBlinking(self):
        return self.isBlinking

    def SetBlinking(self):
        if uicore.registry.GetActive() == self:
            return
        self.isBlinking = True
        sm.ScatterEvent('OnWindowStartBlinking', self)

    def SetNotBlinking(self):
        self.isBlinking = False
        sm.ScatterEvent('OnWindowStopBlinking', self)

    def _handle_start_scale(self, sides):
        sides = [ LEGACY_SIDE_NAME_BY_SIDE[side] for side in sides ]
        self._StartScale(sides=sides)

    def _handle_end_scale(self, sides):
        self.EndScale(None)

    def _is_side_resizable(self, side):
        if not self.IsResizeable() or self.stacked:
            return False
        elif side in {Side.LEFT, Side.RIGHT}:
            return self.fixed_width is None
        elif side in {Side.TOP, Side.BOTTOM}:
            return self.fixed_height is None
        else:
            return True

    def _get_resizer_padding(self):
        return (0, 0, 0, 0)

    def _get_resizer_inner_padding(self):
        margin_left, margin_top, margin_right, margin_bottom = self.GetWindowBorderPadding()
        _, border_top, _, _ = self.GetWindowBorderSize()
        pad_top = margin_top
        if self.active:
            pad_top += border_top
        return (margin_left,
         pad_top,
         margin_right,
         margin_bottom)

    def _update_resizer_padding(self):
        self.__resizer.padding = self._get_resizer_padding()
        self.__resizer.inner_padding = self._get_resizer_inner_padding()

    def Prepare_ScaleAreas_(self):
        if self.__resizer is None:
            index = 0
            if self.__window_controls_cont is not None:
                index = self.__window_controls_cont.GetOrder() + 1
            self.__resizer = Resizer(parent=self, idx=index, locked_sides=filter(lambda s: not self._is_side_resizable(s), Side.iter()), on_start_scale=self._handle_start_scale, on_end_scale=self._handle_end_scale, padding=self._get_resizer_padding(), inner_padding=self._get_resizer_inner_padding())
        else:
            self._update_resizer_padding()
            self.__resizer.locked_sides = [ side for side in Side.iter() if not self._is_side_resizable(side) ]

    def Prepare_LoadingIndicator_(self):
        if self.sr.loadingParent:
            self.sr.loadingParent.Close()
        self.sr.loadingParent = Container(name='__loadingParent', parent=self.sr.maincontainer, state=uiconst.UI_HIDDEN, idx=0)
        self.sr.loadingIndicator = AnimSprite(parent=self.sr.loadingParent, state=uiconst.UI_HIDDEN, align=uiconst.TOPRIGHT, left=5)
        self.sr.loadingIndicator.icons = [ 'ui_38_16_%s' % (210 + i) for i in xrange(8) ]

    def GetStackID(self):
        window_id = self.windowID
        if isinstance(window_id, tuple):
            window_id, _ = window_id
        if not window_id:
            return None
        stack_id_by_window_id = settings.char.windows.Get('stacksWindows', {})
        return stack_id_by_window_id.get(window_id, self.stackID)

    def RegisterStackID(self, stack = None):
        window_id = self.windowID
        if isinstance(window_id, tuple):
            window_id, _ = window_id
        if not window_id:
            return
        stack_id = None
        if stack is not None:
            stack_id = stack.windowID
        stack_id_by_window_id = settings.char.windows.Get('stacksWindows', {})
        stack_id_by_window_id[window_id] = stack_id
        settings.char.windows.Set('stacksWindows', stack_id_by_window_id)

    def OnStackInsert(self, stack):
        self.__stack = stack
        self.align = uiconst.TOALL
        self.__ready = False
        self.left = self.top = self.width = self.height = 0
        self.__ready = True
        self._stack_cacheContents = self.cacheContents
        self.cacheContents = False
        self.state = uiconst.UI_HIDDEN
        self.sr.loadingIndicator.Stop()
        self._update_window_controls_visibility()
        self._UpdateContentPadding()
        self._UpdateBorderPadding()
        self.Prepare_ScaleAreas_()
        self._emit_on_stacked_changed()

    def OnStackRemove(self, correctpos, dragging, grab):
        self.__stack = None
        self.sr.tab = None
        self.align = uiconst.RELATIVE
        self.state = uiconst.UI_NORMAL
        self.grab = grab
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)
        if dragging:
            uicore.uilib.SetMouseCapture(self)
            uthread.new(self._BeginDrag)
            if self.height < self.GetMinHeight():
                self.height = self.GetMinHeight()
            if self.width < self.GetMinWidth():
                self.width = self.GetMinWidth()
        self.ShowBackground()
        self.Prepare_ScaleAreas_()
        if correctpos:
            self.left = uicore.uilib.x - grab[0]
            self.top = uicore.uilib.y - grab[1]
        self._update_window_controls_visibility()
        self._UpdateContentPadding()
        self._UpdateBorderPadding()
        self._emit_on_stacked_changed()

    def _UpdateBorderPadding(self):
        if self.stacked:
            self.sr.maincontainer.padding = 0
        else:
            margin_left, margin_top, margin_right, margin_bottom = self.GetWindowBorderPadding()
            border_left, border_top, border_right, border_bottom = self.GetWindowBorderSize()
            self.sr.maincontainer.padding = (margin_left + border_left,
             margin_top + border_top,
             margin_right + border_right,
             margin_bottom + border_bottom)
        self._update_resizer_padding()

    def _UpdateHeaderAlignment(self):
        if self.sr.headerParent is not None:
            self.sr.headerParent.align = self._GetHeaderAlignment()

    def _GetHeaderAlignment(self):
        if self.extend_content_into_header:
            return uiconst.TOTOP_NOPUSH
        return uiconst.TOTOP

    def InitializeSize(self, useDefaultPos = False):
        d = uicore.desktop
        if useDefaultPos:
            left, top, width, height = self.GetDefaultSizeAndPosition()
        else:
            left, top, width, height, dw, dh = self.GetRegisteredPositionAndSize()
        maxWidth, maxHeight = self.GetMaxWidth(), self.GetMaxHeight()
        minWidth, minHeight = self.GetMinWidth(), self.GetMinHeight()
        if self._fixedWidth:
            self.width = self._fixedWidth
        else:
            self.width = min(maxWidth, max(minWidth, min(d.width, width)))
        if self._fixedHeight:
            self.height = self._fixedHeight
        else:
            self.height = min(maxHeight, max(minHeight, min(d.height, height)))

    def OnResetWindowSettings(self):
        self.__stack = None
        if self.IsMinimized():
            self.Maximize()
        self.state = uiconst.UI_HIDDEN
        self.align = uiconst.TOPLEFT
        self.ShowBackground()
        self.InitializeSize()
        self.InitializeStatesAndPosition()

    def InitializeStatesAndPosition(self, showIfInStack = True, useDefaultPos = False, **kwds):
        self.__ready = False
        log.LogInfo('Window.InitializeStatesAndPosition', self.windowID)
        if self.IsLightBackgroundConfigurable():
            if self.IsLightBackgroundEnabled():
                self.EnableLightBackground()
            else:
                self.DisableLightBackground()
        if self.IsLocked():
            self.Lock()
        else:
            self.Unlock()
        if self.IsMinimized():
            self._SetMaximized()
        stack = None
        stackID = self.GetStackID()
        from carbonui.window.stack import WindowStack
        if not isinstance(self, WindowStack):
            if self.IsStackable() and stackID:
                stack = uicore.registry.GetWindow(stackID)
                if stack and not stack.closing:
                    log.LogInfo('Window.InitializeStatesAndPosition, windowStack already created', self.windowID)
                    stack.InsertWnd(self, False, showIfInStack, 1)
        if not stack or stack.closing:
            collapsed = self.GetRegisteredState('collapsed', False)
            if collapsed:
                self.Collapse()
            elif self.IsCollapsed():
                self.Expand()
            self.UpdatePosition(useDefaultPos)
            if stackID is not None and not isinstance(self, self.GetStackClass()) and self.__stackable:
                self.state = uiconst.UI_HIDDEN
                log.LogInfo('Window.InitializeStatesAndPosition creating new stack while initializing', self.windowID)
                stack = uicore.registry.GetStack(stackID, self.GetStackClass())
                if stack and not stack.closing:
                    stack.InsertWnd(self, True, showIfInStack, 1)
        if not self.InStack() and not self.IsMinimized():
            self.state = uiconst.UI_NORMAL
            self._SetMaximized()
        self._SetOpen(True)
        self.__ready = True

    def InitializeFocus(self):
        focus = uicore.registry.GetFocus()
        from carbonui.control.editPlainText import EditPlainTextCore
        from carbonui.control.singlelineedits.baseSingleLineEdit import BaseSingleLineEdit
        editFieldHasFocus = focus and isinstance(focus, (EditPlainTextCore, BaseSingleLineEdit))
        if not editFieldHasFocus:
            uthread.new(uicore.registry.SetFocus, self)

    def UpdatePosition(self, useDefaultPos = False):
        if useDefaultPos:
            left, top, width, height = self.GetDefaultSizeAndPosition()
        else:
            left, top, width, height, dw, dh = self.GetRegisteredPositionAndSize()
        left = max(0, min(uicore.desktop.width - self.width, left))
        top = max(0, min(uicore.desktop.height - self.height, top))
        leftpush, rightpush = self.GetSideOffset()
        if left in (0, SNAP_DISTANCE):
            left += leftpush
        elif left + self.width in (uicore.desktop.width, uicore.desktop.width - SNAP_DISTANCE):
            left -= rightpush
        self.left = left
        self.top = top
        self.CheckWndPos()

    @classmethod
    def GetSideOffset(cls):
        if uicore.layer.sidePanels:
            return uicore.layer.sidePanels.GetSideOffset()
        return (0, 0)

    def RegisterState(self, statename, value):
        RegisterState(self.windowID, statename, value)

    def GetRegisteredState(self, statename, default = None):
        return GetRegisteredState(self.windowID, statename, default)

    def IsRegisteringPositionAndSizeAllowed(self):
        if self.windowID is None:
            return False
        if self._changing or self.IsMinimized():
            return False
        if not self.InStack():
            if self.GetStackID():
                return False
            if self.GetAlign() != uiconst.RELATIVE:
                return False
        return True

    def RegisterPositionAndSize(self, key = None, windowID = None):
        if not self.IsRegisteringPositionAndSizeAllowed():
            return
        l, t = self._GetPositionToRegister()
        w, h = self._GetSizeToRegister()
        self._RegisterWindowSizeAndPositionSetting(l, t, w, h, windowID)

    def RegisterSize(self):
        if not self.IsRegisteringPositionAndSizeAllowed():
            return
        width, height = self._GetSizeToRegister()
        self._RegisterWindowSizeAndPositionSetting(width=width, height=height)

    def _GetPositionToRegister(self):
        if self.stacked:
            l, t = self.stack.left, self.stack.top
        else:
            l, t = self.left, self.top
        if l is not None:
            l = self._AccountForSideAutoSnapDistance(l)
        return (l, t)

    def _AccountForSideAutoSnapDistance(self, l):
        dw, dh = uicore.desktop.width, uicore.desktop.height
        leftOffset, rightOffset = self.GetSideOffset()
        if l in (leftOffset, leftOffset + 16):
            l -= leftOffset
        elif l + self.width in (dw - rightOffset, dw - rightOffset - 16):
            l += rightOffset
        return l

    def _GetSizeToRegister(self):
        if self.stacked:
            w, h = self.stack.width, self.stack.height
        else:
            w, h = self.width, self.height
        if self.IsCollapsed():
            h = None
        return (w, h)

    def _RegisterWindowSizeAndPositionSetting(self, left = None, top = None, width = None, height = None, windowID = None):
        if windowID is None:
            windowID = self._GetWindowID()
        allWindows = settings.char.windows.Get('windowSizesAndPositions_1', {})
        regLeft, regTop, regWidth, regHeight, _, _ = self.GetRegisteredPositionAndSizeByClass(windowID)
        allWindows[windowID] = (left if left is not None else regLeft,
         top if top is not None else regTop,
         width if width is not None else regWidth,
         height if height is not None else regHeight,
         uicore.desktop.width,
         uicore.desktop.height)
        settings.char.windows.Set('windowSizesAndPositions_1', allWindows)

    def _GetWindowID(self):
        if type(self.windowID) == tuple:
            windowID, _ = self.windowID
        else:
            windowID = self.windowID
        return windowID

    def SetFixedHeightFromContentHeight(self, height):
        window_controls_height = self.__window_controls_cont.padTop + self.__window_controls_cont.padBottom
        fixed_height = height + self.header_height + window_controls_height
        self.SetFixedHeight(fixed_height, force=True)

    def SetFixedHeight(self, height = None, force = False):
        if self._fixedHeight != height or force:
            self._fixedHeight = height
            if height is not None and not self.stacked:
                self.height = height
            self.Prepare_ScaleAreas_()
            self._emit_fixed_height_changed()

    def SetFixedWidth(self, width = None):
        if self._fixedWidth != width:
            self._fixedWidth = width
            if width is not None and not self.stacked:
                self.width = width
            self.Prepare_ScaleAreas_()
            self._emit_fixed_width_changed()

    def GetMinSize(self, *args, **kw):
        width, height = (0, 0)
        if self.sr.headerParent and self.sr.headerParent.state != uiconst.UI_HIDDEN:
            height += self.sr.headerParent.height
        return (width, height)

    def IsCurrentDialog(self):
        return getattr(self, 'isDialog', False) and (not getattr(self, 'isModal', False) or uicore.registry.GetModalWindow() == self)

    def Close(self, setClosed = False, *args, **kwds):
        if self.__closing:
            return
        self.__closing = True
        if setClosed:
            self._SetOpen(False)
        sm.ScatterEvent('OnWindowClosed', self.windowID, self.windowInstanceID, self.__class__)
        if self.__modal_result:
            self._SetModalResult(uiconst.ID_CLOSE)
        self.state = uiconst.UI_HIDDEN
        if self.__header is not None:
            self.__header.unmount(self)
            self.__header.Close()
            self.__header = None
        modalParent = self.sr.modalParent
        stack = self.stack
        super(Window, self).Close()
        if uicore.registry.GetActive() == self:
            if stack is not None:
                uicore.registry.SetFocus(stack)
            else:
                uicore.registry.SetFocus(None)
        if self.__modal_result:
            self._SetModalResult(uiconst.ID_CLOSE)
        if modalParent is not None and not modalParent.destroyed:
            modalParent.Close()
        uicore.registry.UnregisterWindow(self)
        self.UpdateIntersectionBackground()
        if stack is not None and not stack.destroyed:
            stack.Check(checknone=1)

    def HasPendingModalResult(self):
        return bool(self.__modal_result)

    def CloseByUser(self, *args):
        if self.closing:
            return
        if not self.killable or is_blocked('close', self.windowID):
            return
        self._LogWindowClosed()
        PlaySound(uiconst.SOUND_CLOSE)
        self.Close(setClosed=True)

    def _OnResize(self, *args, **kw):
        super(Window, self)._OnResize(*args)
        self.UpdateIntersectionBackground()
        if self.__ready:
            self.RegisterPositionAndSize()
        if self.OnResize_:
            self.OnResize_(self)

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        dirty = self._forceUpdateAlignment or self._alignmentDirty
        ret = super(Window, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        if dirty:
            for sceneCont in self.__scene_containers:
                if not sceneCont.destroyed:
                    sceneCont.UpdateViewPort()

        return ret

    def HideHeader(self):
        self.collapsible = False
        self.show_window_controls = False
        if self.sr.headerParent:
            self.sr.headerParent.state = uiconst.UI_HIDDEN

    def ShowHeader(self):
        self.collapsible = True
        self.show_window_controls = True
        if self.sr.headerParent:
            self.sr.headerParent.state = uiconst.UI_PICKCHILDREN

    def ShowBackground(self):
        self.ShowUnderlay()

    def HideBackground(self):
        self.HideUnderlay()

    def HideUnderlay(self):
        if self.sr.underlay:
            self.sr.underlay.state = uiconst.UI_HIDDEN

    def ShowUnderlay(self):
        if self.sr.underlay:
            self.sr.underlay.state = uiconst.UI_DISABLED

    def Blink(self):
        if self.state == uiconst.UI_HIDDEN and self.sr.tab and hasattr(self.sr.tab, 'Blink'):
            self.sr.tab.Blink(1)

    def GetMenu(self, *args):
        entries = []
        if self.killable:
            text = MenuLabel('/Carbon/UI/Common/Close')
            entry = MenuEntryData(text=text, func=self.CloseByUser)
            entries.append(entry)
        if not self.stacked and self.minimizable and not getattr(self, 'isModal', 0):
            if self.IsMinimized():
                text = MenuLabel('/Carbon/UI/Controls/Window/Maximize')
            else:
                text = MenuLabel('/Carbon/UI/Controls/Window/Minimize')
            entry = MenuEntryData(text=text, func=self.ToggleMinimize)
            entries.append(entry)
        from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataWithEntries
        return CreateMenuDataWithEntries(entries)

    def ShowLoad(self, doBlock = True):
        self.__hide_loading_indicator_requested = False
        if self.sr.loadingParent:
            if doBlock:
                self.sr.loadingParent.state = uiconst.UI_NORMAL
            else:
                self.sr.loadingParent.state = uiconst.UI_DISABLED
            if self.sr.loadingIndicator and hasattr(self.sr.loadingIndicator, 'Play'):
                if not (self.InStack() or self.GetAlign() != uiconst.RELATIVE):
                    self.sr.loadingIndicator.sr.hint = localization.GetByLabel('/Carbon/UI/Controls/Window/Loading')
                    self.sr.loadingIndicator.Play()
        if not self.closing and self.__hide_loading_indicator_requested:
            self.HideLoad()

    def HideLoad(self):
        if self.sr.loadingIndicator and hasattr(self.sr.loadingIndicator, 'Stop'):
            self.sr.loadingIndicator.Stop()
        if self.sr.loadingParent:
            self.sr.loadingParent.state = uiconst.UI_HIDDEN
        self.__hide_loading_indicator_requested = True

    def ShowModal(self):
        return self.ShowDialog(modal=True)

    def ShowDialog(self, modal = False, state = uiconst.UI_NORMAL, fillOpacity = uiconst.DEFAULT_MODAL_OPACITY, closeWhenClicked = False, sceneSaturation = uiconst.DEFAULT_MODAL_SCENE_SATURATION):
        self.isDialog = True
        self.isModal = modal
        self.state = uiconst.UI_HIDDEN
        if modal:
            self.minimizable = False
            if self.parent and not self.parent.destroyed and self.parent.name[:8] == 'l_modal_':
                self.parent.SetOrder(0)
            else:
                layer = self._create_modal_layer(name='l_modal_%s' % self.name, close_when_clicked=closeWhenClicked)
                self.SetParent(layer)
                self.sr.modalParent = layer
                self.ModalPosition()
            uicore.registry.AddModalWindow(self, fillOpacity=fillOpacity, sceneSaturation=sceneSaturation)
        self.__modal_result = uthread.Channel()
        self.state = state
        if modal:
            uicore.registry.SetFocus(self)
        self.HideLoad()
        ret = self.__modal_result.receive()
        return ret

    def _create_modal_layer(self, name, close_when_clicked = False):
        layer = Container(name=name, state=uiconst.UI_NORMAL, parent=uicore.layer.modal, idx=0)
        if close_when_clicked:
            layer.OnClick = self.CloseByUser
        return layer

    def ModalPosition(self):
        otherModal = uicore.registry.GetModalWindow()
        if self.__ShouldAdjustNewModal(otherModal):
            self.left = otherModal.left + 16
            self.top = otherModal.top + 16
            if self.left + self.width > uicore.desktop.width:
                self.left = 0
            if self.top + self.height > uicore.desktop.height:
                self.top = 0
        else:
            cameraOffset = self.__class__.GetDefaultLeftOffset(self.width, align=uiconst.CENTER, left=0)
            self.left = (uicore.desktop.width - self.width) / 2 + cameraOffset
            self.top = (uicore.desktop.height - self.height) / 2

    def __ShouldAdjustNewModal(self, otherModal):
        if not otherModal:
            return False
        if not getattr(otherModal, 'triggersModalAdjustment', True):
            return False
        if otherModal.state != uiconst.UI_NORMAL:
            return False
        if otherModal.parent.state != uiconst.UI_NORMAL:
            return False
        return True

    def ButtonResult(self, button, *args):
        if self.IsCurrentDialog():
            self.SetModalResult(button.btn_modalresult, 'ButtonResult')

    def DefineButtons(self, buttons, okLabel = None, okFunc = 'default', args = 'self', cancelLabel = None, cancelFunc = 'default', okModalResult = 'default', default = None):
        if okLabel is None:
            okLabel = localization.GetByLabel('UI/Common/Buttons/OK')
        if cancelLabel is None:
            cancelLabel = localization.GetByLabel('UI/Common/Buttons/Cancel')
        buttonHeight = 32
        if getattr(self.sr, 'bottom', None) is None:
            self.sr.bottom = self.FindChild('bottom')
            if not self.sr.bottom:
                self.sr.bottom = Container(name='bottom', parent=self.GetMainArea(), align=uiconst.TOBOTTOM, padTop=4, idx=0)
        if self.sr.bottom is None:
            return
        self.sr.bottom.Flush()
        if buttons is None:
            self.sr.bottom.state = uiconst.UI_HIDDEN
            return
        self.sr.bottom.height = buttonHeight
        if okModalResult == 'default':
            okModalResult = uiconst.ID_OK
        if okFunc == 'default':
            okFunc = self.ConfirmFunction
        if cancelFunc == 'default':
            cancelFunc = self.ButtonResult

        def create_ok_button():
            is_ok_default = okModalResult == default if default is not None else True
            return Button(name='ok_dialog_button', label=okLabel, func=okFunc, args=args, btn_modalresult=okModalResult, btn_default=is_ok_default, variant=ButtonVariant.PRIMARY if is_ok_default else ButtonVariant.NORMAL)

        def create_cancel_button():
            is_cancel_default = uiconst.ID_CANCEL == default if default is not None else False
            return Button(name='cancel_dialog_button', label=cancelLabel, func=cancelFunc, args=args, btn_modalresult=uiconst.ID_CANCEL, btn_default=is_cancel_default, btn_cancel=True, variant=ButtonVariant.PRIMARY if is_cancel_default else ButtonVariant.NORMAL)

        def create_close_button():
            is_close_default = uiconst.ID_CLOSE == default if default is not None else False
            return Button(name='close_dialog_button', label=localization.GetByLabel('UI/Common/Buttons/Close'), func=self.CloseByUser, args=args, btn_modalresult=uiconst.ID_CLOSE, btn_default=is_close_default, btn_cancel=True, variant=ButtonVariant.PRIMARY if is_close_default else ButtonVariant.NORMAL)

        def create_yes_button():
            is_yes_default = uiconst.ID_YES == default if default is not None else True
            return Button(name='yes_dialog_button', label=localization.GetByLabel('UI/Common/Buttons/Yes'), func=self.ButtonResult, args=args, btn_modalresult=uiconst.ID_YES, btn_default=is_yes_default, variant=ButtonVariant.PRIMARY if is_yes_default else ButtonVariant.NORMAL)

        def create_no_button():
            is_no_default = uiconst.ID_NO == default if default is not None else False
            return Button(name='no_dialog_button', label=localization.GetByLabel('UI/Common/Buttons/No'), func=self.ButtonResult, args=args, btn_modalresult=uiconst.ID_NO, btn_default=is_no_default, variant=ButtonVariant.PRIMARY if is_no_default else ButtonVariant.NORMAL)

        if isinstance(buttons, (types.ListType, types.TupleType)):
            button_data = []
            for btn in buttons:
                is_default = btn.id == default if default is not None else False
                button_data.append(Button(label=btn.label, func=self.ButtonResult, args=None, btn_modalresult=btn.id, btn_default=is_default, btn_cancel=btn.id == uiconst.ID_CANCEL, variant=ButtonVariant.PRIMARY if is_default else ButtonVariant.NORMAL))

        elif buttons == uiconst.OK:
            button_data = [create_ok_button()]
        elif buttons == uiconst.OKCANCEL:
            button_data = [create_ok_button(), create_cancel_button()]
        elif buttons == uiconst.OKCLOSE:
            button_data = [create_ok_button(), create_close_button()]
        elif buttons == uiconst.YESNO:
            button_data = [create_yes_button(), create_no_button()]
        elif buttons == uiconst.YESNOCANCEL:
            button_data = [create_yes_button(), create_no_button(), create_cancel_button()]
        elif buttons == uiconst.CLOSE:
            button_data = [create_close_button()]
        elif isinstance(okLabel, (types.ListType, types.TupleType)):
            button_data = []
            for index in xrange(len(okLabel)):
                label = okLabel[index]
                additionalArguments = {'Function': okFunc,
                 'Arguments': args,
                 'Cancel Label': cancelLabel,
                 'Cancel Function': cancelFunc,
                 'Modal Result': okModalResult,
                 'Default': default}
                for argName in additionalArguments:
                    if isinstance(additionalArguments[argName], (types.ListType, types.TupleType)) and len(additionalArguments[argName]) > index:
                        additionalArguments[argName] = additionalArguments[argName][index]

                is_default = additionalArguments['Modal Result'] == default if default is not None else additionalArguments['Default']
                button_data.append(Button(label=label, func=additionalArguments['Function'], args=additionalArguments['Arguments'], btn_modalresult=additionalArguments['Modal Result'], btn_default=is_default, btn_cancel=additionalArguments['Modal Result'] == uiconst.ID_CANCEL, variant=ButtonVariant.PRIMARY if is_default else ButtonVariant.NORMAL))

        else:
            button_data = [create_ok_button()]
        buttonGroup = ButtonGroup(parent=self.sr.bottom, align=uiconst.TOBOTTOM, buttons=button_data, button_size_mode=ButtonSizeMode.STRETCH)
        self.sr.bottom.height = max(buttonHeight, buttonGroup.height)
        self.sr.bottom.state = uiconst.UI_PICKCHILDREN

    def ConfirmFunction(self, button, *args):
        uicore.registry.Confirm(button)

    def SetScope(self, scope):
        self.scope = scope

    def SetModalResult(self, result, caller = None):
        if self.__modal_result:
            self._SetModalResult(result)
            self.Close()

    def _SetModalResult(self, result):
        if self.__modal_result:
            uicore.registry.RemoveModalWindow(self)
            self.__modal_result.send(result)
            self.__modal_result = None

    def MakeUnResizeable(self):
        self._resizeable = False
        self.Prepare_ScaleAreas_()
        self.MakeUnstackable()

    def MakeUnstackable(self):
        self.__stackable = False

    def MakeStackable(self):
        self.__stackable = True

    def IsResizeable(self):
        return self._resizeable and not self.IsLocked()

    def SetMinSize(self, size, refresh = 0):
        self.minsize = size
        if self.GetAlign() == uiconst.RELATIVE and not self.InStack():
            if not self.IsCollapsed():
                if self.height < self.minsize[1]:
                    self.height = self.minsize[1]
                if self.width < self.minsize[0]:
                    self.width = self.minsize[0]
                if refresh:
                    self.width, self.height = self.minsize
        if self.stacked:
            self.stack.SetMinWH()

    def SetMaxSize(self, size, refresh = 0):
        self.maxsize = size
        maxWidth, maxHeight = size
        if self.GetAlign() == uiconst.RELATIVE:
            if not self.IsCollapsed():
                if maxWidth is not None and self.width > maxWidth:
                    self.width = maxWidth
                if maxHeight is not None and self.height > maxHeight:
                    self.height = maxHeight
                if refresh:
                    if maxWidth is not None:
                        self.width = maxWidth
                    if maxHeight is not None:
                        self.height = maxHeight
        if self.stacked:
            self.stack.Check()

    def CheckMaxSize(self):
        maxWidth, maxHeight = self.maxsize
        if maxWidth and self.width > maxWidth:
            self.width = maxWidth
        if maxHeight and self.height > maxHeight:
            self.height = maxHeight

    def _SetCaptionText(self, caption):
        if localization.IsValidLabel(caption):
            self.__caption = localization.GetByLabel(caption)
        else:
            self.__caption = caption

    def LockHeight(self, height):
        self._fixedHeight = height
        if not self.InStack():
            self.height = height

    def UnlockHeight(self):
        self._fixedHeight = None

    def LockWidth(self, width):
        self._fixedWidth = width
        if not self.stacked:
            self.width = width

    def UnlockWidth(self):
        self._fixedWidth = None

    def UpdateIntersectionBackground(self):
        if not self.InStack():
            sm.GetService('window').UpdateIntersectionBackground()

    def Maximize(self, retainOrder = False, *args, **kwds):
        if self.closing or self._changing:
            return
        if is_blocked('restore', self.windowID):
            return
        self._changing = True
        if self.stacked:
            self._SetMaximized()
            self.stack.ShowWnd(self)
            self.stack.Maximize()
            self._changing = False
            return
        self.OnStartMaximize_(self)
        if self.IsCollapsed():
            self.Expand(0)
        wasMinimized = self.IsMinimized()
        if not retainOrder:
            uicore.registry.SetFocus(self)
        self._SetMaximized()
        self.state = uiconst.UI_NORMAL
        self.InitializeSize()
        self.InitializeStatesAndPosition()
        kick = [ w for w in self.Find('trinity.Tr2Sprite2dContainer') + self.Find('trinity.Tr2Sprite2d') if hasattr(w, '_OnResize') ]
        for each in kick:
            if hasattr(each, '_OnResize'):
                each._OnResize()

        self.OnEndMaximize_(self)
        self._changing = False
        self._NotifyOfMaximized(wasMinimized)
        self.UpdateIntersectionBackground()

    def _NotifyOfMaximized(self, wasMinimized):
        sm.ScatterEvent('OnWindowMaximized', self, wasMinimized)

    def Minimize(self, animate = True):
        if not self.minimizable:
            return
        if self.stacked:
            return self.stack.Minimize(animate=animate)
        PlaySound(uiconst.SOUND_COLLAPSE)
        uicore.registry.SetFocus(None)
        self._Minimize(animate=animate)
        self.UpdateIntersectionBackground()

    def _Minimize(self, animate = True):
        if self.closing or self.IsMinimized() or self._changing:
            return
        self.OnStartMinimize_(self)
        self._changing = True
        self._SetMinimized()
        if animate:
            self._AnimateMinimize()
        self.state = uiconst.UI_HIDDEN
        self.OnEndMinimize_(self)
        self._changing = False
        sm.ScatterEvent('OnWindowMinimized', self)

    def _AnimateMinimize(self):
        x, y = sm.GetService('neocom').GetMinimizeToPos(self)
        x = float(x) / uicore.desktop.width
        y = float(y) / uicore.desktop.height
        t = Transform(parent=uicore.layer.main, state=uiconst.UI_DISABLED, align=uiconst.TOALL, scalingCenter=(x, y), idx=0)
        wasCacheContent = self.cacheContents
        self.cacheContents = False
        self.SetParent(t)
        animations.Tr2DFlipOut(t, duration=0.3)
        animations.FadeOut(t, duration=0.25, sleep=True)
        self.SetParent(uicore.layer.main)
        self.cacheContents = wasCacheContent
        t.Close()

    def IsMinimized(self):
        if self.stacked:
            return bool(self.stack.IsMinimized())
        return bool(self.GetRegisteredState('minimized'))

    def _SetMinimized(self):
        self.RegisterState('minimized', True)

    def _SetMaximized(self):
        self.RegisterState('minimized', False)

    def _SetCollapsed(self, isCollapsed):
        self.RegisterState('collapsed', isCollapsed)
        self.__collapsed = bool(isCollapsed)
        self._emit_on_collapsed_changed()

    def _SetOpen(self, isOpen):
        self.RegisterState('open', isOpen)

    def _SetHovered(self, isHovered):
        wasHovered = self.__hovered
        self.__hovered = isHovered
        if not wasHovered and isHovered:
            sm.ScatterEvent('OnWindowMouseEnter', self.windowID)
        elif wasHovered and not isHovered:
            sm.ScatterEvent('OnWindowMouseExit', self.windowID)

    def IsHovered(self):
        return self.__hovered

    def OnMouseEnter(self, *args):
        self._SetHovered(isHovered=True)

    def OnMouseExit(self, *args):
        self._SetHovered(isHovered=False)

    def OnMouseDown(self, btnNum, *args):
        if btnNum != uiconst.MOUSELEFT:
            return
        self.OnMouseDown_(self)
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)
        if self.IsLocked():
            self.DisableDrag()
        else:
            self.EnableDrag()
        self.SetOrder(0)

    def GetDragClipRects(self, shiftGroup, ctrlGroup):
        ml, mt, mw, mh = self.GetAbsolute()
        sl, st, sw, sh = self.GetGroupAbsolute(shiftGroup)
        cl, ct, cw, ch = self.GetGroupAbsolute(ctrlGroup)
        pl, pt, pw, ph = self.parent.GetAbsolute()
        x, y = self.dragMousePosition
        return ((0,
          0,
          pw,
          ph - (mt + self.GetCollapsedHeight() - y) + 1), (x - sl,
          y - st,
          pw - (sl + sw - x) + 1,
          ph - (st + sh - y) + 1), (x - cl,
          y - ct,
          pw - (cl + cw - x) + 1,
          ph - (ct + ch - y) + 1))

    def _BeginDrag(self):
        self._dragging = True
        ctrlDragWindows = self.FindConnectingWindows('bottom', includeLocked=False)
        shiftDragWindows = self.FindConnectingWindows(includeLocked=False)
        self.PrepareWindowsForMove(shiftDragWindows)
        while not self.closing and self.IsBeingDragged():
            if uicore.uilib.mouseTravel > 1:
                break
            blue.pyos.synchro.Yield()

        if self.closing or not self.IsBeingDragged() or self.__drag_started:
            return
        if ctrlDragWindows is None:
            ctrlDragWindows = self.FindConnectingWindows('bottom', includeLocked=False)
        if shiftDragWindows is None:
            shiftDragWindows = self.FindConnectingWindows(includeLocked=False)
            self.PrepareWindowsForMove(shiftDragWindows)
        snapGrid = None
        snapGroup = None
        snapIndicator = self.GetSnapIndicator()
        allGrid, myGrid, shiftGrid, ctrlGrid = self.CreateSnapGrid(shiftDragWindows, ctrlDragWindows)
        myRect, shiftRect, ctrlRect = self.GetDragClipRects(shiftDragWindows, ctrlDragWindows)
        initMouseX, initMouseY = self.dragMousePosition
        self.__drag_started = True
        while not self.closing and self.IsBeingDragged() and uicore.uilib.leftbtn and self.GetAlign() == uiconst.RELATIVE:
            self.state = uiconst.UI_DISABLED
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
            self.left = uicore.uilib.x - initMouseX + self.preDragAbs[0]
            self.top = uicore.uilib.y - initMouseY + self.preDragAbs[1]
            for each in shiftDragWindows:
                if each is self:
                    continue
                pl, pt, pw, ph = each.preDragAbs
                if shift or ctrl and each in ctrlDragWindows:
                    each.left = uicore.uilib.x - initMouseX + pl
                    each.top = uicore.uilib.y - initMouseY + pt
                else:
                    each.left = pl
                    each.top = pt

            self.SetOrder(0)
            self.FindWindowToStackTo()
            if shift:
                snapGrid = shiftGrid
                snapGroup = shiftDragWindows
                cursorRect = shiftRect
            elif ctrl:
                cursorRect = ctrlRect
                snapGrid = ctrlGrid
                snapGroup = ctrlDragWindows
            else:
                snapGrid = myGrid
                snapGroup = [self]
                cursorRect = myRect
            uicore.uilib.ClipCursor(*cursorRect)
            self.ShowSnapEdges_Moving(snapGroup, snapGrid, snapIndicator=snapIndicator)
            self.OnDragTick()
            blue.pyos.synchro.Yield()

        if not self.InStack() and self.IsStackable():
            trystackto = self.FindWindowToStackTo()
            self.ClearStackIndication()
            if trystackto:
                if trystackto.stacked:
                    trystackto.stack.CheckStackWith(self)
                else:
                    trystackto.CheckStackWith(self)
        uicore.uilib.UnclipCursor()
        if self.closing:
            return
        if not self.InStack() and snapGrid and snapGroup:
            self.ShowSnapEdges_Moving(snapGroup, snapGrid, doSnap=True)
        self.CleanupParent('snapIndicator')
        self.ClearStackIndication()
        if self.InStack():
            self.state = uiconst.UI_PICKCHILDREN
        else:
            self.state = uiconst.UI_NORMAL
        self.AdjustWindowPositionToFitScreen()
        if not self.closing:
            self.__drag_started = False

    def AdjustWindowPositionToFitScreen(self):
        if self.stacked:
            return
        maxLeftAllowed = uicore.desktop.width - self.WINDOW_NEVER_OFFSCREEN_BUFFER
        if self.left > maxLeftAllowed:
            self.left = maxLeftAllowed
        minLeftAllowed = self.WINDOW_NEVER_OFFSCREEN_BUFFER - self.width
        if self.left < minLeftAllowed:
            self.left = minLeftAllowed
        maxTopAllowed = uicore.desktop.height - self.WINDOW_NEVER_OFFSCREEN_BUFFER
        if self.top > maxTopAllowed:
            self.top = maxTopAllowed
        minTopAllowed = self.WINDOW_NEVER_OFFSCREEN_BUFFER - self.height
        if self.top < minTopAllowed:
            self.top = minTopAllowed

    def CreateSnapGrid(self, shiftGroup = None, ctrlGroup = None):
        leftOffset, rightOffset = self.GetSideOffset()
        allWnds = find_sibling_windows(self)
        desk = uicore.desktop
        hAxes = [0,
         desk.height,
         16,
         desk.height - 16]
        vAxes = [0,
         leftOffset,
         leftOffset + 16,
         desk.width - rightOffset,
         desk.width - 16 - rightOffset]
        if leftOffset < WINDOW_SNAP_DISTANCE:
            vAxes.pop(0)
        hAxesWithOutMe = hAxes[:]
        vAxesWithOutMe = vAxes[:]
        hAxesWithOutShiftGroup = hAxes[:]
        vAxesWithOutShiftGroup = vAxes[:]
        hAxesWithOutCtrlGroup = hAxes[:]
        vAxesWithOutCtrlGroup = vAxes[:]
        hLists = [hAxes,
         hAxesWithOutMe,
         hAxesWithOutShiftGroup,
         hAxesWithOutCtrlGroup]
        vLists = [vAxes,
         vAxesWithOutMe,
         vAxesWithOutShiftGroup,
         vAxesWithOutCtrlGroup]
        for wnd in allWnds:
            l, t, w, h = wnd.GetAbsolute()
            self.AddtoAxeList(wnd, vLists, l, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, vLists, l + w, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t, shiftGroup, ctrlGroup)
            self.AddtoAxeList(wnd, hLists, t + h, shiftGroup, ctrlGroup)

        self.__active_snap_grid = [(hAxes, vAxes),
         (hAxesWithOutMe, vAxesWithOutMe),
         (hAxesWithOutShiftGroup, vAxesWithOutShiftGroup),
         (hAxesWithOutCtrlGroup, vAxesWithOutCtrlGroup)]
        return self.__active_snap_grid

    def AddtoAxeList(self, wnd, lists, val, shiftgroup, ctrlgroup):
        all, minusMe, minusShiftGroup, minusCtrlGroup = lists
        if val not in all:
            all.append(val)
        if wnd != self and val not in minusMe:
            minusMe.append(val)
        if shiftgroup and wnd not in shiftgroup and val not in minusShiftGroup:
            minusShiftGroup.append(val)
        if ctrlgroup and wnd not in ctrlgroup and val not in minusCtrlGroup:
            minusCtrlGroup.append(val)

    def ShowSnapEdges_Scaling(self, snapGrid, showSnap = True, doSnap = False):
        if not self.__scale_sides:
            return
        horizontal, vertical = snapGrid
        snapdist = WINDOW_SNAP_DISTANCE
        match = {}
        for side in self.__scale_sides:
            wnd = self
            minLDist = 1000
            minRDist = 1000
            minTDist = 1000
            minBDist = 1000
            wl, wt, ww, wh = wnd.GetAbsolute()
            if showSnap:
                snapIndicator = wnd.GetSnapIndicator()
                snapIndicator.left = wl
                snapIndicator.top = wt
                snapIndicator.width = ww
                snapIndicator.height = wh
                for each in snapIndicator.children:
                    each.state = uiconst.UI_HIDDEN

            else:
                wnd.HideSnapIndicator()
            if side in ('top', 'bottom'):
                for hAxe in horizontal:
                    tDist = abs(hAxe - wt)
                    bDist = abs(hAxe - (wt + wh))
                    if side == 'top' and tDist <= snapdist and tDist < minTDist:
                        minTDist = tDist
                        match[side, wnd] = hAxe
                    elif side == 'bottom' and bDist <= snapdist and bDist < minBDist:
                        minBDist = bDist
                        match[side, wnd] = hAxe

            elif side in ('left', 'right'):
                for vAxe in vertical:
                    lDist = abs(vAxe - wl)
                    rDist = abs(vAxe - (wl + ww))
                    if side == 'left' and lDist <= snapdist and lDist < minLDist:
                        minLDist = lDist
                        match[side, wnd] = vAxe
                    elif side == 'right' and rDist <= snapdist and rDist < minRDist:
                        minRDist = rDist
                        match[side, wnd] = vAxe

        if showSnap or doSnap:
            checkMultipleSideSnap = {}
            for side, wnd in match.iterkeys():
                if wnd not in checkMultipleSideSnap:
                    checkMultipleSideSnap[wnd] = []
                snapValue = match[side, wnd]
                wl, wt, ww, wh = wnd.GetAbsolute()
                minH = wnd.GetMinHeight()
                snapIndicator = wnd.GetSnapIndicator()
                snapIndicator.state = uiconst.UI_DISABLED
                snapIndicator.SetOrder(1)
                if side == 'left':
                    if doSnap:
                        wnd.left = snapValue
                        if wnd.IsResizeable():
                            wnd.width = wl - snapValue + ww
                    if showSnap:
                        snapIndicator.left = snapValue - 2
                        snapIndicator.width = wl - snapValue + ww + 4
                        snapIndicator.GetChild('sLeft').state = uiconst.UI_DISABLED
                if side == 'right':
                    if doSnap:
                        if wnd.IsResizeable():
                            wnd.width = snapValue - wl
                    if showSnap:
                        snapIndicator.width = snapValue - wl + 4
                        snapIndicator.GetChild('sRight').state = uiconst.UI_DISABLED
                if side == 'top':
                    if doSnap:
                        wnd.top = snapValue
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or max(minH, wt - snapValue + wh)
                    if showSnap:
                        snapIndicator.top = snapValue - 2
                        snapIndicator.height = wt - snapValue + wh + 4
                        snapIndicator.GetChild('sTop').state = uiconst.UI_DISABLED
                if side == 'bottom':
                    if doSnap:
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or max(minH, snapValue - wt)
                    if showSnap:
                        snapIndicator.height = snapValue - wt + 4
                        snapIndicator.GetChild('sBottom').state = uiconst.UI_DISABLED
                checkMultipleSideSnap[wnd].append(side)

    def SetActive(self, *args):
        if self.stacked:
            self.stack.SetActive()
        self.ActivateUnderlay()
        if self.display:
            self.SetNotBlinking()
        self.__active = True
        self.Prepare_ScaleAreas_()
        self.OnSetActive_(self)
        self.OnWindowAboveSetActive()
        if not self.is_stack:
            self._LogWindowEventFocused()
            self.__focused_at_timestamp = gametime.GetWallclockTime()

    def OnSetInactive(self, *args):
        if self.stacked:
            self.stack.OnSetInactive()
        self.DeactivateUnderlay()
        self.__active = False
        self.Prepare_ScaleAreas_()
        self.OnWindowAboveSetInactive()
        if not self.is_stack:
            self._LogWindowUnfocused()

    def ActivateUnderlay(self):
        if self.sr.underlay:
            self.sr.underlay.AnimEntry()

    def DeactivateUnderlay(self):
        if self.sr.underlay:
            self.sr.underlay.AnimExit()

    def HideSnapIndicator(self):
        snapIndicator = self.parent.FindChild('snapIndicator')
        if snapIndicator is not None:
            snapIndicator.Close()

    def GetSnapIndicator(self):
        snapIndicator = self.parent.FindChild('snapIndicator')
        if snapIndicator is None:
            snapIndicator = Container(parent=self.parent, color=(0.0, 1.0, 0.0, 1.0), align=uiconst.TOPLEFT, name='snapIndicator')
            for label, align, iconPath in [('sLeftTop', uiconst.TOPLEFT, 'res:/UI/Texture/Icons/1_16_1.png'),
             ('sRightTop', uiconst.TOPRIGHT, 'res:/UI/Texture/Icons/1_16_3.png'),
             ('sRightBottom', uiconst.BOTTOMRIGHT, 'res:/UI/Texture/Icons/1_16_35.png'),
             ('sLeftBottom', uiconst.BOTTOMLEFT, 'res:/UI/Texture/Icons/1_16_33.png'),
             ('sLeft', uiconst.CENTERLEFT, 'res:/UI/Texture/Icons/1_16_17.png'),
             ('sTop', uiconst.CENTERTOP, 'res:/UI/Texture/Icons/1_16_2.png'),
             ('sRight', uiconst.CENTERRIGHT, 'res:/UI/Texture/Icons/1_16_19.png'),
             ('sBottom', uiconst.CENTERBOTTOM, 'res:/UI/Texture/Icons/1_16_34.png')]:
                Sprite(parent=snapIndicator, name=label, align=align, state=uiconst.UI_HIDDEN, texturePath=iconPath, width=16, height=16)

        return snapIndicator

    def GetStackClass(self):
        from carbonui.window.stack import WindowStack
        return WindowStack

    def IndicateStackable(self, wnd = None):
        if wnd is None:
            if self.sr.snapIndicator:
                animations.FadeOut(self.sr.snapIndicator, duration=0.2, callback=self.sr.snapIndicator.Close)
                self.sr.snapIndicator = None
            return
        if not wnd.IsStackable() or not self.IsStackable():
            return
        if self.sr.snapIndicator is None:
            margin_left, margin_top, margin_right, _ = wnd.GetWindowBorderPadding()
            border_left, border_top, border_right, _ = wnd.GetWindowBorderSize()
            padding = (margin_left + border_left,
             margin_top + border_top,
             margin_right + border_right,
             0)
            self.sr.snapIndicator = Fill(align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, color=eveThemeColor.THEME_ACCENT, opacity=0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, height=wnd.header_height, padding=padding, idx=0)
            animations.FadeTo(self.sr.snapIndicator, startVal=0.0, endVal=0.4, duration=0.2)
        si = self.sr.snapIndicator
        si.state = uiconst.UI_DISABLED
        if si.parent != wnd:
            Transplant(si, wnd, idx=0)
        else:
            si.SetOrder(0)

    def ClearStackIndication(self):
        self.IndicateStackable(None)

    def ShowSnapEdges_Moving(self, snapGroup, snapGrid, snapIndicator = None, doSnap = False):
        if snapGrid is None:
            return
        l, t, w, h = gl, gt, gw, gh = self.GetGroupAbsolute(snapGroup)
        snapdist = WINDOW_SNAP_DISTANCE
        lSnap = None
        rSnap = None
        tSnap = None
        bSnap = None
        minLDist = 1000
        minRDist = 1000
        minTDist = 1000
        minBDist = 1000
        horizontal, vertical = snapGrid
        for hAxe in horizontal:
            tDist = abs(hAxe - t)
            bDist = abs(hAxe - (t + h))
            if tDist <= snapdist and tDist < minTDist:
                tSnap = hAxe
                minTDist = tDist
            elif bDist <= snapdist and bDist < minBDist:
                bSnap = hAxe
                minBDist = bDist

        for vAxe in vertical:
            lDist = abs(vAxe - l)
            rDist = abs(vAxe - (l + w))
            if lDist <= snapdist and lDist < minLDist:
                lSnap = vAxe
                minLDist = lDist
            elif rDist <= snapdist and rDist < minRDist:
                rSnap = vAxe
                minRDist = rDist

        if tSnap is not None:
            t = tSnap
            if bSnap is not None:
                h = bSnap - tSnap
        elif bSnap is not None:
            t = bSnap - h
        if lSnap is not None:
            l = lSnap
            if rSnap is not None:
                w = rSnap - lSnap
        elif rSnap is not None:
            l = rSnap - w
        if snapIndicator and not snapIndicator.destroyed:
            snapIndicator.width = w + 6
            snapIndicator.height = h + 6
            snapIndicator.left = l - 2
            snapIndicator.top = t - 2
            for each in snapIndicator.children:
                each.state = uiconst.UI_HIDDEN

            snapIndicator.SetOrder(1)
            if lSnap is not None:
                snapIndicator.GetChild('sLeft').state = uiconst.UI_DISABLED
            if rSnap is not None:
                snapIndicator.GetChild('sRight').state = uiconst.UI_DISABLED
            if tSnap is not None:
                snapIndicator.GetChild('sTop').state = uiconst.UI_DISABLED
            if bSnap is not None:
                snapIndicator.GetChild('sBottom').state = uiconst.UI_DISABLED
            snapIndicator.state = uiconst.UI_DISABLED
        leftOffset, rightOffset = self.GetSideOffset()
        cornerSnap = ''
        if tSnap in (0, 16):
            cornerSnap = 'top'
        elif bSnap in (uicore.desktop.height, uicore.desktop.height - 16):
            cornerSnap = 'bottom'
        if cornerSnap:
            if lSnap in (leftOffset, leftOffset + 16):
                cornerSnap = cornerSnap + 'left'
            elif rSnap in (uicore.desktop.width, uicore.desktop.width - 16):
                cornerSnap = cornerSnap + 'right'
        if doSnap:
            scaleX = float(w) / gw
            scaleY = float(h) / gh
            diffX = l - gl
            diffY = t - gt
            for wnd in snapGroup:
                wnd.left += diffX
                wnd.top += diffY
                if wnd.IsResizeable():
                    wnd.width = int(wnd.width * scaleX)
                    wnd.height = int(wnd.height * scaleY)

            for wnd in snapGroup:
                if wnd._fixedHeight and wnd.height != wnd._fixedHeight:
                    diff = wnd.height - wnd._fixedHeight
                    bottomAlignedWindows = wnd.FindConnectingWindows('bottom')
                    wnd.height -= diff
                    for each in bottomAlignedWindows[1:]:
                        each.top -= diff

                if wnd._fixedWidth and wnd.width != wnd._fixedWidth:
                    diff = wnd.width - wnd._fixedWidth
                    rightAlignedWindows = wnd.FindConnectingWindows('right')
                    wnd.width -= diff
                    for each in rightAlignedWindows[1:]:
                        each.left -= diff

    def FindWindowToStackTo(self):
        over = uicore.uilib.mouseOver
        if over is self:
            return None
        over = GetWindowAbove(over)
        if not isinstance(over, Window) or not over.IsStackable():
            self.ClearStackIndication()
            return None
        if over.stacked:
            over = over.stack
        l, t, w, h = over.GetAbsolute()
        sl, st, sw, sh = self.GetAbsolute()
        if (l < sl < l + w or l < sl + sw < l + w) and t <= st <= t + over.header_height:
            self.IndicateStackable(over)
            return over
        self.ClearStackIndication()

    def IsStackable(self):
        if self.__stackable and not self.IsLocked():
            shiftonly = settings.user.ui.Get('stackwndsonshift', 0)
            if shiftonly:
                return uicore.uilib.Key(uiconst.VK_SHIFT)
            return 1
        return 0

    def OnMouseUp(self, *args):
        self.ClearStackIndication()
        self.CleanupParent('snapIndicator')
        uicore.uilib.UnclipCursor()
        self._dragging = False
        self._dragEnabled = False
        self.__drag_started = False
        self.RegisterPositionAndSize()

    def OnDblClick(self, *args):
        if getattr(self, 'isDialog', False):
            return
        if uicore.uilib.y - self.top < self.header_height:
            self.ToggleCollapse()

    def ToggleCollapse(self):
        if not self.collapsible:
            return
        self.ResetToggleState()
        if self.collapsed:
            self.Expand()
            PlaySound(uiconst.SOUND_EXPAND)
        else:
            self.Collapse()
            PlaySound(uiconst.SOUND_COLLAPSE)

    def ToggleMinimize(self):
        if self.IsMinimized():
            self.Maximize()
        elif self.minimizable:
            parChildren = self.GetParentLayer().children
            if self.InStack():
                if parChildren and parChildren[0] != self.stack:
                    uicore.registry.SetFocus(self)
                    self.stack.ShowWnd(self)
                elif self.stack.GetActiveWindow() != self:
                    self.stack.ShowWnd(self)
                else:
                    self.Minimize()
            elif parChildren and parChildren[0] != self:
                uicore.registry.SetFocus(self)
            else:
                self.Minimize()

    def GetParentLayer(self):
        if self.InStack():
            return self.stack.parent
        else:
            return self.parent

    def ResetToggleState(self):
        uicore.registry.ResetToggleStateForWnd(getattr(self, 'windowID', None))

    def GetCollapsedHeight(self):
        _, margin_top, _, margin_bottom = self.GetWindowBorderPadding()
        _, border_top, _, border_bottom = self.GetWindowBorderSize()
        return margin_top + border_top + WindowHeaderBase.COLLAPSED_HEIGHT + border_bottom + margin_bottom

    def Collapse(self, forceCollapse = False, checkchain = 1, *args):
        if not self.collapsible or not forceCollapse and self.collapsed:
            return
        if self.sr.bottom:
            self.sr.bottom.state = uiconst.UI_HIDDEN
        if self.sr.main:
            self.sr.main.state = uiconst.UI_HIDDEN
        if not self.parent or not self.collapsible or self.collapsed:
            return
        if self.stacked:
            return self.stack.Collapse()
        bottomAlignedWindows = self.FindConnectingWindows('bottom')
        allAlignedWindows = self.FindConnectingWindows()
        gl, gt, gw, gh = self.GetGroupAbsolute(allAlignedWindows)
        ch = self.GetCollapsedHeight()
        heightDiff = self.height - ch
        self._SetCollapsed(True)
        self.LockHeight(ch)
        alignedToBottom = False
        alignedToTop = False
        pl, pt, pw, ph = self.parent.GetAbsolute()
        if gt in (0, 16):
            alignedToTop = True
        elif gt + gh in (ph, ph - 16):
            alignedToBottom = True
        if alignedToBottom:
            topAlignedWindows = self.FindConnectingWindows('top')
            for wnd in topAlignedWindows:
                wnd.top += heightDiff

        else:
            for wnd in bottomAlignedWindows:
                if wnd == self:
                    continue
                wnd.top -= heightDiff

        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            affected = allAlignedWindows
            for each in affected:
                if each != self:
                    each.Collapse()

        self.OnCollapsed(self)
        self.Prepare_ScaleAreas_()

    def Expand(self, *args):
        if not self.parent or not self.IsCollapsed():
            return
        if self.stacked:
            return self.stack.Expand(*args)
        self.UnlockHeight()
        bottomAlignedWindows = self.FindConnectingWindows('bottom')
        gl, gt, gw, gh = self.GetGroupAbsolute(bottomAlignedWindows)
        pl, pt, pw, ph = self.parent.GetAbsolute()
        alignedToBottom = False
        if gt + gh in (ph, ph - 16):
            alignedToBottom = True
        left, top, width, height, dw, dh = self.GetRegisteredPositionAndSize()
        height = max(height, self.GetMinHeight())
        heightDiff = height - self.height
        self._SetCollapsed(False)
        self.height = height
        if alignedToBottom:
            topAlignedWindows = self.FindConnectingWindows('top')
            for wnd in topAlignedWindows:
                wnd.top = max(0, wnd.top - heightDiff)

        else:
            for wnd in bottomAlignedWindows:
                if wnd == self:
                    continue
                wnd.top = min(wnd.top + heightDiff, uicore.desktop.height - wnd.height)

        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            affected = self.FindConnectingWindows()
            for each in affected:
                if each != self:
                    each.Expand()

        self.OnExpanded(self)
        self.ValidateWindows()
        self.Prepare_ScaleAreas_()
        if self.sr.bottom:
            self.sr.bottom.state = uiconst.UI_PICKCHILDREN
        if self.sr.main:
            self.sr.main.state = uiconst.UI_PICKCHILDREN

    def OnCompactModeEnabled(self):
        pass

    def OnCompactModeDisabled(self):
        pass

    def ValidateWindows(self):
        d = uicore.desktop
        all = uicore.registry.GetValidWindows(getModals=1, floatingOnly=True)
        for wnd in all:
            if wnd.GetAlign() != uiconst.RELATIVE:
                continue
            wnd.left = max(-wnd.width + 64, min(d.width - 64, wnd.left))
            wnd.top = max(0, min(d.height - wnd.GetCollapsedHeight(), wnd.top))

    def CheckStackWith(self, dropWnd):
        if not self.IsStackable():
            return
        if self.sr.modalParent is not None or dropWnd.sr.modalParent is not None or dropWnd == self:
            return
        if self.state == uiconst.UI_HIDDEN:
            return
        if dropWnd.closing:
            return
        wnds = [(self, 0)]
        kill = []
        from carbonui.window.stack import WindowStack
        if isinstance(dropWnd, WindowStack):
            for wnd in dropWnd.GetWindows():
                wnds.append((wnd, wnd.state == uiconst.UI_NORMAL))

            kill.append(dropWnd)
        else:
            wnds.append((dropWnd, 1))
        self._ConstructStack(wnds, kill)

    def CheckWndPos(self, i = 0):
        if self.parent is None or self.parent.destroyed or i == 10:
            return
        if self.locked:
            return
        for each in self.parent.children:
            if each != self and each.state == uiconst.UI_NORMAL:
                if each.left == self.left and each.top == self.top:
                    self.left = self.left + POSOVERLAPSHIFT
                    self.top = self.top + POSOVERLAPSHIFT
                    if self.left + self.width > uicore.desktop.width:
                        self.left = uicore.desktop.width - self.width
                    if self.top + self.height > uicore.desktop.height:
                        self.top = uicore.desktop.height - self.height
                    self.CheckWndPos(i + 1)
                    break

    def _ConstructStack(self, wnds, kill, group = None, groupidx = None):
        stack = uicore.registry.GetStack(str(uthread.uniqueId()), self.GetStackClass())
        if not stack or stack.closing:
            return
        for _wnd in wnds:
            wnd, show = _wnd
            stack.InsertWnd(wnd, 1, show)

        for each in kill:
            if each is not None and not each.destroyed:
                each.Close()

        uicore.registry.SetFocus(stack)

    def SetHeight(self, height):
        if self.GetAlign() == uiconst.RELATIVE and height != self.height:
            self.height = height

    def SetHeight_PushOrPullWindowsBelow(self, newHeight):
        if self.GetAlign() == uiconst.RELATIVE and newHeight != self.height:
            bottomAlignedWindows = self.FindConnectingWindows('bottom')
            heightDiff = newHeight - self.height
            self.height = newHeight
            for wnd in bottomAlignedWindows:
                if wnd == self:
                    continue
                wnd.top += heightDiff

    def GetMinWidth(self):
        minWidth = self._GetMinWidth()
        if self._fixedWidth:
            return min(self._fixedWidth, minWidth)
        w, h = self.GetMinSize()
        return max(w, minWidth)

    def _GetMinWidth(self):
        return self.minsize[0]

    def GetMinHeight(self):
        if self._fixedHeight:
            return min(self._fixedHeight, self._GetMinHeight())
        w, h = self.GetMinSize()
        return max(h, self.minsize[1])

    def _GetMinHeight(self):
        return self.minsize[1]

    def GetMaxWidth(self):
        if self._fixedWidth:
            return self._fixedWidth
        return self.maxsize[0] or sys.maxint

    def GetMaxHeight(self):
        if self._fixedHeight:
            return self._fixedHeight
        return self.maxsize[1] or sys.maxint

    def FindConnectingWindows(self, fromSide = None, wnds = None, validWnds = None, getParallelSides = 0, fullSideOnly = 0, includeLocked = True):
        if validWnds is None:
            validWnds = find_sibling_windows(self)
            validWnds.insert(0, self)
        l, t, w, h = self.GetAbsolute()
        fromWndCorners = [(l, t),
         (l + w, t),
         (l + w, t + h),
         (l, t + h)]
        if fromSide == 'left':
            validCornerPairs = [(3, 2), (0, 1)]
            if getParallelSides:
                validCornerPairs += [(3, 0), (0, 3)]
        elif fromSide == 'right':
            validCornerPairs = [(1, 0), (2, 3)]
            if getParallelSides:
                validCornerPairs += [(1, 2), (2, 1)]
        elif fromSide == 'top':
            validCornerPairs = [(0, 3), (1, 2)]
            if getParallelSides:
                validCornerPairs += [(0, 1), (1, 0)]
        elif fromSide == 'bottom':
            validCornerPairs = [(2, 1), (3, 0)]
            if getParallelSides:
                validCornerPairs += [(3, 2), (2, 3)]
        else:
            validCornerPairs = [(3, 2),
             (0, 1),
             (1, 0),
             (2, 3),
             (0, 3),
             (1, 2),
             (2, 1),
             (3, 0)]
        wnds = wnds or []
        if self not in wnds:
            wnds.append(self)
        for wnd in validWnds:
            if wnd in wnds:
                continue
            wl, wt, ww, wh = wnd.GetAbsolute()
            wndCorners = ((wl, wt),
             (wl + ww, wt),
             (wl + ww, wt + wh),
             (wl, wt + wh))
            m = 0
            for c1, c2 in validCornerPairs:
                c1Pos = fromWndCorners[c1]
                c2Pos = wndCorners[c2]
                if c1Pos == c2Pos:
                    if not fullSideOnly or m == 1:
                        if getParallelSides:
                            wnd.FindConnectingWindows(None, wnds, validWnds, getParallelSides, fullSideOnly)
                        else:
                            wnd.FindConnectingWindows(fromSide, wnds, validWnds, getParallelSides, fullSideOnly)
                        break
                    m += 1

        if not includeLocked:
            wnds = [ wnd for wnd in wnds if not wnd.IsLocked() ]
        return wnds

    def PrepareWindowsForMove(self, wnds):
        for each in wnds:
            each.preDragAbs = each.GetAbsolute()
            each.preDragCursorPos = (uicore.uilib.x, uicore.uilib.y)
            each.SetOrder(0)

    def CleanupParent(self, what):
        for each in self.parent.children[:]:
            if each.name == what:
                each.Close()

    def FindMinMaxScaling(self, sides):
        scaleH, scaleV, scaleAbove, followL, followR, followT, followB, all = self.sortedScaleWindows
        pl, pt, pw, ph = self.parent.GetAbsolute()
        myMinX = minX = 0
        myMaxX = maxX = pw
        myMinY = minY = 0
        myMaxY = maxY = ph
        for wnd in scaleH + [self]:
            spdl, spdt, spdw, spdh = wnd.preDragAbs
            wndMinWidth = wnd.GetMinWidth()
            wndMaxWidth = wnd.GetMaxWidth()
            if 'left' in sides:
                minX = max(minX, spdl + spdw - wndMaxWidth)
                maxX = min(maxX, spdl + spdw - wndMinWidth)
            elif 'right' in sides:
                minX = max(minX, spdl + wndMinWidth)
                maxX = min(maxX, spdl + wndMaxWidth)

        for wnd in scaleV + [self]:
            spdl, spdt, spdw, spdh = wnd.preDragAbs
            wndMinHeight = wnd.GetMinHeight()
            wndMaxHeight = wnd.GetMaxHeight()
            if 'top' in sides:
                minY = max(minY, spdt + spdh - wndMaxHeight)
                maxY = min(maxY, spdt + spdh - wndMinHeight)
            elif 'bottom' in sides:
                minY = max(minY, spdt + wndMinHeight)
                maxY = min(maxY, spdt + wndMaxHeight)

        for wnd in scaleAbove:
            spdl, spdt, spdw, spdh = wnd.preDragAbs
            wndMinHeight = wnd.GetMinHeight()
            wndMaxHeight = wnd.GetMaxHeight()
            minY = max(minY, spdt + wndMinHeight)
            maxY = min(maxY, spdt + wndMaxHeight)

        spdl, spdt, spdw, spdh = self.preDragAbs
        myMinWidth = self.GetMinWidth()
        myMinHeight = self.GetMinHeight()
        myMaxWidth = self.GetMaxWidth()
        myMaxHeight = self.GetMaxHeight()
        if 'top' in sides:
            myMaxY = min(myMaxY, spdt + spdh - myMinHeight)
            myMinY = max(myMinY, spdt + spdh - myMaxHeight)
            for wnd in followT:
                pdl, pdt, pdw, pdh = wnd.preDragAbs
                minY = max(minY, spdt - pdt)

        elif 'bottom' in sides:
            myMinY = max(myMinY, spdt + myMinHeight)
            myMaxY = min(myMaxY, spdt + myMaxHeight)
            for wnd in followB:
                pdl, pdt, pdw, pdh = wnd.preDragAbs
                maxY = min(maxY, spdt + spdh + (ph - (pdt + pdh)))

        if 'left' in sides:
            myMaxX = min(myMaxX, spdl + spdw - myMinWidth)
            myMinX = max(myMinX, spdl + spdw - myMaxWidth)
            for wnd in followL:
                pdl, pdt, pdw, pdh = wnd.preDragAbs
                minX = max(minX, spdl - pdl)

        elif 'right' in sides:
            myMinX = max(myMinX, spdl + myMinWidth)
            myMaxX = min(myMaxX, spdl + myMaxWidth)
            for wnd in followR:
                pdl, pdt, pdw, pdh = wnd.preDragAbs
                maxX = min(maxX, spdl + spdw + (pw - (pdl + pdw)))

        return ((minX,
          minY,
          maxX,
          maxY), (myMinX,
          myMinY,
          myMaxX,
          myMaxY))

    def ModifyRect(self, sides):
        l, t, w, h = self.GetAbsolute()
        mx = uicore.uilib.x
        my = uicore.uilib.y
        rh = rv = 0
        if 'right' in sides:
            rh = l + w - mx
        elif 'left' in sides:
            rh = l - mx
        if 'bottom' in sides:
            rv = t + h - my
        elif 'top' in sides:
            rv = t - my
        return (int(rh),
         int(rv),
         int(rh),
         int(rv))

    @telemetry.ZONE_METHOD
    def UpdateClipCursor(self, rect, mrect):
        ml, mt, mr, mb = mrect
        rl, rt, rr, rb = rect
        uicore.uilib.ClipCursor(rl - ml, rt - mt, rr - mr, rb - mb)

    def GetSidesFromScalerName(self, sName):
        ret = []
        for s in ['Left',
         'Top',
         'Right',
         'Bottom']:
            if s in sName:
                ret.append(s.lower())

        return ret

    def StartScale(self, sender, btn, *args):
        if btn == uiconst.MOUSELEFT:
            sides = self.GetSidesFromScalerName(sender.name)
            self._StartScale(sides=sides)

    def _StartScale(self, sides):
        if not self.IsResizeable() or self.InStack():
            return
        self.__scale_sides = sides
        self.sortedScaleWindows = self.SortScaleWindows(self.__scale_sides)
        self.minmaxScale = self.FindMinMaxScaling(self.__scale_sides)
        self.CreateSnapGrid(self.sortedScaleWindows[-1])
        self._emit_on_start_scale()
        self.OnStartScale_(self)
        self._scaling = True
        uthread.new(self.OnScale)

    def SortScaleWindows(self, sides):
        wnds = []
        for side in sides:
            wnds += self.FindConnectingWindows(side, getParallelSides=1)

        self.PrepareWindowsForMove(wnds)
        ml, mt, mw, mh = self.GetAbsolute()
        scaleWidthMeH = []
        scaleWidthMeV = []
        onLeft = []
        onRight = []
        onBottom = []
        onTop = []
        all = [self]
        scaleAbove = []
        for wnd in wnds:
            if wnd == self or wnd in all:
                continue
            l, t, w, h = wnd.GetAbsolute()
            if l == ml and w == mw:
                scaleWidthMeH.append(wnd)
            elif l >= ml + mw:
                onRight.append(wnd)
            elif l + w <= ml:
                onLeft.append(wnd)
            elif 'right' in sides:
                onRight.append(wnd)
            elif 'left' in sides:
                onLeft.append(wnd)
            if t == mt and h == mh:
                scaleWidthMeV.append(wnd)
            elif t >= mt + mh:
                onBottom.append(wnd)
            elif t + h == mt and 'top' in sides:
                scaleAbove.append(wnd)
            elif t == mt and 'top' in sides:
                onTop.append(wnd)
            all.append(wnd)

        return (scaleWidthMeH,
         scaleWidthMeV,
         scaleAbove,
         onLeft,
         onRight,
         onTop,
         onBottom,
         all)

    @telemetry.ZONE_METHOD
    def OnScale(self, *args):
        mRect = self.ModifyRect(self.__scale_sides)
        while self._scaling and uicore.uilib.leftbtn and self and not self.closing:
            diffx = uicore.uilib.x - self.preDragCursorPos[0]
            diffy = uicore.uilib.y - self.preDragCursorPos[1]
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            allMinMaxRect, myMinMaxRect = self.minmaxScale
            if shift:
                snapGrid = self.__active_snap_grid[2]
                rect = allMinMaxRect
            else:
                snapGrid = self.__active_snap_grid[1]
                rect = myMinMaxRect
            self.UpdateClipCursor(rect, mRect)
            if not shift:
                for wnd in self.sortedScaleWindows[-1]:
                    wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                    wnd.left = wpdl
                    wnd.top = wpdt
                    wnd.width = wpdw
                    wnd.height = wpdh

                scaleH, scaleV, scaleAbove, followL, followR, followT, followB = ([],
                 [],
                 [],
                 [],
                 [],
                 [],
                 [])
            else:
                scaleH, scaleV, scaleAbove, followL, followR, followT, followB, all = self.sortedScaleWindows
            for side in self.__scale_sides:
                if side in ('left', 'right') and self.GetMinWidth() != self.GetMaxWidth():
                    for wnd in scaleH + [self]:
                        wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                        if side == 'left':
                            wnd.left = wpdl + diffx
                            if wnd.IsResizeable():
                                wnd.width = wnd._fixedWidth or wpdw - diffx
                        elif side == 'right':
                            if wnd.IsResizeable():
                                wnd.width = wnd._fixedWidth or wpdw + diffx

                    for wnd in [followR, followL][side == 'left']:
                        wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                        wnd.left = wpdl + diffx

                if side in ('top', 'bottom') and self.GetMinHeight() != self.GetMaxHeight():
                    for wnd in scaleV + [self]:
                        wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                        if side == 'top':
                            if wnd.IsResizeable():
                                wnd.height = wnd._fixedHeight or wpdh - diffy
                            wnd.top = wpdt + diffy
                        elif side == 'bottom':
                            if wnd.IsResizeable():
                                wnd.height = wnd._fixedHeight or wpdh + diffy

                    for wnd in [followB, followT][side == 'top']:
                        wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                        wnd.top = wpdt + diffy

                    for wnd in scaleAbove:
                        wpdl, wpdt, wpdw, wpdh = wnd.preDragAbs
                        if wnd.IsResizeable():
                            wnd.height = wnd._fixedHeight or wpdh + diffy

            self.ShowSnapEdges_Scaling(snapGrid)
            self.OnScale_(self)
            self._OnResize()
            blue.pyos.synchro.SleepWallclock(1)

        self.ValidateWindows()

    def EndScale(self, sender, *args):
        self.CleanupParent('snapIndicator')
        if not self.IsResizeable() or self.InStack():
            return
        self._scaling = False
        uicore.uilib.UnclipCursor()
        if self.closing:
            return
        if self.__active_snap_grid:
            snapGrid = self.__active_snap_grid[1]
            self.ShowSnapEdges_Scaling(snapGrid, showSnap=False, doSnap=True)
        self.RegisterPositionAndSize()
        self._emit_on_end_scale()
        self.OnEndScale_(self)

    def GetGroupAbsolute(self, group):
        return self.GetGroupRect(group, 1)

    def OnResize_(self, *args):
        self.OnResizeUpdate(self)

    def OnResizeUpdate(self, *args):
        pass

    def OnScale_(self, wnd, *args):
        pass

    def OnStartScale_(self, wnd, *args):
        pass

    def OnEndScale_(self, wnd, *args):
        pass

    def OnMouseDown_(self, what):
        pass

    def OnStartMinimize_(self, *args):
        pass

    def OnEndMinimize_(self, *args):
        pass

    def OnStartMaximize_(self, *args):
        pass

    def OnEndMaximize_(self, *args):
        pass

    def OnSetActive_(self, *args):
        pass

    def OnCollapsed(self, wnd, *args):
        pass

    def OnExpanded(self, wnd, *args):
        pass

    def OnDragTick(self, *args):
        pass

    def GetIntersectingWindows(self):
        all = uicore.registry.GetWindows()
        ml, mt, mw, mh = self.GetAbsolute()
        intersecting = []
        for otherWindow in all:
            if otherWindow is self:
                continue
            if otherWindow.stacked:
                continue
            if otherWindow.IsHidden():
                continue
            ol, ot, ow, oh = otherWindow.GetAbsolute()
            if not (ml <= ol < ml + mw or ml < ol + ow <= ml + mw or ml >= ol and ol + ow > ml + mw):
                continue
            if not (mt <= ot < mt + mh or mt < ot + oh <= mt + mh or mt >= ot and ot + oh > mt + mh):
                continue
            intersecting.append(otherWindow)

        return intersecting

    @classmethod
    def GetTopRight_TopOffset(cls):
        leftpush, rightpush = cls.GetSideOffset()
        cornerWnd = None
        for each in uicore.layer.main.children:
            if not isinstance(each, Window) or each.state == uiconst.UI_HIDDEN:
                continue
            if each.left + each.width in (uicore.desktop.width - rightpush, uicore.desktop.width - rightpush - 16):
                if each.top in (0, 16):
                    cornerWnd = each
                    break

        if cornerWnd:
            bottomAlignedWindows = cornerWnd.FindConnectingWindows('bottom')
            if bottomAlignedWindows:
                groupRect = cls.GetGroupRect(bottomAlignedWindows)
                return groupRect[3]

    @classmethod
    def GetBottomLeft_TopOffset(cls):
        leftpush, rightpush = cls.GetSideOffset()
        cornerWnd = None
        for each in uicore.layer.main.children:
            if not isinstance(each, Window) or each.state == uiconst.UI_HIDDEN:
                continue
            if each.left in (leftpush, leftpush + 16):
                if each.top + each.height in (uicore.desktop.height, uicore.desktop.height - 16):
                    cornerWnd = each
                    break

        if cornerWnd:
            topAlignedWindows = cornerWnd.FindConnectingWindows('top')
            if topAlignedWindows:
                groupRect = cls.GetGroupRect(topAlignedWindows)
                return groupRect[1]

    @classmethod
    def _GetDefaultCaption(cls):
        if cls.default_caption:
            if localization.IsValidLabel(cls.default_caption):
                return localization.GetByLabel(cls.default_caption)
            else:
                return cls.default_caption
        if cls.default_captionLabelPath:
            return localization.GetByLabel(cls.default_captionLabelPath)
        return cls.__name__

    @classmethod
    def GetIfOpen(cls, windowID = None, windowInstanceID = None):
        windowID = windowID if windowID else cls.default_windowID
        wnd = uicore.registry.GetWindow(windowID, windowInstanceID)
        return wnd

    @classmethod
    def CloseIfOpen(cls, windowID = None, windowInstanceID = None):
        wnd = cls.GetIfOpen(windowID, windowInstanceID)
        if wnd:
            wnd.Close()

    @classmethod
    def Open(cls, *args, **kwds):
        windowID = kwds.get('windowID', None) or cls.default_windowID
        windowInstanceID = kwds.get('windowInstanceID', None)
        if is_blocked('open', windowID):
            raise UserError('WindowBlockedFromOpening', {'window_name': cls._GetDefaultCaption()})
        wnd = cls.GetIfOpen(windowID=windowID, windowInstanceID=windowInstanceID)
        if wnd:
            wnd.Maximize()
            return wnd
        newWindow = cls(**kwds)
        return newWindow

    @classmethod
    def OpenBehindFullscreenViews(cls, **kwds):
        isSecondaryViewActive = sm.GetService('viewState').IsCurrentViewSecondary()
        windowID = kwds.get('windowID', cls.default_windowID)
        isOverlayed = GetRegisteredState(windowID, 'isOverlayed')
        if isSecondaryViewActive and not isOverlayed:
            wnd = cls.Open(openMinimized=True, idx=(-1), **kwds)
            sm.GetService('window').RegisterAsMinimizedByFullscreenView(wnd)
        else:
            cls.Open(**kwds)

    @classmethod
    def ToggleOpenClose(cls, *args, **kwds):
        wnd = cls.GetIfOpen(windowID=kwds.get('windowID', None), windowInstanceID=kwds.get('windowInstanceID', None))
        if wnd:
            wasCollapsed = wnd.IsCollapsed()
            if wasCollapsed:
                wnd.Expand()
            if wnd.stacked:
                if wnd.stack.GetActiveWindow() != wnd:
                    wnd.Maximize()
                    return wnd
                obscured = wnd.stack.ObscuredByOtherWindows()
            else:
                obscured = wnd.ObscuredByOtherWindows()
            if wnd.IsMinimized():
                wnd.Maximize()
                uicore.registry.SetFocus(wnd)
                return wnd
            if obscured:
                uicore.registry.SetFocus(wnd)
                return wnd
            if not wasCollapsed:
                wnd.CloseByUser()
        else:
            return cls.Open(*args, **kwds)

    def ObscuredByOtherWindows(self):
        intersecting = self.GetIntersectingWindows()
        for wnd in intersecting:
            if self not in uicore.layer.main.children:
                return False
            if wnd not in uicore.layer.main.children:
                continue
            if uicore.layer.main.children.index(self) > uicore.layer.main.children.index(wnd):
                return True

        return False

    @classmethod
    def IsOpen(cls, windowID = None, windowInstanceID = None):
        wnd = cls.GetIfOpen(windowID, windowInstanceID)
        return bool(wnd)

    @classmethod
    def IsOpenByWindowClass(cls):
        wnd = uicore.registry.GetWindowByClass(cls)
        return bool(wnd)

    @classmethod
    def GetRegisteredOrDefaultStackID(cls, windowID = None):
        windowID = windowID or cls.default_windowID
        if windowID:
            all = settings.char.windows.Get('stacksWindows', {})
            if windowID in all:
                return all[windowID]
            return all.get(windowID, cls.default_stackID)

    def GetRegisteredPositionAndSize(self):
        return self.GetRegisteredPositionAndSizeByClass(self.windowID)

    @classmethod
    def GetRegisteredPositionAndSizeByClass(cls, windowID = None):
        windowID = windowID or cls.default_windowID
        if type(windowID) == tuple:
            windowID, subWindowID = windowID
        all = settings.char.windows.Get('windowSizesAndPositions_1', {})
        usingDefault = 1
        if windowID and windowID in all:
            left, top, width, height, cdw, cdh = all[windowID]
            usingDefault = 0
        else:
            cdw, cdh = uicore.desktop.width, uicore.desktop.height
        if usingDefault:
            left, top, width, height = cls.GetDefaultSizeAndPosition()
            pushleft = cls.GetDefaultLeftOffset(width=width, align=uiconst.CENTER, left=left)
            if pushleft < 0:
                left = max(0, left + pushleft)
            elif pushleft > 0:
                left = min(left + pushleft, uicore.desktop.width - width)
        dw, dh = uicore.desktop.width, uicore.desktop.height
        if cdw != dw:
            wDiff = dw - cdw
            if left + width in (cdw, cdw - 16):
                left += wDiff
            elif left not in (0, 16):
                oldCenterX = (cdw - width) / 2
                xPortion = oldCenterX / float(cdw)
                newCenterX = int(xPortion * dw)
                cxDiff = newCenterX - oldCenterX
                left += cxDiff
        if cdh != dh:
            hDiff = dh - cdh
            if top in (0, 16):
                pass
            elif top + height in (cdh, cdh - 16):
                top += hDiff
            else:
                oldCenterY = (cdh - height) / 2
                yPortion = oldCenterY / float(cdh)
                newCenterY = int(yPortion * dh)
                cyDiff = newCenterY - oldCenterY
                top += cyDiff
        return (left,
         top,
         width,
         height,
         dw,
         dh)

    @classmethod
    def GetGroupRect(cls, group, getAbsolute = 0):
        if not len(group):
            return (0, 0, 0, 0)
        l, t, w, h = group[0].GetAbsolute()
        r = l + w
        b = t + h
        for wnd in group[1:]:
            wl, wt, ww, wh = wnd.GetAbsolute()
            l = min(l, wl)
            t = min(t, wt)
            r = max(r, wl + ww)
            b = max(b, wt + wh)

        if getAbsolute:
            return (l,
             t,
             r - l,
             b - t)
        return (l,
         t,
         r,
         b)

    @classmethod
    def GetDefaultSizeAndPosition(cls):
        dw = uicore.desktop.width
        dh = uicore.desktop.height
        if cls.default_fixedWidth:
            width = cls.default_fixedWidth
        elif callable(cls.default_width):
            width = cls.default_width()
        else:
            width = cls.default_width
        if cls.default_fixedHeight:
            height = cls.default_fixedHeight
        elif callable(cls.default_height):
            height = cls.default_height()
        else:
            height = cls.default_height
        if cls.default_left == '__center__':
            left = (dw - width) / 2
        elif cls.default_left == '__right__':
            left = dw - width
        elif callable(cls.default_left):
            left = cls.default_left()
        else:
            left = cls.default_left
        if cls.default_top == '__center__':
            top = (dh - height) / 2
        elif cls.default_top == '__bottom__':
            top = dh - height
        elif callable(cls.default_top):
            top = cls.default_top()
        else:
            top = cls.default_top
        return (left,
         top,
         width,
         height)

    @classmethod
    def GetDefaultLeftOffset(cls, width, align = None, left = 0):
        return sm.GetService('window').GetCameraLeftOffset(width, align, left)

    def RegisterSceneContainer(self, sceneCont):
        self.__scene_containers.add(sceneCont)

    def UnregisterSceneContainer(self, sceneCont):
        if sceneCont in self.__scene_containers:
            self.__scene_containers.remove(sceneCont)

    def Flush(self):
        mainArea = self.GetMainArea()
        if mainArea is not None:
            mainArea.Flush()

    @EatsExceptions('protoClientLogs')
    def _LogWindowEventOpened(self):
        if not self.analyticID:
            return
        message_bus = WindowMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.window_opened(self.analyticID)

    @EatsExceptions('protoClientLogs')
    def _LogWindowClosed(self):
        if not self.__opened_at_timestamp or not self.analyticID:
            return
        seconds, nanos = self.SplitBlueTimeIntoDecimalsAndFractions(self.__opened_at_timestamp)
        message_bus = WindowMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.window_closed(self.analyticID, seconds, nanos)

    @EatsExceptions('protoClientLogs')
    def _LogWindowEventFocused(self):
        if not self.analyticID:
            return
        message_bus = WindowMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.window_focused(self.analyticID)

    @EatsExceptions('protoClientLogs')
    def _LogWindowUnfocused(self):
        if not self.__focused_at_timestamp or not self.analyticID:
            return
        seconds, nanos = self.SplitBlueTimeIntoDecimalsAndFractions(self.__focused_at_timestamp)
        message_bus = WindowMessenger(sm.GetService('publicGatewaySvc'))
        message_bus.window_unfocused(self.analyticID, seconds, nanos)

    @staticmethod
    def SplitBlueTimeIntoDecimalsAndFractions(timestamp):
        if timestamp is None:
            return
        full_duration = gametime.GetSecondsSinceWallclockTime(timestamp)
        fractions, integer = math.modf(full_duration)
        return (int(integer), int(fractions * 1000000000.0))

    def GetWindowSizeForContentSize(self, width = 0, height = 0):
        left, top, right, bottom = self.GetContentToWindowEdgePadding()
        if self.extend_content_into_header:
            height = max(height, self.header_height)
        return (width + left + right, height + top + bottom)

    def GetTotalContentPadding(self):
        pad_top = self.content.padTop
        if not self.extend_content_into_header:
            pad_top += self.header_height
        return (self.content.padLeft,
         pad_top,
         self.content.padRight,
         self.content.padBottom)

    def GetContentToWindowEdgePadding(self):
        left, top, right, bottom = self.GetTotalContentPadding()
        margin_left, margin_top, margin_right, margin_bottom = self.GetWindowBorderPadding()
        border_left, border_top, border_right, border_bottom = self.GetWindowBorderSize()
        return (left + border_left + margin_left,
         top + border_top + margin_top,
         right + border_right + margin_right,
         bottom + border_bottom + margin_bottom)

    def GetWindowBorderSize(self):
        return (1, 1, 1, 1)

    def GetWindowBorderPadding(self):
        return (1, 1, 1, 1)

    def _SetHeader(self, header):
        if self.closing:
            raise RuntimeError("Attempting to assign a header to a window that's in the process of closing, or already closed")
        if self.__header is not None:
            self.__header.SetParent(None)
            self.__header.unmount(self)
        self.__header = header
        self.__header.align = uiconst.TOTOP
        self.__header.SetParent(self.sr.headerParent)
        self.__header.mount(self)
        self._UpdateContentPadding()

    def _OnCaptionChanged(self):
        if self.sr.tab and hasattr(self.sr.tab, 'SetLabel'):
            self.sr.tab.SetLabel(self.caption)

    def _UpdateContentPadding(self):
        if self.closing:
            return
        if self.stacked:
            header = self.stack.header
        else:
            header = self.header
        if header:
            self.__header_has_sufficient_bottom_padding = header.HAS_SUFFICIENT_BOTTOM_PADDING
        self._UpdateHeaderInset()
        old_padding = self.__previous_content_padding
        new_padding = self.content_padding
        self.__previous_content_padding = new_padding
        if self.__apply_content_padding:
            self.content.padding = new_padding
        else:
            self.content.padding = 0
        if old_padding is not None and old_padding != new_padding:
            self._emit_on_content_padding_changed()

    def _UpdateHeaderInset(self, silent = False):
        if not self.closing:
            header_inset = self._ComputeHeaderInset()
            if self.__header_inset != header_inset:
                self.__header_inset = header_inset
                if not silent:
                    self._emit_on_header_inset_changed()

    def _ComputeHeaderInset(self):
        inset_left, _, inset_right, _ = self.content_padding
        if self.__window_controls is not None and self.__window_controls.display:
            inset_right = max(inset_right, self.__window_controls.reserved_width)
        return (inset_left, inset_right)

    def __on_global_window_margin_mode_changed(self, margin_mode):
        if not self.closing:
            self._UpdateContentPadding()
            if self.__on_margin_mode_changed is not None:
                self.__on_margin_mode_changed(self)

    def __on_header_parent_size_changed(self):
        if not self.closing:
            height = self.sr.headerParent.height
            if self.__previous_header_height != height:
                self.__previous_header_height = height
                self.__window_controls_cont.height = height
                self._emit_on_header_height_changed()

    @property
    def iconNum(self):
        return self.icon

    @iconNum.setter
    def iconNum(self, value):
        self.icon = value

    def GetMainArea(self):
        return self.content

    def IsCollapsed(self):
        return self.collapsed

    def IsCompact(self):
        return self.compact

    def IsCompactable(self):
        return self.compactable

    def Compact(self):
        self.compact = True

    def UnCompact(self):
        self.compact = False

    def GetCaption(self, update = 1):
        return self.caption or ''

    def SetCaption(self, caption, *args, **kwds):
        if localization.IsValidLabel(caption):
            caption = localization.GetByLabel(caption)
        self.caption = caption

    def InStack(self):
        return self.stacked

    def IsKillable(self):
        return self.killable

    def MakeKillable(self):
        self.killable = True

    def MakeUnKillable(self):
        self.killable = False

    def IsLocked(self):
        return self.locked

    def IsLockable(self):
        return self.lockable

    def Lock(self):
        self.locked = True

    def Unlock(self):
        self.locked = False

    def HideHeaderButtons(self):
        self.show_window_controls = False

    def GetStack(self):
        return self.stack

    def IsMinimizable(self):
        if is_blocked('minimize', self.windowID):
            return False
        return self.minimizable

    def MakeUnMinimizable(self):
        self.minimizable = False

    def MakeCollapseable(self):
        self.collapsible = True

    def MakeUncollapseable(self):
        self.collapsible = False

    def IsOverlayable(self):
        return self.overlayable
