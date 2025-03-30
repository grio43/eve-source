#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\skillTreeGroups.py
import skillTreeGroupsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class SkillTreeGroupsFSDLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/skillTreeGroups.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/skillTreeGroups.fsdbinary'
    __loader__ = skillTreeGroupsLoader
