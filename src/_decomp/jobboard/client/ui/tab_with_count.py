#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\tab_with_count.py
import carbonui
import eveui
from carbonui.control.tab import Tab
from eve.client.script.ui import eveColor, eveThemeColor

class TabWithCount(Tab):

    def __init__(self, count = 0, count_bg_color = None, *args, **kwargs):
        self._count = count
        self._count_bg_color = count_bg_color
        super(TabWithCount, self).__init__(*args, **kwargs)

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        if self._count == value:
            return
        self._count = value
        self._count_label.text = str(self.count)
        self._count_label.color = carbonui.TextColor.NORMAL if self._count > 0 else carbonui.TextColor.SECONDARY

    def _ConstructLabel(self):
        super(TabWithCount, self)._ConstructLabel()
        self._count_container = eveui.ContainerAutoSize(parent=self, align=carbonui.Align.CENTERLEFT)
        self._count_label = carbonui.TextBody(parent=self._count_container, align=carbonui.Align.CENTER, text=str(self._count), padding=(6, 0, 6, 0), color=carbonui.TextColor.SECONDARY)
        self._bg_frame = eveui.Frame(bgParent=self._count_container, color=self._count_bg_color or eveThemeColor.THEME_FOCUSDARK, opacity=0.4, frameConst=carbonui.uiconst.FRAME_FILLED_CORNER4)

    def UpdateTabSize(self):
        self._count_container.left = self.label.left + self.label.width + 4
        self.sr.width = self._count_container.left + self._count_container.GetAbsoluteSize()[0]

    def OnColorThemeChanged(self):
        super(TabWithCount, self).OnColorThemeChanged()
        color = (self._count_bg_color or eveThemeColor.THEME_FOCUSDARK)[:3]
        self._bg_frame.rgb = color
