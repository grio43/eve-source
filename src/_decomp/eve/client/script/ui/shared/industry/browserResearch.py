#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\browserResearch.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.control.scrollentries import SE_BaseClassCore
import evetypes
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.util import uix
from eveservices.menu import GetMenuService
import localization
HEADERS = ['UI/Agents/Agent',
 'UI/Agents/Research/ResearchFieldShort',
 'UI/Agents/Research/CurrentResearchPointsTitle',
 'UI/Agents/Research/ResearchPointsRateTitle',
 'UI/Agents/AgentLevel',
 'UI/Common/Location']
NO_CONTENT_HINT = 'UI/Agents/Research/NoResearchBeingPerformed'

class BrowserResearch(Container):
    __notifyevents__ = ['OnSessionChanged', 'OnAgentMissionChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isInitialized = False
        sm.RegisterNotify(self)

    def GetResearchData(self):
        return sm.GetService('journal').GetMyAgentJournalDetails()[1]

    def OnTabSelect(self):
        self.UpdateScroll()

    def UpdateScroll(self):
        if not self.isInitialized:
            self.scroll = Scroll(parent=self, id='ResearchBrowser')
            self.isInitialized = True
        self.scroll.ShowLoading()
        scrollList = []
        research = self.GetResearchData()
        for data in research:
            researchEntry = self._MakeResearchEntry(data)
            scrollList.append(researchEntry)

        self.scroll.Load(contentList=scrollList, headers=[ localization.GetByLabel(header) for header in HEADERS ], noContentHint=localization.GetByLabel(NO_CONTENT_HINT))
        self.scroll.HideLoading()

    def _MakeResearchEntry(self, data):
        agentID, researchFieldTypeID, pointsPerDay, currentPoints, level, quality, stationID = data
        researchFieldName = evetypes.GetName(researchFieldTypeID)
        agentName = cfg.eveowners.Get(agentID).name
        stationName = cfg.evelocations.Get(stationID).name
        solarSystemID = sm.GetService('ui').GetStationStaticInfo(stationID).solarSystemID
        text = '<t>'.join([agentName,
         researchFieldName,
         localization.formatters.FormatNumeric(currentPoints, decimalPlaces=2, useGrouping=True),
         localization.formatters.FormatNumeric(pointsPerDay, decimalPlaces=2, useGrouping=True),
         localization.formatters.FormatNumeric(level, decimalPlaces=0),
         stationName])
        return GetFromClass(ResearchEntry, {'agentID': agentID,
         'text': text,
         'label': text,
         'solarSystemID': solarSystemID})

    def OnAgentMissionChange(self, _action, _agentID):
        self.UpdateScroll()

    def OnSessionChanged(self, _isRemote, _session, _change):
        self.UpdateScroll()


class ResearchEntry(SE_BaseClassCore):
    __guid__ = 'listentry.ResearchEntry'

    def Startup(self, *etc):
        self.sr.label = EveLabelMedium(parent=self, left=5, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.line = Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)

    def GetHeight(_self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)

    @classmethod
    def GetCopyData(cls, node):
        return node.label

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = node.label

    @property
    def agentID(self):
        return self.sr.node.agentID

    @property
    def agentTypeID(self):
        return cfg.eveowners.Get(self.agentID).typeID

    def ShowInfo(self):
        sm.GetService('info').ShowInfo(self.agentTypeID, self.agentID)

    def GetMenu(self):
        return GetMenuService().CharacterMenu(self.agentID)
