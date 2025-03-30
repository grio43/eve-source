#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\client\enlistmentChecks.py
import gametime
import eve.common.lib.appConst as appConst
import factionwarfare.client.enrollmentConst as enrollmentConst
from eve.common.script.util.facwarCommon import GetFacwarMinStandingsToJoin
from eve.common.script.sys import idCheckers

class EnlistmentChecksObject(object):

    def __init__(self):
        self.facWarSvc = sm.GetService('facwar')
        self.fwEnlistmentSvc = sm.GetService('fwEnlistmentSvc')

    def CurrentlyInSameFaction(self, factionID):
        return factionID == session.warfactionid

    def HasCorpApplicationPendingWithFactionWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetCorpApplicationPendingWithFactionWarningConst(factionID))

    def GetCorpApplicationPendingWithFactionWarningConst(self, factionID):
        hasReqCorporationRole = session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
        if hasReqCorporationRole:
            factionalWarStatus = self.facWarSvc.GetCorpFactionalWarStatus()
            if factionalWarStatus.status == appConst.facwarCorporationJoining and factionalWarStatus.factionID == factionID:
                return enrollmentConst.WARNING_PENDING_SAME_FACTION
        else:
            corpFactionID = self.fwEnlistmentSvc.GetCorpFactionID()
            if corpFactionID and session.warfactionid != corpFactionID and corpFactionID == factionID:
                return enrollmentConst.WARNING_PENDING_SAME_FACTION
        return False

    def HasCorpApplicationPendingWithDifferentFactionWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetCorpApplicationPendingWithDifferentCons(factionID))

    def GetCorpApplicationPendingWithDifferentCons(self, factionID):
        hasReqCorporationRole = session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
        if hasReqCorporationRole:
            factionalWarStatus = self.facWarSvc.GetCorpFactionalWarStatus()
            if factionalWarStatus.status == appConst.facwarCorporationJoining and factionalWarStatus.factionID != factionID:
                return enrollmentConst.WARNING_PENDING_ANOTHER_FACTION
        else:
            corpFactionID = self.fwEnlistmentSvc.GetCorpFactionID()
            if corpFactionID and session.warfactionid != corpFactionID and corpFactionID != factionID:
                return enrollmentConst.WARNING_PENDING_ANOTHER_FACTION
        return False

    def HasAlreadyInFwWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetAlreadyInFwConst(factionID))

    def GetAlreadyInFwConst(self, factionID):
        if session.warfactionid and session.warfactionid != factionID:
            return enrollmentConst.WARNING_ALREADY_IN_FW
        return False

    def HasDisallowedByCorpWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetDisallowedByCorpConst(factionID))

    def GetDisallowedByCorpConst(self, factionID):
        if idCheckers.IsNPC(session.corpid):
            return False
        allowedFactions = sm.GetService('fwEnlistmentSvc').GetCorpAllowedEnlistmentFactions(session.corpid)
        if factionID not in allowedFactions:
            return enrollmentConst.WARNING_DISALLOWED_BY_CORP
        return False

    def HasStandingWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetStandingConst(factionID))

    def GetStandingConst(self, factionID):
        standings = sm.GetService('standing').GetStanding(factionID, session.charid)
        minStandingsToJoin = GetFacwarMinStandingsToJoin(factionID)
        if standings < minStandingsToJoin:
            return enrollmentConst.WARNING_PENDING_STANDING
        return False

    def HasWrongLocationWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetWrongLocationConst(factionID))

    def GetWrongLocationConst(self, factionID):
        if factionID != self.facWarSvc.GetCurrentStationFactionID():
            return enrollmentConst.WARNING_PENDING_WRONG_LOCATION
        return False

    def HasTrackingThisFactionWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetTrackingThisFactionWarningConst(factionID))

    def GetTrackingThisFactionWarningConst(self, factionID):
        trackedFactionID = self.GetTrackedFactionID()
        if trackedFactionID and trackedFactionID == factionID:
            return enrollmentConst.WARNING_TRACKING_SAME_FACTION
        return False

    def HasTrackingAnotherFactionWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetTrackingAnotherFactionWarningConst(factionID))

    def GetTrackingAnotherFactionWarningConst(self, factionID):
        trackedFactionID = self.GetTrackedFactionID()
        if trackedFactionID and trackedFactionID != factionID:
            return enrollmentConst.WARNING_TRACKING_ANOTHER_FACTION
        return False

    def HasCooldownWarning(self, factionID):
        if self.CurrentlyInSameFaction(factionID):
            return False
        return bool(self.GetCooldownWarning())

    def GetCooldownWarning(self):
        if self.facWarSvc.IsCharacterInFwCooldown():
            return enrollmentConst.WARNING_DIRECT_ENLISTMENT_COOLDOWN
        return False

    def GetTrackedFactionID(self):
        from jobboard.client import get_job_board_service
        JOB_PROVIDER = 'factional_warfare_enlistment'
        provider = get_job_board_service().get_provider(JOB_PROVIDER)
        trackedJobs = provider.get_tracked_jobs()
        if trackedJobs:
            return trackedJobs[0].faction_id

    def _GetFunctions(self):
        return [self.HasCorpApplicationPendingWithFactionWarning,
         self.HasCorpApplicationPendingWithDifferentFactionWarning,
         self.HasAlreadyInFwWarning,
         self.HasDisallowedByCorpWarning,
         self.HasStandingWarning,
         self.HasWrongLocationWarning]

    def HasAnyWarning(self, factionID):
        for func in self._GetFunctions():
            if func(factionID):
                return True

        return False
