#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\moondrillwindow.py
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.window import Window
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from carbonui.control.slider import Slider
from carbonui.control.button import Button
import uthread2
from eve.client.script.ui.control.message import ShowQuickMessage

class MoonDrillWindow(Window):
    __notifyevents__ = ['DoBallsAdded', 'DoBallsRemove']
    default_caption = 'My Window Caption'
    default_windowID = 'myWindowUniqueIDForMoonDrill'
    default_width = 300
    default_height = 300
    default_someValue = 10
    default_otherValue = 20

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self._OnClose = self.Cleanup
        self.sceneManager = sm.GetService('sceneManager')
        self.slash = sm.GetService('slash')
        self.structureBall = None
        self.moonComponent = None
        self.chunkTypeIDs = [45008]
        self.chunkIDs = []
        self.chunkProgress = 0.5
        sm.RegisterNotify(self)
        self.SetupStructureUI()
        self.SetupChunkUI()
        self.SetupCraterUI()
        c = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=25)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='Shoot', func=self._OnFire, width=60)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='Tractor Chunk', func=self._OnTractorChunk, width=60)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='Stasis Chunk', func=self._OnStasisChunk, width=60)

    def Cleanup(self):
        sm.UnregisterNotify(self)

    def SetupStructureUI(self):
        c = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=25)
        EveLabelSmall(name='myLabel', parent=c, left=4, top=8, align=uiconst.TOLEFT, text='Structure ID:')
        self.textInput = SingleLineEditText(name='myTextEdit', parent=c, align=uiconst.TOLEFT, width=200, setvalue='(structure id)')
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='set', func=self._OnSetStructure, width=60)

    def SetupChunkUI(self):
        c = Container(name='toasdfpCont', parent=self.sr.main, align=uiconst.TOTOP, height=25)
        EveLabelSmall(name='myLabesdfl', parent=c, left=4, top=8, align=uiconst.TOLEFT, text='Chunk path:')
        sliderCont = Container(name='mainCont', left=4, width=200, parent=c, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, height=10)
        self.chunkSlider = Slider(name='mySlfsdider', parent=sliderCont, minValue=0.0, maxValue=1.0, value=0.5, callback=self._OnMySliderReleased, showlabel=False)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='spawn', func=self._OnSpawnChunk, width=40)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='unspawn', func=self._OnUnspawnChunk, width=40)

    def SetupCraterUI(self):
        c = Container(name='toasdfpCont', parent=self.sr.main, align=uiconst.TOTOP, height=25)
        EveLabelSmall(name='myLabesdfl', parent=c, left=4, top=8, align=uiconst.TOLEFT, text='Moon Crater:')
        sliderCont = Container(name='mainCont', left=4, width=120, parent=c, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, height=10)
        self.craterSlider = Slider(name='mySlfsdider', parent=sliderCont, minValue=0.0, maxValue=1.0, value=1.0, on_dragging=self._OnPlaceCrater, showlabel=False)
        self.craterSize = SingleLineEditText(name='myIntInput', parent=c, align=uiconst.TOLEFT, width=80, setvalue='70000', minValue=10.0, maxValue=1000000.0, OnChange=self._OnPlaceCrater)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='spawn', func=self._OnPlaceCrater, width=40)
        Button(name='MyButton', align=uiconst.TOLEFT, parent=c, label='unspawn', func=self._OnRemoveCrater, width=40)

    def _OnFire(self, *args):
        if len(self.chunkIDs) > 0:
            self._OnShootChunk(args)
        else:
            self._OnShootMoon(args)

    def _OnShootMoon(self, *args):
        if self.structureBall is None or self.moonComponent is None:
            ShowQuickMessage('Structure with a moon drill not set.')
            return
        sm.ScatterEvent('OnSpecialFX', self.structureBall.id, self.moonComponent.moduleID, self.moonComponent.moduleTypeID, self.moonComponent.targetBall.id, None, 'effects.Laser', True, 1, 1, duration=45000)
        self.moonComponent.PlaceSurfaceImpact()

    def _OnShootChunk(self, *args):
        if not self.chunkIDs:
            return
        sm.ScatterEvent('OnSpecialFX', self.structureBall.id, self.moonComponent.moduleID, self.moonComponent.moduleTypeID, self.chunkIDs[-1], None, 'effects.Laser', True, 1, 1, duration=45000)

    def _OnTractorChunk(self, *args):
        if not self.chunkIDs:
            return
        sm.ScatterEvent('OnSpecialFX', self.structureBall.id, self.moonComponent.moduleID, self.moonComponent.moduleTypeID, self.chunkIDs[-1], None, 'effects.EnergyVampire', True, 1, 1, duration=45000)

    def _OnStasisChunk(self, *args):
        pass

    def _OnSetStructure(self, *args):
        ballID = int(self.textInput.GetValue())
        ball = sm.GetService('michelle').GetBall(ballID)
        if ball is None:
            ShowQuickMessage('Failed to set structure ball')
            return
        self.structureBall = ball
        self.moonComponent = ball._moonDrillComponent
        if self.moonComponent is None:
            ShowQuickMessage('Moon drill component not set')
            return

    def _OnSpawnChunk(self, *args):
        self._UpdateChunk(self.chunkSlider.GetValue())

    def _OnUnspawnChunk(self, *args):
        if self.moonComponent is None:
            ShowQuickMessage('Moon drill component not set')
            return
        self._UpdateChunk(None)

    def _OnPlaceCrater(self, *args):
        if self.moonComponent is None:
            return
        size = float(self.craterSize.GetValue())
        intensity = self.craterSlider.GetValue()
        self.moonComponent.moon.SpawnImpactCrater(self.moonComponent.moonDirection, size)
        self.moonComponent.moon.SetImpactIntensity(intensity)

    def _OnRemoveCrater(self, *args):
        if self.moonComponent is None:
            return
        self.moonComponent.moon.RemoveImpactCrater()

    def _Slash(self, cmd):
        try:
            self.slash.SlashCmd(cmd)
        except:
            pass

    def _UpdateChunk(self, value):
        for chunkID in self.chunkIDs:
            cmd = '/unspawn %d' % chunkID
            self._Slash(cmd)

        self.moonComponent.SetMoonChunk(None)
        self.chunkIDs = []
        if value is None:
            return
        cmd = '/moonmine chunkmove 45008 72 %f 100' % value
        self._Slash(cmd)

    def _OnMySliderReleased(self, slider):
        value = slider.GetValue()
        uthread2.start_tasklet(self._UpdateChunk, value)

    def DoBallsAdded(self, *args, **kw):
        lst = []
        ballsToAdd = args[0]
        for ball, slimItem in ballsToAdd:
            typeID = slimItem.typeID
            if typeID in self.chunkTypeIDs:
                self.chunkIDs.append(ball.id)
                self.moonComponent.SetMoonChunk(ball)

    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        if ball.id not in self.chunkIDs:
            return
        if self.moonComponent is None:
            return
        self.chunkIDs.remove(ball.id)
        self.moonComponent.SetMoonChunk(None)


def OpenWindow():
    Window.CloseIfOpen(windowID=MoonDrillWindow.default_windowID)
    MoonDrillWindow.ToggleOpenClose()
