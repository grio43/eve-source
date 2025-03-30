#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\cameraTool.py
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
import carbonui.const as uiconst
import evecamera
import uthread
import blue
import evegraphics.settings as gfxsettings
BUTTONHINT = '1.\tPerform "Look at" to attach to an item you want to examine (important to achieve proper pan sensitivity).\nYou can orbit while attached.\n\n2.\tDetach camera using right-drag. Move around using pan, rotate and zoom to cursor.\n\n3.\tTake a close look by using ALT+zoom\n'

class CameraTool(Window):
    default_caption = ('Camera Tool',)
    default_windowID = 'CameraToolID'
    default_width = 360
    default_height = 420
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.oldCamID = None
        self.currentController = None
        self.mainCont = Container(parent=self.sr.main, padding=5)
        Button(parent=self.mainCont, align=uiconst.TOTOP, label='Toggle Debug Camera', func=self.ToggleDebugCam, hint=BUTTONHINT)
        self.atLabel = Label(parent=self.mainCont, align=uiconst.TOTOP)
        self.spaceMouseContainer = Container(parent=self.mainCont, align=uiconst.TOTOP, height=100, padding=5)
        speedContainer = Container(parent=self.spaceMouseContainer, align=uiconst.TOTOP, height=40, padding=5)
        Label(parent=speedContainer, text='SpaceMouse Speed:', align=uiconst.TOTOP)
        self.spaceMouseSpeed = Slider(name='mySlider', parent=speedContainer, align=uiconst.TOTOP, minValue=0.01, maxValue=1.0, value=gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT), height=20, on_dragging=self.OnSpaceMouseSpeedSliderChanged)
        accelerationContainer = Container(parent=self.spaceMouseContainer, align=uiconst.TOTOP, height=40, padding=5)
        Label(parent=accelerationContainer, text='SpaceMouse Acceleration:', align=uiconst.TOTOP)
        self.spaceMouseAcceleration = Slider(name='mySlider', parent=accelerationContainer, align=uiconst.TOTOP, minValue=0.01, maxValue=1.0, value=gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT), height=20, on_dragging=self.OnSpaceMouseAccelerationSliderChanged)
        self.spaceMouseContainer.Hide()
        stateCont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=20, padTop=5)
        self.orbitLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ORBIT', padRight=2)
        self.zoomLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ZOOM', padRight=2)
        self.fovZoomLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='FOVZOOM', padRight=2)
        self.panLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='PAN', padRight=2)
        self.rotateLabel = StateCont(parent=stateCont, align=uiconst.TOLEFT, text='ROTATE', padRight=2)
        self.SetCurrentSpaceCameraController()
        uthread.new(self.Update)
        sm.RegisterForNotifyEvent(self, 'OnSpaceMouseAccelerationCoefficientChanged')
        sm.RegisterForNotifyEvent(self, 'OnSpaceMouseSpeedCoefficientChanged')
        sm.RegisterForNotifyEvent(self, 'OnActiveCameraChanged')

    def Close(self, setClosed = False, *args, **kwds):
        sm.UnregisterForNotifyEvent(self, 'OnSpaceMouseAccelerationCoefficientChanged')
        sm.UnregisterForNotifyEvent(self, 'OnSpaceMouseSpeedCoefficientChanged')
        sm.UnregisterForNotifyEvent(self, 'OnActiveCameraChanged')
        if self.oldCamID is not None:
            self.ToggleDebugCam(())
        super(CameraTool, self).Close(setClosed, *args, **kwds)

    def OnActiveCameraChanged(self, _):
        self.SetCurrentSpaceCameraController()

    def OnSpaceMouseAccelerationSliderChanged(self, slider):
        newval = slider.GetValue()
        gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT, newval, pending=False)
        sm.ScatterEvent('OnSpaceMouseAccelerationCoefficientChanged')

    def OnSpaceMouseSpeedSliderChanged(self, slider):
        newval = slider.GetValue()
        gfxsettings.Set(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT, newval, pending=False)
        sm.ScatterEvent('OnSpaceMouseSpeedCoefficientChanged')

    def Update(self):
        while not self.destroyed:
            try:
                self.SetCurrentSpaceCameraController()
                cam = sm.GetService('sceneManager').GetActiveCamera()
                text = 'CameraID: <b>%s</b>' % cam.cameraID
                text += '\n\n_atPosition: %2.5f, %2.5f, %2.5f' % cam._atPosition
                atOffset = cam._atOffset or (0, 0, 0)
                text += '\n_atOffset: %2.5f, %2.5f, %2.5f' % atOffset
                text += '\n_eyePosition: %2.5f, %2.5f, %2.5f' % cam._eyePosition
                eyeOffset = cam._eyeOffset or (0, 0, 0)
                text += '\n_eyeOffset: %2.5f, %2.5f, %2.5f' % eyeOffset
                eyeAndAtOffset = cam._eyeAndAtOffset or (0, 0, 0)
                text += '\n_eyeAndAtOffset: %2.5f, %2.5f, %2.5f' % eyeAndAtOffset
                text += '\nzoomProportion: %2.2f' % cam.GetZoomProportion()
                text += '\nminZoom: %2.2f' % cam.minZoom
                text += '\nmaxZoom: %2.2f' % cam.maxZoom
                text += '\nfov: %2.2f' % cam.fov
                text += '\nznear: %2.1f' % cam._nearClip
                text += '\nzfar: %2.1f' % cam._farClip
                if self.currentController is not None:
                    text += '\nSPACE MOUSE INFO:'
                    text += self.currentController.GetInfo()
                self.atLabel.text = text
                self.zoomLabel.SetActive(cam.zoomTarget is not None)
                self.fovZoomLabel.SetActive(cam.fovTarget is not None)
                self.panLabel.SetActive(cam.panTarget is not None)
                self.orbitLabel.SetActive(cam.orbitTarget is not None)
                self.rotateLabel.SetActive(cam.rotateUpdateThread is not None)
            except:
                raise
            finally:
                blue.synchro.Yield()

    def OnSpaceMouseSpeedCoefficientChanged(self):
        self.MaybeChange(self.spaceMouseSpeed, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_SPEED_COEFFICIENT))

    def OnSpaceMouseAccelerationCoefficientChanged(self):
        self.MaybeChange(self.spaceMouseAcceleration, gfxsettings.Get(gfxsettings.UI_CAMERA_SPACEMOUSE_ACCELERATION_COEFFICIENT))

    def MaybeChange(self, slider, value):
        if slider.GetValue() != value:
            slider.SetValue(value)

    def ToggleDebugCam(self, *args):
        sceneMan = sm.GetService('sceneManager')
        activeCamID = sceneMan.GetActiveCamera().cameraID
        if activeCamID == evecamera.CAM_DEBUG:
            sceneMan.SetPrimaryCamera(self.oldCamID)
            self.oldCamID = None
            sceneMan.UnregisterCamera(evecamera.CAM_DEBUG)
        else:
            self.oldCamID = activeCamID
            sceneMan.SetPrimaryCamera(evecamera.CAM_DEBUG)
        self.SetCurrentSpaceCameraController()

    def SetCurrentSpaceCameraController(self):
        hasChanged = False
        layer = sm.GetService('viewState').GetPrimaryView().layer
        if layer is not None and hasattr(layer, 'cameraController'):
            if self.currentController != getattr(layer.cameraController, 'spaceMouseController', None):
                self.currentController = getattr(layer.cameraController, 'spaceMouseController', None)
                hasChanged = True
        if hasChanged:
            self.ToggleSlider()

    def ToggleSlider(self):
        if self.currentController is not None:
            self.spaceMouseContainer.Show()
        else:
            self.spaceMouseContainer.Hide()


COLOR_ON = Color.GREEN
COLOR_OFF = Color.GRAY1

class StateCont(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.bgFill = Fill(bgParent=self, color=COLOR_OFF)
        self.label = Label(parent=self, align=uiconst.CENTERLEFT, text=attributes.text, padLeft=5, padRight=5)

    def SetActive(self, isActive):
        if isActive:
            self.bgFill.SetRGBA(*COLOR_ON)
        else:
            self.bgFill.SetRGBA(*COLOR_OFF)
