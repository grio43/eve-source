#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureDeployment.py
import evetypes
import localization
import inventorycommon
import inventorycommon.util
import eve.client.script.ui.structure.deployment.deploymentContUtil as dUtil
from caching.memoize import Memoize
from carbon.common.lib.const import SEC
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.common.lib.appConst import corpRoleStationManager, factionTriglavian
from eve.client.script.ui.structure.deployment.miningBeaconEntity import MiningBeaconEntity
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.client.script.ui.structure.deployment.deploymentCont import StructureDeploymentWnd
from eve.client.script.ui.structure.deployment.deploymentEntity import StructurePlacementEntity
from eve.common.script.sys.idCheckers import IsWormholeSystem, IsTriglavianSystem
from eveexceptions import UserError
from eveuniverse.security import is_high_security_solar_system
from eveuniverse.solar_systems import GetNonNpcNullSecSystemsInLightYearDistanceDict, GetAlignmentYawPitchRadians, get_disallowed_categories
from inventorycommon.const import categoryStructure
from moonmining.miningBeacons import GetMiningBeaconPositionsForSolarsystem
from structures import IsDrillingPlatform, MAX_JUMPBRIDGE_RANGE_LIGHTYEARS, FLEX_UNANCHORING_TIME, UNANCHORING_TIME, STATE_UNKNOWN, STATE_UNANCHORED
from structures.deployment import GROUPS_REQUIRING_CONQUERABLE_SYSTEM, MAX_GROUP_PER_SOLARSYSTEM
from structures.types import IsFlexStructure
from utillib import KeyVal

class StructureDeployment(Service):
    __guid__ = 'svc.structureDeployment'
    __dependencies__ = ['machoNet',
     'viewState',
     'michelle',
     'faction',
     'sov',
     'tactical']
    __notifyevents__ = ['OnSessionChanged',
     'OnViewStateChanged',
     'OnClientEvent_WarpStarted',
     'OnItemChange',
     'DoBallClear']

    def Run(self, *args):
        self.isDeploying = False
        self.isMovingStrucuture = False
        self.tacticalOverlayWasOpen = None
        self.invItem = None
        self.wnd = None
        self.entity = None
        self.deploymentBeacons = []
        self.destinationSolarsystemID = None

    def Unanchor(self, structureID, typeID):
        if IsFlexStructure(typeID):
            unanchorDuration = FLEX_UNANCHORING_TIME
        else:
            unanchorDuration = UNANCHORING_TIME
        msgArgs = {'item': typeID,
         'unanchorDuration': unanchorDuration * SEC}
        questionName = 'ConfirmDecommissionStructure'
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
        numWars = len(structureInfo.wars)
        if numWars:
            msgArgs['numWars'] = numWars
            questionName = 'ConfirmDecommissionWarHq'
        if eve.Message(questionName, msgArgs, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.RemoteSvc('structureDeployment').Unanchor(structureID)

    def CancelUnanchor(self, structureID, typeID):
        sm.RemoteSvc('structureDeployment').CancelUnanchor(structureID)

    def IsStructureDeploymentBlocked(self, solarSystemID, typeID):
        disallowedAnchorCategories = get_disallowed_categories(solarSystemID)
        if categoryStructure in disallowedAnchorCategories:
            return True
        if is_high_security_solar_system(solarSystemID):
            disallowedInHighSec = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(typeID, const.attributeDisallowInHighSec, False)
            if disallowedInHighSec:
                return True
        return False

    def Deploy(self, invItem):
        if self.isDeploying:
            return
        if not self.viewState.IsViewActive('inflight'):
            return
        if not InShipInSpace():
            return
        if self.michelle.InWarp():
            raise UserError('ShipInWarp')
        if inventorycommon.util.IsNPC(session.corpid):
            raise UserError('DropNeedsPlayerCorp', {'item': invItem.typeID})
        if not session.corprole & corpRoleStationManager:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/InsufficientRoles')})
        if self.IsStructureDeploymentBlocked(session.solarsystemid, invItem.typeID):
            raise UserError('CantDeployBlocked', {'typeID': invItem.typeID})
        if IsTriglavianSystem(session.solarsystemid):
            raise UserError('CannotBeDeployedInSystemOwnedByFaction', {'deployTypeID': invItem.typeID,
             'factionID': factionTriglavian})
        if invItem.groupID in MAX_GROUP_PER_SOLARSYSTEM:
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                currentlyInSystem = {x for x in bp.slimItems.itervalues() if x.groupID == invItem.groupID and x.state not in (STATE_UNKNOWN, STATE_UNANCHORED)}
                maxStructureGroupPerSolarsystem = MAX_GROUP_PER_SOLARSYSTEM[invItem.groupID]
                if len(currentlyInSystem) >= maxStructureGroupPerSolarsystem:
                    raise UserError('CantDeployStructureGroupMaxAlreadyInSystem', {'type': invItem.typeID,
                     'maxStructureGroupPerSolarsystem': maxStructureGroupPerSolarsystem})
        if invItem.groupID in GROUPS_REQUIRING_CONQUERABLE_SYSTEM:
            if IsWormholeSystem(session.solarsystemid2):
                raise UserError('CantDeployBlocked', {'typeID': invItem.typeID})
            if self.faction.GetFactionOfSolarSystem(session.solarsystemid) is not None:
                raise UserError('CanOnlyBeDeployedInNonEmpireSpace', {'deployTypeID': invItem.typeID})
            if self.sov.GetInfrastructureHubInfo(session.solarsystemid) is None:
                if eve.Message('ConfirmAnchorSovStructureWithoutIHub', {'typeID': invItem.typeID}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return
        try:
            self.invItem = invItem
            self.isDeploying = True
            self.entity = StructurePlacementEntity(invItem.typeID)
            self._SetupDeploymentBeacons(invItem.typeID)
            self.wnd = StructureDeploymentWnd.Open(controller=self, useDefaultPos=True, typeID=invItem.typeID)
            tacticalOverlayOpen = self.tactical.IsTacticalOverlayActive()
            self.tacticalOverlayWasOpen = tacticalOverlayOpen
            if not tacticalOverlayOpen:
                self.tactical.ShowTacticalOverlay()
        except Exception:
            self._Cleanup()
            raise

    def _SetupDeploymentBeacons(self, structureTypeID):
        if not IsDrillingPlatform(structureTypeID):
            return
        miningBeaconPositions = GetMiningBeaconPositionsForSolarsystem(session.solarsystemid)
        for moonID, beaconPosition in miningBeaconPositions.iteritems():
            beacon = MiningBeaconEntity(beaconPosition)
            self.deploymentBeacons.append(beacon)

    def IsDeploying(self):
        return self.isDeploying

    def _Cleanup(self):
        if self.wnd:
            self.wnd.Close()
            self.wnd = None
        if self.tacticalOverlayWasOpen is False:
            self.tactical.HideTacticalOverlay()
            self.tacticalOverlayWasOpen = None
        self.isDeploying = False
        if self.entity:
            self.entity.Close()
            self.entity = None
        self.destinationSolarsystemID = None
        self._CleanupDeploymentBeacons()

    def _CleanupDeploymentBeacons(self):
        while self.deploymentBeacons:
            beacon = self.deploymentBeacons.pop()
            beacon.Close()

    def ConfirmDeployment(self, reinforceWeekday, reinforceHour, profileID = None, structureName = '', bio = '', extraVariables = {}):
        pos = self.entity.GetPosition()
        rotation = self.entity.GetRotation()
        extraConfig = KeyVal()
        if evetypes.IsUpwellStargate(self.invItem.typeID):
            destinationSolarsystemID = extraVariables['destinationSolarsystemID']
            extraConfig.destinationSolarsystemID = destinationSolarsystemID
        sm.RemoteSvc('structureDeployment').Anchor(self.invItem.itemID, pos[0], pos[2], rotation[0], profileID, structureName, bio, reinforceWeekday, reinforceHour, extraConfig)
        self._Cleanup()
        sm.GetService('structureDirectory').Reload()

    def CancelDeployment(self):
        self._Cleanup()

    def IsOnPositionStep(self):
        if not self.wnd:
            return False
        return self.wnd.step == dUtil.STEP_POSITION

    def StartMovingStructure(self):
        self.isMovingStrucuture = True
        self.entity.StartMoving()

    def EndMovingStructure(self):
        self.isMovingStrucuture = False
        if self.entity:
            self.entity.EndMoving()

    def IsMovingStructure(self):
        return self.isMovingStrucuture

    def GetCaption(self):
        return evetypes.GetName(self.invItem.typeID)

    def GetSubCaption(self):
        return 'Drag structure gantry with left mouse button and rotate with right'

    def OnSessionChanged(self, *args):
        self.CancelDeployment()

    def OnItemChange(self, item, change, location):
        if self.invItem and self.invItem.itemID == item.itemID:
            self.CancelDeployment()

    def OnViewStateChanged(self, *args):
        self.CancelDeployment()

    def OnClientEvent_WarpStarted(self, *args):
        self.CancelDeployment()

    def DoBallClear(self, *args):
        self.CancelDeployment()

    def MoveDragObject(self):
        if self.entity:
            self.entity.MoveDragObject()

    def RotateDragObject(self):
        if self.entity:
            self.entity.RotateDragObject()

    def GetEntity(self):
        return self.entity

    def GetDestinationSolarsystemID(self):
        return self.destinationSolarsystemID

    def SetDestinationSolarsystemID(self, solarSystemID):
        self.destinationSolarsystemID = solarSystemID
        yaw, pitch = GetAlignmentYawPitchRadians(session.solarsystemid, solarSystemID)
        self.entity.SetModelRotation(yaw, pitch, 0)
        sm.ScatterEvent('OnExtraDeploymentInfoChanged', {'destinationSolarsystemID': solarSystemID})

    def GetNearbyJumpBridges(self):
        return self._GetNearbyJumpBridges(session.solarsystemid)

    @Memoize(1)
    def _GetNearbyJumpBridges(self, solarSystemID):
        nearbyJumpBridges = sm.RemoteSvc('structureDirectory').GetNearbyJumpBridges()
        return {x.solarSystemID:x for x in nearbyJumpBridges}

    @Memoize
    def GetSystemsInLightYearDistanceForJumpGateDict(self, solarSystemID):
        return GetNonNpcNullSecSystemsInLightYearDistanceDict(solarSystemID, MAX_JUMPBRIDGE_RANGE_LIGHTYEARS)
