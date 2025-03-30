#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\wars\war_cso.py
import gametime
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.util.searchUtil import GetResultsByGroupID
from eve.common.script.net import eveMoniker
from eve.common.script.search.const import MatchBy, ResultType
from eve.common.script.sys.idCheckers import IsNPC
import blue
import uthread
import evewar.util as warUtil
from evewar import warConst
from evewar.util import IsAtWar, IsWarInHostileState, IsWarFinished, IsWarInSpoolup, IsWarInCooldown
import eve.common.lib.appConst as appConst

class Wars(Service):
    __exportedcalls__ = {'GetWars': [],
     'GetRelationship': [],
     'AreInAnyHostileWarStates': []}
    __guid__ = 'svc.war'
    __notifyevents__ = ['OnWarChanged', 'OnSessionChanged']
    __servicename__ = 'war'
    __displayname__ = 'War Client Service'
    __dependencies__ = []

    def __init__(self):
        Service.__init__(self)
        self.warsByOwnerID = {}
        self.warsByWarID = {}
        self.warsEnded = set()
        self.warsStarted = set()

    def GetDependencies(self):
        return self.__dependencies__

    def Run(self, memStream = None):
        self.LogInfo('Starting War')
        self.state = SERVICE_START_PENDING
        self.__warMoniker = None
        self.__warMonikerOwnerID = None
        self.state = SERVICE_RUNNING
        uthread.new(self.CheckForStartOrEndOfWar)

    def Stop(self, memStream = None):
        self.__warMoniker = None
        self.__warMonikerOwnerID = None

    def RefreshMoniker(self):
        if self.__warMoniker is not None:
            self.__warMoniker.UnBind()

    def GetMoniker(self):
        if self.__warMoniker is None:
            self.__warMoniker = eveMoniker.GetWar()
            self.__warMonikerOwnerID = eve.session.allianceid or eve.session.corpid
        if self.__warMonikerOwnerID != (eve.session.allianceid or eve.session.corpid):
            if self.__warMoniker is not None:
                self.__warMoniker.Unbind()
            self.__warMoniker = eveMoniker.GetWar()
            self.__warMonikerOwnerID = eve.session.allianceid or eve.session.corpid
        self.__warMoniker.Bind()
        return self.__warMoniker

    def OnSessionChanged(self, isRemote, sess, change):
        if 'allianceid' not in change and 'corpid' not in change:
            return
        if 'charid' in change and change['charid'][0] is None:
            return
        if session.allianceid:
            self.warsByOwnerID.pop(session.allianceid, None)
        self.warsByOwnerID.pop(session.corpid, None)
        currentlyAtWar = self.IsPlayerCurrentlyAtWarOrInFW()
        sm.ScatterEvent('OnWarStatusUpdated', currentlyAtWar, doAlert=True)

    def OnWarChanged(self, war, ownerIDs, change):
        try:
            warsByOwnerID = {ownerID:warIDs for ownerID, (lastUpdated, warIDs) in self.warsByOwnerID.iteritems()}
            warUtil.HandleWarChange(war, self.warsByWarID, warsByOwnerID, ownerIDs, change)
        except StandardError:
            self.LogException()
        finally:
            corpUISignals.on_war_changed(war, ownerIDs, change)
            sm.GetService('stateSvc').RemoveWarOwners(ownerIDs)
            sm.GetService('tactical').InvalidateFlags()
            sm.ScatterEvent('OnWarStatusUpdated', self.IsPlayerCurrentlyAtWarOrInFW(), doAlert=True)

    def GetWars(self, ownerID, forceRefresh = 0):
        if ownerID in self.warsByOwnerID:
            if forceRefresh or blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0], blue.os.GetWallclockTime()) > 12 * (appConst.HOUR / appConst.MSEC):
                del self.warsByOwnerID[ownerID]
        if ownerID not in self.warsByOwnerID:
            wars = self.GetMoniker().GetWars(ownerID)
            self.PopulateCacheAndCleanupWars(ownerID, wars)
        warIDs = self.warsByOwnerID[ownerID][1]
        return {warID:self.warsByWarID[warID] for warID in warIDs if warID in self.warsByWarID}

    def PopulateCacheAndCleanupWars(self, ownerID, wars):
        self.warsByWarID.update({war.warID:war for war in wars.itervalues()})
        warsByOwnerID = {war.warID for war in wars.itervalues()}
        self.warsByOwnerID[ownerID] = (blue.os.GetWallclockTime(), warsByOwnerID)
        usedWarIDs = set()
        for lastUpdated, warIDs in self.warsByOwnerID.itervalues():
            usedWarIDs.update(warIDs)

        for warID in self.warsByWarID.keys():
            if warID not in usedWarIDs:
                del self.warsByWarID[warID]

    def PrimeWarsForOwners(self, ownerIDs):
        ownersToFetch = set()
        for ownerID in ownerIDs:
            if ownerID in self.warsByOwnerID:
                if blue.os.TimeDiffInMs(self.warsByOwnerID[ownerID][0], blue.os.GetWallclockTime()) > 12 * (appConst.HOUR / appConst.MSEC):
                    ownersToFetch.add(ownerID)
            else:
                ownersToFetch.add(ownerID)

        if ownersToFetch:
            warsByOwnerIDs = sm.RemoteSvc('warsInfoMgr').GetWarsByOwners(ownersToFetch)
            for ownerID, wars in warsByOwnerIDs.iteritems():
                self.PopulateCacheAndCleanupWars(ownerID, wars)

    def GetRelationship(self, ownerID):
        if ownerID == eve.session.corpid:
            return warConst.warRelationshipYourCorp
        if ownerID == eve.session.allianceid:
            return warConst.warRelationshipYourAlliance
        myWarEntityID = session.corpid if session.allianceid is None else session.allianceid
        wars = self.GetWars(myWarEntityID)
        entities = (ownerID, myWarEntityID)
        if IsAtWar(wars.itervalues(), entities, blue.os.GetWallclockTime()):
            return warConst.warRelationshipAtWarCanFight
        for war in wars.itervalues():
            if myWarEntityID == war.againstID and ownerID in war.allies:
                return warConst.warRelationshipAlliesAtWar
            if ownerID == war.againstID and myWarEntityID in war.allies:
                return warConst.warRelationshipAlliesAtWar
            if ownerID in war.allies and myWarEntityID in war.allies:
                return warConst.warRelationshipAlliesAtWar

        return warConst.warRelationshipUnknown

    def AreInAnyHostileWarStates(self, ownerID):
        if ownerID not in self.warsByOwnerID:
            self.GetWars(ownerID)
        warsForOwnerID = self.warsByOwnerID[ownerID]
        timestamp, warIDs = warsForOwnerID[0], warsForOwnerID[1]
        for warID in warIDs:
            war = self.warsByWarID[warID]
            if (ownerID in {war.declaredByID, war.againstID} or ownerID in war.allies) and IsWarInHostileState(war, blue.os.GetWallclockTime()):
                return True

        return False

    def CheckForStartOrEndOfWar(self):
        while self.state == SERVICE_RUNNING:
            if session.charid:
                try:
                    self._CheckForWarStartingOrEnding()
                except StandardError:
                    self.LogException()

            blue.pyos.synchro.SleepWallclock(10000)

    def _CheckForWarStartingOrEnding(self):
        wars = self.GetWars(session.allianceid or session.corpid)
        now = blue.os.GetWallclockTime()
        yesterday = now - appConst.DAY - appConst.HOUR
        ownersToUpdate = set()
        warStartedOrExpired = False
        for war in wars.itervalues():
            if IsWarFinished(war) and war.warID not in self.warsEnded:
                ownersToUpdate.update([war.declaredByID, war.againstID])
                self.warsEnded.add(war.warID)
                warStartedOrExpired = True
            elif IsWarInHostileState(war, now) and yesterday <= war.timeStarted < now and war.warID not in self.warsStarted:
                ownersToUpdate.update([war.declaredByID, war.againstID] + war.allies.keys())
                self.warsStarted.add(war.warID)
                warStartedOrExpired = True

        if ownersToUpdate:
            sm.GetService('stateSvc').RemoveWarOwners(ownersToUpdate)
            sm.GetService('tactical').InvalidateFlags()
        if warStartedOrExpired:
            currentlyAtWar = self.IsPlayerCurrentlyAtWarOrInFW()
            sm.ScatterEvent('OnWarStatusUpdated', currentlyAtWar, doAlert=True)

    def GetAllyNegotiations(self):
        warMoniker = self.GetMoniker()
        return filter(lambda x: x.warNegotiationTypeID == warConst.WAR_NEGOTIATION_TYPE_ALLY_OFFER, warMoniker.GetNegotiations())

    def GetSurrenderNegotiations(self, warID):
        warMoniker = self.GetMoniker()
        return filter(lambda x: x.warNegotiationTypeID == warConst.WAR_NEGOTIATION_TYPE_SURRENDER_OFFER and x.warID == warID, warMoniker.GetNegotiations())

    def CreateWarAllyOffer(self, warID, iskValue, defenderID, message):
        warMoniker = self.GetMoniker()
        warMoniker.CreateWarAllyOffer(warID, iskValue, defenderID, message)

    def RetractWarAllyOffer(self, warNegotiationID):
        self.GetMoniker().RetractWarAllyOffer(warNegotiationID)

    def CreateSurrenderNegotiation(self, warID, iskValue, message):
        warMoniker = self.GetMoniker()
        warMoniker.CreateSurrenderNegotiation(warID, iskValue, message)

    def GetWarNegotiation(self, warNegotiationID):
        return self.GetMoniker().GetWarNegotiation(warNegotiationID)

    def AcceptAllyNegotiation(self, warNegotiationID):
        warMoniker = self.GetMoniker()
        warMoniker.AcceptAllyNegotiation(warNegotiationID)

    def DeclineAllyOffer(self, warNegotiationID):
        self.GetMoniker().DeclineAllyOffer(warNegotiationID)

    def RetractMutualWar(self, warID):
        warMoniker = self.GetMoniker()
        warMoniker.RetractMutualWar(warID)

    def AcceptSurrender(self, warNegotiationID):
        warMoniker = self.GetMoniker()
        warMoniker.AcceptSurrender(warNegotiationID)

    def DeclineSurrender(self, warNegotiationID):
        self.GetMoniker().DeclineSurrender(warNegotiationID)

    def SetOpenForAllies(self, warID, state):
        self.GetMoniker().SetOpenForAllies(warID, state)

    def GMJoinDefender(self, warID, entityID):
        warMoniker = self.GetMoniker()
        warEntityID = session.corpid if session.allianceid is None else session.allianceid
        warMoniker.GMJoinDefender(warID, entityID, warEntityID)

    def GMActivateDefender(self, warID, allyID):
        warMoniker = self.GetMoniker()
        warMoniker.GMActivateDefender(warID, allyID)

    def GMDeactivateDefender(self, warID, allyID):
        warMoniker = self.GetMoniker()
        warMoniker.GMDeactivateDefender(warID, allyID)

    def GMExtendAllyContract(self, warID, allyID, time):
        warMoniker = self.GetMoniker()
        warMoniker.GMExtendAllyContract(warID, allyID, time)

    def GMSetDeclareTime(self, warID, time):
        mon = self.GetMoniker()
        mon.GMSetDeclareTime(warID, time)

    def GMSetWarFinishTime(self, warID, time):
        mon = self.GetMoniker()
        mon.GMSetWarFinishTime(warID, time)

    def IsAllyInWar(self, warID):
        warEntityID = session.allianceid or session.corpid
        war = self.warsByWarID.get(warID, None)
        if war is None:
            return False
        allyRow = war.allies.get(warEntityID, None)
        if allyRow is not None and allyRow.timeFinished > blue.os.GetWallclockTime():
            return True
        return False

    def IsPlayerCurrentlyAtWarOrInFW(self):
        if session.warfactionid:
            return True
        ownerID = session.allianceid or session.corpid
        return self._IsOwnerAtWar(ownerID)

    def _IsOwnerAtWar(self, ownerID):
        if ownerID not in self.warsByOwnerID:
            self.GetWars(ownerID)
        timestampAndWars = self.warsByOwnerID.get(ownerID, None)
        if not timestampAndWars:
            return False
        ownerWars = timestampAndWars[1]
        now = gametime.GetWallclockTime()
        for eachWarID in ownerWars:
            eachWar = self.warsByWarID.get(eachWarID)
            if not eachWar:
                continue
            if IsWarInSpoolup(eachWar):
                continue
            if IsWarFinished(eachWar):
                continue
            if ownerID not in (eachWar.declaredByID, eachWar.againstID) and ownerID in getattr(eachWar, 'allies', ()):
                allyRow = eachWar.allies[ownerID]
                if allyRow.timeStarted > now or allyRow.timeFinished < now:
                    continue
            if eachWar.timeFinished is None or IsWarInCooldown(eachWar):
                return True

        return False

    def SearchForWarableEntity(self, searchStr, exact):
        searchBy = MatchBy.exact_phrase_only if exact else MatchBy.partial_terms
        warableResult, allResultsByGroupID = uthread.parallel([(sm.RemoteSvc('lookupSvc').LookupWarableCorporationsOrAlliances, (searchStr, exact)), (GetResultsByGroupID, (searchStr, [ResultType.corporation], searchBy))])
        warableByID = {x.ownerID:x for x in warableResult}
        allCorpResults = allResultsByGroupID.get(ResultType.corporation, [])
        nonWarableCorpIDs = {x for x in allCorpResults if x not in warableByID and not IsNPC(x)}
        cfg.eveowners.Prime(nonWarableCorpIDs)
        searchStrLower = searchStr.lower()
        corpIDsThatStartWithSearchStr = [ x for x in nonWarableCorpIDs if cfg.eveowners.Get(x).name.lower().startswith(searchStrLower) ]
        return (warableByID, corpIDsThatStartWithSearchStr)

    def GetPeaceTreaties(self):
        outgoingTreaties, incomingTreaties = sm.RemoteSvc('peaceTreatyMgr').GetPeaceTreatiesForSession()
        return (outgoingTreaties, incomingTreaties)
