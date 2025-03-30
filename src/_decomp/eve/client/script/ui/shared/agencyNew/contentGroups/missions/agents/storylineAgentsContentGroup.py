#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\missions\agents\storylineAgentsContentGroup.py
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetTimeRemainingText
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageStorylineAgents import ContentPageStorylineAgents
from localization import GetByLabel

class StorylineAgentsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupStorylineAgents

    def IsEnabled(self):
        return bool(self.GetContentProvider().GetActiveStorylineAgents())

    def GetDisabledHint(self):
        return GetByLabel('UI/Agency/StorylineAgentsDisabledHint')

    def GetTimeRemaining(self):
        timesRemaining = [ contentPiece.GetTimeRemaining() for contentPiece in self.GetContentPieces() if contentPiece.GetTimeRemaining() > 0 ]
        if timesRemaining:
            return min(timesRemaining)

    def GetExpiryTimeText(self):
        return GetTimeRemainingText(self.GetTimeRemaining())

    def IsNewContentAvailable(self):
        return self.IsEnabled()

    @staticmethod
    def GetContentPageClass():
        return ContentPageStorylineAgents
