#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\snap.py
from carbonui.uicore import uicore
SNAP_DISTANCE = 16
WINDOW_SNAP_DISTANCE = 12

def find_sibling_windows(window, predicate = None):
    all_windows = uicore.registry.GetWindows()
    windows = []
    for sibling in all_windows:
        if sibling == window or not sibling.display or sibling.stacked or sibling.parent != window.parent:
            continue
        if predicate is None or predicate(sibling):
            windows.append(sibling)

    return windows
