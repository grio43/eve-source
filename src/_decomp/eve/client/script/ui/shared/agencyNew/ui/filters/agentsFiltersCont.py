#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\agentsFiltersCont.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui.filters.baseFiltersCont import BaseFiltersCont
from eve.client.script.ui.shared.agencyNew.ui.controls.filterCombo import FilterCombo
from eve.common.lib import appConst
from localization import GetByLabel
from npcs.npccorporations import get_corporation_ids_by_faction_id

class AgentsFiltersCont(BaseFiltersCont):
    default_name = 'AgentsFiltersCont'

    def ConstructFilters(self):
        FilterCombo(name='agentLevelCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/AgentFinder/AgentLevel'), options=self.GetLevelComboOptions(), callback=self.OnLevelCombo, select=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTLEVEL))
        self.ConstructDistanceCombo()
        self.ConstructSecurityCombo()
        FilterCombo(name='agentFactionCombo', parent=self.filtersCont, align=uiconst.TOTOP, label=GetByLabel('UI/Common/Faction'), options=self.GetFactions(), callback=self.OnFactionCombo, select=self.GetSelectedFaction())
        selectValue = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTCORP)
        self.corpCombo = FilterCombo(name='corpCombo', parent=self.filtersCont, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, label=GetByLabel('UI/Common/Corp'), callback=self.OnCorpCombo, select=selectValue)
        factionID = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTFACTION)
        self.UpdateCorpCombo(factionID)
        checkBoxContainer = Container(name='checkBoxContainer', parent=self.filtersCont, align=uiconst.TOTOP, top=10, height=20)
        Checkbox(parent=checkBoxContainer, align=uiconst.CENTERRIGHT, checked=agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTIGNORESTANDINGSREQUIREMENT), callback=self.OnOnlyShowAvailableCheckbox)
        EveLabelMedium(parent=checkBoxContainer, align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/OnlyShowAvailableAgents'))

    def GetSelectedFaction(self):
        return agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTFACTION)

    def OnFactionCombo(self, comboBox, key, factionID):
        self.UpdateCorpCombo(factionID)
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTFACTION, factionID)

    def UpdateCorpCombo(self, factionID):
        corpIDs = get_corporation_ids_by_faction_id(factionID, default=[])
        options = self.GetCorpComboOptions(corpIDs)
        filterValue = self._GetCorpComboFiltervalue(corpIDs)
        self.corpCombo.LoadOptions(options, select=filterValue)
        self.corpCombo.display = self.ShouldShowCorpCombo(factionID)

    def _GetCorpComboFiltervalue(self, corpIDs):
        filterValue = agencyFilters.GetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTCORP)
        if filterValue not in corpIDs:
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_AGENTCORP, agencyConst.FILTERVALUE_ANY)
            filterValue = agencyConst.FILTERVALUE_ANY
        return filterValue

    def ShouldShowCorpCombo(self, factionID):
        showCorpCombo = factionID != agencyConst.FILTERVALUE_ANY
        return showCorpCombo

    def OnLevelCombo(self, comboBox, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTLEVEL, value)

    def GetLevelComboOptions(self):
        levels = [(GetByLabel('UI/Agency/HighestAvailable'), agencyConst.AGENTLEVEL_HIGHESTAVAILABLE), (GetByLabel('UI/Agency/AnyLevel'), agencyConst.FILTERVALUE_ANY)]
        levels.extend([ (GetByLabel('UI/Agency/LevelX', level=i), i) for i in xrange(1, self.GetMaxLevel()) ])
        return levels

    def GetMaxLevel(self):
        return 6

    def OnCorpCombo(self, comboBox, key, value):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTCORP, value)

    def GetFactions(self):
        factionIDs = set((factionID for factionID in appConst.factions if factionID not in appConst.factionsWithoutAgents))
        options = [ (self._GetLabelWithStanding(factionID), factionID) for factionID in factionIDs ]
        options.sort()
        options.insert(0, [GetByLabel('UI/Agency/AnyFaction'), agencyConst.FILTERVALUE_ANY])
        return options

    def GetCorpComboOptions(self, corpIDs):
        options = []
        for corpID in corpIDs:
            label = self._GetLabelWithStanding(corpID)
            options.append([label, corpID])

        options.sort()
        options.insert(0, [GetByLabel('UI/Agency/AnyCorp'), agencyConst.FILTERVALUE_ANY])
        return options

    def _GetLabelWithStanding(self, ownerID):
        standing = sm.GetService('standing').GetStandingWithSkillBonus(ownerID, session.charid)
        ownerName = cfg.eveowners.Get(ownerID).name
        label = "%s <color='gray'>%s</color>" % (ownerName, round(standing, 2))
        return label

    def OnOnlyShowAvailableCheckbox(self, checkbox):
        agencyFilters.SetFilterValue(self.contentGroupID, agencyConst.FILTERTYPE_AGENTIGNORESTANDINGSREQUIREMENT, checkbox.GetValue())
