#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\tagsFSDLoader.py
import tagsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class TagsFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/tags.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/tags.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/tags.fsdbinary'
    __loader__ = tagsLoader

    @classmethod
    def GetByID(cls, tagID):
        return cls.GetData().get(tagID, None)
