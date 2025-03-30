#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\musicTriggers.py
import musicTriggersLoader
from fsdBuiltData.common.base import BuiltDataLoader

class MusicTriggers(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/musicTriggers.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/musicTriggers.fsdbinary'
    __loader__ = musicTriggersLoader


def GetMusicTriggers():
    return MusicTriggers.GetData()


def GetMusicTrigger(musicTriggerID):
    musicTrigger = MusicTriggers.GetData().get(musicTriggerID, {})
    return musicTrigger
