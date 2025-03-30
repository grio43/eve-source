#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentProviders\contentProviderHelp.py
from utillib import KeyVal
from eve.client.script.ui.shared.agencyNew import agencyConst, agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentProviders.baseContentProvider import BaseContentProvider
from fsdBuiltData.client.agency.helpVideoFSDLoader import AgencyHelpVideosFSDLoader
from fsdBuiltData.client.agency.helpVideoGroupsFSDLoader import AgencyHelpVideoGroupsFSDLoader

class ContentProviderHelp(BaseContentProvider):
    contentType = agencyConst.CONTENTTYPE_HELP
    contentGroup = contentGroupConst.contentGroupHelp

    @staticmethod
    def GetVideoGroups():
        return AgencyHelpVideoGroupsFSDLoader.GetData()

    @staticmethod
    def GetVideoGroup(groupID):
        return AgencyHelpVideoGroupsFSDLoader.GetByID(groupID)

    @staticmethod
    def GetVideo(videoID):
        video = AgencyHelpVideosFSDLoader.GetByID(videoID)
        return KeyVal(id=videoID, nameID=video.nameID, descriptionID=video.descriptionID, path=video.path)
