#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pirateinsurgency\campaignClientSnapshot.py
if False:
    from typing import Set
from pirateinsurgency.const import get_state_debug_string

class CampaignClientSnapshot(object):

    def __init__(self, campaignID, fsmState, stateExpiryTimestamp, warzoneID, originSolarsystemID, coveredSolarsystemIDs, structureID, piratePointsRequired, antipiratePointsRequired, piratePointsScored, antipiratePointsScored, pirateFactionID):
        self._campaignID = campaignID
        self._fsmState = fsmState
        self._stateExpiryTimestamp = stateExpiryTimestamp
        self._warzoneID = warzoneID
        self._originSolarsystemID = originSolarsystemID
        self._coveredSolarsystemIDs = coveredSolarsystemIDs
        self._structureID = structureID
        self._piratePointsRequired = piratePointsRequired
        self._antipiratePointsRequired = antipiratePointsRequired
        self._piratePointsScored = piratePointsScored
        self._antipiratePointsScored = antipiratePointsScored
        self._pirateFactionID = pirateFactionID

    def __repr__(self):
        return 'CampaignClientSnapshot<campaignID={0}, fsmState={1}, warzoneID={2}, originSolarsystemID={3}>'.format(self._campaignID, get_state_debug_string(self._fsmState), self._warzoneID, self._originSolarsystemID)

    @property
    def campaignID(self):
        return self._campaignID

    @property
    def fsmState(self):
        return self._fsmState

    @property
    def stateExpiryTimestamp(self):
        return self._stateExpiryTimestamp

    @property
    def warzoneID(self):
        return self._warzoneID

    @property
    def originSolarsystemID(self):
        return self._originSolarsystemID

    @property
    def coveredSolarsystemIDs(self):
        return self._coveredSolarsystemIDs

    @property
    def structureID(self):
        return self._structureID

    @property
    def piratePointsRequired(self):
        return self._piratePointsRequired

    @property
    def antipiratePointsRequired(self):
        return self._antipiratePointsRequired

    @property
    def piratePointsScored(self):
        return self._piratePointsScored

    @property
    def antipiratePointsScored(self):
        return self._antipiratePointsScored

    @property
    def pirateFactionID(self):
        return self._pirateFactionID
