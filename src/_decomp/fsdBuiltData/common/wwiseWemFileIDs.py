#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\wwiseWemFileIDs.py
import wwiseWemFileIDsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class WwiseWemFileIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/wwiseWemFileIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/wwiseWemFileIDs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/wwiseWemFileIDs.fsdbinary'
    __loader__ = wwiseWemFileIDsLoader

    def __init__(self):
        super(WwiseWemFileIDs, self).__init__()
        self.wwiseWemFileIDsDict = self.TransformToDict()

    def TransformToDict(self):
        wemFileIDDict = {}
        wemFileIDs = self.GetData()
        for wemFileID, wemFileData in wemFileIDs.iteritems():
            wemFileIDDict[wemFileID] = {'IsEssential': wemFileData.IsEssential}

        return wemFileIDDict
