#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\layout.py
import mathext
from carbonui.uicore import uicore
from carbonui.window.snap import SNAP_DISTANCE

class AnchorSide(object):
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    HORIZONTAL = 5
    VERTICAL = 6


class Anchor(object):

    def __init__(self, side, offset):
        self.side = side
        self.offset = offset


class Rect(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @classmethod
    def from_element(cls, element):
        left, top, width, height = element.GetAbsolute()
        return cls(left, top, width, height)

    @classmethod
    def from_elements(cls, elements):
        return reduce(lambda a, b: a.merge(b), [ cls.from_element(e) for e in elements ])

    def merge(self, other):
        left = min(self.x, other.x)
        top = min(self.y, other.y)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        return Rect(x=left, y=top, width=right - left, height=bottom - top)


class AnchoredWindowGroup(object):

    def __init__(self, anchors, windows, boundaries):
        self.anchors = anchors
        self.windows = windows
        self.boundaries = boundaries


def capture_desktop_window_layout():
    all_windows = uicore.registry.GetValidWindows(getModals=True, floatingOnly=True, getHidden=True)
    desktop_rect = Rect.from_element(uicore.desktop)
    window_groups = []
    processed_windows = set()
    for window in all_windows:
        if window in processed_windows:
            continue
        connected_windows = window.FindConnectingWindows(validWnds=all_windows, fullSideOnly=False)
        group_rect = Rect.from_elements(connected_windows)
        group = AnchoredWindowGroup(anchors=_get_window_desktop_anchors(window_group_rect=group_rect, desktop_rect=desktop_rect), windows=connected_windows, boundaries=group_rect)
        window_groups.append(group)
        processed_windows.update(connected_windows)

    return window_groups


CENTER_THRESHOLD = 32

def _get_window_desktop_anchors(window_group_rect, desktop_rect):
    anchors = []
    left_offset, right_offset = _get_side_offset()
    margin_left = window_group_rect.left - desktop_rect.left
    margin_right = desktop_rect.right - window_group_rect.right
    if margin_left in (0, left_offset, left_offset + SNAP_DISTANCE):
        anchors.append(Anchor(side=AnchorSide.LEFT, offset=margin_left))
    elif margin_right in (0, right_offset, right_offset + SNAP_DISTANCE):
        anchors.append(Anchor(side=AnchorSide.RIGHT, offset=margin_right))
    elif abs(margin_left - margin_right) < CENTER_THRESHOLD:
        anchors.append(Anchor(AnchorSide.HORIZONTAL, offset=0.5))
    elif margin_left < margin_right:
        anchors.append(Anchor(side=AnchorSide.LEFT, offset=margin_left))
    else:
        anchors.append(Anchor(side=AnchorSide.RIGHT, offset=margin_right))
    margin_top = window_group_rect.top - desktop_rect.top
    margin_bottom = desktop_rect.bottom - window_group_rect.bottom
    if margin_top in (0, SNAP_DISTANCE):
        anchors.append(Anchor(side=AnchorSide.TOP, offset=margin_top))
    elif margin_bottom in (0, SNAP_DISTANCE):
        anchors.append(Anchor(side=AnchorSide.BOTTOM, offset=margin_bottom))
    elif abs(margin_top - margin_bottom) < CENTER_THRESHOLD:
        anchors.append(Anchor(AnchorSide.VERTICAL, offset=0.5))
    elif margin_top < margin_bottom:
        anchors.append(Anchor(side=AnchorSide.TOP, offset=margin_top))
    else:
        anchors.append(Anchor(side=AnchorSide.BOTTOM, offset=margin_bottom))
    return anchors


def apply_desktop_window_layout(anchored_window_groups):
    for anchored_window_group in anchored_window_groups:
        group_rect = anchored_window_group.boundaries
        for anchor in anchored_window_group.anchors:
            for window in anchored_window_group.windows:
                if anchor.side == AnchorSide.LEFT:
                    window.left = min(max(0, uicore.desktop.width - window.width), anchor.offset + (window.left - group_rect.left))
                elif anchor.side == AnchorSide.TOP:
                    window.top = min(max(0, uicore.desktop.height - window.height), anchor.offset + (window.top - group_rect.top))
                elif anchor.side == AnchorSide.RIGHT:
                    window.left = min(max(0, uicore.desktop.width - window.width), uicore.desktop.width - (anchor.offset + group_rect.width) + (window.left - group_rect.left))
                elif anchor.side == AnchorSide.BOTTOM:
                    window.top = max(0, uicore.desktop.height - (anchor.offset + group_rect.height) + (window.top - group_rect.top))
                elif anchor.side == AnchorSide.HORIZONTAL:
                    group_half_width = int(round(group_rect.width / 2.0))
                    group_center = uicore.desktop.width * anchor.offset
                    offset_in_group = window.left - group_rect.left
                    window.left = mathext.clamp(value=group_center - group_half_width + offset_in_group, low=0, high=uicore.desktop.width - window.width)
                elif anchor.side == AnchorSide.VERTICAL:
                    group_half_height = int(round(group_rect.height / 2.0))
                    group_center = uicore.desktop.height * anchor.offset
                    offset_in_group = window.top - group_rect.top
                    window.top = mathext.clamp(value=group_center - group_half_height + offset_in_group, low=0, high=uicore.desktop.height - window.height)


def _get_side_offset():
    side_panel_layer = uicore.layer.sidePanels
    if side_panel_layer:
        return side_panel_layer.GetSideOffset()
    return (0, 0)
