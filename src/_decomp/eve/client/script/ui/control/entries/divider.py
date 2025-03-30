#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\divider.py
from carbonui.control.scrollentries import SE_BaseClassCore

class DividerEntry(SE_BaseClassCore):
    __guid__ = 'listentry.Divider'
    __params__ = []
    default_showHilite = False

    def Load(self, node):
        self.sr.node = node

    def GetHeight(self, *args):
        node, width = args
        node.height = node.Get('height', 0) or 12
        return node.height
