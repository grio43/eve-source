#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\performancebenchmark.py
import math
import os
import sys
import time
import blue
import geo2
import carbonui.const as uiconst
import carbonui.fontconst
import carbonui.graphs.axis as axis
import carbonui.graphs.axislabels as axislabels
import eveprefs
import evetypes
import trinity
import uthread
import utillib
import eve.client.script.environment.model.turretSet as turretSet
import logging
from carbon.common.lib.serverInfo import GetServerInfo
from carbonui import Density
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.slider import Slider
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.parklife.sceneManager import GetSceneManager
from eve.client.script.remote.michelle import GetMichelle
from eve.client.script.ui.camera.hangarCamera import HangarCamera
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveEdit import Edit
from eve.client.script.ui.control.eveLabel import EveHeaderSmall
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.util import uix
from statscapture import camerapresets
from statscapture.performancemeasurements import Measurement
from .performancebenchmarkdata import *
PERFMEASUREMENTS_URL = 'http://trilambda-ws:8088/'
PERFMEASUREMENTS_UPLOAD_URL = PERFMEASUREMENTS_URL + 'measurement/'
BENCHMARK_MAX_DURATION_IN_MS = 600000.0
BENCHMARK_DEFAULT_DURATION_IN_MS = 10000.0
MIN_PAN_DISTANCE = 0.001
MAX_PAN_DISTANCE = 1000000.0
_tags = ''
log = logging.getLogger(__name__)

def ClampPan(pan):
    return min(MAX_PAN_DISTANCE, max(pan, MIN_PAN_DISTANCE))


class SceneDirector(object):
    __notifyevents__ = ['DoBallsAdded']

    def __init__(self):
        self.slash = sm.GetService('slash').SlashCmd
        self.initialSceneState = set([])
        self.damage = DAMAGE_NONE
        self.boosters = BOOSTERS_HIGH
        sm.RegisterNotify(self)

    def SetCamera(self, yaw, pitch, pan):
        cam = GetSceneManager().GetActiveCamera()
        cam.SetYaw(math.radians(yaw))
        cam.SetPitch(math.radians(pitch))
        pan = ClampPan(pan)
        newPos = geo2.Vec3Add(geo2.Vec3Scale(cam.GetLookAtDirection(), pan), cam.GetAtPosition())
        if isinstance(cam, HangarCamera):
            cam.SetEyePosition(newPos)
        else:
            cam.TransitTo(atPosition=cam.GetAtPosition(), eyePosition=newPos)

    def GoToAndReturnStartPosition(self, stayHere):
        bp = GetMichelle().GetBallpark()
        if stayHere:
            startPos = bp.GetCurrentEgoPos()
        else:
            startPos = (2500000000000.0, 0.0, 0.0)
            self.slash('/tr me pos=%s,%s,%s' % (startPos[0], startPos[1], startPos[2]))
        return startPos

    def SpawnTestcase(self, testID, startPos):
        self._SpawnShips(startPos, TEST_CASES[testID])

    def SpawnSingleObjectCube(self, typeID, startPos, numOfRows = 10):
        testCase = TestCase([typeID], numOfRows, evetypes.GetRadius(typeID) * 4)
        self._SpawnShips(startPos, testCase)

    def _SpawnShips(self, startPos, testCase):
        scene = GetSceneManager().GetRegisteredScene('default')
        if not self.initialSceneState:
            self.initialSceneState = set(scene.objects)
        yCount = 0
        xPos = startPos[0]
        for cntr in xrange(testCase.number_of_rows ** 2):
            typeId = testCase.ship_list[cntr % len(testCase.ship_list)]
            if yCount >= testCase.number_of_rows:
                xPos += testCase.distance_between_ships
                yCount = 0
            for zCount in xrange(testCase.number_of_rows):
                self.slash('/spawn %s pos=%s,%s,%s' % (typeId,
                 xPos,
                 yCount * testCase.distance_between_ships + startPos[1],
                 zCount * testCase.distance_between_ships + startPos[2]))

            yCount += 1

    def DoBallsAdded(self, balls):
        uthread.new(self._DoBallsAdded, balls)

    def _DoBallsAdded(self, balls):
        for ball, _ in balls:
            model = ball.GetModel()
            self._SetDamage(model, self.damage)
            self._SetBoosters(model, self.boosters)

    def GetShips(self):
        scene = GetSceneManager().GetRegisteredScene('default')
        additions = set(scene.objects) - self.initialSceneState
        for each in additions:
            if each.__bluetype__ == 'trinity.EveShip2' and each.name.startswith('10000') and each.translationCurve.id != session.shipid:
                yield each

    def ClearAll(self, *_):
        for each in self.GetShips():
            self.slash('/unspawn %s' % each.name)

    def SetDamage(self, damage):
        self.damage = damage
        for each in self.GetShips():
            self._SetDamage(each, damage)

    def SetBoosters(self, boosters):
        self.boosters = boosters
        for each in self.GetShips():
            self._SetBoosters(each, boosters)

    def SetTurrets(self, turretTypeID):
        if turretTypeID == -1:
            return
        for each in self.GetShips():
            self._SetTurrets(each, turretTypeID)

    @staticmethod
    def _SetDamage(model, damage):
        if model is not None and hasattr(model, 'SetImpactDamageState'):
            shield, armor, hull = damage
            model.SetImpactDamageState(shield, armor, hull, True)

    @staticmethod
    def _SetBoosters(model, boosters):
        if model is not None and hasattr(model, 'boosters'):
            model.boosters.alwaysOn = boosters > 0.0
            model.boosters.alwaysOnIntensity = boosters

    @staticmethod
    def _SetTurrets(model, turretTypeID):
        newTurretSet = turretSet.TurretSet.FitTurret(model, turretTypeID, 1)
        if newTurretSet is None:
            log.error('Invalid turret type ID for ship')
            return


class PerformanceBenchmarkWindow(Window):
    default_caption = 'Performance Tools'
    default_windowID = 'PerformanceToolsWindowID'
    default_width = 220
    default_height = 200
    default_wontUseThis = 10
    default_minSize = (600, 600)

    def __init__(self, **kw):
        self.lastPitch = 0.0
        self.lastYaw = 0.0
        self.pan = 0.0
        self.camLock = False
        self.benchmarkDuration = BENCHMARK_DEFAULT_DURATION_IN_MS
        self.last_test_case_name = ''
        self.benchmarkRunning = False
        self.sceneDirector = None
        self.benchmarkButton = None
        self.testOptions = [('classic cube of death', CUBE_CLASSIC),
         ('capital wrecks of death', CUBE_CAPITAL_WRECKS),
         ('AmarrCube', CUBE_AMARR),
         ('CaldariCube', CUBE_CALDARI),
         ('GallenteCube', CUBE_GALLENTE),
         ('MinmatarCube', CUBE_MINMATAR),
         ('UltraLODCube', CUBE_LOD),
         ('Single Object', CUBE_ADD_MORE_HERE)]
        self.damageOptions = [('Damage None', DAMAGE_NONE), ('Damage Armor', DAMAGE_ARMOR), ('Damage Hull', DAMAGE_HULL)]
        self.boosterOptions = [('Boosters High', BOOSTERS_HIGH), ('Boosters Low', BOOSTERS_LOW), ('Boosters Off', BOOSTERS_OFF)]
        self.testCaseDescription = {CUBE_CLASSIC: 'Spawns a cube with a lot of different ships.',
         CUBE_CAPITAL_WRECKS: 'Spawns a cube with a lot of wrecks.',
         CUBE_AMARR: 'Spawns a cube of Amarr ships.',
         CUBE_CALDARI: 'Spawns a cube of Caldari ships.',
         CUBE_GALLENTE: 'Spawns a cube of Gallente ships.',
         CUBE_MINMATAR: 'Spawns a cube of Minmatar ships.',
         CUBE_LOD: 'Spawns a cube of ships around the camera.',
         CUBE_ADD_MORE_HERE: 'Spawn objects with specified type ID.'}
        self.camPresetOptions = [('None', CAMERA_PRESETS[CAMERA_PRESET_NONE]),
         ('Deathcube Far', CAMERA_PRESETS[CAMERA_PRESET_FAR]),
         ('Deathcube Medium', CAMERA_PRESETS[CAMERA_PRESET_MEDIUM]),
         ('Deathcube Near', CAMERA_PRESETS[CAMERA_PRESET_NEAR]),
         ('Deathcube UltraLOD', CAMERA_PRESETS[CAMERA_PRESET_ULTRA_LOD])]
        super(PerformanceBenchmarkWindow, self).__init__(**kw)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.lastPitch = 0.0
        self.lastYaw = 0.0
        self.pan = 0.0
        self.camLock = False
        self.benchmarkDuration = BENCHMARK_DEFAULT_DURATION_IN_MS
        self.last_test_case_name = ''
        self.benchmarkRunning = False
        self.sceneDirector = SceneDirector()
        self.ConstructTurrentContainer()
        self.ConstructCameraContainer()
        self.ConstructDurationContainer()
        self.ConstructTestCaseContainer()
        self.benchmarkButton = Button(name='myButton', parent=self.content, align=uiconst.CENTERBOTTOM, label='Start Benchmark', func=self.ToggleBenchmark)

    def ConstructCameraContainer(self):
        EveHeaderSmall(parent=self.content, text='Camera', align=uiconst.TOTOP, padTop=8)
        self.ConstructPresetContainer()
        self.ConstructPitchContainer()
        self.ConstructYawContainer()
        self.ConstructPanContainer()
        buttonBox = Container(name='buttonBox', parent=self.content, align=uiconst.TOTOP, padTop=3, height=32)
        Button(parent=buttonBox, label='Capture camera coords', align=uiconst.TORIGHT, func=self.OnStoreCurrentCameraValues, hint='Captures the current camera coordinates and saves them in the input fields')
        uthread.new(self._GetCurrentCameraValues)

    def ConstructTestCaseContainer(self):
        EveHeaderSmall(parent=self.content, text='Test Case Name', align=uiconst.TOTOP, padTop=8)
        test_case_cont = Container(name='testCaseCont', parent=self.content, align=uiconst.TOTOP, height=32)
        self.test_case_field = SingleLineEditText(name='testCaseNameField', parent=test_case_cont, align=uiconst.TOTOP, setvalue=str(self.last_test_case_name))
        self.test_case_field.OnChange = self.OnTestNameChange

    def ConstructDurationContainer(self):
        EveHeaderSmall(parent=self.content, text='Duration', align=uiconst.TOTOP, padTop=8)
        maxSeconds = int(BENCHMARK_MAX_DURATION_IN_MS / 1000)
        defaultSeconds = int(BENCHMARK_DEFAULT_DURATION_IN_MS / 1000)
        self.durationSlider = Slider(name='mySlider', parent=self.content, minValue=1, maxValue=maxSeconds, value=defaultSeconds, increments=[ i + 1 for i in xrange(maxSeconds) ], on_dragging=self._OnTimeChanged, align=uiconst.TOTOP, getHintFunc=self.GetSliderHint)
        self.progress = Gauge(name='progress', parent=self.content, color=Color.WHITE, align=uiconst.TOTOP, padTop=20, padBottom=30)
        self._OnTimeChanged(self.durationSlider)

    def GetSliderHint(self, slider):
        return '%i ms' % (slider.GetValue() * 1000)

    def ConstructPanContainer(self):
        panCont = Container(name='panCont', parent=self.content, align=uiconst.TOTOP, height=32, padTop=3)
        label_container = Container(parent=panCont, align=uiconst.TOLEFT, width=40)
        Label(name='panLabel', parent=label_container, align=uiconst.CENTERLEFT, padTop=3, text='Pan')
        self.panField = SingleLineEditInteger(name='panField', parent=panCont, align=uiconst.TOTOP, minValue=MIN_PAN_DISTANCE, maxValue=MAX_PAN_DISTANCE, setvalue=0)
        self.panField.OnChange = self.OnCamChange

    def ConstructYawContainer(self):
        yawCont = Container(name='yawCont', parent=self.content, align=uiconst.TOTOP, height=32, padBottom=3)
        label_container = Container(parent=yawCont, align=uiconst.TOLEFT, width=40)
        Label(name='yawLabel', parent=label_container, align=uiconst.CENTERLEFT, padTop=3, text='Yaw')
        self.yawField = SingleLineEditFloat(name='yawField', parent=yawCont, align=uiconst.TOTOP, minValue=-180.0, maxValue=180.0, setvalue=str(self.lastYaw))
        self.yawField.OnChange = self.OnCamChange

    def ConstructPitchContainer(self):
        pitchCont = Container(name='pitchCont', parent=self.content, align=uiconst.TOTOP, height=32, padBottom=3)
        label_container = Container(parent=pitchCont, align=uiconst.TOLEFT, width=40)
        Label(name='pitchLabel', parent=label_container, align=uiconst.CENTERLEFT, text='Pitch')
        self.pitchField = SingleLineEditFloat(name='pitchField', parent=pitchCont, align=uiconst.TOTOP, maxValue=180.0, setvalue=str(self.lastPitch))
        self.pitchField.OnChange = self.OnCamChange

    def ConstructPresetContainer(self):
        presetCont = Container(name='presetCont', parent=self.content, align=uiconst.TOTOP, height=32, padBottom=3, padTop=3)
        label_container = Container(parent=presetCont, align=uiconst.TOLEFT, width=40)
        Label(name='presetCombo', parent=label_container, align=uiconst.CENTERLEFT, text='Preset')
        self.camPresetDelete = Button(parent=presetCont, align=uiconst.TORIGHT, label='x', padLeft=3, state=uiconst.UI_DISABLED, func=self._OnDeletePreset)
        Button(parent=presetCont, align=uiconst.TORIGHT, label='+', padLeft=2, func=self._OnSavePreset)
        self.cboCamPresets = Combo(parent=presetCont, align=uiconst.TOALL, options=self.camPresetOptions + camerapresets.GetAllPresets(), callback=self.OnCamPreset)

    def ConstructTurrentContainer(self):
        EveHeaderSmall(parent=self.content, text='Test Cases', align=uiconst.TOTOP)
        self.testCombo = Combo(parent=self.content, align=uiconst.TOTOP, options=self.testOptions, callback=self.TestComboChanged)
        self.testCombo.SetHint(self.testCaseDescription[1])
        buttonBox = Container(parent=self.content, align=uiconst.TOTOP, height=24)
        Button(parent=buttonBox, label='Add turrets', align=uiconst.TORIGHT, func=self.OnTurretButtonPressed, density=Density.COMPACT)
        self.turretTypeIDInput = SingleLineEditText(name='turretTypeID', parent=buttonBox, align=uiconst.TORIGHT, integermode=(0, sys.maxint), setvalue=str('-1'))
        Label(parent=buttonBox, text='Turret TypeID:', padTop=4, padRight=4, align=uiconst.TORIGHT)
        self.turretTypeIDInput.Disable()
        self.typeID = SingleLineEditText(name='typeID', parent=buttonBox, align=uiconst.TORIGHT, integermode=(0, sys.maxint))
        self.typeID.Disable()
        Label(parent=buttonBox, text='Single object TypeID', padTop=4, padRight=4, align=uiconst.TORIGHT)
        buttonBox = Container(name='buttonBox', parent=self.content, align=uiconst.TOTOP, padTop=3, height=24)
        self.stayHereCheckbox = Checkbox(parent=buttonBox, text=u'Stay where you are', align=uiconst.TOLEFT, checked=False)
        Button(parent=buttonBox, label='Spawn', align=uiconst.TORIGHT, func=self.SpawnTestcase, padLeft=3)
        Button(parent=buttonBox, label='Clear', align=uiconst.TORIGHT, func=self.sceneDirector.ClearAll)
        self.damageCombo = Combo(parent=buttonBox, align=uiconst.TORIGHT, options=self.damageOptions, callback=self.DamageComboChanged)
        self.boosterCombo = Combo(parent=buttonBox, align=uiconst.TORIGHT, options=self.boosterOptions, callback=self.BoosterComboChanged)

    def _AddHeader(self, text):
        EveHeaderSmall(parent=self.sr.main, text=text, align=uiconst.TOTOP, padding=(8, 6, 0, 3))

    def _SetupTestCasePanel(self, mainCont):
        cont = Container(name='cont', parent=mainCont, align=uiconst.TOTOP, padLeft=4, padRight=4, height=60)
        self.testCombo = Combo(parent=cont, align=uiconst.TOTOP, options=self.testOptions, callback=self.TestComboChanged)
        self.testCombo.SetHint(self.testCaseDescription[1])
        buttonBox = Container(parent=cont, align=uiconst.TOTOP, padTop=3, padBottom=3, height=20)
        Button(parent=buttonBox, label='Add turrets', align=uiconst.TORIGHT, func=self.OnTurretButtonPressed, width=40, height=18)
        self.turretTypeIDInput = SingleLineEditText(name='turretTypeID', parent=buttonBox, align=uiconst.TORIGHT, integermode=(0, sys.maxint), setvalue=str('-1'), padRight=4)
        Label(parent=buttonBox, text='Turret TypeID:', padTop=4, padRight=4, align=uiconst.TORIGHT)
        self.turretTypeIDInput.Disable()
        self.typeID = SingleLineEditText(name='typeID', parent=buttonBox, align=uiconst.TORIGHT, integermode=(0, sys.maxint), padRight=4)
        self.typeID.Disable()
        Label(parent=buttonBox, text='Single object TypeID', padTop=4, padRight=4, align=uiconst.TORIGHT)
        buttonBox = Container(name='buttonBox', parent=cont, align=uiconst.TOTOP, padTop=3, height=20)
        self.stayHereCheckbox = Checkbox(parent=buttonBox, text=u'Stay where you are', align=uiconst.TOLEFT, checked=False, height=18, width=140)
        Button(parent=buttonBox, label='Spawn', align=uiconst.TORIGHT, func=self.SpawnTestcase, width=40, height=18)
        Button(parent=buttonBox, label='Clear', align=uiconst.TORIGHT, func=self.sceneDirector.ClearAll, width=40, height=18)
        self.damageCombo = Combo(parent=buttonBox, align=uiconst.TORIGHT, options=self.damageOptions, callback=self.DamageComboChanged)
        self.boosterCombo = Combo(parent=buttonBox, align=uiconst.TORIGHT, options=self.boosterOptions, callback=self.BoosterComboChanged)

    def _SetupCameraPanel(self, mainCont):
        presetCont = Container(name='presetCont', parent=mainCont, align=uiconst.TOTOP, height=18, padBottom=4, padLeft=4, padRight=4)
        Label(name='presetCombo', parent=presetCont, align=uiconst.TOLEFT, width=40, text='Preset')
        self.camPresetDelete = Button(parent=presetCont, align=uiconst.TORIGHT, width=16, height=18, label='x', padLeft=2, state=uiconst.UI_DISABLED, func=self._OnDeletePreset)
        Button(parent=presetCont, align=uiconst.TORIGHT, width=16, height=18, label='+', padLeft=2, func=self._OnSavePreset)
        self.cboCamPresets = Combo(parent=presetCont, align=uiconst.TOTOP, options=self.camPresetOptions + camerapresets.GetAllPresets(), callback=self.OnCamPreset)
        pitchCont = Container(name='pitchCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='pitchLabel', parent=pitchCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pitch')
        self.pitchField = SingleLineEditFloat(name='pitchField', parent=pitchCont, align=uiconst.TOTOP, maxValue=180.0, setvalue=str(self.lastPitch))
        self.pitchField.OnChange = self.OnCamChange
        yawCont = Container(name='yawCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='yawLabel', parent=yawCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Yaw')
        self.yawField = SingleLineEditFloat(name='yawField', parent=yawCont, align=uiconst.TOTOP, minValue=-180.0, maxValue=180.0, setvalue=str(self.lastYaw))
        self.yawField.OnChange = self.OnCamChange
        panCont = Container(name='panCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4)
        Label(name='panLabel', parent=panCont, align=uiconst.TOLEFT, width=40, padTop=3, text='Pan')
        self.panField = SingleLineEditInteger(name='panField', parent=panCont, align=uiconst.TOTOP, minValue=MIN_PAN_DISTANCE, maxValue=MAX_PAN_DISTANCE, setvalue=0)
        self.panField.OnChange = self.OnCamChange
        buttonBox = Container(name='buttonBox', parent=mainCont, align=uiconst.TOTOP, padTop=3, height=20, padRight=4)
        Button(parent=buttonBox, label='Capture camera coords', align=uiconst.TORIGHT, func=self.OnStoreCurrentCameraValues, width=40, height=18, hint='Captures the current camera coordinates and saves them in the input fields')
        uthread.new(self._GetCurrentCameraValues)

    def _SetupDurationPanel(self, parent):
        maxSeconds = int(BENCHMARK_MAX_DURATION_IN_MS / 1000)
        defaultSeconds = int(BENCHMARK_DEFAULT_DURATION_IN_MS / 1000)
        self.durationSlider = Slider(name='mySlider', parent=parent, minValue=1, maxValue=maxSeconds, value=defaultSeconds, increments=[ i + 1 for i in xrange(maxSeconds) ], on_dragging=self._OnTimeChanged, align=uiconst.TOTOP, padLeft=10, padRight=10)
        self.progress = Gauge(name='progress', parent=parent, color=Color.WHITE, align=uiconst.TOTOP, padTop=20, padLeft=10, padRight=10, padBottom=30)
        self._OnTimeChanged(self.durationSlider)

    def _SetupTestCaseNamePanel(self, mainCont):
        test_case_cont = Container(name='testCaseCont', parent=mainCont, align=uiconst.TOTOP, height=20, padLeft=4, padRight=4, padTop=4)
        self.test_case_field = SingleLineEditText(name='testCaseNameField', parent=test_case_cont, align=uiconst.TOTOP, setvalue=str(self.last_test_case_name))
        self.test_case_field.OnChange = self.OnTestNameChange

    def OnTestNameChange(self, *_):
        self.last_test_case_name = self.test_case_field.GetValue()

    def _OnTimeChanged(self, slider):
        self.benchmarkDuration = slider.GetValue() * 1000

    def TestComboChanged(self, *_):
        self.testCombo.SetHint(self.testCaseDescription[self.testCombo.GetValue()])
        if self.testCombo.GetValue() == CUBE_ADD_MORE_HERE:
            self.typeID.Enable()
            self.turretTypeIDInput.Enable()
        else:
            self.typeID.Disable()

    def DamageComboChanged(self, *_):
        self.sceneDirector.SetDamage(self.damageCombo.GetValue())

    def BoosterComboChanged(self, *_):
        self.sceneDirector.SetBoosters(self.boosterCombo.GetValue())

    def OnTurretButtonPressed(self, *_):
        self.sceneDirector.SetTurrets(int(self.turretTypeIDInput.GetValue()))

    def OnCamChange(self, *_):
        if self.camLock:
            return
        self.lastPitch = float(self.pitchField.GetValue())
        self.lastYaw = float(self.yawField.GetValue())
        self.pan = int(self.panField.GetValue())
        self.sceneDirector.SetCamera(self.lastYaw, self.lastPitch, self.pan)

    def OnCamPreset(self, *_):
        idx = self.cboCamPresets.GetIndex()
        self.camPresetDelete.SetState(uiconst.UI_DISABLED if idx < len(self.camPresetOptions) else uiconst.UI_NORMAL)
        presId = self.cboCamPresets.GetValue()
        if presId == 0:
            return
        pitch, yaw, pan = presId
        self.camLock = True
        self.pitchField.SetValue(pitch)
        self.yawField.SetValue(yaw)
        self.panField.SetValue(pan)
        self.camLock = False
        self.OnCamChange()

    def _OnDeletePreset(self, *_):
        ret, block = sm.StartService('gameui').MessageBox('Are you sure you want to delete this camera preset?', 'Delete Camera Preset', uiconst.OKCANCEL, uiconst.QUESTION)
        if ret == uiconst.ID_OK:
            name = self.cboCamPresets.GetKey()
            camerapresets.DeletePreset(name)
            for i, x in enumerate(self.cboCamPresets.entries):
                if x[0] == name:
                    del self.cboCamPresets.entries[i]
                    break

            self.cboCamPresets.SelectItemByIndex(0)

    def _OnSavePreset(self, *_):
        layout = [{'type': 'btline'},
         {'type': 'labeltext',
          'label': 'Preset Name',
          'text': '',
          'frame': 1,
          'labelwidth': 180},
         {'type': 'edit',
          'setvalue': self.cboCamPresets.GetKey(),
          'key': 'name',
          'label': '_hide',
          'required': 1,
          'frame': 1,
          'setfocus': 1,
          'selectall': 1},
         {'type': 'bbline'}]
        OKCANCEL = 1
        popup = uix.HybridWnd(layout, caption='Save Camera Preset', windowID='saveCameraPreset', modal=1, buttons=OKCANCEL, location=None, minW=240, minH=80)
        if not popup:
            return
        name = popup['name']
        if name in [ x[0] for x in self.camPresetOptions ]:
            return
        preset = (self.lastPitch, self.lastYaw, self.pan)
        camerapresets.SavePreset(preset, name)
        for i, x in enumerate(self.cboCamPresets.entries):
            if x[0] == name:
                self.cboCamPresets.entries[i] = (x[0], preset)
                self.cboCamPresets.SelectItemByLabel(name)
                return

        self.cboCamPresets.entries.append((name, preset))
        self.cboCamPresets.SelectItemByLabel(name)

    def ToggleBenchmark(self, *_):
        if not self.benchmarkRunning and ResultDialog.IsOpen():
            ret, block = sm.StartService('gameui').MessageBox('Are you sure you want to close the old result window, including the captured data?', 'Close old result window?', uiconst.OKCANCEL, uiconst.QUESTION)
            if ret == uiconst.ID_OK:
                ResultDialog.GetIfOpen().Close()
            else:
                return
        self.progress.SetValue(0)

        def _thread():
            measurement = Measurement()
            measurement.Begin()
            startTime = blue.os.GetWallclockTime()
            try:
                while self.benchmarkRunning:
                    blue.synchro.Yield()
                    t1 = blue.os.GetWallclockTime()
                    timeFromStartInMs = float(blue.os.TimeDiffInUs(startTime, t1)) / 1000.0
                    if blue.os.TimeDiffInMs(startTime, t1) > self.benchmarkDuration:
                        self.benchmarkRunning = False
                        break
                    self.progress.SetValue(timeFromStartInMs / self.benchmarkDuration, animate=False)

            finally:
                measurement.TakeScreenshot()
                measurement.End()

            test_case_name = self.last_test_case_name
            test_system_info = self._GetMachineAndServerInfo()
            ResultDialog.Open(measurement=measurement, test_case_name=test_case_name, test_system_info=test_system_info, duration=self.benchmarkDuration, camera={'pitch': self.lastPitch,
             'yaw': self.lastYaw,
             'pan': self.pan})
            self.benchmarkButton.SetLabel('Start Benchmark')

        if self.benchmarkRunning:
            self.benchmarkRunning = False
        else:
            self.benchmarkRunning = True
            self.benchmarkButton.SetLabel('Stop Benchmark')
            uthread.new(_thread)

    def _GetMachineAndServerInfo(self):
        adapters = trinity.adapters
        ident = adapters.GetAdapterInfo(adapters.DEFAULT_ADAPTER)
        serverInfo = GetServerInfo()
        trinity_platform = trinity.platform
        gpu_vendor = ident.description.split()[0]
        computerName = os.environ.get('COMPUTERNAME')
        result_obj = {'triplatform': trinity_platform,
         'driverVendor': gpu_vendor,
         'server': serverInfo['name'],
         'computerName': computerName}
        return result_obj

    def OnStoreCurrentCameraValues(self, *_):
        self._GetCurrentCameraValues()

    def _GetCurrentCameraValues(self):
        self.camLock = True
        cam = GetSceneManager().GetActiveCamera()
        yaw = math.degrees(cam.yaw)
        if yaw < -180:
            yaw = 360 + yaw
        self.lastPitch = math.degrees(cam.pitch)
        self.lastYaw = yaw
        self.pan = ClampPan(int(cam.GetZoomDistance()))
        self.pitchField.SetValue(self.lastPitch)
        self.yawField.SetValue(self.lastYaw)
        self.panField.SetValue(self.pan)
        self.camLock = False
        self.OnCamChange()

    def SpawnTestcase(self, *_):
        testID = self.testCombo.GetValue()
        stayHere = self.stayHereCheckbox.GetValue()
        startPos = self.sceneDirector.GoToAndReturnStartPosition(stayHere)
        if testID == CUBE_ADD_MORE_HERE:
            self.sceneDirector.SpawnSingleObjectCube(self.typeID.GetValue(), startPos)
        else:
            self.sceneDirector.SpawnTestcase(testID, startPos)


class ResultDialog(Window):
    default_width = 500
    default_height = 540
    default_windowID = 'ResultDialog'
    default_minSize = (500, 540)

    def __init__(self, **kw):
        self.resultText = None
        self.exportPath = None
        self.test_case_name = None
        self.test_system_info = None
        self.duration = 0.0
        self.camera = None
        self.measurement = None
        self.nameEdit = None
        self.tags = None
        super(ResultDialog, self).__init__(**kw)

    def ApplyAttributes(self, *args):
        global _tags
        super(ResultDialog, self).ApplyAttributes(*args)
        self.measurement = args[0].get('measurement', {})
        self.resultText = args[0].get('resultText', '')
        self.test_case_name = args[0].get('test_case_name', '')
        self.test_system_info = args[0].get('test_system_info', {})
        self.duration = args[0].get('duration', 1.0)
        self.camera = args[0].get('camera', None)
        controlsContainer = Container(name='controlsContainer', parent=self.sr.main, align=uiconst.TOBOTTOM, padding=10, height=132)
        LABEL_WIDTH = 200
        nameContainer = Container(parent=controlsContainer, align=uiconst.TOTOP, height=28, padBottom=4)
        Label(parent=nameContainer, align=uiconst.TOLEFT, text='Test case name:', width=LABEL_WIDTH)
        self.nameEdit = SingleLineEditText(parent=nameContainer, align=uiconst.TOBOTTOM, height=24, setvalue=self.test_case_name)
        tagsContainer = Container(parent=controlsContainer, align=uiconst.TOTOP, height=28, padBottom=4)
        Label(parent=tagsContainer, align=uiconst.TOLEFT, text='Tags (coma separated):', width=LABEL_WIDTH)
        self.tags = SingleLineEditText(parent=tagsContainer, align=uiconst.TOBOTTOM, height=24, setvalue=_tags)
        self.tags.OnChange = self._OnTagsChange
        postContainer = Container(parent=controlsContainer, align=uiconst.TOTOP, height=36, padBottom=4)
        Label(parent=postContainer, align=uiconst.TOLEFT, text='Post to <a href="%s">%s</a>' % (PERFMEASUREMENTS_URL, PERFMEASUREMENTS_URL), width=LABEL_WIDTH, state=uiconst.UI_ACTIVE)
        Button(label='Post Results', align=uiconst.TOBOTTOM, parent=postContainer, func=self.PostResults)
        exportContainer = Container(parent=controlsContainer, align=uiconst.TOTOP, height=24, padBottom=4)
        Label(parent=exportContainer, align=uiconst.TOLEFT, text='Export folder:', width=LABEL_WIDTH)
        self.exportPath = SingleLineEditText(parent=exportContainer, align=uiconst.TOALL, setvalue='%s/PerformanceMetrics/' % os.path.splitdrive(__file__)[0])
        Button(align=uiconst.TORIGHT, parent=exportContainer, label='Export', func=self.Export)
        info = self.measurement.GetInfo()
        result = 'Min: %0.1fms Max: %0.1fms\n' % (info.frameTime.min, info.frameTime.max)
        result += 'Median:  %0.1fms %0.1ffps\n' % (info.frameTime.median, 1000.0 / info.frameTime.median)
        result += 'Average: %0.1fms %0.1ffps\n' % (info.frameTime.avg, 1000.0 / info.frameTime.avg)
        result += 'Start System Memory: %0.1fmb\n' % (info.systemMemory.start,)
        result += 'End System Memory: %0.1fmb\n' % (info.systemMemory.end,)
        result += 'Start GPU Memory (est): %0.1fmb\n' % (info.gpuMemory.start,)
        result += 'End GPU Memory (est): %0.1fmb\n' % (info.gpuMemory.end,)
        result += 'DP: Min: %s  Max: %s   Avg:  %s' % (info.drawPrimitives.min, info.drawPrimitives.max, info.drawPrimitives.avg)
        Edit(name='resultText', parent=self.sr.main, align=uiconst.TOBOTTOM, setvalue=result.replace('\n', '<br>'), height=self.height / 3, padding=10, readonly=True)
        graphContainer = Container(name='graphContainer', parent=self.sr.main, align=uiconst.TOALL, padding=10)
        self.CreateGraph(self.measurement.GetFrameTimes(), graphContainer)

    def _OnTagsChange(self, *_):
        global _tags
        _tags = self.tags.GetValue()

    def CreateGraph(self, data, main):
        times = sorted(data.keys())
        values = [ data[x] for x in times ]
        Label(parent=main, align=uiconst.TOTOP, text='Frame Time', fontsize=carbonui.fontconst.EVE_LARGE_FONTSIZE)
        verticalAxis = axis.AutoTicksAxis(axis.GetRangeFromSequences(values), tickCount=10, margins=(0.1, 0.1))
        horizontalAxis = axis.AutoTicksCategoryAxis(times, tickCount=5)
        axislabels.AxisLabels(parent=main, align=uiconst.TOLEFT, width=50, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0)
        graphArea = GraphArea(name='graph', parent=main, align=uiconst.TOALL)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, color=(1, 1, 1, 0.2), minFactor=1.0, maxFactor=0.0)
        LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=values, color=(1.0, 0.5, 0.5, 0.8), lineWidth=1)

    def Export(self, *_):
        exportFolderPath = '%s' % self.exportPath.GetValue()
        test_case_name = self.nameEdit.GetValue() or time.strftime('%Y%m%d%H%M%S', self.measurement.GetEndTime())
        exportName = '%s_%s_%s_%s_%s' % (self.test_system_info['computerName'],
         self.test_system_info['triplatform'],
         self.test_system_info['driverVendor'],
         self.test_system_info['server'],
         test_case_name)
        exportFileName = exportName + '.csv'
        self.measurement.ExportCsv(os.path.join(exportFolderPath, exportFileName))
        app = {'name': 'EVE Client',
         'version': '%s %s.%s' % (eveprefs.boot.codename, eveprefs.boot.version, eveprefs.boot.build),
         'server': utillib.GetServerName()}
        benchmark = {'duration': self.duration}
        if self.camera:
            benchmark['camera'] = self.camera
        self.measurement.Export(test_case_name, os.path.join(exportFolderPath, exportName + '.json'), app, benchmark)

    def PostResults(self, *_):
        test_case_name = self.nameEdit.GetValue() or time.strftime('%Y%m%d%H%M%S', self.measurement.GetEndTime())
        app = {'name': 'EVE Client',
         'version': '%s %s.%s' % (eveprefs.boot.codename, eveprefs.boot.version, eveprefs.boot.build),
         'server': utillib.GetServerName()}
        benchmark = {'duration': self.duration}
        if self.camera:
            benchmark['camera'] = self.camera
        try:
            self.measurement.Upload(test_case_name, app, benchmark, self.tags.GetValue())
        except:
            uicore.Message('CustomNotify', {'notify': 'Failed to post results'})
            raise

        uicore.Message('CustomNotify', {'notify': 'Successfully posted results to the server'})
