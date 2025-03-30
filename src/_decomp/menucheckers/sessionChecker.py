#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\sessionChecker.py
from evestations.data import service_in_station_operation
from menucheckers.baseCheckers import _ServiceAccessChecker
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsPlayerCorporation, IsDockableStructure, IsWormholeSystem, IsNPC, IsCapsule
from inventorycommon import const as invConst
from menucheckers.decorators import decorated_checker, explain_failure_with
from structures import SERVICE_REPROCESSING, SERVICE_INSURANCE
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER, ROLE_GMH
from evefleet import fleetRoleLeader, fleetRoleWingCmdr, fleetRoleSquadCmdr, fleetCmdrRoles
from eve.client.script.parklife import states
from destiny import DSTBALL_WARP
import dogma.const as dogmaconst

@decorated_checker

class SessionChecker(_ServiceAccessChecker):

    def __init__(self, session, sm = None):
        super(SessionChecker, self).__init__(sm)
        self.session = session
        self._failure_label = None

    def __getattr__(self, attr):
        return getattr(self.session, attr)

    @property
    def failure_label(self):
        try:
            return self._checker.failure_label
        except (AttributeError, ReferenceError):
            return self._failure_label

    @failure_label.setter
    def failure_label(self, value):
        try:
            self._checker.failure_label = value
        except (AttributeError, ReferenceError):
            self._failure_label = value

    def IsAccountant(self):
        return bool(self.corprole & appConst.corpRoleAccountant)

    def IsAccountantOrJunior(self):
        return bool(self.corprole & (appConst.corpRoleJuniorAccountant | appConst.corpRoleAccountant))

    def IsAllianceMember(self):
        return bool(getattr(self.session, 'allianceid', None))

    def IsEquipmentConfigurator(self):
        return bool(self.corprole & appConst.corpRoleEquipmentConfig)

    def IsExecutorCorp(self):
        if not self.IsAllianceMember():
            return False
        allianceInfo = self.sm.GetService('alliance').GetAlliance(self.allianceid)
        return self.corpid == allianceInfo.executorCorpID

    def IsChatManager(self):
        return bool(self.corprole & appConst.corpRoleChatManager)

    def IsCorpDirector(self):
        return bool(self.corprole & appConst.corpRoleDirector)

    def IsDiplomat(self):
        return bool(self.corprole & (appConst.corpRoleDirector | appConst.corpRoleDiplomat))

    def IsElevatedPlayer(self):
        return bool(self.role & ROLEMASK_ELEVATEDPLAYER)

    def IsInPlayerCorp(self):
        return IsPlayerCorporation(self.corpid)

    @explain_failure_with('UI/Menusvc/MenuHints/NotInWarpRange')
    def isInWarpRange(self, distance):
        return distance is not None and distance > appConst.minWarpDistance

    def IsInWormholeSystem(self):
        return IsWormholeSystem(self.solarsystemid)

    def IsInZeroSec(self):
        return self.sm.GetService('map').GetSecurityClass(self.solarsystemid) == appConst.securityClassZeroSec

    def IsPersonnelManager(self):
        return bool(self.corprole & appConst.corpRolePersonnelManager)

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreCloaked')
    def isPilotCloaked(self):
        ball = self.getBall(self.shipid)
        return ball and bool(ball.isCloaked)

    def IsPilotControllingStructure(self):
        return self.IsPilotInStructure() and self.structureid == self.shipid

    def IsPilotControllingUndockableStructure(self):
        if not self.IsPilotControllingStructure():
            return False
        ball = self.getBall(self.shipid)
        return ball and not IsDockableStructure(ball.typeID)

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreCriminal')
    def isPilotCriminal(self):
        return self.sm.GetService('crimewatchSvc').IsCriminal(session.charid)

    def IsPilotDocked(self):
        return self.IsPilotInStation() or self.IsPilotInStructure()

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreDockedInStructure')
    def IsPilotDockedInStructure(self):
        return self.IsPilotInStructure() and not self.IsPilotControllingStructure()

    def IsPilotFleetCommander(self):
        return self.fleetrole in fleetCmdrRoles

    def IsPilotFleetLeader(self):
        return self.fleetrole == fleetRoleLeader

    def IsPilotFleetMember(self):
        return bool(self.fleetid)

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreInCapsule')
    def IsPilotInCapsule(self):
        activeShip = self.getActiveShipGodmaItem()
        return activeShip and IsCapsule(activeShip.groupID)

    def IsPilotInNpcCorp(self):
        return IsNPC(self.corpid)

    @staticmethod
    def isPilotInSameCorpAs(ownerID):
        return ownerID in sm.GetService('corp').GetMemberIDs()

    def isPilotInSameFleetAs(self, ownerID):
        return self.IsPilotFleetMember() and ownerID in sm.GetService('fleet').GetMembers()

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreNotInShip')
    def IsPilotInShipInSpace(self):
        return bool(self.solarsystemid) and bool(self.shipid) and not bool(self.structureid)

    def IsPilotInStation(self):
        return bool(self.stationid)

    def IsPilotInStructure(self):
        return bool(self.structureid)

    def IsPilotSquadCommander(self):
        return self.fleetrole == fleetRoleSquadCmdr

    @explain_failure_with('UI/Menusvc/MenuHints/YouAreInWarp')
    def isPilotWarping(self):
        ball = self.getBall(self.shipid)
        return ball and ball.mode == DSTBALL_WARP

    def IsPilotWingCommander(self):
        return self.fleetrole == fleetRoleWingCmdr

    def IsStationManager(self):
        return bool(self.corprole & appConst.corpRoleStationManager)

    def IsStarbaseCaretaker(self):
        return bool(self.corprole & appConst.corpRoleStarbaseCaretaker)

    def IsTrader(self):
        return bool(self.corprole & appConst.corpRoleTrader)

    def canInsure(self, stationServices):
        if self.stationid:
            return appConst.stationServiceInsurance in stationServices
        if self.structureid:
            return self.isStructureServiceAvailableToPilot(SERVICE_INSURANCE)
        return False

    def canRefine(self, stationServices):
        if self.stationid:
            if appConst.stationServiceRefinery in stationServices:
                return True
            if appConst.stationServiceReprocessingPlant in stationServices:
                return True
        elif self.structureid:
            return self.isStructureServiceAvailableToPilot(SERVICE_REPROCESSING)
        return False

    def CanRepairAtStation(self):
        if not self.stationid:
            return False
        return sm.GetService('station').IsStationServiceAvailable(appConst.stationServiceRepairFacilities)

    def canTakeFromCorpDivision(self, stationID, flagID):
        if flagID not in invConst.flagCorpSAGs:
            return False
        if stationID is None:
            return False
        roleRequired = appConst.corpHangarTakeRolesByFlag[flagID]
        if stationID == self.hqID:
            rolesToUse = self.rolesAtHQ
        elif stationID == self.baseID:
            rolesToUse = self.rolesAtBase
        else:
            rolesToUse = self.rolesAtOther
        if roleRequired & rolesToUse:
            return True
        return False

    def CanTakeFromDeliveries(self):
        return self.IsAccountantOrJunior() or self.IsTrader()

    def HasGMHRole(self):
        return bool(self.role & ROLE_GMH)

    def getActiveShipGodmaItem(self):
        return self.GetStateManager().GetItem(self.shipid)

    def getBall(self, ballID = None):
        bp = self.getBallpark()
        if not bp:
            return None
        return bp.GetBall(ballID or self.shipid)

    def isShipJumpCapable(self):
        if self.IsPilotInStructure():
            return False
        if self.IsInWormholeSystem():
            return False
        if not self.getActiveShipAttributeValue(dogmaconst.attributeCanJump):
            return False
        return True

    def canOpenJumpPortal(self):
        return self.isShipJumpCapable() and self.isShipFittedWithModuleWithRequiredAttribute(dogmaconst.attributeJumpPortalPassengerRequiredAttributeID)

    def canPerformGroupJump(self):
        return self.isShipJumpCapable() and self.getActiveShipAttributeValue(dogmaconst.attributeJumpConduitPassengerRequiredAttributeID)

    def isShipFittedWithModuleWithRequiredAttribute(self, requiredAttributeID):
        shipItem = self.getActiveShipGodmaItem()
        if shipItem is None:
            return False
        stateManager = self.GetStateManager()
        for moduleItem in shipItem.modules:
            if stateManager.GetAttributeValueByID(moduleItem.itemID, requiredAttributeID):
                return True

        return False

    def getActiveShipAttributeValue(self, attributeID):
        if not self.shipid:
            return None
        stateManager = self.GetStateManager()
        return stateManager.GetAttributeValueByID(self.shipid, attributeID)

    def GetWarFactionID(self):
        return self.warfactionid
