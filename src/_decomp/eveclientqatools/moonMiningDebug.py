#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\moonMiningDebug.py
import blue
import evetypes
import gametime
import geo2
from carbon.common.lib.const import MSEC
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.button.group import ButtonGroup
from carbonui.control.window import Window
from eve.common.script.sys.idCheckers import IsCelestial
from inventorycommon.const import categoryShip, categoryStructure, typeChunkMedium, typeChunkSmall, typeChunkLarge
from fsdBuiltData.client.effectSequences import GetSequence
from carbonui.primitives.layoutGrid import LayoutGrid
DISTANCE = 100000000
MOON_MINING_SEQUENCE = 'moon_mining'

def CreateInput(label, parent, align, callback, startVal = '', ints = None):
    c = Container(name='sourceContainer', parent=parent, align=uiconst.TOTOP, height=18, width=150, padBottom=20)
    if ints is None:
        return SingleLineEditText(name=label + '_input', align=align, label=label, parent=c, width=100, height=18, setvalue=startVal, OnFocusLost=callback, OnReturn=callback)
    return SingleLineEditInteger(name=label + '_input', align=align, label=label, parent=c, width=100, height=18, setvalue=startVal, OnFocusLost=callback, OnReturn=callback, minValue=ints[0], maxValue=ints[1])


def CreateDropdown(label, parent, align, values, callback):
    c = Container(name='sourceContainer', parent=parent, align=uiconst.TOTOP, height=18, width=150, padBottom=20)
    return Combo(name=label + '_combo', align=align, width=100, height=18, parent=c, label=label, options=values, callback=callback, select=None if len(values) == 0 else values[0][1])


def SetDropdownOptions(combo, listOfNewOptions, newSelected = None):
    combo.LoadOptions([ (str(key), value) for key, value in listOfNewOptions ], newSelected)
    return combo.selectedValue


class MoonMiningDebug(Window):
    default_windowID = 'moonMiningDebugWindow'

    def __init__(self, **kwargs):
        super(MoonMiningDebug, self).__init__(**kwargs)
        self.fxSequencer = sm.GetService('FxSequencer')
        self.michelle = sm.GetService('michelle')
        self.source = None
        self.destination = None
        self.module = 'None'
        self.moon = None
        self.startFrom = None
        self.phase = [ s.name for s in GetSequence(MOON_MINING_SEQUENCE) ][0]
        self.ballIDs = []
        self.sourceInput = None
        self.moduleInput = None
        self.selectedPhaseInput = None
        self.destInput = None
        self.moonInput = None
        self.startFromInput = None
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.SetCaption('Multi effect debug window')
        self.UpdateBallIDs()
        self.Layout()

    def Layout(self):
        self.main_container = ContainerAutoSize(parent=self.content, align=uiconst.TOPLEFT, padTop=16, callback=self._on_main_cont_size_changed, only_use_callback_when_size_changes=True)
        self.layout_grid = LayoutGrid(name='iconContainer', parent=self.main_container, align=uiconst.TOPLEFT, columns=2, cellSpacing=(8, 24))
        self.sourceInput = Combo(align=uiconst.TOPLEFT, parent=self.layout_grid, label='SourceID', options=self.shipBallIDs, callback=self.OnSourceChanged, select=None if len(self.shipBallIDs) == 0 else self.shipBallIDs[0][1])
        self.destInput = Combo(align=uiconst.TOPLEFT, parent=self.layout_grid, label='DestinationID', options=self.ballIDs, callback=self.OnDestChanged, select=None if len(self.ballIDs) == 0 else self.ballIDs[0][1])
        self.moduleInput = Combo(align=uiconst.TOPLEFT, parent=self.layout_grid, label='ModuleID', options=[], callback=self.OnModuleChanged, select=None)
        self.moonInput = Combo(align=uiconst.TOPLEFT, parent=self.layout_grid, label='MoonID', options=self.moonIDs, callback=self.OnMoonChanged, select=None if len(self.moonIDs) == 0 else self.moonIDs[0][1])
        phase_options = [ (v.name, v.name) for v in GetSequence(MOON_MINING_SEQUENCE) ]
        self.selectedPhaseInput = Combo(align=uiconst.TOPLEFT, parent=self.layout_grid, label='Phase', options=phase_options, callback=self.OnPhaseSelected, select=None if len(phase_options) == 0 else phase_options[0][1])
        self.startFromInput = SingleLineEditInteger(align=uiconst.TOPLEFT, label='StartFrom', parent=self.layout_grid, setvalue=0, OnFocusLost=self.OnStartFromChanged, OnReturn=self.OnStartFromChanged, minValue=0, maxValue=1000000)
        self.layout_grid.AddCell(ButtonGroup(name='buttonGroup', buttons=[Button(label='Play', func=self.PlayEffect), Button(label='Stop', func=self.StopEffect), Button(label='Update Lists', func=self.Update)]), colSpan=2)

    def _on_main_cont_size_changed(self):
        width, height = self.GetWindowSizeForContentSize(height=self.main_container.height, width=self.main_container.width)
        self.SetFixedWidth(width=width)
        self.SetFixedHeight(height=height)

    def GetLabel(self, itemid):
        name = ''
        if itemid in cfg.evelocations:
            name = cfg.evelocations.Get(itemid).locationName
        if name == '':
            typeID = self.michelle.GetBall(itemid).GetTypeID()
            name = evetypes.GetName(typeID)
        if name == '':
            name = str(itemid)
        return name

    def GetModuleLabel(self, sourceID, moduleID):
        module = self.michelle.GetBall(sourceID).modules[moduleID]
        if hasattr(module, 'turretTypeID'):
            return evetypes.GetName(module.turretTypeID)
        return str(moduleID)

    def UpdateBallIDs(self):
        ballIDsAndPos = {b:self.michelle.GetBall(b).GetVectorAt(blue.os.GetSimTime()) for b in self.michelle.GetBallpark().GetBallsInRange(session.shipid, DISTANCE) if b > 0}
        ballIDsAndPos = {b:geo2.Vec3Length(geo2.Vector(pos.x, pos.y, pos.z)) for b, pos in ballIDsAndPos.iteritems()}
        ballIDsAndPos[session.shipid] = 0
        self.ballIDs = [ (self.GetLabel(ballID), ballID) for ballID in sorted(ballIDsAndPos.keys(), key=lambda x: ballIDsAndPos[x]) ]
        self.moonIDs = [ (name, ballID) for name, ballID in self.ballIDs if IsCelestial(ballID) ]
        self.shipBallIDs = [ (name, ballID) for name, ballID in self.ballIDs if evetypes.GetCategoryID(self.michelle.GetBall(ballID).GetTypeID()) in (categoryShip, categoryStructure) ]
        self.chunkIDs = [ (name, ballID) for name, ballID in self.ballIDs if self.michelle.GetBall(ballID).GetTypeID() in (typeChunkSmall, typeChunkMedium, typeChunkLarge) ]

    def Update(self, *args):
        self.UpdateBallIDs()
        self.source = SetDropdownOptions(self.sourceInput, self.shipBallIDs, self.source)
        self.destination = SetDropdownOptions(self.destInput, self.ballIDs, self.chunkIDs[0][1])
        self.moon = SetDropdownOptions(self.moonInput, self.moonIDs, self.moon)
        self.SetModule()

    def OnSourceChanged(self, *args):
        self.source = self.sourceInput.selectedValue
        self.SetModule()

    def SetModule(self):
        ball = self.michelle.GetBall(self.source)
        modules = []
        if hasattr(ball, 'modules'):
            modules = [ (self.GetModuleLabel(self.source, mid), mid) for mid in ball.modules.keys() ]
            self.module = modules[0][1]
        modules.insert(0, ('None', 0))
        self.module = SetDropdownOptions(self.moduleInput, modules, self.module)

    def OnModuleChanged(self, *args):
        if self.moduleInput.selectedValue == 0:
            self.module = None
            return
        self.module = self.moduleInput.selectedValue

    def OnDestChanged(self, *args):
        self.destination = self.destInput.selectedValue

    def OnPhaseSelected(self, *args):
        self.phase = self.selectedPhaseInput.selectedValue

    def OnMoonChanged(self, *args):
        self.moon = self.moonInput.selectedValue

    def OnStartFromChanged(self, *args):
        self.startFrom = int(self.startFromInput.GetText()) * MSEC

    def PlayEffect(self, *args):
        if self.startFrom is None:
            self.startFrom = 0
        self.fxSequencer.OnSpecialFX(self.source, self.module, None, self.destination, None, 'effects.MultiEffect', False, 1, True, duration=-1, repeat=None, startTime=blue.os.GetSimTime(), timeFromStart=gametime.GetWallclockTime() - self.startFrom, graphicInfo={'sequence': MOON_MINING_SEQUENCE,
         'phase': self.phase,
         'moonID': self.moon,
         'triggers': ['moduleID',
                      'moonID',
                      'shipID',
                      'targetID']})

    def StopEffect(self, *args):
        self.fxSequencer.OnSpecialFX(self.source, self.module, None, self.destination, None, 'effects.MultiEffect', False, 0, False, duration=-1, repeat=None, startTime=0, timeFromStart=0, graphicInfo={'sequence': MOON_MINING_SEQUENCE,
         'phase': self.phase,
         'moonID': self.moon,
         'triggers': ['moduleID',
                      'moonID',
                      'shipID',
                      'targetID']})


def OpenMoonMiningDebugWindow():
    MoonMiningDebug().ConstructLayout()
