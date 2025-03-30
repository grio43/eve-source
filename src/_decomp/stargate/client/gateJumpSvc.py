#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\gateJumpSvc.py
import localization
import logging
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.uicore import uicore
import gametime
from eveexceptions import UE_LOCID
from stargate.client import get_gate_lock_messenger
from stargate.client.emanationLockVisualization import EmanationLockVisualization
from stargate.client.const import SETTINGS_FIRST_WARNING_SHOWN
from stargate.client.jump_checks import check_cancel_stargate_jump
from stargate.client.gateLockController import GateLockController
from stargate.client.gate_signals import *
from spacecomponents.common.helper import HasAlignmentBasedTollSpaceComponent, GetAlignmentBasedTollSpaceComponent
log = logging.getLogger(__name__)

class GateJumpSvc(Service):
    __guid__ = 'svc.gatejump'
    __servicename__ = 'gatejump'
    __displayname__ = 'Gate Jump service'
    __startupdependencies__ = ['publicGatewaySvc',
     'sessionMgr',
     'michelle',
     'starmap']
    __notifyevents__ = ['OnSessionChanged', 'OnStargateModelLoaded', 'OnCharacterSessionChanged']

    def Run(self, *args):
        Service.Run(self, *args)
        self._lockController = GateLockController.get_instance(get_gate_lock_messenger(self.publicGatewaySvc))
        on_lock_changed.connect(self.OnEmanationLockChanged)
        on_lock_changed_in_restricted_system.connect(self.OnEmanationLockChangedInRestrictedSystem)
        on_lock_added.connect(self.OnEmanationLockAdded)
        on_lock_removed.connect(self.OnEmanationLockRemoved)

    def OnStargateModelLoaded(self, space_object):
        lock_details = self.GetGateLockDetails()
        if lock_details is None:
            return
        EmanationLockVisualization.update_gate_space_object_visuals(space_object, lock_details.gate_id)

    def OnSessionChanged(self, isremote, session, change):
        if self._IsSolarSystemTransition(change):
            self._lockController.on_entered_system(session.solarsystemid2)

    def OnCharacterSessionChanged(self, oldCharacter, newCharacter):
        self._lockController.on_character_changed()

    def _IsSolarSystemTransition(self, change):
        return 'solarsystemid2' in change

    def OnEmanationLockRemoved(self, lock_details):
        self._OnEmanationLockUpdated(lock_details)

    def OnEmanationLockAdded(self, lock_details):
        self._OnEmanationLockUpdated(lock_details)

    def OnEmanationLockChangedInRestrictedSystem(self, lock_details, previous_lock):
        self._OnEmanationLockUpdated(lock_details)

    def OnEmanationLockChanged(self, lock_details, previous_lock):
        self._OnEmanationLockUpdated(lock_details)

    def _OnEmanationLockUpdated(self, lock_details):
        sm.ScatterEvent('OnEmanationLockUpdated', lock_details)
        if session.solarsystemid is None:
            return
        lock_details = self.GetGateLockDetails()
        if lock_details is None:
            EmanationLockVisualization.clear_blocked_gate_visuals(session.solarsystemid2)
        else:
            EmanationLockVisualization.update_blocked_gate_visuals(session.solarsystemid2, lock_details.gate_id)

    def CheckForGateRestriction(self, solarSystemID, stargateID):
        gateRestriction = self.GetGateLockDetails()
        if gateRestriction is not None and solarSystemID == gateRestriction.solar_system_id and stargateID != gateRestriction.gate_id and gateRestriction.expiry_time > gametime.now():
            return True
        return False

    def JumpThroughGate(self, stargateID, typeID, beaconID, solarSystemID):
        if beaconID is None:
            return
        remoteBallpark = self.michelle.GetRemotePark()
        if remoteBallpark is None:
            return
        if solarSystemID is not None:
            if check_cancel_stargate_jump(stargateID, solarSystemID):
                return
        self.LogNotice('Stargate Jump from', session.solarsystemid2, 'to', stargateID)
        if not self._canUseGate(stargateID, typeID):
            return
        if self.CheckForGateRestriction(session.solarsystemid, stargateID):
            lock_details = self.GetGateLockDetails()
            time_remaining = max(gametime.GetTimeUntilNowFromDateTime(lock_details.expiry_time), 0)
            uicore.Message('CantJumpEmanationLockedToAnotherGate', {'gateName': (UE_LOCID, lock_details.gate_id),
             'timeLeft': long(time_remaining)}, uiconst.CLOSE)
            return
        if solarSystemID in self._lockController.get_restricted_systems():
            systemName = cfg.evelocations.Get(solarSystemID).locationName
            hasShownFirstWarning = settings.char.ui.Get(SETTINGS_FIRST_WARNING_SHOWN, False)
            if hasShownFirstWarning:
                uicore.Message('EmanationLockEnterGateToRestrictedSystemNotification', {'system': systemName})
            else:
                settings.char.ui.Set(SETTINGS_FIRST_WARNING_SHOWN, True)
                uicore.Message('EmanationLockFirstWarning', {'system': systemName})
        self.sessionMgr.PerformSessionChange(localization.GetByLabel('UI/Inflight/Jump'), remoteBallpark.CmdStargateJump, stargateID, beaconID, session.shipid)
        if self.IsNextSystemInRoute(solarSystemID):
            sm.ScatterEvent('OnClientEvent_JumpedToNextSystemInRoute')

    def IsNextSystemInRoute(self, solarSystemID):
        destinationPath = self.starmap.GetDestinationPath()
        isSystemNextInRoute = destinationPath and destinationPath[0] == solarSystemID
        return isSystemNextInRoute

    def _canUseGate(self, itemID, typeID):
        if HasAlignmentBasedTollSpaceComponent(typeID):
            ballpark = self.michelle.GetBallpark()
            alignmentTollComponent = GetAlignmentBasedTollSpaceComponent(ballpark.componentRegistry, itemID)
            return alignmentTollComponent.CheckWithPlayer(ballpark)
        return True

    def GetGateLockDetails(self):
        return self._lockController.get_current_system_lock()
