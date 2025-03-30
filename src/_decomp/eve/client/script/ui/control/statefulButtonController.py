#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\statefulButtonController.py
from eve.client.script.ui.const import buttonConst
from localization import GetByLabel
from signals.signal import Signal

class StatefulButtonController(object):
    __notifyevents__ = ['OnDestinationSet',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished',
     'OnWarpActive',
     'OnBallparkCall',
     'OnDockingProgressChanged',
     'OnClientEvent_UndockingAborted']

    def __init__(self, *args, **kwargs):
        self.onNewState = Signal(signalName='onNewState')
        self.onSetBusy = Signal(signalName='onSetBusy')
        self.buttonState = buttonConst.STATE_NONE
        super(StatefulButtonController, self).__init__(*args, **kwargs)
        sm.RegisterNotify(self)

    def OnDestinationSet(self, *args, **kwargs):
        self.SendNewStateSignal()

    def OnClientEvent_WarpStarted(self, *args):
        if self.buttonState not in (buttonConst.STATE_WARPTO, buttonConst.STATE_DOCK):
            return
        self.SendNewStateSignal()
        self.onSetBusy(buttonConst.STATE_PREPARING_WARP)

    def OnWarpActive(self, *args):
        if self.buttonState != buttonConst.STATE_PREPARING_WARP:
            return
        self.SendNewStateSignal()

    def OnClientEvent_WarpFinished(self, *args):
        if self.buttonState != buttonConst.STATE_WARPING:
            return
        self.SendNewStateSignal()

    def SendNewStateSignal(self):
        self.onNewState(self.GetButtonState())

    def OnBallparkCall(self, functionName, args):
        relevantShipEvents = ('FollowBall', 'Stop', 'GotoDirection', 'GotoPoint', 'Orbit')
        isBallMyShip = args[0] == session.shipid
        if isBallMyShip and functionName in relevantShipEvents:
            self.SendNewStateSignal()

    def OnDockingProgressChanged(self, progressFloat):
        if self.buttonState not in (buttonConst.STATE_UNDOCK, buttonConst.STATE_UNDOCKING):
            return
        self.SendNewStateSignal()

    def OnClientEvent_UndockingAborted(self, itemID):
        self.SendNewStateSignal()

    def IsButtonEnabled(self):
        return True

    def GetButtonTexturePath(self):
        return buttonConst.BUTTON_TEXTURE_PATH_BY_STATE.get(self.buttonState, None)

    def GetButtonLabel(self):
        buttonLabelPath = buttonConst.BUTTON_LABEL_PATH_BY_STATE.get(self.buttonState, None)
        if not buttonLabelPath:
            return
        return GetByLabel(buttonLabelPath)

    def GetButtonFunction(self):
        if self.buttonState in (buttonConst.STATE_UNDOCK, buttonConst.STATE_UNDOCKING):
            return lambda x: sm.GetService('undocking').UndockBtnClicked()

    def GetButtonState(self):
        self.buttonState = self._GetButtonState()
        return self.buttonState

    def _GetButtonState(self):
        return buttonConst.STATE_NONE

    def GetWarpingState(self):
        michelle = sm.GetService('michelle')
        if michelle.IsPreparingWarp():
            return buttonConst.STATE_PREPARING_WARP
        if michelle.InWarp():
            return buttonConst.STATE_WARPING

    def GetDisabledHint(self):
        pass
