#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\navigation.py
import os
import videoplayer
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui.camera.capitalHangarCameraController import CapitalHangarCameraController
from eve.client.script.ui.camera.debugCameraController import DebugCameraController
from eve.client.script.ui.camera.modularHangarCameraController import ModularHangarCameraController
from eve.client.script.ui.camera.modularHangarCapitalCameraController import ModularHangarCapitalCameraController
import blue
from carbon.common.script.util import mathCommon
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.util import uix
import evecamera
import uthread
import carbonui.const as uiconst
from carbon.common.script.util.timerstuff import AutoTimer
import localization
from carbonui.control.layer import LayerCore
from eve.client.script.ui.camera.hangarCameraController import HangarCameraController
import inventorycommon.const as invconst
from eve.common.script.sys import eveCfg
from logmodule import LogException
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
from menu import MenuList

class HangarLayer(LayerCore):
    __notifyevents__ = ['OnActiveCameraChanged']

    def __init__(self, *args, **kwds):
        LayerCore.__init__(self, *args, **kwds)
        self.looking = 0
        self.scene = None
        self.cameraController = None
        self.maxZoom = 750.0
        self.minZoom = 150.0
        self.isMouseMoving = False
        self.mouseDownPick = None
        self.startYaw = None
        self.prevYaw = None
        self.prevDirection = None
        self.numSpins = 0
        self.spinThread = None
        self.prevSpinTime = None
        self.fadeLayer = Container(bgParent=self, bgColor=Color.BLACK, opacity=0.0)

    def Startup(self):
        pass

    def GetMenu(self):
        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        scene = sm.StartService('sceneManager').GetRegisteredScene('hangar')
        if scene:
            projection, view, viewport = uix.GetFullscreenProjectionViewAndViewport()
            pick = scene.PickObject(x, y, projection, view, viewport)
            if pick and pick.name == str(eveCfg.GetActiveShip()):
                return self.GetShipMenu()

    def OnMouseEnter(self, *args):
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def OnDropData(self, dragObj, nodes):
        sm.GetService('loading').StopCycle()
        station = sm.GetService('station')
        if len(nodes) == 1:
            node = nodes[0]
            if getattr(node, '__guid__', None) not in ('xtriui.InvItem', 'listentry.InvItem'):
                return
            if eve.session.shipid == node.item.itemID:
                eve.Message('CantMoveActiveShip', {})
                return
            if node.item.categoryID == const.categoryShip and node.item.singleton:
                if not node.item.ownerID == eve.session.charid:
                    eve.Message('CantDoThatWithSomeoneElsesStuff')
                    return
                station.TryActivateShip(node.item)

    @staticmethod
    def GetShipMenu():
        if not eveCfg.GetActiveShip():
            return MenuList()
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        hangarItems = hangarInv.List(const.flagHangar)
        activeShip = eveCfg.GetActiveShip()
        for each in hangarItems:
            if each.itemID == activeShip:
                return GetMenuService().InvItemMenu(each)

    def OnDblClick(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()

    def OnBillboardClicked(self):
        videoPath = videoplayer.playlistresource.get_currently_played_video('dynamic:/hangarvideos')
        if not videoPath:
            return
        fileName = os.path.basename(videoPath)
        try:
            if fileName.startswith('c_'):
                corpID = self.GetContentID(fileName)
                sm.GetService('info').ShowInfo(invconst.typeCorporation, corpID)
            elif fileName.startswith('s_'):
                offerID = self.GetContentID(fileName)
                sm.GetService('vgsService').ShowOffer(offerID)
            elif fileName.startswith('v_'):
                dirName = os.path.dirname(videoPath)
                videoPath = self.GetContentID(fileName)
                uicore.cmd.OpenVideoPlayerWindow(videoPath=videoPath)
        except Exception as e:
            LogException('Failed to complete billboard click action video: %s' % videoPath)

    def GetContentID(self, fileName):
        return fileName.split('_')[1]

    def OnMouseDown(self, *args):
        self.mouseDownPick = self.GetAreaPick()
        cameraIsFixed = False
        if self.cameraController:
            self.cameraController.OnMouseDown(*args)
            cameraIsFixed = getattr(self.cameraController.GetCamera(), 'fixed', False)
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_DISABLED
        if cameraIsFixed:
            self.cursor = uiconst.UICURSOR_DEFAULT
        else:
            self.cursor = uiconst.UICURSOR_DRAGGABLE
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        uicore.uilib.SetCapture(self)

    def GetAreaPick(self):
        if self.cameraController:
            pick = self.cameraController.GetPick()
            if pick:
                areaID, _ = pick
                return areaID

    def OnMouseUp(self, button, *args):
        sm.ScatterEvent('OnCameraDragEnd')
        self.isMouseMoving = False
        if self.cameraController:
            self.cameraController.OnMouseUp(button, *args)
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        self.cursor = None
        uicore.uilib.UnclipCursor()
        if uicore.uilib.GetCapture() == self:
            uicore.uilib.ReleaseCapture()
        areaID = self.GetAreaPick()
        if button == 0 and areaID == self.mouseDownPick == 'billboard':
            self.OnBillboardClicked()
        self.mouseDownPick = None

    def OnMouseWheel(self, *args):
        if self.cameraController:
            self.cameraController.OnMouseWheel(*args)

    def OnMouseMove(self, *args):
        if uicore.IsDragging():
            return
        if self.cameraController:
            self.cameraController.OnMouseMove(*args)
            if uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
                self._ActivateSpinThread()

    def GetShipSpins(self):
        return self.numSpins

    def OnOpenView(self, **kwargs):
        self._ActivateSpinThread()
        self.spinCounterLabel = eveLabel.EveLabelLargeBold(parent=self, align=uiconst.CENTERBOTTOM, top=14, hint=localization.GetByLabel('UI/Station/Hangar/ShipSpinCounter'), state=uiconst.UI_NORMAL, color=(1, 1, 1, 1))
        self.numSpins = 0
        self.spinCounterLabel.Hide()
        self.spinCounterLabel.startSpinCount = self.numSpins
        self.spinCounterLabel.displayTriggered = False
        self.spinCounterTimer = None
        self.InitCameraController()

    def InitCameraController(self):
        camera = sm.GetService('sceneManager').GetActivePrimaryCamera()
        if camera:
            self.UpdateCameraController(camera.cameraID)

    def OnActiveCameraChanged(self, cameraID):
        self.UpdateCameraController(cameraID)

    def UpdateCameraController(self, cameraID):
        if self.cameraController:
            self.cameraController.Deactivate()
        if cameraID == evecamera.CAM_HANGAR:
            self.cameraController = HangarCameraController()
        elif cameraID == evecamera.CAM_CAPITALHANGAR:
            self.cameraController = CapitalHangarCameraController()
        elif cameraID == evecamera.CAM_MODULARHANGAR:
            self.cameraController = ModularHangarCameraController()
        elif cameraID == evecamera.CAM_DEBUG:
            self.cameraController = DebugCameraController()
        elif cameraID == evecamera.CAM_MODULARHANGAR_CAPITAL:
            self.cameraController = ModularHangarCapitalCameraController()
        else:
            self.cameraController = None
        if self.cameraController:
            self.cameraController.Activate()

    def OnCloseView(self, *args):
        self.KillSpinThread()
        if self.spinCounterLabel:
            self.spinCounterLabel.Close()

    def HideSpinCounter(self):
        if self.spinCounterTimer:
            self.spinCounterTimer = None
        uicore.animations.FadeOut(self.spinCounterLabel, duration=0.5, sleep=True)
        self.spinCounterLabel.displayTriggered = False

    def _CountRotations(self, curYaw):
        spinDirection = mathCommon.GetLesserAngleBetweenYaws(self.prevYaw, curYaw)
        if spinDirection == 0.0:
            return
        if self.prevDirection is None:
            self.prevDirection = spinDirection
        if self.prevDirection * spinDirection < 0.0:
            self.prevYaw = self.startYaw = curYaw
            self.prevDirection = spinDirection
        caughtSpin = False
        if self.prevYaw < curYaw:
            caughtSpin = self.prevYaw < self.startYaw < curYaw and spinDirection > 0.0
        elif self.prevYaw > curYaw:
            caughtSpin = self.prevYaw > self.startYaw > curYaw and spinDirection < 0.0
        if caughtSpin:
            self.numSpins += 1
            self.spinCounterLabel.text = FmtAmt(self.numSpins)
            self.spinCounterTimer = AutoTimer(30000, self.HideSpinCounter)
            if self.numSpins >= self.spinCounterLabel.startSpinCount + 10 and not self.spinCounterLabel.displayTriggered:
                self.spinCounterLabel.Show()
                uicore.animations.BlinkIn(self.spinCounterLabel, duration=0.5, endVal=0.6, loops=2)
                self.spinCounterLabel.displayTriggered = True
            elif self.numSpins % 1000 == 0 and self.spinCounterLabel.displayTriggered:
                uicore.animations.SpColorMorphTo(self.spinCounterLabel, startColor=(1.0, 1.0, 1.0, 0.6), endColor=(0.0, 1.0, 1.0, 1.0), duration=1.0, sleep=True)
                uicore.animations.SpColorMorphTo(self.spinCounterLabel, startColor=(0.0, 1.0, 1.0, 1.0), endColor=(1.0, 1.0, 1.0, 0.6), duration=1.0)
            elif self.numSpins % 100 == 0 and self.spinCounterLabel.displayTriggered:
                uicore.animations.SpColorMorphTo(self.spinCounterLabel, startColor=(1.0, 1.0, 1.0, 0.6), endColor=(1.0, 1.0, 1.0, 1.0), duration=0.75, sleep=True)
                uicore.animations.SpColorMorphTo(self.spinCounterLabel, startColor=(1.0, 1.0, 1.0, 1.0), endColor=(1.0, 1.0, 1.0, 0.6), duration=0.75)
            if self.numSpins % 20 == 0 and self.spinCounterLabel.displayTriggered:
                sm.ScatterEvent('OnSpinThresholdReached', self.numSpins)
            elif self.numSpins == 10 or self.numSpins == 42:
                sm.ScatterEvent('OnSpinThresholdReached', self.numSpins)
        self.prevYaw = curYaw

    def _ActivateSpinThread(self):
        if self.spinThread is None:
            self.spinThread = uthread.new(self._PollCamera)

    def KillSpinThread(self):
        if self.spinThread:
            self.spinThread.kill()
            self.spinThread = None

    def _IsCameraSpinning(self, curYaw):
        now = blue.os.GetSimTime()
        if self.prevSpinTime is None:
            self.prevSpinTime = now
        if self.prevYaw is None:
            self.startYaw = self.prevYaw = curYaw
        notIdleFor1Sec = now < self.prevSpinTime + const.SEC
        cameraMoved = self.prevYaw != curYaw
        if cameraMoved:
            self.prevSpinTime = now
        return notIdleFor1Sec or cameraMoved

    def _PollCamera(self):
        cameraStillSpinning = True
        while cameraStillSpinning:
            blue.pyos.synchro.Yield()
            if self.cameraController is None or self.cameraController.GetCamera() is None:
                break
            camera = self.cameraController.GetCamera()
            curYaw = camera.GetYaw()
            cameraStillSpinning = self._IsCameraSpinning(curYaw)
            if cameraStillSpinning:
                self._CountRotations(curYaw)

        self.spinThread = None

    def FadeIn(self, duration = 0.5, sleep = False):
        sceneMan = sm.GetService('sceneManager')
        sceneMan.FadeIn(duration, sleep)

    def FadeOut(self, duration = 0.5, sleep = False):
        sceneMan = sm.GetService('sceneManager')
        sceneMan.FadeOut(duration, sleep)
