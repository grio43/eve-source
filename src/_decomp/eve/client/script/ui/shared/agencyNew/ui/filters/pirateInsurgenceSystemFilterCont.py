#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\pirateInsurgenceSystemFilterCont.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.common.script.util.facwarCommon import GetPirateFWFactions
from localization import GetByLabel
CORRUPTION_OPTIONS = [ [GetByLabel('UI/Agency/PirateIncursions/StageX', stage=x), x] for x in xrange(0, 6) ]

class PirateInsurgenceSystemFilterCont(BaseFiltersCont):
    default_name = 'PirateInsurgenceSystemFilterCont'

    def ConstructFilters(self):
        self.ConstructDistanceCombo()
        self.ConstructFactionCombo()
        self.ConstructCorruptionCombo()
        self.ConstrucSuppressionCombo()

    def ConstructFactionCombo(self):
        self.factionCombo = FilterCombo(name='factionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Faction'), options=self._GetFactionOptions(), callback=self.OnFactionCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SYSTEMFACTION))

    def ConstructCorruptionCombo(self):
        self.corruptionCombo = FilterCombo(name='corruptionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/PirateIncursions/CorruptionStage'), options=self._GetCorruptionSuppressionOptions(), callback=self.OnCorruptionCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_CORRUPTION))

    def ConstrucSuppressionCombo(self):
        self.suppressionCombo = FilterCombo(name='suppressionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Agency/PirateIncursions/SuppressionStage'), options=self._GetCorruptionSuppressionOptions(), callback=self.OnSuppressionCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SUPPRESSION))

    def _GetFactionOptions(self):
        factionIDs = set((factionID for factionID in GetPirateFWFactions()))
        options = [ (cfg.eveowners.Get(factionID).name, factionID) for factionID in factionIDs ]
        options.sort()
        options.insert(0, [GetByLabel('UI/Agency/AnyFaction'), agencyConst.FILTERVALUE_ANY])
        return options

    def OnFactionCombo(self, comboBox, key, factionID):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SYSTEMFACTION, factionID)

    def _GetCorruptionSuppressionOptions(self):
        options = CORRUPTION_OPTIONS[:]
        options.sort()
        options.insert(0, [GetByLabel('UI/Agency/PirateIncursions/AnyStage'), agencyConst.FILTERVALUE_ANY])
        return options

    def OnCorruptionCombo(self, comboBox, key, corruptionStage):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_CORRUPTION, corruptionStage)

    def OnSuppressionCombo(self, comboBox, key, suppressionStage):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_SUPPRESSION, suppressionStage)
