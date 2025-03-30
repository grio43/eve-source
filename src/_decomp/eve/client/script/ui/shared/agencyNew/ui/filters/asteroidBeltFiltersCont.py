#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\asteroidBeltFiltersCont.py
import evetypes
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew import agencyFilters, agencyConst
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from evedungeons.client.oreTypesInDungeons.const import ORE_TYPES_BY_VALUE
from localization import GetByLabel

class AsteroidBeltFiltersCont(BaseFiltersCont):
    default_name = 'AsteroidBeltFiltersCont'

    def ConstructFilters(self):
        super(AsteroidBeltFiltersCont, self).ConstructFilters()
        self.ConstructOreTypeCombo()

    def ConstructOreTypeCombo(self):
        self.oreTypeCombo = FilterCombo(name='oreTypeCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Ledger/OreTypeFilter'), options=self._GetOreTypeOptions(), callback=self.OnOreTypeCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ORETYPE))

    def _GetOreTypeOptions(self):
        options = [(GetByLabel('UI/Generic/Any'), agencyConst.FILTERVALUE_ANY)]
        oreTypeOptions = [ (evetypes.GetName(oreTypeID), oreTypeID) for oreTypeID in ORE_TYPES_BY_VALUE ]
        oreTypeOptions.sort(key=lambda oreOption: oreOption[0])
        options.extend(oreTypeOptions)
        return options

    def OnOreTypeCombo(self, comboBox, key, oreTypeID):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_ORETYPE, oreTypeID)
