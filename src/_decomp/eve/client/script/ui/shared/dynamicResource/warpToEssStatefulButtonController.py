#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicResource\warpToEssStatefulButtonController.py
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.control.statefulButtonController import StatefulButtonController
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import WarpToItem

class WarpToEssButtonController(StatefulButtonController):

    def __init__(self):
        StatefulButtonController.__init__(self)

    def _GetButtonState(self):
        michelle = sm.GetService('michelle')
        if michelle.IsPreparingWarp():
            return buttonConst.STATE_PREPARING_WARP
        elif michelle.InWarp():
            return buttonConst.STATE_WARPING
        elif self.IsEssWarpable() and not self.AmIInsideTheEssInstance():
            return buttonConst.STATE_WARPTO
        else:
            return buttonConst.STATE_NONE

    def GetButtonFunction(self):
        return self.WarpToEss

    def OnClientEvent_WarpFinished(self, *args):
        self.SendNewStateSignal()

    def IsEssWarpable(self):
        dynamicResourceSvc = sm.GetService('dynamicResourceSvc')
        essDataSource = dynamicResourceSvc.GetESSDataForCurrentSystem()
        if essDataSource is None:
            return False
        beaconID = essDataSource.get('beaconID', None)
        if beaconID is None:
            return False
        michelle = sm.GetService('michelle')
        ball = michelle.GetBall(beaconID)
        if ball is None:
            return False
        return michelle.IsPositionWithinWarpDistance((ball.x, ball.y, ball.z))

    def WarpToEss(self, *args):
        dynamicResourceSvc = sm.GetService('dynamicResourceSvc')
        essDataSource = dynamicResourceSvc.GetESSDataForCurrentSystem()
        beaconID = essDataSource.get('beaconID', None)
        WarpToItem(beaconID)

    def AmIInsideTheEssInstance(self):
        dynamicResourceSvc = sm.GetService('dynamicResourceSvc')
        essDataSource = dynamicResourceSvc.GetESSDataForCurrentSystem()
        essID = essDataSource.get('essID', None)
        if essID is None:
            return False
        else:
            distance = sm.GetService('michelle').GetBallpark().GetSurfaceDist(session.shipid, essID)
            if distance is None:
                return False
            return True
