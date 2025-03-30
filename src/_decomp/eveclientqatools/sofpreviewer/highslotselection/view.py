#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\highslotselection\view.py
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper
from carbonui.primitives.container import Container
import carbonui.const as uiconst

class HighSlotSelectionView(object):

    def __init__(self, controller):
        self.checkBoxes = []
        self._controller = controller
        self._checkBoxContainers = []
        self._highSlotContainer = None
        self._checkBoxContainer = None
        self.showBannerSetCheckbox = None

    def Setup(self, inputContainer, viewModel):
        _highSlotContainer = Container(name='_highSlotContainer', parent=inputContainer)
        highslotContainer = Container(name='highSlotContainer', parent=_highSlotContainer, align=uiconst.TOLEFT, height=250, width=250)
        self._highSlotContainer = highslotContainer
        bannerBoxContainer = ViewHelper.CreateContainer(name='Banner checkbox container', parent=self._highSlotContainer)
        self.showBannerSetCheckbox = ViewHelper.CreateCheckbox(name='Show_Banner_set', align=uiconst.TOLEFT, parent=bannerBoxContainer, checkboxLabel='Banner', checkboxCallback=self._controller.OnShowBannerSetToggled, noPadding=True)
        self.turretFilter = ViewHelper.CreateInput('Filter', '', self._controller.OnTurretFilterChanged, highslotContainer)
        self.combo = self._CreateDropDown('High slot item', viewModel, self._controller.OnTurretSelected, viewModel.selectedHighSlotItem)
        self.SetupTurretPicking(viewModel.turretLocatorCount)

    def RefreshDropDown(self, viewModel):
        options = [ (slot.name, i) for i, slot in enumerate(viewModel.availableHighSlots) ]
        self.combo.LoadOptions(options)

    def SetupTurretPicking(self, locatorCount):
        self._ClearTurretSelection()
        self.checkBoxes = []
        if self._checkBoxContainer is None:
            checkBoxLabel = ViewHelper.CreateLabel('Active turret slot', width=100, height=10, parent=self._highSlotContainer)
            self._checkBoxContainer = ViewHelper.CreateScrollContainer(name='Turret_Scroll', width=60, height=150, parent=self._highSlotContainer)
        for i in range(0, locatorCount):
            turretName = '%s' % (i + 1)
            container = ViewHelper.CreateContainer(turretName, self._checkBoxContainer, padTop=0)
            checkBox = ViewHelper.CreateCheckbox(turretName, turretName, self._controller.OnTurretChecked, container, noPadding=True)
            self._checkBoxContainers.append(container)
            self.checkBoxes.append(checkBox)

    def _ClearTurretSelection(self):
        for checkbox in self.checkBoxes:
            checkbox.Close()

        for container in self._checkBoxContainers:
            container.Close()

    def _CreateDropDown(self, name, viewModel, OnChangedFunc, selectedhighSlotItem):
        highSlotNames = [ slot.name for slot in viewModel.availableHighSlots if slot.name is not None ]
        return ViewHelper.CreateDropdown(name, highSlotNames, OnChangedFunc, ViewHelper.GetComboListIndex(highSlotNames, selectedhighSlotItem.name), self._highSlotContainer, align=uiconst.TOLEFT)
