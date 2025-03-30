#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureDocking.py
from carbon.common.lib.const import UE_LOC
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.client.script.ui.shared.skillRequirementDialog import prompt_missing_skill_requirements
from eve.common.script.sys.eveCfg import IsControllingStructure
from eveexceptions import UserError

class StructureDocking(Service):
    __guid__ = 'svc.structureDocking'
    __dependencies__ = ['autoPilot',
     'clientDogmaIM',
     'gameui',
     'sessionMgr']

    @property
    def dogmaLocation(self):
        return self.clientDogmaIM.GetDogmaLocation()

    def Undock(self, structureID):
        if not self._InStateToUndock(structureID):
            return False

        def TryUndockOnServer(doIgnoreContraband):
            if session.shipid == session.structureid:
                shipID = None
            else:
                shipID = session.shipid
            sm.RemoteSvc('structureDocking').Undock(session.structureid, shipID, ignoreContraband=doIgnoreContraband)

        try:
            ignoreContraband = settings.user.suppress.Get('suppress.ShipContrabandWarningUndock', None) == uiconst.ID_OK
            self.sessionMgr.PerformSessionChange('undock', TryUndockOnServer, doIgnoreContraband=ignoreContraband)
            sm.GetService('space').PrioritizeLoadingForIDs([structureID])
        except UserError as e:
            if e.msg == 'ShipContrabandWarningUndock':
                if eve.Message(e.msg, e.dict, uiconst.OKCANCEL, suppress=uiconst.ID_OK) == uiconst.ID_OK:
                    self.sessionMgr.PerformSessionChange('undock', TryUndockOnServer, doIgnoreContraband=True)
                else:
                    return False
            else:
                raise

        self.CloseStationWindows()
        return True

    def _InStateToUndock(self, structureID):
        if not session.structureid:
            return False
        if not session.solarsystemid:
            return False
        if structureID != session.structureid:
            return False
        return True

    def Dock(self, structureID):

        def RequestDocking():
            if session.shipid and session.solarsystemid:
                try:
                    sm.RemoteSvc('structureDocking').Dock(structureID, session.shipid)
                except UserError as e:
                    if e.msg == 'DockingRequestDenied':
                        reason = e.dict.get('reason')
                        if reason != (UE_LOC, 'UI/Station/StationManagment/ShipTooLarge'):
                            sm.ScatterEvent('OnDockingRequestWasDenied', structureID)
                    raise

        sm.ScatterEvent('OnClientEvent_DockCmdExecuted', structureID)
        self.autoPilot.NavigateSystemTo(structureID, 2500, RequestDocking)

    def ActivateShip(self, shipID):
        if session.structureid and not IsControllingStructure():
            typeID = sm.GetService('invCache').GetInventoryFromId(shipID).typeID
            if len(self.dogmaLocation.GetMissingSkills(typeID)) > 0:
                prompt_missing_skill_requirements(typeID)
                return
            self.dogmaLocation.MakeShipActive(shipID)

    def LeaveShip(self, shipID):
        if session.structureid:
            capsuleID = self.gameui.GetShipAccess().LeaveShip(shipID)
            self.dogmaLocation.MakeShipActive(capsuleID)

    def CloseStationWindows(self):
        from reprocessing.ui.reprocessingWnd import ReprocessingWnd
        ReprocessingWnd.CloseIfOpen()
