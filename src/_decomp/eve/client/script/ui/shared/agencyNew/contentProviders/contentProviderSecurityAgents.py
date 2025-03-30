#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderSecurityAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.contentProviderAgents import ContentProviderAgents
from eve.common.lib import appConst

class ContentProviderSecurityAgents(ContentProviderAgents):
    contentType = agencyConst.CONTENTTYPE_SECURITYAGENTS
    contentGroup = contentGroupConst.contentGroupMissionAgentsSecurity

    def CheckDivisionValidCriteria(self, agent):
        return agent.divisionID == appConst.corpDivisionSecurity

    def CheckAgentTypeIDCriteria(self, agent):
        return agent.agentTypeID == appConst.agentTypeBasicAgent
