#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\exploration\escalationsContentGroup.py
from eve.client.script.ui.shared.agencyNew.agencyUtil import GetTimeRemainingText
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageEscalations import ContentPageEscalations
from localization import GetByLabel

class EscalationsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupEscalations

    def IsEnabled(self):
        return bool(self.GetContentPieces())

    def GetDisabledHint(self):
        return GetByLabel('UI/Agency/EscalationsDisabledHint')

    def GetTimeRemaining(self):
        timesRemaining = [ contentPiece.GetTimeRemaining() for contentPiece in self.GetContentPieces() ]
        if timesRemaining:
            return min(timesRemaining)

    def GetExpiryTimeText(self):
        return GetTimeRemainingText(self.GetTimeRemaining())

    def IsNewContentAvailable(self):
        return self.IsEnabled()

    @staticmethod
    def GetContentPageClass():
        return ContentPageEscalations
