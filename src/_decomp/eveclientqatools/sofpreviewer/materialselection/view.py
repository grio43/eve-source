#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\materialselection\view.py
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper
from carbonui.primitives.container import Container
import carbonui.const as uiconst

class MaterialSelectionView(object):

    def __init__(self, controller):
        self.controller = controller
        self.centerContainer = None
        self.matcombo1 = None
        self.matcombo2 = None
        self.matcombo3 = None
        self.matcombo4 = None
        self.matcombo5 = None
        self.matcombo6 = None

    def CreateDropDown(self, name, viewModel, OnChangedFunc, currentMat):
        return ViewHelper.CreateDropdown(name, viewModel.sofMaterials, OnChangedFunc, ViewHelper.GetComboListIndex(viewModel.sofMaterials, currentMat), self.centerContainer, align=uiconst.CENTER)

    def Setup(self, inputContainer, viewModel):
        _centerContainer = Container(name='_centerContainer', parent=inputContainer)
        centerContainer = Container(name='centerContainer', parent=_centerContainer, align=uiconst.CENTERTOP, height=320, width=250)
        self.centerContainer = centerContainer
        self.matcombo1 = self.CreateDropDown('Material 1', viewModel, self.controller.OnMat1ComboChange, viewModel.currentMat[0])
        self.matcombo2 = self.CreateDropDown('Material 2', viewModel, self.controller.OnMat2ComboChange, viewModel.currentMat[1])
        self.matcombo3 = self.CreateDropDown('Material 3', viewModel, self.controller.OnMat3ComboChange, viewModel.currentMat[2])
        self.matcombo4 = self.CreateDropDown('Material 4', viewModel, self.controller.OnMat4ComboChange, viewModel.currentMat[3])
        self.matcombo5 = self.CreateDropDown('Pattern Material 1', viewModel, self.controller.OnPatternMat1ComboChange, viewModel.currentPatternMat[0])
        self.matcombo6 = self.CreateDropDown('Pattern Material 2', viewModel, self.controller.OnPatternMat2ComboChange, viewModel.currentPatternMat[1])
