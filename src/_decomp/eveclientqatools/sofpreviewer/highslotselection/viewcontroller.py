#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\highslotselection\viewcontroller.py
from viewmodel import HighSlotSelectionViewModel
from view import HighSlotSelectionView
from eve.client.script.environment.model.turretSet import TurretSet
import trinity

class HighSlotSelectionViewController(object):

    def __init__(self, model, parentController, parentView):
        self._parentController = parentController
        self._parentView = parentView
        self._model = model
        self._dna = parentController.GetPreviewDna()
        turretLocatorCount = model.GetTurretLocatorCount(dna=self._dna)
        self.viewModel = HighSlotSelectionViewModel(self._model, turretLocatorCount)
        self.view = None

    def ShowUI(self, parentContainer):
        self.view = HighSlotSelectionView(self)
        self.view.Setup(parentContainer, self.viewModel)
        return self.view

    def OnTurretSelected(self, comboBox, highSlotItem, index):
        self.viewModel.selectedHighSlotItem = self.viewModel.availableHighSlots[index]
        self._PlaceSelectedTurretsOnModel()

    def UpdateDNA(self, dna):
        self._dna = dna
        self.viewModel.turretLocatorCount = self._model.GetTurretLocatorCount(self._dna)
        if self.view is not None:
            self.view.SetupTurretPicking(self.viewModel.turretLocatorCount)

    def OnTurretChecked(self, checkbox):
        self._PlaceSelectedTurretsOnModel()

    def _PlaceSelectedTurretsOnModel(self):
        del self._parentController.shipModel.turretSets[:]
        for index, checkbox in enumerate(self.view.checkBoxes):
            checked = checkbox.GetValue()
            if not checked:
                continue
            TurretSet.FitTurret(self._parentController.shipModel, self.viewModel.selectedHighSlotItem.typeID, locatorID=index + 1)

    def OnTurretFilterChanged(self, *args):
        filter = self.view.turretFilter.GetValue()
        self.viewModel.availableHighSlots = HighSlotSelectionViewModel.CreateHighSlotSelection(self._model, filter)
        self.view.RefreshDropDown(self.viewModel)

    def OnShowBannerSetToggled(self, checkbox):
        checked = checkbox.GetValue()
        ship = self._parentController.shipModel
        self.ShowBanner(checked, ship)

    def ShowBanner(self, flag, ship):
        if ship is None:
            return
        for attachment in ship.attachments:
            if not isinstance(attachment, trinity.EveBannerSet):
                continue
            imageMap = attachment.effect.resources.FindByName('ImageMap')
            if imageMap:
                if flag:
                    imageMap.resourcePath = 'res:/UI/Texture/previewBannerVertical.dds'
                else:
                    imageMap.resourcePath = ''

    @property
    def isShowBannerChecked(self):
        if self.view is not None:
            return self.view.showBannerSetCheckbox.GetValue()
        return False
