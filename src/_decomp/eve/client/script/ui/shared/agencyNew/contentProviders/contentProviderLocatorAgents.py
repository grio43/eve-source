#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderLocatorAgents.py
from eve.client.script.ui.shared.agencyNew import agencyConst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.contentProviderAgents import ContentProviderAgents
from eve.common.lib import appConst

class ContentProviderLocatorAgents(ContentProviderAgents):
    contentType = agencyConst.CONTENTTYPE_LOCATORAGENTS
    contentGroup = contentGroupConst.contentGroupMissionAgentsLocator

    def CheckDivisionValidCriteria(self, agent):
        return agent.isLocatorAgent
