#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\layout\aspect_ratio.py
from eveui import Container
from eveui.constants import Align

class AspectRatioContainer(Container):
    default_align = Align.center

    def __init__(self, aspect_ratio = 16.0 / 9.0, contain = True, **kwargs):
        self._aspect_ratio = aspect_ratio
        self._contain = contain
        super(AspectRatioContainer, self).__init__(**kwargs)

    def UpdateAlignment(self, *args, **kwargs):
        max_width, max_height = self.parent.GetCurrentAbsoluteSize()
        max_ratio = max_width / float(max_height)
        if self._contain:
            if max_ratio < self._aspect_ratio:
                height = max_width / self._aspect_ratio
                width = max_width
            else:
                height = max_height
                width = max_height * self._aspect_ratio
        elif max_ratio < self._aspect_ratio:
            height = max_height
            width = max_height * self._aspect_ratio
        else:
            height = max_width / self._aspect_ratio
            width = max_width
        self.SetSize(round(width), round(height))
        return super(AspectRatioContainer, self).UpdateAlignment(*args, **kwargs)
