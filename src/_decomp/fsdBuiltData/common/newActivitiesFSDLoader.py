#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\newActivitiesFSDLoader.py
import newActivitiesLoader
from fsdBuiltData.common.base import BuiltDataLoader

class NewActivitiesFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/newActivities.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/newActivities.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/newActivities.fsdbinary'
    __loader__ = newActivitiesLoader
