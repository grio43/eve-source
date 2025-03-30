#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\mouse_inside_scroll_entry.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import SE_BaseClassCore

class MouseInsideScrollEntry(SE_BaseClassCore):
    onMouseEntyerThread = None

    def OnMouseEnter(self, *args):
        if self.onMouseEntyerThread is None:
            SE_BaseClassCore.OnMouseEnter(self, *args)
            self.onMouseEntyerThread = AutoTimer(10, self.MonitorMouseOver)

    def OnMouseExit(self, *args):
        if not self.IsMouseInsideEntry():
            self.OnMouseNoLongerInEntry()

    def KillHilite(self):
        SE_BaseClassCore.OnMouseExit(self)
        self.onMouseEntyerThread = None

    def MonitorMouseOver(self):
        if self.destroyed:
            self.onMouseEntyerThread = None
        elif not self.IsMouseInsideEntry():
            self.OnMouseNoLongerInEntry()

    def OnMouseNoLongerInEntry(self):
        self.KillHilite()
