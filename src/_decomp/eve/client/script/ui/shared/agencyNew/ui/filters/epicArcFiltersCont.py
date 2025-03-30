#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\epicArcFiltersCont.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from localization import GetByLabel

class EpicArcFiltersCont(BaseFiltersCont):
    default_name = 'EpicArcFiltersCont'

    def ConstructFilters(self):
        FilterCombo(parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Faction'), options=self.GetTypeOptions(), callback=self.OnTypeCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_EPICARCFACTION))

    def OnTypeCombo(self, comboBox, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_EPICARCFACTION, value)

    def GetTypeOptions(self):
        ret = [(GetByLabel('UI/Common/Any'), agencyConst.FILTERVALUE_ANY)]
        factionIDs = sm.GetService('epicArc').GetEpicArcFactionIDs()
        factionOptions = sorted([ (cfg.eveowners.Get(factionID).ownerName, factionID) for factionID in factionIDs ], key=lambda factionOption: factionOption[0])
        ret.extend(factionOptions)
        return ret
