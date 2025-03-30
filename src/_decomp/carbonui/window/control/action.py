#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\control\action.py
import abc
import weakref
import eveicon
import localization
import signals
import uihider
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.window.util import is_blocked

class WindowActionImportance(object):
    core = 1
    extra = 2
    content = 3


class WindowActionBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, window, available = True, available_check = None, enabled = True, enabled_check = None, ui_name = None, importance = WindowActionImportance.core, importance_check = None):
        self.__window_ref = weakref.ref(window)
        self.__available = available_check(window) if available_check is not None else available
        self.__available_check = available_check
        self.__enabled = enabled_check(window) if enabled_check is not None else enabled
        self.__enabled_check = enabled_check
        self.__ui_name = ui_name
        self.__importance = importance_check(window) if importance_check is not None else importance
        self.__importance_check = importance_check
        self.__on_available_changed = None
        self.__on_enabled_changed = None
        self.__on_icon_changed = None
        self.__on_label_changed = None
        self.__on_importance_changed = None

    @abc.abstractproperty
    def icon(self):
        pass

    @property
    def on_icon_changed(self):
        if self.__on_icon_changed is None:
            self.__on_icon_changed = signals.Signal('{}.on_icon_changed'.format(self.__class__.__name__))
        return self.__on_icon_changed

    @abc.abstractproperty
    def label(self):
        pass

    @property
    def on_label_changed(self):
        if self.__on_label_changed is None:
            self.__on_label_changed = signals.Signal('{}.on_label_changed'.format(self.__class__.__name__))
        return self.__on_label_changed

    @property
    def available(self):
        return self.__available

    @property
    def on_available_changed(self):
        if self.__on_available_changed is None:
            self.__on_available_changed = signals.Signal('{}.on_available_changed'.format(self.__class__.__name__))
        return self.__on_available_changed

    @property
    def enabled(self):
        return self.__enabled

    @property
    def on_enabled_changed(self):
        if self.__on_enabled_changed is None:
            self.__on_enabled_changed = signals.Signal('{}.on_enabled_changed'.format(self.__class__.__name__))
        return self.__on_enabled_changed

    @property
    def importance(self):
        return self.__importance

    @property
    def on_importance_changed(self):
        if self.__on_importance_changed is None:
            self.__on_importance_changed = signals.Signal('{}.on_importance_changed'.format(self.__class__.__name__))
        return self.__on_importance_changed

    @property
    def ui_name(self):
        return self.__ui_name

    @property
    def window(self):
        window = self.__window_ref()
        if window is not None and not window.destroyed:
            return window

    @abc.abstractmethod
    def execute(self):
        pass

    def update(self):
        window = self.window
        if window is None:
            return
        if self.__available_check is not None:
            available = self.__available_check(window)
            if self.__available != available:
                self.__available = available
                self.on_available_changed(self)
        if self.__enabled_check is not None:
            enabled = self.__enabled_check(window)
            if self.__enabled != enabled:
                self.__enabled = enabled
                self.on_enabled_changed(self)
        if self.__importance_check is not None:
            importance = self.__importance_check(window)
            if self.__importance != importance:
                self.__importance = importance
                self.on_importance_changed(self)


class WindowToggleAction(WindowActionBase):

    def __init__(self, window, callback, toggled_check, toggled_on_icon, toggled_off_icon, toggled_on_label, toggled_off_label, available = True, available_check = None, enabled = True, enabled_check = None, importance = WindowActionImportance.core, importance_check = None):
        super(WindowToggleAction, self).__init__(window=window, available=available, available_check=available_check, enabled=enabled, enabled_check=enabled_check, importance=importance, importance_check=importance_check)
        self._callback = callback
        self._toggled_on = toggled_check(window)
        self._toggled_check = toggled_check
        self._toggled_on_icon = toggled_on_icon
        self._toggled_off_icon = toggled_off_icon
        self._toggled_on_label = toggled_on_label
        self._toggled_off_label = toggled_off_label

    @property
    def icon(self):
        if self.toggled_on:
            return self._toggled_on_icon
        else:
            return self._toggled_off_icon

    @property
    def label(self):
        if self.toggled_on:
            return self._toggled_on_label
        else:
            return self._toggled_off_label

    @property
    def toggled_on(self):
        return self._toggled_on

    def execute(self):
        if self.available and self.enabled:
            window = self.window
            if window is None:
                return
            self._callback(window)
            self._update_toggled_state()

    def update(self):
        super(WindowToggleAction, self).update()
        self._update_toggled_state()

    def _update_toggled_state(self):
        window = self.window
        if window is None:
            return
        toggled_on = self._toggled_check(window)
        if self._toggled_on != toggled_on:
            self._toggled_on = toggled_on
            if self._toggled_on_icon != self._toggled_off_icon:
                self.on_icon_changed(self)
            if self._toggled_on_label != self._toggled_off_label:
                self.on_label_changed(self)


class WindowAction(WindowActionBase):

    def __init__(self, window, label, icon, callback, available = True, available_check = None, enabled = True, enabled_check = None, ui_name = None, importance = WindowActionImportance.core, importance_check = None):
        super(WindowAction, self).__init__(window=window, available=available, available_check=available_check, enabled=enabled, enabled_check=enabled_check, ui_name=ui_name, importance=importance, importance_check=importance_check)
        self._label = label
        self._icon = icon
        self._callback = callback

    @property
    def label(self):
        return self._label

    @property
    def icon(self):
        return self._icon

    def execute(self):
        if self.available and self.enabled:
            window = self.window
            if window is not None:
                return self._callback(window)


class WindowMenuAction(WindowAction):
    pass


class CloseWindowAction(WindowAction):

    def __init__(self, window):
        if window.is_stack:
            label = localization.GetByLabel('UI/Control/EveWindow/CloseStack')
        else:
            label = localization.GetByLabel('UI/Common/Buttons/Close')
        super(CloseWindowAction, self).__init__(window=window, icon=eveicon.close, label=label, callback=lambda _window: _window.CloseByUser(), available_check=lambda _window: _window.killable, enabled_check=lambda _window: not is_blocked('close', _window.windowID), ui_name='CloseButtonIcon')
        window.on_killable_changed.connect(self._on_killable_changed)
        uihider.CommandBlockerService.instance().subscribe(self.update)

    def _on_killable_changed(self, window):
        self.update()


class MinimizeWindowAction(WindowAction):

    def __init__(self, window):
        if window.is_stack:
            label = localization.GetByLabel('UI/Control/EveWindow/MinimizeStack')
        else:
            label = localization.GetByLabel('UI/Control/EveWindow/Minimize')

        def enabled_check(_window):
            return not is_blocked('minimize', _window.windowID) and ServiceManager.Instance().GetService('neocom').IsAvailable()

        super(MinimizeWindowAction, self).__init__(window=window, icon=eveicon.minimize, label=label, callback=lambda _window: _window.Minimize(), available_check=lambda _window: _window.minimizable, enabled_check=enabled_check, ui_name='MinimizeButtonIcon')
        uihider.CommandBlockerService.instance().subscribe(self.update)
        ServiceManager.Instance().RegisterForNotifyEvent(self, 'OnNeocomAvailableChanged')
        window.on_minimizable_changed.connect(self._on_window_minimizable_changed)

    def _on_window_minimizable_changed(self, window):
        self.update()

    def OnNeocomAvailableChanged(self):
        self.update()


class LightBackgroundWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(LightBackgroundWindowAction, self).__init__(window=window, toggled_on_icon=eveicon.light_background_on, toggled_off_icon=eveicon.light_background_off, toggled_on_label=localization.GetByLabel('/Carbon/UI/Controls/Window/DisableLightBackground'), toggled_off_label=localization.GetByLabel('/Carbon/UI/Controls/Window/EnableLightBackground'), callback=self._toggle_light_background, toggled_check=lambda _window: _window.IsLightBackgroundEnabled(), available_check=lambda _window: _window.IsLightBackgroundConfigurable(), importance=WindowActionImportance.extra)
        window.on_light_background_changed.connect(self._on_light_background_changed)

    @staticmethod
    def _toggle_light_background(window):
        if window.IsLightBackgroundEnabled():
            window.DisableLightBackground()
        else:
            window.EnableLightBackground()

    def _on_light_background_changed(self, window):
        self.update()


class CompactModeWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(CompactModeWindowAction, self).__init__(window=window, toggled_on_icon=eveicon.uncompact, toggled_off_icon=eveicon.compact, toggled_on_label=localization.GetByLabel('/Carbon/UI/Controls/Window/DisableCompactMode'), toggled_off_label=localization.GetByLabel('/Carbon/UI/Controls/Window/EnableCompactMode'), callback=self._toggle_compact_mode, toggled_check=lambda _window: _window.compact, available_check=lambda _window: _window.compactable, enabled_check=lambda _window: not is_blocked('compact', _window.windowID), importance=WindowActionImportance.extra)
        uihider.CommandBlockerService.instance().subscribe(self.update)
        window.on_compact_mode_changed.connect(self._on_window_compact_mode_changed)

    @staticmethod
    def _toggle_compact_mode(window):
        window.compact = not window.compact

    def _on_window_compact_mode_changed(self, window):
        self.update()


class LockWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(LockWindowAction, self).__init__(window=window, callback=self._toggle_locked, toggled_on_icon=eveicon.locked, toggled_off_icon=eveicon.unlocked, toggled_on_label=localization.GetByLabel('/Carbon/UI/Controls/Window/Unlock'), toggled_off_label=localization.GetByLabel('/Carbon/UI/Controls/Window/Lock'), toggled_check=lambda _window: _window.locked, available_check=self._is_available, enabled_check=self._is_enabled, importance_check=self._get_importance)
        window.on_lockable_changed.connect(self._on_window_lockable_changed)
        window.on_locked_changed.connect(self._on_window_locked_changed)
        uihider.CommandBlockerService.instance().subscribe(self.update)

    @staticmethod
    def _is_available(window):
        if window.locked:
            return True
        elif window.lockable:
            return True
        else:
            return False

    @staticmethod
    def _is_enabled(window):
        action = 'lock' if not window.locked else 'unlock'
        return not is_blocked(action, window.windowID) and window.lockable

    @staticmethod
    def _get_importance(window):
        if window.locked:
            return WindowActionImportance.core
        else:
            return WindowActionImportance.extra

    @staticmethod
    def _toggle_locked(window):
        window.locked = not window.locked

    def _on_window_lockable_changed(self, window):
        self.update()

    def _on_window_locked_changed(self, window):
        self.update()


class OverlayWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(OverlayWindowAction, self).__init__(window=window, callback=self._toggle_overlay, toggled_check=lambda _window: _window.IsOverlayed(), toggled_on_icon=eveicon.overlay_fullscreen_on, toggled_off_icon=eveicon.overlay_fullscreen_off, toggled_on_label=localization.GetByLabel('/Carbon/UI/Controls/Window/DisableOverlayMode'), toggled_off_label=localization.GetByLabel('/Carbon/UI/Controls/Window/EnableOverlayMode'), available_check=lambda _window: _window.IsOverlayable(), importance=WindowActionImportance.extra)

    @staticmethod
    def _toggle_overlay(window):
        if window.IsOverlayed():
            window.SetNotOverlayed()
        else:
            window.SetOverlayed()


class CollapseWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(CollapseWindowAction, self).__init__(window=window, callback=self._toggle_collapsed, toggled_check=lambda _window: _window.collapsed, toggled_on_icon=eveicon.expand, toggled_off_icon=eveicon.collapse, toggled_on_label=localization.GetByLabel('/Carbon/UI/Controls/Window/Expand'), toggled_off_label=localization.GetByLabel('/Carbon/UI/Controls/Window/Collapse'), available_check=lambda _window: _window.collapsible, importance=WindowActionImportance.extra)
        window.on_collapsed_changed.connect(self._on_window_collapsed_changed)
        window.on_collapsible_changed.connect(self._on_window_collapsible_changed)

    @staticmethod
    def _toggle_collapsed(window):
        window.collapsed = not window.collapsed

    def _on_window_collapsible_changed(self, window):
        self.update()

    def _on_window_collapsed_changed(self, window):
        self.update()
