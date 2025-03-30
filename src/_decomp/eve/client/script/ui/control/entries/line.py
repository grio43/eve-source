#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\line.py
from carbonui.control.scrollentries import SE_BaseClassCore

class Line(SE_BaseClassCore):
    __guid__ = 'listentry.Line'
    __params__ = []
    default_showHilite = False

    def Load(self, node):
        self.sr.node = node
        self.sr.node.height = getattr(node, 'height', 1)

    def GetHeight(self, *args):
        node, width = args
        return node.height
