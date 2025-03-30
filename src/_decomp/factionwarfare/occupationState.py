#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\occupationState.py
from factionwarfare.const import ADJACENCY_STATES, ADJACENCY_STATE_FRONTLINE, ADJACENCY_STATE_SECONDLINE, ADJACENCY_STATE_BACKLINE

class OccupationState(object):

    def __init__(self, occupierID, adjacencyState, potentialOccupierIDs, pirateFactionID):
        if occupierID is None:
            raise ValueError('occupierID cannot be None')
        if adjacencyState not in ADJACENCY_STATES:
            raise ValueError('adjacencyState not valid. Must be one of {0}'.format(ADJACENCY_STATES))
        if occupierID not in potentialOccupierIDs and occupierID != pirateFactionID:
            raise ValueError('potentialOccupierIDs must include occupierID')
        potentialOccupierIDs = set(potentialOccupierIDs)
        if len(potentialOccupierIDs) != 2:
            raise ValueError('potentialOccupierIDs must have exactly 2 different items')
        if pirateFactionID is None:
            raise ValueError('pirateFactionID cannot be None')
        self._occupierID = occupierID
        self._adjacencyState = adjacencyState
        self._attackerID = set.difference(potentialOccupierIDs, [self._occupierID]).pop()
        self._pirateFactionID = pirateFactionID

    def __repr__(self):
        return 'OccupationState(occupierID=%r, adjacencyState=%r, potentialOccupierIDs=%r)' % (self.occupierID, self.adjacencyState, self.potentialOccupierIDs)

    def __eq__(self, other):
        if isinstance(other, OccupationState):
            return self._occupierID == other._occupierID and self._adjacencyState == other._adjacencyState and self._attackerID == other._attackerID and self._pirateFactionID == other._pirateFactionID
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def occupierID(self):
        return self._occupierID

    @property
    def attackerID(self):
        return self._attackerID

    @property
    def potentialOccupierIDs(self):
        return [self._occupierID, self._attackerID]

    @property
    def pirateFactionID(self):
        return self._pirateFactionID

    @property
    def adjacencyState(self):
        return self._adjacencyState

    @property
    def isFrontline(self):
        return self._adjacencyState == ADJACENCY_STATE_FRONTLINE

    @property
    def isSecondline(self):
        return self._adjacencyState == ADJACENCY_STATE_SECONDLINE

    @property
    def isBackline(self):
        return self._adjacencyState == ADJACENCY_STATE_BACKLINE

    def GetCopyWithNewAdjacency(self, newAdjacencyState):
        return OccupationState(self._occupierID, newAdjacencyState, self.potentialOccupierIDs, self.pirateFactionID)

    def GetOtherParticipant(self, ownerID):
        if ownerID == self.attackerID:
            return self.occupierID
        if ownerID == self.occupierID:
            return self.attackerID
