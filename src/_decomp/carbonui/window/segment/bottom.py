#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\segment\bottom.py
import weakref
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.window.segment.underlay import WindowSegmentUnderlay

class WindowSegmentBottom(ContainerAutoSize):

    def __init__(self, window, align_mode = None, pad_top = 0):
        self._window_ref = weakref.ref(window)
        pad_left, _, pad_right, pad_bottom = window.content_padding
        super(WindowSegmentBottom, self).__init__(parent=window.content, align=uiconst.TOBOTTOM, padding=(-pad_left,
         pad_top,
         -pad_right,
         -pad_bottom), idx=0)
        WindowSegmentUnderlay(bgParent=self, align=uiconst.TOALL)
        self._content = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=align_mode, padding=(pad_left,
         pad_bottom,
         pad_right,
         pad_bottom))
        window.on_content_padding_changed.connect(self._on_window_content_padding_changed)

    @property
    def content(self):
        return self._content

    def _on_window_content_padding_changed(self, window):
        pad_left, _, pad_right, pad_bottom = window.content_padding
        self.padding = (-pad_left,
         self.padTop,
         -pad_right,
         -pad_bottom)
        self.content.padding = (pad_left,
         pad_bottom,
         pad_right,
         pad_bottom)

    def Close(self):
        window = self._window_ref()
        if window is not None:
            window.on_content_padding_changed.disconnect(self._on_window_content_padding_changed)
        super(WindowSegmentBottom, self).Close()
