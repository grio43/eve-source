#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\soundIDs.py
import soundIDsLoader
from fsdBuiltData.common.base import BuiltDataLoader
from fsdBuiltData.common.wwiseEvents import GetWwiseEventName

class SoundIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/soundIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/soundIDs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/soundIDs.fsdbinary'
    __loader__ = soundIDsLoader

    def __init__(self):
        super(SoundIDs, self).__init__()


def GetSound(soundID):
    return SoundIDs.GetData().get(soundID, None)


def GetSoundAttribute(soundID, attributeName, default = None):
    if isinstance(soundID, (int, long)):
        return getattr(GetSound(soundID), attributeName, None) or default
    return getattr(soundID, attributeName, None) or default


def GetSoundIDDictionary():
    return SoundIDs.GetData()


def GetSoundEventName(soundID, default = None):
    wwiseID = GetSoundAttribute(soundID, 'wwiseEvent', default)
    if wwiseID:
        eventName = GetWwiseEventName(wwiseID)
        if eventName:
            return eventName
    return default
