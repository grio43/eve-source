#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderDistributionAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.contentProviderAgents import ContentProviderAgents
from eve.common.lib import appConst

class ContentProviderDistributionAgents(ContentProviderAgents):
    contentType = agencyConst.CONTENTTYPE_DISTRIBUTIONAGENTS
    contentGroup = contentGroupConst.contentGroupMissionAgentsDistribution

    def CheckDivisionValidCriteria(self, agent):
        return agent.divisionID == appConst.corpDivisionDistribution

    def CheckAgentTypeIDCriteria(self, agent):
        return agent.agentTypeID == appConst.agentTypeBasicAgent
