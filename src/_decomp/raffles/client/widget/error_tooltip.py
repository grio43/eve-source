#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\error_tooltip.py
import functools
import threadutils
import uthread2
import eveui
from raffles.client.localization import get_error_message

@threadutils.threaded
def show_error_tooltip(owner, error, error_kwargs = None, on_finished = None):
    tooltip = eveui.show_persistent_tooltip(owner=owner, load_function=functools.partial(_load_error_tooltip, error, error_kwargs))
    uthread2.sleep(2.5)
    if tooltip:
        tooltip.CloseWithFade()
    if on_finished:
        on_finished()


def _load_error_tooltip(error, error_kwargs, panel, owner):
    error_kwargs = error_kwargs or {}
    panel.LoadGeneric1ColumnTemplate()
    panel.AddLabelMedium(align=eveui.Align.center_left, text=get_error_message(error, **error_kwargs), color=(1.0, 0.651, 0.302))
