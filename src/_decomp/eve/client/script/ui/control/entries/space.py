#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\space.py
from carbonui.control.scrollentries import SE_BaseClassCore

class Space(SE_BaseClassCore):
    __guid__ = 'listentry.Space'
    __params__ = ['height']
    default_showHilite = False

    def Load(self, node):
        self.sr.node = node

    def GetHeight(self, *args):
        node, width = args
        node.height = node.height
        return node.height
