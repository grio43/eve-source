#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\uihider\ui.py
import abc
import weakref
from carbonui.uicore import uicore

class InputDisabler(object):

    def __init__(self, is_context_menu_disabled = False, is_manual_piloting_disabled = False):
        self.is_context_menu_disabled = is_context_menu_disabled
        self.is_manual_piloting_disabled = is_manual_piloting_disabled

    def register_handlers(self):
        uicore.uilib.SetEventHandlerResolver(self.resolve_event_handler)
        uicore.uilib.SetMenuHandlerResolver(self.resolve_menu_handler)

    def unregister_handlers(self):
        uicore.uilib.SetEventHandlerResolver(None)
        uicore.uilib.SetMenuHandlerResolver(None)

    def resolve_event_handler(self, ui_object, handler_name):
        if self.is_manual_piloting_disabled:
            if handler_name == 'OnDblClick':
                if is_name_equal(ui_object, 'l_inflight'):
                    return (None, None)
            elif handler_name == 'OnKeyDown':
                if is_name_equal(ui_object, 'Desktop'):
                    return (None, None)
            elif handler_name == 'OnClick':
                name = getattr(ui_object, 'name', None)
                if name == 'SpeedGauge':
                    return (None, None)
                if 'ModuleButton_' in name:
                    target_id = sm.GetService('target').GetActiveTargetID()
                    if target_id is None:
                        return (None, None)
        return ui_object.FindEventHandler(handler_name)

    def resolve_menu_handler(self, ui_object):
        if self.is_context_menu_disabled:
            return None


def is_name_equal(ui_object, name):
    return getattr(ui_object, 'name', None) == name
