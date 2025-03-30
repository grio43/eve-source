#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\undockingSvc.py
import blue
import gametime
import uthread
from carbon.common.script.sys.service import Service
from carbonui.uicore import uicore
from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd
from eve.client.script.ui.station.undockQuestions import IsOkToUndock, IsOkToUndockWithMissingCargo, CheckOkToUndockWhileAttackerInFW
from eve.common.lib import appConst as const
from eveexceptions import UserError
from journey.journey_messanger import JourneyMessenger
UNDOCK_STEPS = 3
UNDOCK_DELAY = 5000

class UndockingSvc(Service):
    __guid__ = 'svc.undocking'
    __servicename__ = 'undocking'

    def Run(self, memStream = None):
        self.LogInfo('Starting Undocking Service')
        self._exitTriggeredTimestamp = None
        self._exitingLocation = None
        self.pastUndockPointOfNoReturn = False
        self.undockCheck = None
        self._message_bus = None

    @property
    def message_bus(self):
        if self._message_bus is None:
            self._message_bus = JourneyMessenger(sm.GetService('publicGatewaySvc'))
        return self._message_bus

    def ActivateUndockCheck(self, undockCheck):
        self.undockCheck = undockCheck

    def DeactivateUndockCheck(self):
        self.undockCheck = None

    def CanUndock(self):
        if not callable(self.undockCheck):
            return True
        return self.undockCheck()

    def CheckUndock(self):
        CheckOkToUndockWhileAttackerInFW()

    def UndockBtnClicked(self):
        if self._exitTriggeredTimestamp:
            self.AbortUndock()
            return
        self.ExitDockableLocation()

    def ExitDockableLocation(self):
        if self._exitTriggeredTimestamp:
            return
        if not self.CanUndock():
            self.AbortUndock()
            return
        try:
            self.CheckUndock()
        except UserError as e:
            self.AbortUndock()
            uicore.Message(e.msg, e.dict)
            return

        exitingTime = gametime.GetWallclockTime()
        self._exitTriggeredTimestamp = exitingTime
        self._exitingLocation = session.stationid or session.structureid
        self.PrepareExit()
        if not IsOkToUndock():
            self.AbortUndock()
            return
        shipID = session.shipid
        if shipID is None:
            self._DealWithMissingShip()
            self.ResetDockingVariables()
            return
        if not IsOkToUndockWithMissingCargo():
            self.ResetDockingVariables()
            return
        uthread.new(self.message_bus.linked, 'Undock')
        uthread.new(self._Undock_Thread, shipID, exitingTime)

    def PrepareExit(self):
        viewSvc = sm.GetService('viewState')
        currentView = viewSvc.GetCurrentView()
        if currentView.name == 'hangar':
            currentView.StartExitAnimation()

    def _Undock_Thread(self, shipID, exitingTime):
        if not self._exitTriggeredTimestamp:
            sm.ScatterEvent('OnDockingProgressChanged', None)
            return
        sm.ScatterEvent('OnUndockingStarted', self._exitingLocation)
        undockDelay = GetUndockDelay()
        sleepingTime = undockDelay / UNDOCK_STEPS
        for i in xrange(UNDOCK_STEPS):
            progress = float(i) / UNDOCK_STEPS
            sm.ScatterEvent('OnDockingProgressChanged', progress)
            blue.synchro.SleepSim(sleepingTime)
            if self._exitTriggeredTimestamp != exitingTime:
                sm.ScatterEvent('OnDockingProgressChanged', None)
                return

        sm.ScatterEvent('OnDockingProgressChanged', 1)
        self.pastUndockPointOfNoReturn = True
        self.UndockAttempt(shipID)

    def UndockAttempt(self, shipID):
        success = False
        try:
            if session.stationid:
                success = sm.GetService('station').UndockAttempt(shipID)
            elif session.structureid:
                success = sm.GetService('structureDocking').Undock(session.structureid)
        except:
            self.AbortUndock()
            raise

        if success:
            locationID = self._exitingLocation
            self.ResetDockingVariables()
            sm.ScatterEvent('OnUndockingCompleted', locationID)
        else:
            self.AbortUndock()

    def _DealWithMissingShip(self):
        shipID = ShipPicker()
        if shipID is not None:
            sm.GetService('clientDogmaIM').GetDogmaLocation().MakeShipActive(shipID)
        else:
            eve.Message('NeedShipToUndock')

    def AbortUndock(self):
        locationID = self._exitingLocation
        self.ResetDockingVariables()
        ReloadLobbyWnd()
        viewSvc = sm.GetService('viewState')
        currentView = viewSvc.GetCurrentView()
        if currentView.name == 'hangar':
            currentView.StopExitAnimation()
        sm.ScatterEvent('OnUndockingAborted', locationID)

    def PastUndockPointOfNoReturn(self):
        return self.pastUndockPointOfNoReturn

    def IsExiting(self):
        return bool(self._exitTriggeredTimestamp)

    def GetUndockLocation(self):
        if not self.IsExiting():
            return None
        return self._exitingLocation

    def ResetDockingVariables(self):
        self._exitTriggeredTimestamp = None
        self._exitingLocation = None
        self.pastUndockPointOfNoReturn = False


def GetUndockDelay():
    undockDelay = UNDOCK_DELAY
    if session and session.nextSessionChange:
        duration = session.nextSessionChange - blue.os.GetSimTime()
        if duration > 0:
            undockDelay = max(undockDelay, (duration / const.SEC + 1) * 1000)
    return undockDelay


def ShipPicker():
    hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
    items = hangarInv.List(const.flagHangar)
    tmplst = []
    for item in items:
        if item[const.ixCategoryID] == const.categoryShip and item[const.ixSingleton]:
            import evetypes
            tmplst.append((evetypes.GetName(item[const.ixTypeID]), item[const.ixItemID], item[const.ixTypeID]))

    import localization
    from eve.client.script.ui.util import uix
    ret = uix.ListWnd(tmplst, 'item', localization.GetByLabel('UI/Station/SelectShip'), None, 1)
    if ret is None:
        return
    return ret[1]
