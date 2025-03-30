#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\sunwidget.py
import uthread
import blue
import trinity
import geo2
import evetypes
import math
from carbonui.control.combo import Combo
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from fsdBuiltData.common.graphicIDs import GetGraphicFile
import carbonui.const as uiconst
from carbonui.control.window import Window
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from carbonui.primitives.container import Container
from carbonui.control.checkbox import Checkbox
from carbonui.control.slider import Slider

class SunDirector(object):

    def __init__(self):
        self._updatePosition = False
        self._intensity = None
        self._viewVec = None
        self._closeColorHSV = None
        self._farColorHSV = None
        self.Reset()

    @staticmethod
    def _GetSunBall():
        scm = sm.GetService('sceneManager')
        scene = scm.GetRegisteredScene('default')
        if scene:
            return scene.sunBall

    @staticmethod
    def _GetSunRadius():
        sunball = SunDirector._GetSunBall()
        radius = sunball.radius / 2
        for each in sunball.model.effectChildren:
            if 'half' in each.name.lower():
                radius /= 2
                break

        return radius

    @staticmethod
    def _GetShipPosition():
        ballpark = sm.GetService('michelle').GetBallpark()
        ship = ballpark.GetBallById(ballpark.ego)
        return (ship.x, ship.y, ship.z)

    def GetSunTypeID(self):
        sunball = self._GetSunBall()
        if sunball:
            return sunball.typeID

    def SetColorByTypeID(self, typeID):
        graphicID = evetypes.GetGraphicID(typeID)
        sunGraphicFile = GetGraphicFile(graphicID)
        sunball = self._GetSunBall()
        if sunball:
            try:
                sunball.Reload(sunGraphicFile, typeID)
            except:
                pass

    def SetColor(self, closeColor, farColor):
        self.SetColorHSV(trinity.TriColor(*closeColor).GetHSV(), trinity.TriColor(*farColor).GetHSV())

    def SetColorHSV(self, closeColorHSV, farColorHSV):
        self._closeColorHSV = closeColorHSV
        self._farColorHSV = farColorHSV
        sunball = SunDirector._GetSunBall()
        if sunball:
            sunball.sunColorClose = closeColorHSV
            sunball.sunColorFar = farColorHSV

    def SetVisible(self, visible):
        sunball = self._GetSunBall()
        if sunball:
            sunball.model.display = visible
            sunball.lensflare.display = visible

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        self._intensity = value
        if not self._updatePosition:
            self._UpdatePos()

    def SetFollowCamera(self, value):
        prev = self._updatePosition
        self._updatePosition = value
        if value and not prev:
            uthread.new(self._UpdatePositionThread)

    def Reset(self):
        self.SetFollowCamera(False)
        sunball = self._GetSunBall()
        if not sunball:
            return
        sunball.x = 0
        sunball.y = 0
        sunball.z = 0
        self.SetColorByTypeID(sunball.typeID)
        shipPos = self._GetShipPosition()
        self._viewVec = geo2.Vec3Negate(geo2.Vec3Normalize(shipPos))
        self._intensity = 1 - math.log10(geo2.Vec3Length(shipPos) / self._GetSunRadius()) / 3
        self.SetVisible(True)

    def _UpdatePositionThread(self):
        while self._updatePosition:
            self._viewVec = sm.GetService('sceneManager').GetActiveCamera().GetViewVector()
            self._UpdatePos()
            blue.synchro.Yield()

    def _UpdatePos(self):
        sunball = self._GetSunBall()
        if not sunball:
            return
        position = self._GetShipPosition()
        distance = self._GetSunRadius() * math.pow(10, 3.0 * (1.0 - self._intensity))
        position = geo2.Vec3Add(position, geo2.Vec3ScaleD(self._viewVec, distance))
        sunball.x = position[0]
        sunball.y = position[1]
        sunball.z = position[2]


class SunWidgetWindow(Window):
    default_caption = 'Sun Widget'
    default_windowID = 'SunWidgetWindowID'
    default_width = 260
    default_height = 220
    default_minSize = (260, 220)
    default_maxSize = (260, 220)
    __notifyevents__ = ['OnWindowClosed', 'OnSessionChanged']

    def __init__(self, **kw):
        self.sunDirector = None
        self.intensitySlider = None
        super(SunWidgetWindow, self).__init__(**kw)
        self.MakeUnResizeable()
        sm.RegisterNotify(self)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.sunDirector = SunDirector()
        self.sunOptions = [ (u'{0} [{1}]'.format(evetypes.GetName(sun), sun), sun) for sun in evetypes.GetTypeIDsByGroup(6) ]
        self.sunOptions.insert(0, ('True White', -1))
        self.main_container = None
        self.Layout()

    def LayoutOld(self):
        self._AddHeader('Model')
        self._SetupModelPanel(self.sr.main)
        self._AddHeader('Position')
        self._SetupPositionPanel(self.sr.main)
        self._AddHeader('Radiating Color')
        self._SetupColorPanel(self.sr.main)
        self._AddHeader('Intensity')
        self._SetupIntensityPanel(self.sr.main)
        Button(parent=self.sr.main, label='Reset', align=uiconst.CENTERBOTTOM, func=self.OnResetClicked, width=40, height=18)

    def Layout(self):
        self.SetMinSize([260, 270])
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP)
        self._AddHeader('Model')
        self.displayCheckbox = Checkbox(parent=self.main_container, text=u'Display', align=uiconst.TOTOP, checked=True, callback=self.OnDisplayToggled)
        self._AddHeader('Position')
        self.followCheckbox = Checkbox(parent=self.main_container, text=u'Follow Camera', align=uiconst.TOTOP, checked=False, callback=self.OnFollowToggled)
        self._AddHeader('Radiating Color')
        self.colorCombo = Combo(parent=self.main_container, align=uiconst.TOTOP, options=self.sunOptions, callback=self.OnColorSelected, adjustWidth=True)
        self.colorCombo.SelectItemByValue(self.sunDirector.GetSunTypeID())
        self._AddHeader('Intensity')
        self.intensitySlider = Slider(name='intensitySlider', parent=self.main_container, minValue=0.0, maxValue=1.0, value=self.sunDirector.intensity, increments=[ float(x) / 1000 for x in range(0, 1001) ], on_dragging=self.OnIntensityChanged, align=uiconst.TOTOP)
        Button(parent=self.content, label='Reset', align=uiconst.CENTERBOTTOM, func=self.OnResetClicked)

    def _AddHeader(self, text):
        EveHeaderSmall(parent=self.main_container, text=text, align=uiconst.TOTOP)

    def _SetupModelPanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=20)
        buttonBox = Container(name='buttonBox', parent=cont, align=uiconst.TOTOP, padTop=3, height=20)
        self.displayCheckbox = Checkbox(parent=buttonBox, text=u'Display', align=uiconst.TOLEFT, checked=True, callback=self.OnDisplayToggled, height=18, width=120)

    def _SetupPositionPanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=20)
        buttonBox = Container(name='buttonBox', parent=cont, align=uiconst.TOTOP, padTop=3, height=20)
        self.followCheckbox = Checkbox(parent=buttonBox, text=u'Follow Camera', align=uiconst.TOLEFT, checked=False, callback=self.OnFollowToggled, height=18, width=120)

    def _SetupColorPanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=20)
        self.colorCombo = Combo(parent=cont, align=uiconst.TOTOP, options=self.sunOptions, callback=self.OnColorSelected)
        self.colorCombo.SelectItemByValue(self.sunDirector.GetSunTypeID())

    def _SetupIntensityPanel(self, mainCont):
        self.intensitySlider = Slider(name='intensitySlider', parent=mainCont, minValue=0.0, maxValue=1.0, value=self.sunDirector.intensity, increments=[ float(x) / 1000 for x in range(0, 1001) ], on_dragging=self.OnIntensityChanged, align=uiconst.TOTOP, padLeft=10, padRight=10)

    def OnDisplayToggled(self, *_):
        self.sunDirector.SetVisible(self.displayCheckbox.GetValue())

    def OnFollowToggled(self, *_):
        self.sunDirector.SetFollowCamera(self.followCheckbox.GetValue())

    def OnResetClicked(self, *_):
        self._reset()

    def _reset(self):
        self.displayCheckbox.SetChecked(True, True)
        self.followCheckbox.SetChecked(False, True)
        self.sunDirector.Reset()
        self.intensitySlider.SetValue(self.sunDirector.intensity)
        self.colorCombo.SelectItemByValue(self.sunDirector.GetSunTypeID())

    def OnColorSelected(self, *_):
        val = self.colorCombo.GetValue()
        if val is -1:
            self.sunDirector.SetColor((255, 255, 255, 255), (0, 0, 0, 0))
        else:
            self.sunDirector.SetColorByTypeID(val)
        self.OnDisplayToggled()
        self.OnIntensityChanged()

    def OnIntensityChanged(self, *_):
        if self.intensitySlider is not None:
            self.sunDirector.intensity = self.intensitySlider.GetValue()

    def OnSessionChanged(self, *_):
        self._reset()

    def OnWindowClosed(self, windowID, *_):
        if windowID is self.default_windowID:
            self.sunDirector.Reset()
