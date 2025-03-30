#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rwservice.py
from carbon.common.script.sys.service import Service
from eve.common.script.sys.idCheckers import IsCorporation, IsNPC
import gametime
import inventorycommon.const as invconst
import logging
from eveservices.xmppchat import GetChatService
from localization import GetByLabel, GetByMessageID
from resourcewars.client.firstcompletiontracker import FirstCompletionTracker
from resourcewars.client.incomingtransmissionwindow import show_incoming_transmission_window
from resourcewars.client.objectivefeedback import ObjectiveFeedback
from resourcewars.common.const import HAULER_STATE_FULL, HAULER_STATE_DESTROYED, HAULER_STATE_AVAILABLE, RW_CORPORATIONS, FACTION_TO_PIRATE_CORP, HAULER_STATE_SECURED, FACTION_TO_RW_LP_CORP
import uthread2
logger = logging.getLogger(__name__)

class HaulerProgress(object):

    def __init__(self, contents, capacity, haulerState):
        self.contents = contents
        self.capacity = capacity
        self.state = haulerState

    def is_present(self):
        return self.state == HAULER_STATE_AVAILABLE

    def is_full(self):
        return self.state in (HAULER_STATE_FULL, HAULER_STATE_SECURED)

    def destroy(self):
        self.state = HAULER_STATE_DESTROYED

    def set_full(self):
        self.state = HAULER_STATE_FULL


class RWService(Service):
    __guid__ = 'svc.RWService'
    serviceName = 'svc.RWService'
    __displayname__ = 'RWService'
    __servicename__ = 'RWService'
    __dependencies__ = ['audio',
     'michelle',
     'standing',
     'uiHighlightingService']
    __notifyevents__ = ['OnRWDungeonCompletedWithRewards',
     'OnRWDungeonCompletedWithoutRewards',
     'OnRWDungeonEntered',
     'OnRWDungeonExited',
     'OnHaulerDestroyed',
     'OnHaulerEntered',
     'OnHaulerFull',
     'OnHaulerQuantityChanged',
     'OnRWIncomingAlliedForces',
     'OnRWIncomingAlliedReinforcements',
     'OnRWIncomingEnemyReinforcements',
     'OnRWTimerStarted',
     'OnRWPirateDestroyed',
     'OnRWDungeonLobbyEntered',
     'OnRWDungeonLobbyExited']

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self.activeDungeonInstance = None
        self.haulerProgress = {}
        self.startTime = None
        self.duration = None
        self.siteTarget = None
        self.pirates_killed = 0
        self.siteData = None
        self.activeChatChannel = None
        self.lastSiteNameID = None
        self.firstCompletionTracker = FirstCompletionTracker(self.uiHighlightingService, self.standing)
        self.objective_feedback = ObjectiveFeedback()
        self.enemy_eliminated_audio_tasklet = None

    def get_site_name(self):
        if self.lastSiteNameID is not None:
            return GetByMessageID(self.lastSiteNameID)
        return GetByLabel('UI/Chat/ChannelNames/resourceWars')

    def _join_resource_wars_channel(self, instanceID):
        chat_svc = GetChatService()
        if self.activeChatChannel is not None:
            chat_svc.LeaveChannel(self.activeChatChannel)
        sm.ProxySvc('XmppChatMgr').EnsureResourceWarsChannelExists(instanceID)
        newChannelID = 'resourcewars_%d' % instanceID
        chat_svc.JoinChannel(newChannelID)
        self.activeChatChannel = newChannelID
        channelWindow = chat_svc.GetGroupChatWindow(self.activeChatChannel)
        if channelWindow is not None:
            channelWindow.MakeUnKillable()

    def OnRWDungeonEntered(self, instanceID, startTime, duration, siteTarget, ore_quantities_by_hauler_id, pirates_killed, asteroid_ids):
        self.activeDungeonInstance = instanceID
        self.siteTarget = siteTarget
        self._set_deadline(startTime, duration)
        self.pirates_killed = pirates_killed
        for haulerID, progress in ore_quantities_by_hauler_id:
            self.haulerProgress[haulerID] = HaulerProgress(*progress)

        self._join_resource_wars_channel(instanceID)
        sm.ScatterEvent('OnRWDungeonEnteredInClient')
        self.firstCompletionTracker.on_rw_dungeon_entered()
        self.activate_asteroid_explosions(asteroid_ids)

    def OnRWDungeonExited(self, instanceID, asteroid_ids):
        logger.debug('Exited dungeon %s', instanceID)
        self.flush()
        sm.ScatterEvent('OnRWDungeonExitedInClient')
        self.audio.SendUIEvent('res_wars_timer_stop')
        self.deactivate_asteroid_explosions(asteroid_ids)

    def activate_asteroid_explosions(self, asteroid_ids):
        for asteroid_id in asteroid_ids:
            ball = self.michelle.GetBall(asteroid_id)
            if hasattr(ball, 'ActivateExplodeOnRemove'):
                ball.ActivateExplodeOnRemove()

    def deactivate_asteroid_explosions(self, asteroid_ids):
        for asteroid_id in asteroid_ids:
            ball = self.michelle.GetBall(asteroid_id)
            if hasattr(ball, 'DeactivateExplodeOnRemove'):
                ball.DeactivateExplodeOnRemove()

    def _play_completion_audio(self, isVictory):
        jingle = 'res_wars_mission_success_play' if isVictory else 'res_wars_mission_fail_play'
        message = 'voc_rw_aura_success_aura_play' if isVictory else 'voc_rw_aura_expeditiondisbanded_aura_play'
        self.audio.SendUIEvent('res_wars_timer_stop')
        self.audio.SendUIEvent(jingle)
        self.audio.SendUIEvent(message)

    def OnRWDungeonCompletedWithRewards(self, instanceID, isVictory, completionData):
        self._on_dungeon_completion(instanceID, isVictory, completionData, isRewarded=True)

    def OnRWDungeonCompletedWithoutRewards(self, instanceID, isVictory, completionData):
        self._on_dungeon_completion(instanceID, isVictory=False, completionData=completionData, isRewarded=False)

    def _on_dungeon_completion(self, instanceID, isVictory, completionData, isRewarded):
        logger.debug('Completed dungeon %s', instanceID)
        self.flush()
        sm.ScatterEvent('OnRWDungeonExitedInClient')
        self._play_completion_audio(isVictory)
        self.objective_feedback.show_view(isVictory, isRewarded, completionData)
        self.firstCompletionTracker.on_rw_dungeon_completed(isVictory)

    def OnHaulerEntered(self, haulerID, contents, capacity, isRespawned):
        logger.debug('Hauler %s entered (%s/%s)', haulerID, contents, capacity)
        if haulerID not in self.haulerProgress:
            logger.debug('Initiating progress for entering hauler %s (%s/%s)', haulerID, contents, capacity)
            self.haulerProgress[haulerID] = HaulerProgress(contents, capacity, HAULER_STATE_AVAILABLE)
            sm.ScatterEvent('OnHaulerEnteredInClient', haulerID, self.haulerProgress[haulerID])
            if isRespawned:
                self.audio.SendUIEvent('voc_rw_aura_haulerreinforcements_aura_play')

    def OnHaulerDestroyed(self, haulerID):
        if haulerID in self.haulerProgress:
            self.haulerProgress[haulerID].destroy()
        sm.ScatterEvent('OnHaulerDestroyedInClient', haulerID)

    def _play_audio_if_all_enemies_are_eliminated(self):
        ballpark = self.michelle.GetBallpark()
        for ball, item in ballpark.GetBallsAndItems():
            if item.categoryID == invconst.categoryEntity and item.ownerID in FACTION_TO_PIRATE_CORP.values():
                return

        self.audio.SendUIEvent('voc_rw_aura_enenyeliminated_aura_play')

    def OnRWPirateDestroyed(self, pirateKillCount):
        logger.debug('OnRWPirateDestroyed  %s', pirateKillCount)
        if pirateKillCount > self.pirates_killed:
            self.pirates_killed = pirateKillCount
            sm.ScatterEvent('OnRWPirateDestroyedInClient', self.pirates_killed)
            if self.enemy_eliminated_audio_tasklet is not None:
                self.enemy_eliminated_audio_tasklet.kill()
            self.enemy_eliminated_audio_tasklet = uthread2.call_after_simtime_delay(self._play_audio_if_all_enemies_are_eliminated, 5)

    def OnHaulerFull(self, haulerID):
        logger.debug('Hauler %s full', haulerID)
        if haulerID in self.haulerProgress:
            self.haulerProgress[haulerID].set_full()
        sm.ScatterEvent('OnHaulerFullInClient', haulerID)

    def OnHaulerQuantityChanged(self, haulerID, changeQuantity, totalQuantity, ownerID, typeID):
        progress = self.haulerProgress.get(haulerID, None)
        if progress is None:
            logger.warn('rwService::OnHaulerQuantityChanged Hauler %s not found', haulerID)
            return
        progress.contents = max(progress.contents, totalQuantity)
        sm.ScatterEvent('OnHaulerQuantityChangedInClient', haulerID, changeQuantity, totalQuantity, ownerID, typeID)

    def OnRWTimerStarted(self, startTime, duration):
        logger.debug('Got timer started event %s %s', startTime, duration)
        self._set_deadline(startTime, duration)
        deadline = startTime + duration
        criticalTime = self.get_critical_time()
        sm.ScatterEvent('OnRWTimerStartedInClient', deadline, criticalTime)

    def OnRWDungeonLobbyEntered(self, siteData, secondsRemaining):
        self.siteData = siteData
        self.lastSiteNameID = self.siteData.dungeonNameID
        show_incoming_transmission_window(siteData, secondsRemaining)

    def OnRWDungeonLobbyExited(self):
        self.flush()

    def _on_rw_timer_ended(self, start_time):
        if self.startTime == start_time:
            logger.debug('rw timer ended %s', start_time)
            self.flush()
            sm.ScatterEvent('OnRWTimerEndedInClient')

    def _set_deadline(self, startTime, duration):
        if startTime is None:
            return
        self.startTime = startTime
        self.duration = duration
        simtimeUntilDeadline = gametime.GetSecondsUntilSimTime(startTime + duration)
        uthread2.call_after_simtime_delay(self._on_rw_timer_ended, simtimeUntilDeadline, self.startTime)

    def get_haulers_present(self):
        present = []
        for haulerID, haulerProgress in self.haulerProgress.iteritems():
            if haulerProgress.state == HAULER_STATE_AVAILABLE:
                present.append(haulerID)

        return present

    def has_a_hauler_been_filled_past_half_capacity(self):
        for haulerID, haulerProgress in self.haulerProgress.iteritems():
            if haulerProgress.state in (HAULER_STATE_FULL, HAULER_STATE_SECURED):
                return True
            if haulerProgress.state == HAULER_STATE_AVAILABLE:
                if haulerProgress.contents > haulerProgress.capacity / 2:
                    return True

        return False

    def get_hauler_progress(self):
        return self.haulerProgress

    def get_progress_for_hauler(self, haulerID):
        return self.haulerProgress.get(haulerID, None)

    def get_hauler_capacity(self, haulerID):
        hauler = self.haulerProgress.get(haulerID, None)
        if hauler is not None:
            return hauler.capacity * 0.1

    def get_deadline(self):
        if self.startTime is not None:
            return self.startTime + self.duration

    def get_critical_time(self):
        if self.startTime is not None:
            return self.startTime + self.duration * 0.75

    def get_site_target(self):
        return self.siteTarget

    def get_site_progress(self):
        return sum([ p.contents for p in self.haulerProgress.values() if p.is_full() ])

    def get_pirates_killed(self):
        return self.pirates_killed

    def is_in_rw_dungeon_or_lobby(self):
        in_lobby = self.siteData is not None
        return in_lobby or self.is_in_rw_dungeon()

    def is_in_rw_dungeon(self):
        return bool(self.activeDungeonInstance)

    def _make_chat_window_killable(self):
        if self.activeChatChannel is None:
            return
        channelWindow = GetChatService().GetGroupChatWindow(self.activeChatChannel)
        if channelWindow is not None:
            channelWindow.MakeKillable()

    def flush(self):
        self.activeDungeonInstance = None
        self.startTime = None
        self.duration = None
        self.siteTarget = None
        self.haulerProgress.clear()
        self.flushTimer = None
        self.siteData = None
        self._make_chat_window_killable()

    def is_rw_corporation(self, corpID):
        return IsCorporation(corpID) and corpID in RW_CORPORATIONS

    def OnRWIncomingAlliedForces(self):
        self.audio.SendUIEvent('voc_rw_aura_incomingalliedforces_aura_play')

    def OnRWIncomingAlliedReinforcements(self):
        self.audio.SendUIEvent('voc_rw_aura_alliedreinforcements_aura_play')

    def OnRWIncomingEnemyReinforcements(self):
        self.audio.SendUIEvent('voc_rw_aura_enemyreinforcements_aura_play')

    def is_rw_corp_station(self, corpID):
        if not session.stationid or not sm.GetService('station').stationItem or not self.is_rw_corporation(corpID):
            return False
        station_owner_corp = sm.GetService('station').stationItem.ownerID
        if not IsNPC(station_owner_corp):
            return False
        station_faction = sm.GetService('map').GetItem(session.solarsystemid2).factionID
        station_rw_corp = self.get_rw_corp_for_faction_and_system(station_faction)
        return corpID == station_rw_corp

    def get_rw_corp_for_faction_and_system(self, factionID):
        if not self.is_rw_system() and not self.is_high_sec():
            return None
        else:
            return FACTION_TO_RW_LP_CORP.get(factionID, None)

    def is_rw_system(self):
        return sm.RemoteSvc('RWManager').solarsystem_contains_rw_instances()

    def is_high_sec(self):
        return sm.GetService('map').GetSecurityClass(session.solarsystemid2) == const.securityClassHighSec
