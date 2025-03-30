#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\vertical_centered_container.py
import contextlib
import math
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize

class VerticalCenteredContainer(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP

    def __init__(self, **kwargs):
        kwargs['callback'] = self._on_size_change
        super(VerticalCenteredContainer, self).__init__(**kwargs)

    @contextlib.contextmanager
    def auto_size_disabled(self):
        was_enabled = self.isAutoSizeEnabled
        self.DisableAutoSize()
        try:
            yield self
        finally:
            if was_enabled:
                self.EnableAutoSize()

    def _on_size_change(self):
        to_top_aligned_children = filter(lambda child: child.align == uiconst.TOTOP, self.children)
        if to_top_aligned_children:
            content_height = 0
            for i, child in enumerate(to_top_aligned_children):
                content_height += child.height + child.padTop + child.padBottom
                if i > 0:
                    content_height += child.top

            if content_height <= 0:
                return
            _, height = self.GetCurrentAbsoluteSize()
            adjusted_top = max(0, math.floor((height - content_height) / 2.0))
            to_top_aligned_children[0].top = adjusted_top

    def SetSizeAutomatically(self):
        if self.align == uiconst.TOALL:
            self._on_size_change()
        else:
            super(VerticalCenteredContainer, self).SetSizeAutomatically()
