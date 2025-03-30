#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsBrowser.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container

class StandingsBrowser(ScrollContainer):
    default_name = 'StandingsBrowser'

    def ApplyAttributes(self, attributes):
        ScrollContainer.ApplyAttributes(self, attributes)
        self.onSelected = attributes.onSelected

    def LoadEntries(self):
        self.Flush()
