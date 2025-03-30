#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\materialselection\viewcontroller.py
from viewmodel import MaterialSelectionViewModel
from view import MaterialSelectionView
import fsdBuiltData.common.graphicMaterialSets as graphicMaterialSets
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper

class MaterialSelectionViewController(object):

    def __init__(self, model, parentController, parentView):
        self.parentController = parentController
        self.parentView = parentView
        self.model = model
        self.viewModel = MaterialSelectionViewModel(self.model)
        self.view = None

    def ShowUI(self, parentContainer):
        self.view = MaterialSelectionView(self)
        self.view.Setup(parentContainer, self.viewModel)
        return self.view

    def OnMat1ComboChange(self, comboBox, material, value):
        self.viewModel.currentMat[0] = material
        self.parentController.UpdatePreviewShip()

    def OnMat2ComboChange(self, comboBox, material, value):
        self.viewModel.currentMat[1] = material
        self.parentController.UpdatePreviewShip()

    def OnMat3ComboChange(self, comboBox, material, value):
        self.viewModel.currentMat[2] = material
        self.parentController.UpdatePreviewShip()

    def OnMat4ComboChange(self, comboBox, material, value):
        self.viewModel.currentMat[3] = material
        self.parentController.UpdatePreviewShip()

    def OnPatternMat1ComboChange(self, comboBox, material, value):
        self.viewModel.currentPatternMat[0] = material
        self.parentController.UpdatePreviewShip()

    def OnPatternMat2ComboChange(self, comboBox, material, value):
        self.viewModel.currentPatternMat[1] = material
        self.parentController.UpdatePreviewShip()

    def UpdateCombobox(self, materialSet, func, combo, onComboChange):
        item = func(materialSet, 'None')
        idx = ViewHelper.GetComboListIndex(self.model.sofMaterials, item)
        combo.SelectItemByValue(idx)
        onComboChange(combo, item, idx)

    def OnMaterialSetIDChange(self, materialSet):
        changes = [(graphicMaterialSets.GetMaterial1, self.view.matcombo1, self.OnMat1ComboChange),
         (graphicMaterialSets.GetMaterial2, self.view.matcombo2, self.OnMat2ComboChange),
         (graphicMaterialSets.GetMaterial3, self.view.matcombo3, self.OnMat3ComboChange),
         (graphicMaterialSets.GetMaterial4, self.view.matcombo4, self.OnMat4ComboChange),
         (graphicMaterialSets.GetCustomMaterial1, self.view.matcombo5, self.OnPatternMat1ComboChange),
         (graphicMaterialSets.GetCustomMaterial2, self.view.matcombo6, self.OnPatternMat2ComboChange)]
        for change in changes:
            self.UpdateCombobox(materialSet, *change)

    def AppendMaterialToDna(self, dna):
        if any((x != 'None' for x in self.viewModel.currentMat)):
            dna += ':material?' + str(self.viewModel.currentMat[0]) + ';' + str(self.viewModel.currentMat[1]) + ';' + str(self.viewModel.currentMat[2]) + ';' + str(self.viewModel.currentMat[3])
        return dna

    @property
    def currentPatternMat(self):
        return self.viewModel.currentPatternMat
