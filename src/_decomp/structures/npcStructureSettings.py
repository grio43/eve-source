#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\npcStructureSettings.py
from brennivin.itertoolsext import FrozenDict
from caching import Memoize
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import npcStructureSettingsLoader
except ImportError:
    npcStructureSettingsLoader = None

class NpcStructureSettings(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/npcStructureSettings.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticData/server/npcStructureSettings.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/npcStructureSettings.fsdbinary'
    __loader__ = npcStructureSettingsLoader


@Memoize
def GetNpcStructureSettings(structureTypeID):
    structureSettings = NpcStructureSettings.GetData().get(structureTypeID, None)
    if not structureSettings:
        return frozenset()
    return structureSettings


@Memoize
def GetFwNpcStructureSettingValueForSettingID(settingID, structureTypeID):
    allSettings = GetNpcStructureSettings(structureTypeID)
    if not allSettings:
        return FrozenDict()
    return FrozenDict(allSettings.warFactionIdBased.get(settingID, {}))
