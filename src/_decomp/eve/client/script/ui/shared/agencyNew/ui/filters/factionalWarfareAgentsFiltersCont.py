#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\filters\factionalWarfareAgentsFiltersCont.py
from eve.client.script.ui.shared.agencyNew import agencyConst, agencyFilters
from eve.client.script.ui.shared.agencyNew.ui.filters.agentsFiltersCont import AgentsFiltersCont
from eve.common.lib import appConst
from localization import GetByLabel

class FactionalWarfareAgentsFiltersCont(AgentsFiltersCont):

    def GetFactions(self):
        options = sorted([ (self._GetLabelWithStanding(factionID), factionID) for factionID in appConst.factionsEmpires ])
        options.insert(0, (GetByLabel('UI/Agency/AnyFaction'), agencyConst.FILTERVALUE_ANY))
        return options

    def ShouldShowCorpCombo(self, factionID):
        return False

    def GetMaxLevel(self):
        return 5

    def GetSelectedFaction(self):
        savedFaction = super(FactionalWarfareAgentsFiltersCont, self).GetSelectedFaction()
        if savedFaction == agencyConst.FILTERVALUE_ANY:
            if not session.warfactionid:
                return savedFaction
            warFactionID = session.warfactionid
            agencyFilters.SetFilterValueWithoutEvent(self.contentGroupID, agencyConst.FILTERTYPE_AGENTFACTION, warFactionID)
            return warFactionID
        return savedFaction

    def GetDefaultFilters(self):
        if not session.warfactionid:
            return agencyConst.FILTER_DEFAULTS
        defaultCopy = agencyConst.FILTER_DEFAULTS.copy()
        defaultCopy[agencyConst.FILTERTYPE_AGENTFACTION] = session.warfactionid
        return defaultCopy
