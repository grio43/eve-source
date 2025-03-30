#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\insurgencyMusicMgr.py
import eveaudio
from eveaudio.musicMgrBase import MusicManagerBase
from eveaudio.utils import Singleton
from eve.client.script.parklife import states
INSURGENCY_MANAGER_NAME = 'insurgency'

class InsurgencyMusicManager(MusicManagerBase):
    __metaclass__ = Singleton

    def __init__(self):
        super(InsurgencyMusicManager, self).__init__()
        self.musicLocationName = INSURGENCY_MANAGER_NAME
        self.isInsurgencySystem = False
        self.lastInsurgencyStatus = False
        self.corruptionStage = 0
        self.suppressionStage = 0
        self.isInCombat = False
        self.lastCombatStatus = False
        self.lastInsurgencyLevel = ''
        self.threatList = {}
        self.playMusicEvent = 'music_eve_dynamic_play'
        self.stopMusicEvent = 'music_eve_dynamic_stop'

    def IsActive(self):
        return self.isInsurgencySystem

    def _GetCorruptionSuppressionStageSwitch(self, stage):
        return {0: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_A,
         1: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_B,
         2: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_C,
         3: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_D,
         4: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_E,
         5: eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_LEVEL_F}.get(stage, None)

    def UpdateIsInsurgencySystem(self, value):
        self.lastInsurgencyStatus = self.isInsurgencySystem
        self.isInsurgencySystem = value

    def UpdateCorruptionStage(self, stage):
        self.corruptionStage = stage
        if not self.isInsurgencySystem:
            self.UpdateIsInsurgencySystem(True)

    def UpdateSuppressionStage(self, stage):
        self.suppressionStage = stage
        if not self.isInsurgencySystem:
            self.UpdateIsInsurgencySystem(True)

    def UpdateCombatStatus(self, itemID, flag, flagState):
        if flag == states.threatTargetsMe:
            if flagState:
                self.threatList[itemID] = flagState
            elif self.threatList.has_key(itemID):
                self.threatList.pop(itemID, None)
        if len(self.threatList) > 0:
            self.isInCombat = True
        elif len(self.threatList) == 0:
            self.isInCombat = False

    def UpdateState(self):
        if self.isInsurgencySystem and not self.lastInsurgencyStatus:
            self.lastInsurgencyStatus = True
            self.ScheduleMusicTrigger(eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY)
        if self.isInCombat and not self.lastCombatStatus:
            self.lastCombatStatus = True
            self.ScheduleMusicTrigger(eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_COMBAT_PLAY)
        elif not self.isInCombat and self.lastCombatStatus:
            self.lastCombatStatus = False
            self.ScheduleMusicTrigger(eveaudio.MUSIC_SWITCH_HAVOC_INSURGENCY_COMBAT_STOP)
        corruptionSwitch = self._GetCorruptionSuppressionStageSwitch(self.corruptionStage)
        suppressionSwitch = self._GetCorruptionSuppressionStageSwitch(self.suppressionStage)
        currentInsurgencyLevel = None
        if corruptionSwitch > suppressionSwitch:
            currentInsurgencyLevel = corruptionSwitch
        else:
            currentInsurgencyLevel = suppressionSwitch
        if self.lastInsurgencyStatus != currentInsurgencyLevel:
            self.ScheduleMusicTrigger(currentInsurgencyLevel)
            self.lastInsurgencyStatus = currentInsurgencyLevel
