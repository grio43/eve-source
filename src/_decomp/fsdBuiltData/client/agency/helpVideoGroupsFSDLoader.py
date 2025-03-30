#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\agency\helpVideoGroupsFSDLoader.py
import agencyHelpVideoGroupsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class AgencyHelpVideoGroupsFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/agencyHelpVideoGroups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/agencyHelpVideoGroups.fsdbinary'
    __loader__ = agencyHelpVideoGroupsLoader

    @classmethod
    def GetByID(cls, groupID):
        return cls.GetData().get(groupID, None)
