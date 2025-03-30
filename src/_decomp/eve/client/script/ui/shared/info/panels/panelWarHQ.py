#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelWarHQ.py
import uthread
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.corporation.war.warEntry import WarEntrySimple
from eve.common.lib import appConst as const
from localization import GetByLabel

class WarHQ(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureID = attributes.structureID
        self.wars = None

    def Load(self):
        self.Flush()
        self.warHqScroll = Scroll(name='warHqScroll', parent=self, padding=const.defaultPadding)
        uthread.new(self._LoadWars)

    def _LoadWars(self):
        text = GetByLabel('UI/InfoWindow/WarHQHeader')
        scrollList = [GetFromClass(Header, {'label': text})]
        wars = self.GetWars()
        wars = sorted(wars, key=lambda x: x.timeDeclared, reverse=True)
        for war in wars:
            scrollList.append(GetFromClass(WarEntrySimple, {'war': war,
             'label': ''}))

        self.warHqScroll.Load(contentList=scrollList)

    def GetWars(self):
        if self.wars is None:
            self.wars = sm.RemoteSvc('warsInfoMgr').GetWarsForStructure(self.structureID)
        return self.wars
