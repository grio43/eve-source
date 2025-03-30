#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\factionalWarfareSystemFiltersCont.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.agencyConst import ADJACENCY_FILTERS
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.common.lib import appConst
from factionwarfare.const import ADJACENCY_STATES
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_TEXT
from localization import GetByLabel

class FactionalWarfareSystemFiltersCont(BaseFiltersCont):
    default_name = 'FactionalWarfareSystemFiltersCont'

    def ConstructFilters(self):
        self.ConstructDistanceCombo()
        self.ConstructFactionCombo()
        self.ConstructAdjancyCombo()

    def ConstructFactionCombo(self):
        self.factionCombo = FilterCombo(name='factionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Faction'), options=self._GetFactionOptions(), callback=self.OnFactionCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SYSTEMFACTION))

    def ConstructAdjancyCombo(self):
        self.adjancyCombo = FilterCombo(name='adjancyCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/Adjacency'), options=self._GetAdjacencyOptions(), callback=self.OnAdjacencyComboChanged, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_FWADJACENCY))

    def _GetFactionOptions(self):
        factionIDs = set((factionID for factionID in appConst.factionsEmpires if factionID not in appConst.factionsWithoutAgents))
        options = [ (cfg.eveowners.Get(factionID).name, factionID) for factionID in factionIDs ]
        options.sort()
        options.insert(0, [GetByLabel('UI/Agency/AnyFaction'), agencyConst.FILTERVALUE_ANY])
        return options

    def OnFactionCombo(self, comboBox, key, factionID):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SYSTEMFACTION, factionID)

    def _GetAdjacencyOptions(self):
        options = [ (ADJACENCY_TO_LABEL_TEXT.get(key), value) for key, value in ADJACENCY_FILTERS.iteritems() ]
        options.insert(0, [GetByLabel('UI/Agency/AnyAdjacency'), agencyConst.FILTERVALUE_ANY])
        return options

    def OnAdjacencyComboChanged(self, comboBox, key, adjacencyValue):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_FWADJACENCY, adjacencyValue)
