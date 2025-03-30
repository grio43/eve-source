#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelUsedWith.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.item import GetItemEntriesByMetaGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.common.lib import appConst

class PanelUsedWith(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.isInitialized = False

    def Load(self):
        if self.isInitialized:
            return
        self.scroll = Scroll(name='scroll', parent=self, padding=appConst.defaultPadding)
        scrolllist = self.GetScrollList(self.typeID)
        self.scroll.Load(fixedEntryHeight=27, contentList=scrolllist)
        self.isInitialized = True

    def GetScrollList(self, data, *args):
        usedWith = sm.GetService('info').GetUsedWithTypeIDs(self.typeID)
        return GetItemEntriesByMetaGroup(usedWith)
