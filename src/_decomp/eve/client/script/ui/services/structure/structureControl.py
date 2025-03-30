#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureControl.py
import evetypes
from caching.memoize import Memoize
from carbon.common.lib.const import UE_LOC
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.common.lib.appConst import corpRoleStationManager
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveexceptions import UserError
from inventorycommon.const import groupCapsule
from localization import GetByLabel
from menucheckers import CelestialChecker, SessionChecker
from structures import SETTING_DEFENSE_CAN_CONTROL_STRUCTURE
CAPSULE_SHIPID = -1

class StructureControl(Service):
    __guid__ = 'svc.structureControl'

    def __init__(self):
        self.oldShipID = None
        super(StructureControl, self).__init__()

    def TakeControl(self, structureID):
        if session.structureid and session.solarsystemid and structureID == session.structureid and not IsControllingStructure():
            sm.RemoteSvc('structureControl').TakeControl(session.structureid)
            self.oldShipID = None

    def BoardStructure(self, structureID):
        if session.structureid:
            return
        if not session.solarsystemid:
            return
        self.oldShipID = None
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(structureID)
        if structureInfo.solarSystemID != session.solarsystemid:
            raise RuntimeError("Structure isn't in this solar system")
        playerShipTypeID = sm.GetService('invCache').GetInventoryFromId(session.shipid).typeID
        if evetypes.GetGroupID(playerShipTypeID) != groupCapsule:
            if eve.Message('BoardingFlexStructure', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
                return
            self.oldShipID = session.shipid
        else:
            self.oldShipID = CAPSULE_SHIPID
        sm.StartService('sessionMgr').PerformSessionChange('board', sm.RemoteSvc('structureControl').BoardStructure, structureID)

    def ReleaseControl(self):
        if session.shipid == session.structureid:
            sm.RemoteSvc('structureControl').ReleaseControl()
            self.oldShipID = None

    def BoardPreviousShip(self):
        shipID, isCapsule = self.GetOldShipInfo()
        if not isCapsule:
            shipID = self._GetShipIDToBoardFromStructures(shipID)
            if shipID is None:
                raise UserError('CustomInfo', {'info': GetByLabel('UI/Inflight/HUDOptions/CantBoardShipFromStructure')})
        self.EjectFromStructure(shipID)

    def _GetShipIDToBoardFromStructures(self, oldShipID):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems.get(oldShipID)
        if not slimItem:
            return
        celestialChecker = CelestialChecker(slimItem, cfg, SessionChecker(session, sm))
        if celestialChecker.OfferBoardShip():
            return oldShipID
        if celestialChecker.failure_label:
            text = GetByLabel(celestialChecker.failure_label)
            raise UserError('CustomNotify', {'notify': text})

    def EjectFromStructure(self, shipID = None):
        if session.shipid == session.structureid:
            sm.StartService('sessionMgr').PerformSessionChange('board', sm.RemoteSvc('structureControl').EjectFromStructure, shipID)
            self.oldShipID = None

    @Memoize(0.1)
    def MayTakeControl(self, structureID):
        if structureID is None:
            return False
        return sm.GetService('structureSettings').CharacterHasSetting(structureID, SETTING_DEFENSE_CAN_CONTROL_STRUCTURE)

    @staticmethod
    def GetStructurePilot(structureID):
        if structureID is None:
            return
        return sm.RemoteSvc('structureControl').GetStructurePilot(structureID)

    @staticmethod
    def CheckCanDisableServiceModule(moduleItem):
        if session.corprole & corpRoleStationManager != corpRoleStationManager or session.corpid != moduleItem.ownerID:
            raise UserError('CrpAccessDenied', {'reason': (UE_LOC, 'UI/Corporations/AccessRestrictions/InsufficientRoles')})

    def GetOldShipInfo(self):
        if self.oldShipID == CAPSULE_SHIPID:
            return (None, True)
        return (self.oldShipID, False)
