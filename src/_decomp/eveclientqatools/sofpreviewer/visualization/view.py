#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\visualization\view.py
import evegraphics.utils as gfxutils
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.decorative.panelUnderlay import PanelUnderlay
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eveclientqatools.sofpreviewer import viewhelper as ViewHelper
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.line import Line
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveLabelSmall

class VisualizationView(object):

    def __init__(self, controller):
        self.controller = controller
        self.dirtSlider = None
        self.materialSetIDCombo = None
        self.resPathInsertEdit = None
        self.variantCombo = None
        self.controllerParent = None
        self.controllers = None
        self.materialSetFilteredByRace = None

    def Setup(self, inputContainer, viewModel):
        _rightContainer = Container(name='_rightContainer', parent=inputContainer)
        rightContainer = Container(name='rightContainer', parent=_rightContainer, align=uiconst.TOLEFT, height=320, width=300)
        self.dirtSlider = ViewHelper.CreateSlider('Dirt', 0.0, 100.0, 50.0, self.controller.OnDirtSliderChange, rightContainer)
        self.UpdateDirtSliderLabel()
        self.materialSetIDCombo, self.materialSetFilteredByRace = ViewHelper.CreateDropdownWithCheckbox('materialSetID', [], 0, self.controller._OnMaterialSetIDChange, 'Filter By Race', self.controller.OnMaterialSetFiltered, rightContainer)
        self.controller._FilterMaterialSet(False)
        self.resPathInsertEdit = ViewHelper.CreateInput('resPathInsert', '', self.controller.OnResPathInsertChange, rightContainer)
        self.variantCombo = ViewHelper.CreateDropdown('Variants:', viewModel.sofVariants, self.controller.OnVariantComboChange, ViewHelper.GetComboListIndex(viewModel.sofVariants, viewModel.currentVariant), rightContainer)
        self.controllerParent = Container(parent=rightContainer, align=uiconst.TOTOP, height=68, padTop=16, padLeft=5, padRight=5)
        self.controllers = None

    def UpdateDirtSliderLabel(self):
        dirtLevel = gfxutils.RemapDirtLevel(self.dirtSlider.GetValue())
        self.dirtSlider.SetLabel('Dirt level: ' + str(round(dirtLevel, 2)))

    def RefreshStateMachine(self, stateMachineController):
        if self.controllers:
            self.controllers.Close()
        self.controllers = ScrollContainer(parent=self.controllerParent, align=uiconst.TOTOP, height=68)
        PanelUnderlay(bgParent=self.controllers)
        for name, value in stateMachineController.GetVariables().items():
            line = Container(parent=self.controllers, align=uiconst.TOTOP, height=32, state=uiconst.UI_NORMAL)
            EveLabelSmall(parent=line, align=uiconst.CENTERLEFT, text=name, left=4)
            varType = stateMachineController.GetVariableType(name)
            if varType == 1:
                SingleLineEditInteger(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=32, setvalue=str(int(value)), OnFocusLost=stateMachineController.OnControllerVariable, OnReturn=stateMachineController.OnControllerVariable, sendSelfAsArgument=True)
            elif varType == 2:
                Checkbox(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=32, setvalue=str(value), floats=(None, None), callback=stateMachineController.OnControllerBoolVariable)
            elif varType == 3:
                Combo(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=32, options=stateMachineController.GetEnumValues(name), callback=stateMachineController.OnControllerEnumVariable, select=value)
            else:
                SingleLineEditFloat(align=uiconst.CENTERRIGHT, name=name, parent=line, width=150, height=32, setvalue=str(value), OnFocusLost=stateMachineController.OnControllerVariable, OnReturn=stateMachineController.OnControllerVariable, sendSelfAsArgument=True)
            Line(parent=line, align=uiconst.TOBOTTOM, opacity=0.05)
