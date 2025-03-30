#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\impactVisualizationWnd.py
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.button.group import ButtonGroup
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from carbonui.control.window import Window
from eveclientqatools.impactVisualizationController import ImpactVisualizationController

class ImpactVisualizationWnd(Window):
    default_name = 'Impact Visualizer'
    default_windowID = 'ImpactVisualizerWnd%s' % default_name
    default_caption = default_name
    default_minSize = (370, 470)
    default_clipChildren = True

    def CloseByUser(self, *args):
        self.impactVisualizationController.Close()
        self.Close(setClosed=True)

    def ApplyAttributes(self, attributes):
        self.impactVisualizationController = ImpactVisualizationController(shipId=session.shipid)
        Window.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def ConstructLayout(self):
        standardSectionHeaderPadding = (0, 8, 0, 24)
        standardSectionLineBreakPadding = (0, 8, 0, 0)
        self.currentShipIDSectionCont = ContainerAutoSize(name='currentShipIDSectionCont', parent=self.sr.main, align=uiconst.TOTOP)
        Line(parent=self.sr.main, align=uiconst.TOTOP, padding=standardSectionLineBreakPadding)
        self.impactVelocitySectionCont = ContainerAutoSize(name='impactVelocitySectionCont', parent=self.sr.main, align=uiconst.TOTOP, height=200)
        Line(parent=self.sr.main, align=uiconst.TOTOP, padding=standardSectionLineBreakPadding)
        self.impactMassSectionCont = ContainerAutoSize(name='impactMassSectionCont', parent=self.sr.main, align=uiconst.TOTOP, height=100)
        Line(parent=self.sr.main, align=uiconst.TOTOP, padding=standardSectionLineBreakPadding)
        self.damageLocationSectionCont = ContainerAutoSize(name='damageLocationSectionCont', parent=self.sr.main, align=uiconst.TOTOP, height=100)
        EveCaptionSmall(name='currentShipIDLabel', parent=self.currentShipIDSectionCont, text='Current ShipID', align=uiconst.TOTOP, padding=standardSectionHeaderPadding)
        self.shipIDEditField = SingleLineEditText(parent=self.currentShipIDSectionCont, align=uiconst.TOTOP, label='ShipID', setvalue=str(self.impactVisualizationController.shipId), OnChange=self.SetShipID)
        EveCaptionSmall(name='impactVelocityLabel', parent=self.impactVelocitySectionCont, text='Impact Velocity', align=uiconst.TOTOP, padding=standardSectionHeaderPadding)
        SingleLineEditFloat(parent=self.impactVelocitySectionCont, align=uiconst.TOTOP, OnChange=self.impactVisualizationController.OnSetImpactVelocityScalar, label='m/s')
        EveCaptionSmall(name='impactMassLabel', parent=self.impactMassSectionCont, text='Impact Mass', align=uiconst.TOTOP, padding=standardSectionHeaderPadding)
        SingleLineEditFloat(parent=self.impactMassSectionCont, align=uiconst.TOTOP, label='Kg', OnChange=self.impactVisualizationController.OnSetImpactMass)
        EveCaptionSmall(name='damageLocationLabel', parent=self.damageLocationSectionCont, align=uiconst.TOTOP, text='Damage Locator', padding=(0, 8, 0, 0))
        self.damageLocationEditCont = Container(name='damageLocationEditCont', parent=self.damageLocationSectionCont, align=uiconst.TOTOP, height=40)
        self.damageLocatorEditField = SingleLineEditInteger(parent=self.damageLocationEditCont, align=uiconst.TOLEFT, maxValue=self.impactVisualizationController.damageLocatorsMaxValue, maxWidth=10, OnChange=self.impactVisualizationController.SetDamageLocator)
        self.randomDamageLocatorsCheckboxContainer = ContainerAutoSize(parent=self.damageLocationEditCont, align=uiconst.TOLEFT, width=200, height=20)
        self.randomizedDamageLocataorCheckbox = Checkbox(parent=self.randomDamageLocatorsCheckboxContainer, align=uiconst.CENTER, text='Random Damage Locators', padding=(8, 0, 0, 0), callback=self.RandomizeDamageLocatorsCallback)
        self.buttonGroup = ButtonGroup(parent=self.sr.main)
        self.applyImpactButton = self.buttonGroup.AddButton('Apply', self.ApplyPhysicalImpactCallback)

    def SetShipID(self, shipId):
        if self.impactVisualizationController.OnSetShipId(shipId):
            self.damageLocatorEditField.SetMaxValue(self.impactVisualizationController.damageLocatorsMaxValue)
            self.shipIDEditField.SetValue(self.impactVisualizationController.shipId)
            if self.impactVisualizationController.damageLocatorsMaxValue >= self.impactVisualizationController.damageLocatorID:
                self.damageLocatorEditField.SetValue(self.impactVisualizationController.damageLocatorID)
            else:
                self.damageLocatorEditField.SetValue(0)

    def ApplyPhysicalImpactCallback(self, *args):
        self.impactVisualizationController.ApplyPhysicalImpact()
        if self.randomizedDamageLocataorCheckbox.GetValue():
            self.damageLocatorEditField.SetValue(self.impactVisualizationController.damageLocatorID)

    def RandomizeDamageLocatorsCallback(self, checkbox):
        self.impactVisualizationController.randomize = checkbox.GetValue()
        if checkbox.GetValue():
            self.damageLocatorEditField.Disable()
        else:
            self.damageLocatorEditField.Enable()
