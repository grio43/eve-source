#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\behavior\focus.py
from contextlib import contextmanager
import carbonui.uicore
import proper
import threadutils

class FocusBehavior(proper.Observable):

    def __init__(self, focus_on_click = True, **kwargs):
        self.focus_on_click = focus_on_click
        self.__registry_update_suppressed = False
        super(FocusBehavior, self).__init__(**kwargs)
        self.bind(is_focusable=self.__on_is_focusable)

    @proper.ty(default=True)
    def is_focusable(self):
        pass

    @proper.ty
    def focused(self):
        pass

    @focused.default
    def __default_focused(self):
        return carbonui.uicore.uicore.registry.GetFocus() is self

    @focused.after_change
    def __update_focused(self, focus):
        if not self.__registry_update_suppressed:
            carbonui.uicore.uicore.registry.SetFocus(self if focus else None)

    def focus_next(self):
        carbonui.uicore.uicore.registry.FindFocus(1)

    def focus_previous(self):
        carbonui.uicore.uicore.registry.FindFocus(-1)

    def on_click(self, click_count):
        stop_propagation = False
        try:
            on_click = super(FocusBehavior, self).on_click
        except AttributeError:
            pass
        else:
            stop_propagation = on_click(click_count)

        if not self.focused and self.focus_on_click:
            self.focused = True
            stop_propagation = True
        return stop_propagation

    def __on_is_focusable(self, _, is_focusable):
        if not is_focusable and self.focused:
            self.focused = False

    @contextmanager
    def __suppress_registry_update(self):
        self.__registry_update_suppressed = True
        try:
            yield
        finally:
            self.__registry_update_suppressed = False

    @property
    def isTabStop(self):
        return self.is_focusable

    @threadutils.threaded
    def OnSetFocus(self):
        with self.__suppress_registry_update():
            self.focused = True

    @threadutils.threaded
    def OnKillFocus(self):
        with self.__suppress_registry_update():
            self.focused = False

    def Close(self):
        self.focused = False
        super(FocusBehavior, self).Close()
