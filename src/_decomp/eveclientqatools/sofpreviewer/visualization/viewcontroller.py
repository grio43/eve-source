#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\visualization\viewcontroller.py
from view import VisualizationView
from viewmodel import RightViewModel
import evegraphics.utils as gfxutils
import fsdBuiltData.common.graphicMaterialSets as graphicMaterialSets
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper

class VisualizationViewController(object):

    def __init__(self, model, parentController, parentView):
        self.parentController = parentController
        self.parentView = parentView
        self.model = model
        self.viewModel = RightViewModel(self.model)
        self.view = None

    def ShowUI(self, parentContainer):
        self.view = VisualizationView(self)
        self.view.Setup(parentContainer, self.viewModel)
        return self.view

    def _FilterMaterialSet(self, filterByRace):
        self.parentController.FilterMaterialSet(filterByRace)

    def GetCurrentMaterialSet(self):
        materialSetID = self.GetCurrentMaterialSetID()
        print 'trying to find materialset for ' + str(materialSetID)
        materialSet = graphicMaterialSets.GetGraphicMaterialSet(materialSetID)
        return materialSet

    def GetCurrentMaterialSetID(self):
        if not hasattr(self.view, 'materialSetIDCombo'):
            return -1
        return self.view.materialSetIDCombo.GetValue()

    def FilterMaterialSet(self, options):
        self.view.materialSetIDCombo.LoadOptions(options)
        if hasattr(self, 'view'):
            ViewHelper.TrySettingComboValue(self.view.materialSetIDCombo, 0)

    def AppendResPathToDna(self, dna):
        if self.viewModel.currentResPathInsert is not None:
            dna += ':respathinsert?' + str(self.viewModel.currentResPathInsert)
        return dna

    def AppendVariantToDna(self, dna):
        if self.viewModel.currentVariant != 'None':
            dna += ':variant?' + str(self.viewModel.currentVariant)
        return dna

    def RefreshStateMachine(self, stateMachineController):
        self.view.RefreshStateMachine(stateMachineController)

    @property
    def currentDirtLevel(self):
        return self.viewModel.currentDirtLevel

    def OnResPathInsertChange(self, *args):
        resPathInsert = self.view.resPathInsertEdit.GetValue()
        print 'new respathinsert: ' + resPathInsert
        if len(resPathInsert) == 0:
            self.viewModel.currentResPathInsert = None
        else:
            self.viewModel.currentResPathInsert = resPathInsert
        self.parentController.UpdatePreviewShip()

    def OnPatternComboChange(self, comboBox, pattern, value):
        self.parentController.OnPatternComboChange(comboBox, pattern, value)

    def OnDirtSliderChange(self, slider):
        self.viewModel.currentDirtLevel = gfxutils.RemapDirtLevel(slider.GetValue())
        self.parentController.UpdatePreviewShip()

    def OnVariantComboChange(self, comboBox, variant, value):
        self.viewModel.currentVariant = variant
        self.parentController.UpdatePreviewShip()

    def OnMaterialSetFiltered(self, checkbox):
        materialSetFiltered = checkbox.GetValue()
        self.parentController.FilterMaterialSet(materialSetFiltered)

    def _OnMaterialSetIDChange(self, *args):
        self.parentController.OnMaterialSetIDChange(args)

    def OnMaterialSetIDChange(self, materialSet):
        self.view.resPathInsertEdit.SetValue(graphicMaterialSets.GetResPathInsert(materialSet, ''))
        self.OnResPathInsertChange()
