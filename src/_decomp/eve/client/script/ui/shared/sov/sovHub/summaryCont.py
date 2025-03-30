#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\summaryCont.py
from carbonui.primitives.container import Container
import carbonui
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.shared.sov.sovHub.powerCapacity import PowerCapacityCont
from eveexceptions import ExceptionEater
from localization import GetByLabel

class SummaryCont(ContainerAutoSize):
    default_minHeight = 36
    default_align = carbonui.Align.TOTOP

    def ApplyAttributes(self, attributes):
        super(SummaryCont, self).ApplyAttributes(attributes)
        self.hubController = attributes.hubController
        self.hubController.on_online_state_changed.connect(self.OnOnlineStateChanged)
        self.hubController.workforceController.on_workforce_changed.connect(self.OnWorkforceChanged)
        self.ConstructuUI()

    def ConstructuUI(self):
        labelGridCont = ContainerAutoSize(parent=self, align=carbonui.Align.TOTOP)
        self.labelGrid = LayoutGrid(parent=labelGridCont, columns=3, cellSpacing=10)
        self.onlineUpgradesNumLabel = carbonui.TextDetail(name='onlineUpgradesNumLabel', parent=self.labelGrid, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/NumUpgradesOnline', numOnline=''), align=carbonui.Align.TOPLEFT)
        carbonui.TextDetail(name='slash', parent=self.labelGrid, text='/', align=carbonui.Align.TOPLEFT)
        self.installedUpgradesNumLabel = carbonui.TextDetail(name='installedUpgradesNumLabel', parent=self.labelGrid, text=GetByLabel('UI/Sovereignty/SovHub/HubWnd/NumUpgradesInstalled', numInstalled=''), align=carbonui.Align.TOPLEFT, color=carbonui.TextColor.SECONDARY)
        self.powerCapParent = Container(name='powerCapParent', parent=self, align=carbonui.Align.TOTOP, height=10)
        labelCont = ContainerAutoSize(parent=self.powerCapParent, align=carbonui.Align.TOLEFT)
        self.powerCapacityCont = PowerCapacityCont(parent=self.powerCapParent, left=6)
        self.powerCapacityLabel = carbonui.TextDetail(name='powerCapacity', parent=labelCont, text='', align=carbonui.Align.CENTERLEFT, color=carbonui.TextColor.SECONDARY, pickState=carbonui.PickState.ON)
        self.powerCapacityLabel.hint = GetByLabel('Tooltips/StructureUI/SovHubMaxPower')

    def LoadSummary(self):
        online, installed = self.hubController.GetNumSimulatedUpgradesOnlineAndInstalled()
        self.onlineUpgradesNumLabel.text = GetByLabel('UI/Sovereignty/SovHub/HubWnd/NumUpgradesOnline', numOnline=online)
        self.installedUpgradesNumLabel.text = GetByLabel('UI/Sovereignty/SovHub/HubWnd/NumUpgradesInstalled', numInstalled=installed)
        installedPower = self.hubController.GetSimulatedPowerOfAllInstalled()
        self.powerCapacityLabel.text = GetByLabel('UI/Sovereignty/SovHub/HubWnd/PowerCapacity', installed=installedPower, maxPower=self.hubController.maxPower)
        self.powerCapParent.height = max(self.powerCapParent.height, self.powerCapacityLabel.textheight)
        self.powerCapacityCont.LoadUpgrades(self.hubController.maxPower, self.hubController.installedUpgradesSimulated)

    def OnOnlineStateChanged(self, typeID):
        self.LoadSummary()

    def OnWorkforceChanged(self):
        self.LoadSummary()

    def Close(self):
        with ExceptionEater('Closing SummaryCont'):
            self.hubController.on_online_state_changed.disconnect(self.OnOnlineStateChanged)
            self.hubController.workforceController.on_workforce_changed.disconnect(self.OnWorkforceChanged)
            self.hubController = None
        super(SummaryCont, self).Close()
