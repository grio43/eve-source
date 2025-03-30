#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\compatibility.py
import functools
import carbonui.uicore
from eveui.keyboard import Key
from eveui.mouse import Mouse

class CarbonEventHandler(object):

    def HasEventHandler(self, handler_name):
        wrapper = _CARBON_EVENT_WRAPPERS.get(handler_name, None)
        if wrapper is not None and hasattr(self, wrapper.eveui_name):
            return True
        else:
            return super(CarbonEventHandler, self).HasEventHandler(handler_name)

    def FindEventHandler(self, handler_name):
        wrapper = _CARBON_EVENT_WRAPPERS.get(handler_name, None)
        if wrapper is not None and hasattr(self, wrapper.eveui_name):
            return ((), functools.partial(wrapper, self))
        else:
            return super(CarbonEventHandler, self).FindEventHandler(handler_name)


class _CarbonWrapper(object):

    def __init__(self, eveui_name, wrapper_func):
        self.eveui_name = eveui_name
        self.wrapper_func = wrapper_func

    def __call__(self, *args, **kwargs):
        return self.wrapper_func(*args, **kwargs)


_CARBON_EVENT_WRAPPERS = {}

def _carbon_event_wrapper(carbon_event_name, eveui_event_name):
    if carbon_event_name in _CARBON_EVENT_WRAPPERS:
        raise ValueError('carbonui event {} already wrapped'.format(carbon_event_name))

    def inner(f):
        _CARBON_EVENT_WRAPPERS[carbon_event_name] = _CarbonWrapper(eveui_event_name, f)

    return inner


@_carbon_event_wrapper('OnMouseEnter', 'on_mouse_enter')
def on_mouse_enter_wrapper(ui_object):
    _execute_handler_maybe(ui_object, 'on_mouse_enter')


@_carbon_event_wrapper('OnMouseExit', 'on_mouse_exit')
def on_mouse_exit_wrapper(ui_object):
    _execute_handler_maybe(ui_object, 'on_mouse_exit')


@_carbon_event_wrapper('OnClick', 'on_click')
def on_click_wrapper(ui_object):
    _propagate_up(ui_object, 'on_click', click_count=1)


@_carbon_event_wrapper('OnDblClick', 'on_click')
def on_double_click_wrapper(ui_object):
    _propagate_up(ui_object, 'on_click', click_count=2)


@_carbon_event_wrapper('OnTripleClick', 'on_click')
def on_triple_click_wrapper(ui_object):
    _propagate_up(ui_object, 'on_click', click_count=3)


@_carbon_event_wrapper('OnChar', 'on_char')
def on_char_wrapper(ui_object, character, _):
    if character not in (Key.enter, Key.backspace, 127):
        return _propagate_up(ui_object, 'on_char', unichr(character))


@_carbon_event_wrapper('OnKeyDown', 'on_key_down')
def on_key_down_wrapper(ui_object, key, _):
    _propagate_up(ui_object, 'on_key_down', key)


@_carbon_event_wrapper('OnKeyUp', 'on_key_up')
def on_key_up_wrapper(ui_object, key, _):
    _propagate_up(ui_object, 'on_key_up', key)


@_carbon_event_wrapper('OnMouseDown', 'on_mouse_down')
def on_mouse_down_wrapper(ui_object, button):
    _propagate_up(ui_object, 'on_mouse_down', Mouse(button))


@_carbon_event_wrapper('OnMouseUp', 'on_mouse_up')
def on_mouse_up_wrapper(ui_object, button):
    _propagate_up(ui_object, 'on_mouse_up', Mouse(button))


@_carbon_event_wrapper('OnMouseMove', 'on_mouse_move')
def on_mouse_move_wrapper(ui_object, *args):
    _propagate_up(ui_object, 'on_mouse_move')


def _propagate_up(ui_object, method_name, *args, **kwargs):
    stopper = carbonui.uicore.uicore.desktop
    return _propagate_up_until(stopper, ui_object, method_name, *args, **kwargs)


def _propagate_up_until(stopper, ui_object, method_name, *args, **kwargs):
    while ui_object and ui_object is not stopper:
        if hasattr(ui_object, method_name):
            stop_propagation = getattr(ui_object, method_name)(*args, **kwargs)
            if stop_propagation:
                carbonui.uicore.uicore.uilib.StopKeyDownAcceleratorThread()
                return True
        ui_object = ui_object.parent

    return False


def _execute_handler_maybe(ui_object, method_name, *args, **kwargs):
    if hasattr(ui_object, method_name):
        return getattr(ui_object, method_name)(*args, **kwargs)
