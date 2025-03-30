#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\musicDebuggerSvc.py
from carbon.common.script.sys.service import Service
from eveaudio.fsdUtils import GetMusicTriggerFromOperation
from fsdBuiltData.client.musicTriggers import GetMusicTrigger

class MusicDebuggerSvc(Service):
    __guid__ = 'svc.musicDebugger'
    __servicename__ = 'musicDebugger'
    __displayname__ = 'Music Debugger'
    __dependencies__ = ['insider']
    __exportedcalls__ = {'SetDungeonChangeCallback': []}
    __notifyevents__ = ['OnAbyssalContentFinished', 'OnDungeonEntered', 'OnDungeonExited']

    def __init__(self):
        super(MusicDebuggerSvc, self).__init__()
        self.dungeonChangeCallback = None

    def SetDungeonChangeCallback(self, pythonFunc):
        self.dungeonChangeCallback = pythonFunc

    def OnAbyssalContentFinished(self, *args, **kwargs):
        if self.dungeonChangeCallback:
            self.dungeonChangeCallback(0)

    def OnDungeonEntered(self, dungeonID, instanceID):
        if self.dungeonChangeCallback:
            self.dungeonChangeCallback(dungeonID)

    def OnDungeonExited(self, dungeonID, instanceID):
        if self.dungeonChangeCallback:
            self.dungeonChangeCallback(0)
