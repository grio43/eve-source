#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\overview\window.py
from eve.client.script.ui.inflight.overview.overviewWindowUtil import OpenOverview

def reset_overview_window(method):

    def run_method_and_reset_overview_window_decorator(*args, **kwargs):
        was_window_open = is_window_open()
        if was_window_open:
            close_window()
        result = method(*args, **kwargs)
        if was_window_open:
            open_window()
        return result

    return run_method_and_reset_overview_window_decorator


def is_window_open():
    from eve.client.script.ui.inflight.overview.overviewWindowUtil import IsOverviewWndOpen
    return IsOverviewWndOpen()


def close_window():
    from eve.client.script.ui.inflight.overview.overviewWindowUtil import CloseAllOverviewWindows
    return CloseAllOverviewWindows()


def open_window():
    if session.solarsystemid:
        OpenOverview()
