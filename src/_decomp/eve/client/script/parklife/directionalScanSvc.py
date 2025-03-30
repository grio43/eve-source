#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\directionalScanSvc.py
import blue
import geo2
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.service import Service
from eve.client.script.ui.camera.cameraUtil import GetBallPosition, GetBall
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import GetScanAngle, GetScanRangeInMeters
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos
from eveexceptions import UserError
THROTTLE_TIME = 1500

class DirectionalScanSvc(Service):
    __guid__ = 'svc.directionalScanSvc'
    __servicename__ = 'svc.directionalScanSvc'
    __displayname__ = 'Directional Scan Service'
    __notifyevents__ = []
    __dependencies__ = []
    __uthreads__ = []

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.isScanning = False
        self.hasScanExecutedDuringKeyPress = False

    def GetScanMan(self):
        return sm.GetService('scanSvc').GetScanMan()

    def DirectionalScan(self, direction = None, *args):
        self.hasScanExecutedDuringKeyPress = True
        if self.isScanning:
            return
        results = []
        scanAngle = GetScanAngle()
        scanRange = GetScanRangeInMeters()
        if not direction:
            direction = self.GetScanDirection()
        if not direction:
            return
        sm.ScatterEvent('OnDirectionalScanStarted')
        self.isScanning = True
        try:
            results = self.GetScanMan().ConeScan(scanAngle, scanRange, *direction)
            self.PlayResultSound(results)
            sm.ScatterEvent('OnDirectionalScanComplete', scanAngle, scanRange, direction, results)
        except UserError as e:
            raise e
        finally:
            uthread.new(self.ReportCooldownAfterThrottle)

    def PlayResultSound(self, results):
        if results:
            PlaySound('msg_newscan_directional_scan_results_play')
        else:
            PlaySound('msg_newscan_directional_scan_noresults_play')

    def ReportCooldownAfterThrottle(self):
        blue.synchro.SleepWallclock(THROTTLE_TIME)
        self.isScanning = False
        sm.ScatterEvent('OnDirectionalScanCooldown')

    def GetScanDirection(self):
        spaceCamera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not spaceCamera:
            return
        direction = spaceCamera.GetLookAtDirection()
        direction = geo2.Vec3Negate(direction)
        return direction

    def IsScanning(self):
        return self.isScanning

    def OnCmdDirectionalScanUnload(self, *args):
        if not self.hasScanExecutedDuringKeyPress:
            self.DirectionalScan()

    def OnCmdDirectionalScanLoad(self):
        self.hasScanExecutedDuringKeyPress = False

    def GetSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        solarSystemView = SolarSystemViewPanel.GetIfOpen()
        if solarSystemView and not solarSystemView.destroyed:
            return solarSystemView

    def GetDirectionalScanHandler(self):
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            return solarSystemView.GetDirectionalScanHandler()

    def ScanTowardsItem(self, itemID, mapPosition = None):
        if self.IsScanning():
            return
        ball = GetBall(itemID)
        if mapPosition:
            bp = sm.GetService('michelle').GetBallpark()
            egoPos = bp.GetCurrentEgoPos()
            egoPos = SolarSystemPosToMapPos(egoPos)
            direction = geo2.Vec3Normalize(geo2.Vec3Subtract(egoPos, mapPosition))
        elif ball:
            pos = GetBallPosition(ball)
            direction = geo2.Vec3Normalize(pos)
            direction = geo2.Vec3Negate(direction)
        else:
            direction = None
        uthread.new(self.DirectionalScan, geo2.Vec3Negate(direction))
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        directionalScanHandler = self.GetDirectionalScanHandler()
        if direction and directionalScanHandler:
            camera.Track(None)
            camera.StopUpdateThreads()
            directionalScanHandler.SetScanTarget(direction)
        else:
            camera.Track(itemID)
