#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\helpContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageHelp import ContentPageHelp
from localization import GetByMessageID
import evelink
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from fsdBuiltData.client.agency.helpVideoFSDLoader import AgencyHelpVideosFSDLoader

class HelpContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupHelp

    def GetNameWithLink(self, videoID = None, *args, **kwargs):
        if not videoID:
            return
        video = AgencyHelpVideosFSDLoader.GetByID(videoID)
        nameID = video.nameID
        videoPath = video.path
        return evelink.local_service_link(method='AgencyOpenAndShowHelpVideo', text='%s: %s' % (self.GetName(), GetByMessageID(nameID)), contentGroupID=self.contentGroupID, itemID=self.itemID, videoID=videoID, videoPath=videoPath)

    @staticmethod
    def GetContentPageClass():
        return ContentPageHelp

    @staticmethod
    def IsTabGroup():
        return True
