#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\agency\helpVideoFSDLoader.py
import agencyHelpVideosLoader
from fsdBuiltData.common.base import BuiltDataLoader

class AgencyHelpVideosFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/agencyHelpVideos.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/agencyHelpVideos.fsdbinary'
    __loader__ = agencyHelpVideosLoader

    @classmethod
    def GetByID(cls, videoID):
        return cls.GetData().get(videoID, None)
