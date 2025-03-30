#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\divider_line.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill

class DividerLine(Container):
    _line = None

    def __init__(self, parent = None, width = 1, height = 1, **kwargs):
        super(DividerLine, self).__init__(parent=parent, width=width, height=height, **kwargs)
        self._line = Fill(parent=self, align=uiconst.TOALL, color=(1.0, 1.0, 1.0, 0.1))
