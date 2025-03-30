#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\eveMusicService.py
import audio2
import gametime
import logging
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtDate
from eveaudio.const import MASTER_MUSIC_GRAPH
from eveaudio.eveaudiomanager import GetAudioManager
from eveaudio.fsdUtils import GetMusicTriggerFromConversation, GetMusicTriggerFromOperation
from eve.client.script.ui.view.viewStateConst import ViewState
from fsdBuiltData.client.musicTriggers import GetMusicTrigger
logger = logging.getLogger(__name__)

class DynamicMusicService(Service):
    __guid__ = 'svc.dynamicMusic'
    __exportedcalls__ = {'GetProcessedMusicEvents': [],
     'SetDebugMusicTriggerCallback': [],
     'StopMusic': []}
    __notifyevents__ = ['OnAudioActivated',
     'OnAudioDeactivated',
     'OnConversationStarted',
     'OnDungeonTriggerMusic',
     'OnOperationMadeActive',
     'OnViewStateChanged']
    __dependencies__ = ['audio']
    __startupdependencies__ = ['viewState', 'node_graph']

    def __init__(self):
        Service.__init__(self)

    def Run(self, *args):
        Service.Run(self, *args)
        self.audioManager = GetAudioManager()
        self.debugMusicTriggerCallback = None
        self.lastEventSent = ''
        self.masterMusicNodeGraph = None
        self.musicEmitter = audio2.GetMusicPlayer()
        self.processedEvents = []

    def GetProcessedMusicEvents(self):
        return self.processedEvents

    def MusicVolumeChangedByUser(self, volume):
        normalizedVolume = min(1.0, max(0.0, volume))
        self.audioManager.SetGlobalRTPC('volume_music', normalizedVolume)

    def StopMusic(self):
        if self.musicEmitter:
            self.musicEmitter.StopAll()

    def SendMusicEvent(self, event, forcePlay = False):
        if not forcePlay:
            if event == self.lastEventSent:
                return
        playingID = self.musicEmitter.SendEvent(event)
        sent = True if playingID > 0 else False
        self.processedEvents.append((event, FmtDate(gametime.GetSimTime()), sent))
        self.lastEventSent = event
        if self.debugMusicTriggerCallback:
            self.debugMusicTriggerCallback(event, playingID)
        logger.info('%s sent to music system', event)

    def StartMusicNodeGraph(self):
        if not self.masterMusicNodeGraph and self.audioManager.enabled:
            self.masterMusicNodeGraph = self.node_graph.start_node_graph(MASTER_MUSIC_GRAPH)
            logger.info('The master music graph (id %d) has been started.', MASTER_MUSIC_GRAPH)

    def StopMusicNodeGraph(self):
        if self.masterMusicNodeGraph:
            self.node_graph.stop_node_graph(self.masterMusicNodeGraph.instance_id)
            self.masterMusicNodeGraph = None
            logger.info('The master music graph (id %d) has been stopped.', MASTER_MUSIC_GRAPH)

    def OnAudioActivated(self):
        self.StartMusicNodeGraph()

    def OnAudioDeactivated(self):
        self.StopMusicNodeGraph()

    def OnOperationMadeActive(self, categoryID, operationID, oldCategoryID, oldOperationID, isSilent):
        musicTriggerID, musicTrigger = GetMusicTriggerFromOperation(operationID)
        if musicTrigger:
            self._ScheduleFSDMusicTrigger(musicTrigger)

    def OnConversationStarted(self, conversationID):
        musicTriggerID, musicTrigger = GetMusicTriggerFromConversation(conversationID)
        if musicTrigger:
            self._ScheduleFSDMusicTrigger(musicTrigger)

    def OnDungeonTriggerMusic(self, dungeonID, musicTriggerID):
        self.ScheduleMusicTriggerByID(musicTriggerID)

    def OnViewStateChanged(self, fromView, toView):
        if toView == ViewState.Login or toView == ViewState.CharacterSelector:
            self.StartMusicNodeGraph()

    def ScheduleMusicTriggerByID(self, musicTriggerId):
        musicTriggerObj = GetMusicTrigger(int(musicTriggerId))
        if musicTriggerObj:
            self.SendMusicEvent(musicTriggerObj.trigger)

    def _ScheduleFSDMusicTrigger(self, musicTriggerObj):
        if hasattr(musicTriggerObj, 'trigger'):
            self.SendMusicEvent(musicTriggerObj.trigger)

    def SetDebugMusicTriggerCallback(self, pythonFunc):
        self.debugMusicTriggerCallback = pythonFunc
