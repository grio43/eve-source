#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\characterCheckers.py
import sys
from menucheckers import decorated_checker
from menucheckers.baseCheckers import _BaseSessionWrappingChecker
from eve.common.lib import appConst
import evefleet.const as fleetConst
from eve.common.script.sys.idCheckers import IsNPC, IsSolarSystem, IsStation
from globalConfig.getFunctions import IsPlayerBountyHidden

@decorated_checker

class CharacterChecker(_BaseSessionWrappingChecker):

    def __init__(self, characterID, isMultiSelection, session, sm = None):
        super(CharacterChecker, self).__init__(session, sm)
        self.characterID = characterID
        self._multiSelection = isMultiSelection
        self._agentSvc = None
        self._addressbookSvc = None
        self._fleetSvc = None

    @property
    def agents(self):
        if self._agentSvc is None:
            self._agentSvc = self.sm.GetService('agents')
        return self._agentSvc

    @property
    def addressbook(self):
        if self._addressbookSvc is None:
            self._addressbookSvc = self.sm.GetService('addressbook')
        return self._addressbookSvc

    @property
    def fleetSvc(self):
        if self._fleetSvc is None:
            self._fleetSvc = self.sm.GetService('fleet')
        return self._fleetSvc

    def OfferAddAllianceContact(self):
        if self.IsNPC():
            return False
        if not self.session.IsAllianceMember():
            return False
        if not self.session.IsDiplomat():
            return False
        if not self.session.IsExecutorCorp():
            return False
        return not self.IsInAllianceAddressBook()

    def OfferAddCorpContact(self):
        if self.IsNPC():
            return False
        if not self.session.IsDiplomat():
            return False
        return not self.IsInCorpAddressBook()

    def OfferAddContact(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return not self.IsInAddressBook()

    def OfferAddToAddressBook(self):
        if self.IsMe():
            return False
        if self.IsInAddressBook():
            return False
        if not self.IsNPC():
            return False
        if not self.IsAgent():
            return False
        return True

    def OfferAllowCorpRoles(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.isPilotInSameCorpAs(self.characterID):
            return False
        if not self.IsMe():
            return False
        if not bool(self.GetBlockedRoles()):
            return False
        return True

    def OfferAwardCorpMemberDecoration(self):
        if self.IsNPC():
            return False
        if self.session.IsPilotInNpcCorp():
            return False
        if not self.session.isPilotInSameCorpAs(self.characterID):
            return False
        return self.session.IsPersonnelManager()

    def OfferBlockContact(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return not self.IsBlocked()

    def OfferCapturePortrait(self):
        if self.IsNPC():
            return False
        return True

    def OfferCloneInstallation(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return self.HasCloneBay()

    def OfferDuelMenuEntry(self):
        if self._multiSelection:
            return False
        if self.session.IsInZeroSec():
            return False
        if self.IsNPC():
            return False
        if self.IsMe():
            return False
        if self.isPilotInLimitedEngagementWith(self.characterID):
            return False
        return True

    def OfferEditCorpMember(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.isPilotInSameCorpAs(self.characterID):
            return False
        if not self.session.IsCorpDirector():
            return False
        return True

    def OfferExpelCorpMember(self):
        if self.IsNPC():
            return False
        if self.IsMe():
            return False
        if not self.session.isPilotInSameCorpAs(self.characterID):
            return False
        if not self.session.IsCorpDirector():
            return False
        return True

    def OfferFleetMenu(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        return self.session.isPilotInSameFleetAs(self.characterID)

    def OfferFormFleetWith(self):
        if self.IsNPC():
            return False
        if self.session.IsPilotFleetMember():
            return False
        return True

    def OfferGiveMoney(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return True

    def OfferInvitePilotToFleet(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        if self.session.isPilotInSameFleetAs(self.characterID):
            return False
        return self.IsPilotFleetCreator() or self.session.IsPilotFleetCommander()

    def OfferInviteToChat(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return True

    def OfferMapMenu(self):
        if self._multiSelection:
            return False
        agentInfo = self.GetAgentInfo()
        if not agentInfo:
            return False
        if not agentInfo.solarsystemID:
            return False
        locationID = agentInfo.stationID or agentInfo.solarsystemID
        if IsSolarSystem(locationID):
            return True
        if IsStation(locationID):
            return True
        if self.sm.GetService('structureDirectory').GetStructureInfo(locationID) is not None:
            return True
        return False

    def OfferPlaceBounty(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if IsPlayerBountyHidden(self.sm.GetService('machoNet')):
            return False
        return True

    def OfferQuitCorp(self):
        if not self.IsMe():
            return False
        if self.session.IsPilotInNpcCorp():
            return False
        if self.IsPilotCEO():
            return False
        return True

    def OfferRemoveContact(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return self.IsInAddressBook()

    OfferEditContact = OfferRemoveContact

    def OfferReportMenuEntry(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsAgent():
            return False
        if self.IsNPC():
            return False
        return True

    def OfferResignAsCEO(self):
        if not self.IsMe():
            return False
        return self.IsPilotCEO()

    def OfferTradeWithCharacter(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        if not self.IsGuest():
            return False
        return True

    def OfferTransferCorpCash(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.IsAccountant():
            return False
        return True

    def OfferRemoveAllianceContact(self):
        if not self.session.IsAllianceMember():
            return False
        if self.IsNPC():
            return False
        if not self.session.IsDiplomat():
            return False
        if not self.session.IsExecutorCorp():
            return False
        return self.IsInAllianceAddressBook()

    OfferEditEditAllianceContact = OfferRemoveAllianceContact

    def OfferRemoveCorpContact(self):
        if self.IsNPC():
            return False
        if not self.session.IsDiplomat():
            return False
        return self.IsInCorpAddressBook()

    OfferEditCorpContact = OfferRemoveCorpContact

    def OfferRemoveFromAddressbook(self):
        if self.IsMe():
            return False
        if not self.IsNPC():
            return False
        if not self.IsAgent():
            return False
        return self.IsInAddressBook()

    def OfferSendCorpInvite(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.IsPersonnelManager():
            return False
        if self.session.isPilotInSameCorpAs(self.characterID):
            return False
        return True

    def OfferSendPilotEVEMail(self):
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return True

    def OfferShowInfo(self):
        if not self.IsAgent():
            return True
        return not self.IsAura()

    def OfferStartConversation(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if self.IsNPC():
            return False
        return True

    def OfferStartConversationAgent(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        if not self.IsNPC():
            return False
        return self.IsAgent()

    def OfferUnblockContact(self):
        if self._multiSelection:
            return False
        if self.IsMe():
            return False
        return self.IsBlocked()

    def OfferViewCorpMemberDetails(self):
        if self._multiSelection:
            return False
        if self.IsNPC():
            return False
        if not self.session.isPilotInSameCorpAs(self.characterID):
            return False
        if self.session.IsCorpDirector():
            return False
        return True

    def IsAgent(self):
        return self.agents.IsAgent(self.characterID)

    def IsAura(self):
        agentInfo = self.GetAgentInfo()
        if not agentInfo:
            return False
        return agentInfo.agentTypeID == appConst.agentTypeAura

    def IsBlocked(self):
        return self.addressbook.IsBlocked(self.characterID)

    def IsGuest(self):
        if self.session.stationid and self.sm.GetService('station').IsGuest(self.characterID):
            return True
        if self.session.structureid and self.sm.GetService('structureGuests').IsGuest(self.characterID):
            return True
        return False

    def IsMe(self):
        return self.characterID == self.session.charid

    def IsNPC(self):
        return IsNPC(self.characterID)

    def IsInAddressBook(self):
        return self.addressbook.IsInAddressBook(self.characterID, 'contact')

    def IsInAllianceAddressBook(self):
        return self.addressbook.IsInAddressBook(self.characterID, 'alliancecontact')

    def IsInCorpAddressBook(self):
        return self.addressbook.IsInAddressBook(self.characterID, 'corpcontact')

    def IsPilotFleetCreator(self):
        memberInfo = self.GetFleetMembers().get(self.session.charid)
        return memberInfo and memberInfo.job & fleetConst.fleetJobCreator

    def GetAgentInfo(self):
        return self.agents.GetAgentByID(self.characterID)

    def GetAgentLocation(self):
        agentInfo = self.GetAgentInfo()
        if getattr(agentInfo, 'locationID', None):
            return agentInfo.locationID
        elif getattr(agentInfo, 'stationID', None):
            return agentInfo.stationID
        else:
            return getattr(agentInfo, 'solarsystemID', None)

    def GetFleetMembers(self):
        return self.fleetSvc.GetMembers()

    def GetMemberInfo(self):
        return self.GetFleetMembers().get(self.characterID)

    def HasCloneBay(self):
        return self.sm.GetService('clonejump').HasCloneReceivingBay()


import evefleet
from eve.client.script.util.bubble import SlimItemFromCharID

@decorated_checker

class FleetMemberChecker(CharacterChecker):

    def __init__(self, characterID, session, cfg, sm = None):
        super(FleetMemberChecker, self).__init__(characterID, 0, session, sm)
        self.typeID = cfg.eveowners.Get(characterID).typeID

    def OfferAddPilotToWatchlist(self):
        if self.IsMe():
            return False
        return not self.IsFavorite()

    def OfferBridgeToMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.GetShipItem():
            return False
        if not self.HasActiveBeacon():
            return False
        return self.session.canOpenJumpPortal()

    def OfferGroupJumpToFleetMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.GetShipItem():
            return False
        if not self.HasActiveBeacon():
            return False
        return self.session.canPerformGroupJump()

    def OfferBroadcastTravelToMe(self):
        if not self.IsMe():
            return False
        if self.IsPilotFleetCreator():
            return True
        if self.session.IsPilotFleetCommander():
            return True
        return False

    def OfferJumpToFleetMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if self.GetShipItem():
            return False
        if not self.HasActiveBeacon():
            return False
        return self.session.isShipJumpCapable()

    def OfferKickFleetMember(self):
        if self.IsMe():
            return False
        if self.IsPilotFleetCreator():
            return True
        if self.IsSubordinate():
            return True
        return False

    def OfferMakeFleetLeader(self):
        if self.IsMe():
            return False
        return self.IsPilotFleetCreator()

    def OfferRemovePilotFromWatchlist(self):
        if self.IsMe():
            return False
        return self.IsFavorite()

    def OfferWarpToMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        return self.session.isInWarpRange(self.GetDistanceToActiveShip() or sys.maxint)

    def OfferWarpFleetToMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.session.IsPilotFleetLeader():
            return False
        return self.session.isInWarpRange(self.GetDistanceToActiveShip() or sys.maxint)

    def OfferWarpWingToMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.session.IsPilotWingCommander():
            return False
        return self.session.isInWarpRange(self.GetDistanceToActiveShip() or sys.maxint)

    def OfferWarpSquadToMember(self):
        if self.IsMe():
            return False
        if not self.session.IsPilotInShipInSpace():
            return False
        if not self.session.IsPilotSquadCommander():
            return False
        return self.session.isInWarpRange(self.GetDistanceToActiveShip() or sys.maxint)

    def IsCommander(self):
        memberInfo = self.GetMemberInfo()
        return memberInfo and memberInfo.job & evefleet.fleetCmdrRoles

    def IsFavorite(self):
        return self.fleetSvc.IsFavorite(self.characterID)

    def IsFleetMember(self):
        if not self.session.IsPilotFleetMember():
            return False
        if not self.GetMemberInfo():
            return False
        return True

    def IsSubordinate(self):
        return self.fleetSvc.IsMySubordinate(self.characterID)

    def HasActiveBeacon(self):
        return self.fleetSvc.HasActiveBeacon(self.characterID)

    def GetDistanceToActiveShip(self):
        bp = self.getBallpark()
        if bp is None:
            return
        if self.session.shipid not in bp.balls:
            return
        shipItem = self.GetShipItem()
        if not shipItem:
            return
        otherBall = bp.GetBall(shipItem.itemID)
        if not otherBall:
            return
        return max(0, otherBall.surfaceDist)

    def GetShipItem(self):
        return SlimItemFromCharID(self.characterID)
