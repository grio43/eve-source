#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\fwAdvantageSvc.py
from brennivin.threadutils import expiring_memoize
from carbon.common.script.sys.service import Service, ROLEMASK_ELEVATEDPLAYER
from eve.common.script.util.facwarCommon import GetOccupationEnemyFaction
from eveexceptions import UserError
from factionwarfare.activity.client.noticeMessenger import NoticeMessenger
from factionwarfare.activity.client.requestMessenger import PublicRequestsMessenger as ActivityRequestsMessenger
from factionwarfare.admin.client.requestMessenger import PublicRequestsMessenger as AdminRequestsMessenger
from factionwarfare.advantageState import AdvantageState

class FwAdvantageSvc(Service):
    __guid__ = 'svc.fwAdvantageSvc'
    __displayname__ = 'FW Advantage client service'
    __startupdependencies__ = ['publicGatewaySvc']
    __notifyevents__ = []

    def Run(self, memStream = None):
        self._activityRequestsMessenger = ActivityRequestsMessenger(self.publicGatewaySvc)
        self._noticeMessenger = NoticeMessenger(self.publicGatewaySvc)
        self._noticeMessenger.on_score_contribution_notice.connect(self._OnScoreContribution)
        self._noticeMessenger.on_solar_system_scores_notice.connect(self._OnSolarSystemScoresUpdated)
        self._adminRequestsMessenger = AdminRequestsMessenger(self.publicGatewaySvc)

    def _OnScoreContribution(self, solarsystemID, characterID, factionID, contribution):
        if characterID != session.charid:
            return
        sm.ScatterEvent('OnSolarsystemAdvantageScoreContribution_Local', solarsystemID, factionID, contribution)

    def _OnSolarSystemScoresUpdated(self, solarSystemScores):
        solarsystemID = solarSystemScores.solar_system_id
        scores = solarSystemScores.scores
        activityTrackerState = {score.faction_id:(score.contribution, score.floor) for score in scores}
        try:
            advantageState = AdvantageState.CreateAdvantageStateFromActivityState(activityTrackerState)
        except ValueError:
            self.LogException('_OnSolarSystemScoresUpdated failed to convert incoming activityTrackerState')
            return

        with self._AdvantageStateCacheLock(solarsystemID):
            self._GetAdvantageStateWithCache.prime_cache_result((self, solarsystemID), advantageState)
        if solarsystemID == session.solarsystemid2:
            sm.ScatterEvent('OnSolarsystemAdvantageStateUpdated_Local')

    def GetAdvantageState(self, solarsystemID):
        with self._AdvantageStateCacheLock(solarsystemID):
            return self._GetAdvantageStateWithCache(solarsystemID)

    def _AdvantageStateCacheLock(self, solarsystemID):
        return self.LockedService(('AdvantageStateCache', solarsystemID))

    @expiring_memoize(10)
    def _GetAdvantageStateWithCache(self, solarsystemID):
        return _GetAdvantageStateFromActivityTracker(self._activityRequestsMessenger, solarsystemID)

    def HandleSlashCmd(self, commandLine):
        if not session.role & ROLEMASK_ELEVATEDPLAYER:
            return
        commandLine = commandLine.lower().strip()
        commands = commandLine.split()
        if commands[0] == '/advantage':
            if len(commands) == 5 and commands[1] in ('add', 'set'):
                try:
                    solarsystemID = session.solarsystemid2 if commands[2] == 'local' else int(commands[2])
                    factionID = int(commands[3])
                    points = int(commands[4])
                except Exception:
                    raise UserError('SlashError', {'reason': 'Invalid command `%s`<br>/advantage add local|SOLARSYSTEM_ID FACTION_ID NUM_POINTS' % commandLine})

                occupationState = sm.GetService('fwWarzoneSvc').GetOccupationState(solarsystemID)
                if occupationState is None:
                    raise UserError('SlashError', {'reason': 'Error: %s is not a warzone solar system' % solarsystemID})
                if not (factionID == occupationState.occupierID or factionID == GetOccupationEnemyFaction(occupationState.occupierID)):
                    raise UserError('SlashError', {'reason': 'Error: %s is not a faction in this warzone' % solarsystemID})
                if commands[1] == 'add':
                    self._adminRequestsMessenger.increment_contribution_score(solarsystemID, factionID, points)
                elif commands[1] == 'set':
                    self._adminRequestsMessenger.set_contribution_score(solarsystemID, factionID, points)
                return
        raise UserError('SlashError', {'reason': 'Invalid command `%s`<br>Usage:<br>/advantage add local|SOLARSYSTEM_ID FACTION_ID NUM_POINTS<br>/advantage set local|SOLARSYSTEM_ID FACTION_ID NUM_POINTS' % commands})


def _GetAdvantageStateFromActivityTracker(activityPublicRequestsMessenger, solarsystemID):
    solar_system_scores = activityPublicRequestsMessenger.get_solar_system_scores(solarsystemID)
    activityTrackerState = {score.faction_id:(score.contribution, score.floor) for score in solar_system_scores.scores}
    advantageState = AdvantageState.CreateAdvantageStateFromActivityState(activityTrackerState)
    return advantageState
