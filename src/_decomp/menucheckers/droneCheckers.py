#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\droneCheckers.py
import inventorycommon.const as invConst
import eve.common.lib.appConst as appConst
from menucheckers.decorators import decorated_checker, explain_failure_with
from menucheckers.itemCheckers import ItemChecker
from evetypes import GetGroupNameByGroup

@decorated_checker

class DroneChecker(ItemChecker):

    def __init__(self, droneItem):
        super(DroneChecker, self).__init__(droneItem)

    def OfferAbandonDrone(self):
        if not self.IsOwnedByMe():
            return False
        return self.HasDroneState()

    def OfferDroneAssist(self):
        if not self.IsOwnedByMe():
            return False
        if not self.IsControlledByActiveShip():
            return False
        if not self.session.IsPilotFleetMember():
            return False
        return True

    OfferDroneGuard = OfferDroneAssist

    def OfferDroneUnanchorObject(self):
        if not self.HasDroneState():
            return False
        if not self.IsControlledByActiveShip():
            return False
        if not self.IsUnanchoringDrone():
            return False
        return True

    def OfferEngageTarget(self):
        if not self.HasDroneState():
            return False
        if not self.IsControlledByActiveShip():
            return False
        if self.IsMiningDrone() or self.IsUnanchoringDrone() or self.IsSalvageDrone():
            return False
        return True

    def OfferMineWithDrone(self):
        if not self.HasDroneState():
            return False
        if not self.IsControlledByActiveShip():
            return False
        return self.IsMiningDrone()

    def OfferReturnAndOrbit(self):
        if not self.HasDroneState():
            return False
        if not self.IsControlledByActiveShip():
            return False
        if not self.IsOwnedByMe():
            return False
        return True

    def OfferReturnToDroneBay(self):
        if not self.HasDroneState():
            return False
        if not self.IsOwnedByMe():
            return False
        return True

    def OfferSalvage(self):
        if not self.IsControlledByActiveShip():
            return False
        return self.IsSalvageDrone()

    def OfferScoopDroneToBay(self):
        if not self.IsDirectlyInSpace():
            return False
        if not self.IsInPilotLocation():
            return False
        if not self.IsWithinWarpDistance():
            return False
        if not self.IsScoopableDrone():
            return False
        if self.session.IsPilotControllingStructure():
            return False
        return True

    @explain_failure_with('UI/Menusvc/MenuHints/DoNotControlDrone')
    def IsControlledByActiveShip(self):
        return self.GetController() == self.session.shipid

    @explain_failure_with('UI/Menusvc/MenuHints/ThisIsNot', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsMiningDrone(self):
        return self.item.groupID == invConst.groupMiningDrone

    @explain_failure_with('UI/Menusvc/MenuHints/ThisIsNot', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsUnanchoringDrone(self):
        return self.item.groupID == invConst.groupUnanchoringDrone

    @explain_failure_with('UI/Menusvc/MenuHints/ThisIsNot', groupName=(GetGroupNameByGroup, 'groupID'))
    def IsSalvageDrone(self):
        return self.item.groupID == invConst.groupSalvageDrone

    @explain_failure_with('UI/Menusvc/MenuHints/DroneIncapacitated')
    def IsControlled(self):
        return bool(self.GetController())

    @explain_failure_with('UI/Menusvc/MenuHints/DoNotOwnDrone')
    def IsOwnedByMe(self):
        return super(DroneChecker, self).IsOwnedByMe()

    @explain_failure_with('UI/Menusvc/MenuHints/DroneCannotBeScooped')
    def IsScoopableDrone(self):
        return not self.HasDroneState()

    def IsWithinWarpDistance(self):
        ballpark = self.GetBallpark()
        if not ballpark:
            return False
        if self.item.itemID not in ballpark.balls:
            return False
        if self.session.shipid not in ballpark.balls:
            return False
        return ballpark.DistanceBetween(self.session.shipid, self.item.itemID) <= appConst.minWarpDistance

    def GetController(self):
        try:
            return self.item.droneState.controllerID
        except AttributeError:
            return None

    @explain_failure_with('UI/Menusvc/MenuHints/DroneIncapacitated')
    def HasDroneState(self):
        return bool(getattr(self.item, 'droneState', False))
