#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\cynoTravelSvc.py
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eveexceptions import UserError

class CynoTravelSvc(Service):
    __guid__ = 'svc.cynoTravel'
    __servicename__ = 'CynoTravel'
    __displayname__ = 'Cyno Travel service'
    __startupdependencies__ = ['sessionMgr', 'michelle', 'fleet']
    __notifyevents__ = ['OnGroupJumpAnchorActivated', 'OnGroupJumpedPassenger']

    def OnGroupJumpAnchorActivated(self, toSolarsystemID, numPassengers):
        uicore.Message('GroupJumpAnchorActivated', {'toSolarsystemID': toSolarsystemID,
         'numPassengers': numPassengers})

    def OnGroupJumpedPassenger(self, anchorCharID, toSolarsystemID):
        uicore.Message('GroupJumpedPassenger', {'anchorCharID': anchorCharID,
         'toSolarsystemID': toSolarsystemID})

    def JumpToFleetModuleBeacon(self, charID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump To Module Beacon Fleet', charID, beaconID, solarsystemID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdJumpToFleetModuleBeacon, charID, beaconID, solarsystemID)

    def JumpToFleetDeployableBeacon(self, deployableID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump To Deployable Beacon Fleet', deployableID, solarsystemID, beaconID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdJumpToFleetDeployableBeacon, deployableID, solarsystemID, beaconID)

    def JumpToStructureBeacon(self, solarsystemID, structureID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Jump to structure beacon', structureID)
        self.sessionMgr.PerformSessionChange('jump', sm.RemoteSvc('structureCynoBeaconMgr').CmdJumpToStructureBeacon, structureID, solarsystemID)

    def BridgeToFleetModuleBeacon(self, charID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        bp.CmdBridgeToFleetModuleBeacon(charID, beaconID, solarsystemID)

    def BridgeToFleetDeployableBeacon(self, deployableID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('Bridge To Deployable Beacon Fleet', deployableID, solarsystemID, beaconID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdBridgeToFleetDeployableBeacon, deployableID, solarsystemID, beaconID)

    def BridgeToBeaconStructure(self, solarsystemID, structureID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        if not session.fleetid:
            raise UserError('FleetNotInFleet')
        sm.RemoteSvc('structureCynoBeaconMgr').CmdBridgeToStructureBeacon(structureID, solarsystemID)

    def JumpThroughFleet(self, otherCharID, otherShipID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        bridge = self.fleet.GetActiveBridgeForShip(otherShipID)
        if bridge is None:
            return
        solarsystemID, beaconID = bridge
        self.LogNotice('Jump Through Fleet', otherCharID, otherShipID, beaconID, solarsystemID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdJumpThroughFleet, otherCharID, otherShipID, beaconID, solarsystemID)

    def GroupJumpToFleetModuleBeacon(self, charID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('GroupJump To Module Beacon Fleet', charID, beaconID, solarsystemID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdGroupJumpToFleetModuleBeacon, charID, beaconID, solarsystemID)

    def GroupJumpToFleetDeployableBeacon(self, deployableID, solarsystemID, beaconID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        self.LogNotice('GroupJump To Deployable Beacon Fleet', deployableID, solarsystemID, beaconID)
        self.sessionMgr.PerformSessionChange('jump', bp.CmdGroupJumpToFleetDeployableBeacon, deployableID, solarsystemID, beaconID)

    def GroupJumpToStructureBeacon(self, solarsystemID, structureID):
        bp = self.michelle.GetRemotePark()
        if bp is None:
            return
        if not session.fleetid:
            raise UserError('FleetNotInFleet')
        self.LogNotice('GroupJump to structure beacon', structureID)
        self.sessionMgr.PerformSessionChange('jump', sm.RemoteSvc('structureCynoBeaconMgr').CmdGroupJumpToStructureBeacon, structureID, solarsystemID)
