#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\paragonLpStoreFilters.py
import eveicon
import characterdata.factions
import evetypes
from carbonui.control.combo import Combo
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.services.setting import SessionSettingBool
from carbonui.button.menu import MenuButtonIcon
from eve.common.lib import appConst
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.station.loyaltyPointStore.lpStoreFilters import LPStoreFiltersBase
from carbonui import uiconst
from localization import GetByLabel
from eve.client.script.ui.station.loyaltyPointStore.paragonLpStoreConst import FILTER_ACQUIRED, FILTER_ALLIANCE_EMBLEMS, FILTER_ALL_FACTIONS, FILTER_ALL_HULLS, FILTER_CORP_EMBLEMS, FILTER_FACTION, FILTER_HULL, FILTER_OTHER_FACTIONS
ADDITIONAL_FILTERS_PANEL_MIN_WIDTH = 32
ADDITIONAL_FILTERS_PANEL_MIN_HEIGHT = 32
ADDITIONAL_FILTERS_PANEL_WIDTH = 230
ADDITIONAL_FILTERS_PANEL_HEIGHT = 145
ADDITIONAL_FILTERS_ANIM_DURATION = 0.1
ADDITIONAL_FILTERS_FADE_DURATION = 0.2

class ParagonLPStoreFilters(LPStoreFiltersBase):

    def ApplyAttributes(self, attributes):
        self.lpSvc = sm.GetService('lpstore')
        self.filters = {}
        self._InitFilters()
        self.corporationEmblemsSetting = SessionSettingBool(self.filters[FILTER_CORP_EMBLEMS])
        self.corporationEmblemsSetting.on_change.connect(self._OnChange)
        self.allianceEmblemsSetting = SessionSettingBool(self.filters[FILTER_ALLIANCE_EMBLEMS])
        self.allianceEmblemsSetting.on_change.connect(self._OnChange)
        self.acquiredEmblemsSetting = SessionSettingBool(self.filters[FILTER_ACQUIRED])
        self.acquiredEmblemsSetting.on_change.connect(self._OnChange)
        super(ParagonLPStoreFilters, self).ApplyAttributes(attributes)

    def Close(self):
        self.corporationEmblemsSetting.on_change.disconnect(self._OnChange)
        self.allianceEmblemsSetting.on_change.disconnect(self._OnChange)
        self.acquiredEmblemsSetting.on_change.disconnect(self._OnChange)
        super(ParagonLPStoreFilters, self).Close()

    def ConstructLayout(self):
        self._ConstructCombos()
        self._ConstructAdditionalFilters()
        self._ConstructSearchBar()

    def _ConstructCombos(self):
        self.factionCombo = Combo(parent=self, name='factionCombo', align=uiconst.TOLEFT, padLeft=4, width=180, callback=self._OnChange)
        self._PopulateFactionCombo()
        self.hullTypeCombo = Combo(parent=self, name='hullTypeCombo', align=uiconst.TOLEFT, padLeft=4, width=180, callback=self._OnChange)
        self._PopulateHullCombo()

    def _ConstructAdditionalFilters(self):
        self.filterBtn = MenuButtonIcon(parent=self, name='filterBtn', align=uiconst.TOLEFT, padLeft=4, texturePath=eveicon.tune, get_menu_func=self._GetAdditionalFiltersMenu)

    def _ConstructSearchBar(self):
        self.filterEdit = QuickFilterEdit(name='filterEdit', parent=self, hintText=GetByLabel('UI/Common/Search'), maxLength=64, OnClearFilter=self._OnFilterEditCleared, align=uiconst.TORIGHT, width=120, isTypeField=True)
        self.filterEdit.ReloadFunction = self._OnFilterEdit

    def _PopulateFactionCombo(self):
        options = []
        for factionID in appConst.factionByRace.values():
            name = characterdata.factions.get_faction_name(factionID)
            options.append((name, factionID))

        options.sort(cmp=_cmp)
        options.insert(0, (GetByLabel('UI/LPStore/AllFactionsComboEntry'), FILTER_ALL_FACTIONS))
        options.append((GetByLabel('UI/LPStore/OtherFactionsComboEntry'), FILTER_OTHER_FACTIONS))
        self.factionCombo.LoadOptions(options)
        self.factionCombo.SetValue(self.filters[FILTER_FACTION])

    def _PopulateHullCombo(self):
        options = []
        groupIDs = sm.GetService('cosmeticsLicenseSvc').get_all_licensed_ship_groups()
        for groupID in groupIDs:
            name = evetypes.GetGroupNameByGroup(groupID)
            options.append((name, groupID))

        options.sort(cmp=_cmp)
        options.insert(0, (GetByLabel('UI/LPStore/AllHullsComboEntry'), FILTER_ALL_HULLS))
        self.hullTypeCombo.LoadOptions(options)
        self.hullTypeCombo.SetValue(self.filters[FILTER_HULL])

    def _GetAdditionalFiltersMenu(self):
        menuData = MenuData()
        menuData.AddCaption(GetByLabel('UI/LPStore/ParagonAdditionalFiltersTitle'))
        menuData.AddCheckbox(text=GetByLabel('UI/LPStore/ParagonAdditionalFilters_CorpEmblems'), setting=self.corporationEmblemsSetting)
        menuData.AddCheckbox(text=GetByLabel('UI/LPStore/ParagonAdditionalFilters_AllianceEmblems'), setting=self.allianceEmblemsSetting)
        menuData.AddCheckbox(text=GetByLabel('UI/LPStore/ParagonAdditionalFilters_HideAcquired'), setting=self.acquiredEmblemsSetting)
        return menuData

    def _OnChange(self, *args):
        self._UpdateFilters()
        self.lpSvc.ChangeParagonFilters(self.filters)

    def _UpdateFilters(self):
        self.filters[FILTER_FACTION] = self.factionCombo.GetValue()
        self.filters[FILTER_HULL] = self.hullTypeCombo.GetValue()
        self.filters[FILTER_CORP_EMBLEMS] = self.corporationEmblemsSetting.get()
        self.filters[FILTER_ALLIANCE_EMBLEMS] = self.allianceEmblemsSetting.get()
        self.filters[FILTER_ACQUIRED] = self.acquiredEmblemsSetting.get()

    def _InitFilters(self):
        self.filters = self.lpSvc.GetCurrentParagonFilters()

    def GetCurrentFilters(self):
        return (self.filters, self.filterEdit.GetValue().lstrip().lower())

    def Refresh(self):
        pass


def _cmp(a, b):
    if a[0] < b[0]:
        return -1
    elif a[0] > b[0]:
        return 1
    else:
        return 0
