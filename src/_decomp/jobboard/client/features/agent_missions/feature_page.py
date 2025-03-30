#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\agent_missions\feature_page.py
import localization
from jobboard.client.ui.pages.content_tag_page import ContentTagPage

class AgentMissionsFeaturePage(ContentTagPage):

    @property
    def info_tooltip(self):
        return localization.GetByLabel('UI/Opportunities/VisibilityAgentMissions')
