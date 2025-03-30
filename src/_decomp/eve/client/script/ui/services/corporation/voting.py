#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corporation\voting.py
from carbon.common.script.sys.crowset import CRowset
from carbon.common.script.sys.service import Service
from corporation.voting import *
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from locks import RLock
from itertools import chain
from caching.memoize import Memoize
from collections import defaultdict
from gametime import GetWallclockTime
from eve.common.lib import appConst as const
from eve.common.script.net.eveMoniker import GetCorpRegistry

class CorporationVotes(Service):
    __servicename__ = 'corpvotes'
    __displayname__ = 'Corporation Voting Service'
    __guid__ = 'svc.corpvotes'
    __notifyevents__ = ['OnVoteCaseChanged',
     'OnVoteCast',
     'DoSessionChanging',
     'OnShareChange',
     'OnCorporationChanged',
     'OnSanctionedActionChanged']

    def __init__(self):
        Service.__init__(self)
        self._voteCases = None
        self.voteCaseOptions = {}
        self.votesByVoteCaseID = {}
        self.sanctionedActionsByState = defaultdict(list)
        self.canRunForCEO = None
        self.canViewVotes = None
        self.canVote = None
        self.remoteSvc = None
        self.readlock = None
        self._voteCaseHeader = None

    def Run(self, *args):
        Service.Run(self, args)
        self.readlock = RLock('corpvotes')
        self.remoteSvc = sm.RemoteSvc('voteManager')

    def FlushAll(self):
        self._voteCases = None
        self.voteCaseOptions.clear()
        self.votesByVoteCaseID.clear()
        self.canRunForCEO = None
        self.canViewVotes = None
        self.canVote = None
        self.sanctionedActionsByState.clear()
        self._GetShares.clear_memoized()

    @property
    def voteCases(self):
        with self.readlock:
            if self._voteCases is None:
                self._voteCases = self.remoteSvc.GetVoteCasesByCorporation(session.corpid)
        return self._voteCases

    @property
    def voteCaseHeader(self):
        if self._voteCaseHeader is None:
            for vc in chain(self.voteCases.itervalues()):
                self._voteCaseHeader = vc.header
                break

        return self._voteCaseHeader

    def OnVoteCaseChanged(self, corporationID, voteCaseID):
        if session.corpid == corporationID:
            self._voteCases = None
            self.voteCaseOptions.pop(voteCaseID, None)
            self.votesByVoteCaseID.pop(voteCaseID, None)
        corpUISignals.on_vote_case_changed(corporationID, voteCaseID)

    def OnVoteCast(self, corporationID, voteCaseID):
        if corporationID == session.corpid:
            self.votesByVoteCaseID.pop(voteCaseID, None)
        corpUISignals.on_vote_cast(corporationID, voteCaseID)

    def OnShareChange(self, shareholderID, corporationID, _):
        if shareholderID == session.charid or corporationID == session.corpid:
            self.FlushAll()

    def DoSessionChanging(self, _, __, change):
        if 'corpid' in change:
            self.FlushAll()

    def OnCorporationChanged(self, corpID, change):
        if corpID == session.corpid:
            self.FlushAll()

    def OnSanctionedActionChanged(self, corporationID, voteCaseID):
        self.sanctionedActionsByState.clear()
        corpUISignals.on_sanctioned_action_changed(corporationID, voteCaseID)

    def GetVoteCasesByCorporation(self, corporationID, status = VOTECASE_STATUS_ALL):
        if corporationID == session.corpid:
            voteCases = self.voteCases
        else:
            voteCases = self.remoteSvc.GetVoteCasesByCorporation(corporationID, VOTECASE_STATUS_ALL)
        try:
            return voteCases[status]
        except KeyError:
            return CRowset(self.voteCaseHeader, chain(voteCases[VOTECASE_STATUS_OPEN], voteCases[VOTECASE_STATUS_CLOSED]))

    def GetVoteCase(self, corporationID, voteCaseID):
        for vc in chain(self.voteCases[VOTECASE_STATUS_OPEN], self.voteCases[VOTECASE_STATUS_CLOSED]):
            if vc.voteCaseID == voteCaseID:
                return vc

        vc = self.remoteSvc.GetVoteCase(corporationID, voteCaseID)
        status = VOTECASE_STATUS_OPEN if vc.endDateTime > GetWallclockTime() else VOTECASE_STATUS_CLOSED
        self._voteCases[status].append(vc)
        return vc

    def GetVoteCaseOptions(self, voteCaseID, corporationID = None):
        if corporationID is None:
            corporationID = session.corpid
        if corporationID == session.corpid:
            with self.readlock:
                if voteCaseID not in self.voteCaseOptions:
                    self.voteCaseOptions[voteCaseID] = self.remoteSvc.GetVoteCaseOptions(corporationID, voteCaseID)
            return self.voteCaseOptions[voteCaseID]
        return self.remoteSvc.GetVoteCaseOptions(corporationID, voteCaseID)

    def GetVotes(self, corporationID, voteCaseID):
        if corporationID == session.corpid:
            with self.readlock:
                if voteCaseID not in self.votesByVoteCaseID:
                    self.votesByVoteCaseID[voteCaseID] = self.remoteSvc.GetVotes(voteCaseID)
                return self.votesByVoteCaseID[voteCaseID]
        return self.remoteSvc.GetVotes(voteCaseID)

    def CanViewVotes(self, corporationID):
        if corporationID == session.corpid:
            with self.readlock:
                if self.canViewVotes is None:
                    self.canViewVotes = self.remoteSvc.CanViewVotes(session.corpid)
            return self.canViewVotes
        return self.remoteSvc.CanViewVotes(corporationID or session.corpid)

    def CanVote(self, corporationID):
        if corporationID == session.corpid:
            with self.readlock:
                if self.canVote is None:
                    self.canVote = self._CanVote(corporationID)
            return self.canVote
        return self._CanVote(corporationID)

    def _CanVote(self, corporationID):
        isCEOTypePerson = sm.GetService('corp').GetCorporation().ceoID == session.charid
        if session.corpid == corporationID and isCEOTypePerson:
            return True
        personalShares, _ = self._GetShares()
        if corporationID in personalShares:
            return True
        if isCEOTypePerson and session.corpid != corporationID and session.corpid in GetCorpRegistry().GetShareholders(corporationID):
            return True
        return False

    @Memoize
    def _GetShares(self):
        corpShares = []
        personalShares = sm.GetService('corp').GetSharesByShareholder()
        if session.corprole & (const.corpRoleAccountant | const.corpRoleJuniorAccountant):
            corpShares = sm.GetService('corp').GetSharesByShareholder(1)
        return (personalShares, corpShares)

    def CanRunForCEO(self):
        if not sm.GetService('skills').GetSkill(const.typeCorporationManagement):
            return 0
        if self.canRunForCEO is None:
            self.canRunForCEO = self.remoteSvc.CanRunForCEO()
        return self.canRunForCEO

    def CreateVote(self, voteData):
        voteCaseText = voteData['title']
        description = voteData['description']
        voteType = voteData['votetype']
        duration = voteData['time']
        if voteType == voteShares:
            options = (('UI/Corporations/CorporationWindow/Politics/CreateShares', {'shares': voteData['shares']}),
             ('UI/Corporations/CorporationWindow/Politics/DoNotCreateShares',),
             voteData['shares'],
             None,
             None)
        elif voteType == voteItemLockdown:
            options = (('UI/Corporations/CorporationWindow/Politics/LockdownItem', {'item': voteData['typeID']}),
             ('UI/Corporations/CorporationWindow/Politics/DontLockdownItem', {'item': voteData['typeID']}),
             voteData['itemID'],
             voteData['typeID'],
             voteData['locationID'])
        elif voteType == voteItemUnlock:
            options = (('UI/Corporations/CorporationWindow/Politics/UnlockItem', {'item': voteData['typeID']}),
             ('UI/Corporations/CorporationWindow/Politics/DontUnlockItem', {'item': voteData['typeID']}),
             voteData['itemID'],
             voteData['typeID'],
             voteData['locationID'])
        elif voteType == voteKickMember:
            options = (('UI/Corporations/CorporationWindow/Politics/ExpelFromCorporation', {'char': voteData['kickmember']}),
             ('UI/Corporations/CorporationWindow/Politics/DontExpelFromCorporation', {'memberName': voteData['memberName']}),
             voteData['kickmember'],
             None,
             None)
        elif voteType == voteCEO:
            options = (('UI/Corporations/CorporationWindow/Politics/SomeoneForCEO', {'char': session.charid}),
             ('UI/Corporations/CorporationWindow/Politics/DontChangeCEO',),
             session.charid,
             None,
             None)
        elif voteType == voteGeneral:
            options = [ option for option in voteData['options'] ]
        else:
            self.LogError('Unknown Vote type %d' % voteType)
            return
        self.remoteSvc.InsertVoteCase(voteCaseText, description, voteType, options, duration)

    def InsertVote(self, corpID, voteCaseID, voteValue):
        self.remoteSvc.InsertVote(corpID, voteCaseID, voteValue)

    def GetSanctionedActions(self, state):
        with self.readlock:
            if state not in self.sanctionedActionsByState:
                now = GetWallclockTime()
                for action in self.remoteSvc.GetCorpSanctionedActions().itervalues():
                    if action.inEffect == 0 and action.expires > now:
                        self.sanctionedActionsByState[SANCTIONED_ACTION_STATUS_NOT_IN_EFFECT].append(action)
                    elif action.inEffect:
                        self.sanctionedActionsByState[SANCTIONED_ACTION_STATUS_IN_EFFECT].append(action)
                    elif action.expires < now:
                        self.sanctionedActionsByState[SANCTIONED_ACTION_STATUS_EXPIRED].append(action)

        try:
            return self.sanctionedActionsByState[state]
        except KeyError:
            return []

    def ApplySanctionedAction(self, voteCaseID):
        self.remoteSvc.ActivateSanctionedAction(voteCaseID)

    def IsBlueprintSubjectOfActiveVoteCase(self, blueprintID):
        now = GetWallclockTime()
        for voteCase in self.GetVoteCasesByCorporation(session.corpid, voting.VOTECASE_STATUS_OPEN):
            if voteCase.endDateTime > now:
                for option in self.GetVoteCaseOptions(voteCase.voteCaseID, voteCase.corporationID):
                    if option.parameter == blueprintID:
                        return True

        return False

    def IsBlueprintSubjectOfPendingUnlockAction(self, blueprintID):
        return blueprintID in {sa.parameter for sa in self.GetSanctionedActions(voting.SANCTIONED_ACTION_STATUS_NOT_IN_EFFECT) if sa.voteType == voting.voteItemUnlock and sa.parameter and not sa.inEffect}
