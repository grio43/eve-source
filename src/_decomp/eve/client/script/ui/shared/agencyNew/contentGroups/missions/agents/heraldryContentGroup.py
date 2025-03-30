#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\agents\heraldryContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageHeraldryAgents import ContentPageHeraldryAgents

class HeraldryContentGroup(BaseContentGroup):

    @staticmethod
    def GetContentPageClass():
        return ContentPageHeraldryAgents

    @staticmethod
    def IsContentAvailable():
        return sm.GetService('agents').IsHeraldryAvailable()

    def IsEnabled(self):
        return sm.GetService('agents').IsHeraldryAvailable()
