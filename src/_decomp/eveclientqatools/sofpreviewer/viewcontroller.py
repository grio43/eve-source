#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\viewcontroller.py
import blue
import trinity
import fsdBuiltData.common.graphicMaterialSets as graphicMaterialSets
from eveclientqatools.sofpreviewer.model import SofPreviewerModel
from eveclientqatools.sofpreviewer.view import SofPreviewerView
from eveclientqatools.sofpreviewer.statemachinecontroller import StateMachineController
from materialselection.viewcontroller import MaterialSelectionViewController
from visualization.viewcontroller import VisualizationViewController
from sofselection.viewcontroller import SofSelectionViewController
from highslotselection.viewcontroller import HighSlotSelectionViewController

class SofPreviewerController(object):

    def __init__(self):
        self.view = SofPreviewerView(controller=self)
        self.model = SofPreviewerModel()
        self.updateShip = True
        self.sofSelectionViewController = SofSelectionViewController(self.model, self, self.view)
        self.materialSelectionViewController = MaterialSelectionViewController(self.model, self, self.view)
        self.visualizationViewController = VisualizationViewController(self.model, self, self.view)
        self.highSlotSelectionViewController = HighSlotSelectionViewController(self.model, self, self.view)
        self.stateMachineController = StateMachineController()

    @property
    def shipModel(self):
        return self.view.previewCont.context.GetModel()

    def UpdatePlayerShip(self):
        michelle = sm.GetService('michelle')
        ship = michelle.GetBall(session.shipid)
        if ship is None:
            return
        ship.UnfitHardpoints()
        ship.Release()
        while ship.model is not None:
            blue.synchro.Yield()

        ship.released = False
        ship.GetDNA = self.GetPreviewDna
        ship.LoadModel()
        ship.Assemble()
        if self.visualizationViewController.currentDirtLevel is not None:
            ship.model.dirtLevel = self.visualizationViewController.currentDirtLevel
        self.stateMachineController.ApplyTo(ship.model)
        ship.model.StartControllers()
        self.highSlotSelectionViewController.UpdateDNA(ship.GetDNA())
        self.highSlotSelectionViewController.ShowBanner(True, ship.model)

    def ShowUI(self):
        self.view.ShowUI(self.sofSelectionViewController, self.materialSelectionViewController, self.visualizationViewController, self.highSlotSelectionViewController)
        self.view.previewCont.PreviewSofDna(self.GetPreviewDna())
        self.ReloadStateMachineOptions()
        return self

    def GetPreviewDna(self):
        dna = self.sofSelectionViewController.GetCurrentHull() + ':' + self.sofSelectionViewController.viewModel.currentFaction + ':' + self.sofSelectionViewController.viewModel.currentRace
        dna = self.materialSelectionViewController.AppendMaterialToDna(dna)
        dna = self.visualizationViewController.AppendResPathToDna(dna)
        dna = self.visualizationViewController.AppendVariantToDna(dna)
        dna = self.AppendCurrentPatternToDna(dna)
        if self.view is not None and self.view.dnaLabel is not None:
            self.view.dnaLabel.text = dna
        return dna

    def AppendCurrentPatternToDna(self, dna):
        if self.sofSelectionViewController.currentPattern != 'None':
            dna += ':pattern?' + str(self.sofSelectionViewController.currentPattern) + ';' + str(self.materialSelectionViewController.currentPatternMat[0]) + ';' + str(self.materialSelectionViewController.currentPatternMat[1])
        return dna

    def ReloadStateMachineOptions(self):
        model = self.shipModel
        hull = self.sofSelectionViewController.GetCurrentHull()
        self.stateMachineController.SetupForHullAndModel(hull, model)
        self.visualizationViewController.RefreshStateMachine(self.stateMachineController)

    def UpdatePreviewShip(self):
        dna = self.GetPreviewDna()
        self.highSlotSelectionViewController.UpdateDNA(dna)
        if self.view.previewCont is not None and self.updateShip:
            self.view.previewCont.PreviewSofDna(dna, dirt=self.visualizationViewController.currentDirtLevel)
            self.ReloadStateMachineOptions()
            self.highSlotSelectionViewController.ShowBanner(self.highSlotSelectionViewController.isShowBannerChecked, self.shipModel)

    def GetCurrentMaterialSetID(self):
        if not hasattr(self.view.rightView, 'rightView') or not hasattr(self.view.rightView, 'materialSetIDCombo'):
            return -1
        return self.view.rightView.materialSetIDCombo.GetValue()

    def FilterMaterialSet(self, filterByRace):
        materialSets = graphicMaterialSets.GetGraphicMaterialSets()
        availableMaterialSets = []
        self.sofSelectionViewController.FilterMaterialSet(filterByRace, materialSets, availableMaterialSets)
        availableMaterialSets = sorted(availableMaterialSets, key=lambda x: x[0])
        options = [('None', -1)] + [ ('%s: %s' % keyAndDesc, keyAndDesc[0]) for keyAndDesc in availableMaterialSets ]
        self.visualizationViewController.FilterMaterialSet(options)

    def OnMaterialSetIDChange(self, *args):
        self.updateShip = False
        materialSet = self.visualizationViewController.GetCurrentMaterialSet()
        self.sofSelectionViewController.OnMaterialSetIDChange(materialSet)
        self.materialSelectionViewController.OnMaterialSetIDChange(materialSet)
        self.visualizationViewController.OnMaterialSetIDChange(materialSet)
        self.updateShip = True
        self.UpdatePreviewShip()
        self.sofSelectionViewController.UpdateIcon()

    def OnApplyButton(self, *args):
        self.UpdatePlayerShip()

    def OnCopyDnaButton(self, *args):
        blue.pyos.SetClipboardData(self.GetPreviewDna())

    @property
    def isMaterialSetFilteredByRace(self):
        return self.view.rightView.materialSetFilteredByRace.GetValue()
