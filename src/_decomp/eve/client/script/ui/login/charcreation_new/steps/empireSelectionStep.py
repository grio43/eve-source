#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelectionStep.py
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.control.window import Window
from eve.client.script.ui.login.charcreation_new import soundConst
from eve.client.script.ui.login.charcreation_new.charCreation import BaseCharacterCreationStep
from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import MINIMIZE_ANIMATION_DURATION
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionHeader import EmpireSelectionHeader
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionMapView import EmpireSelectionMapView
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionMenu import EmpireSelectionMenu
from eve.client.script.ui.login.charcreation_new.charCreationSignals import onEmpireFactionSelected
import charactercreator.const as ccConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.sidePanelFactionAndSchool import SidePanelFactionAndSchool
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.sidePanelShip import SidePanelShip

class EmpireSelectionStep(BaseCharacterCreationStep):
    stepID = ccConst.EMPIRESTEP

    def ApplyAttributes(self, attributes):
        super(EmpireSelectionStep, self).ApplyAttributes(attributes)
        self.mainCont = Container(name='mainCont', parent=self, clipChildren=True)
        self.header = EmpireSelectionHeader(parent=self, align=uiconst.CENTERTOP, top=60)
        SidePanelShip(parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.05, 0.2, 332, 391), opacity=0.0)
        SidePanelFactionAndSchool(parent=self, align=uiconst.TOPLEFT_PROP, pos=(0.95, 0.35, 436, 0))
        onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        self.empireSelectMenu = EmpireSelectionMenu(parent=self.mainCont, align=uiconst.TOPLEFT_PROP, state=uiconst.UI_DISABLED, pos=(0.5, 0.75, 0.7, 208))
        animEntry = not self.IsSchoolSelected()
        self.mapView = EmpireSelectionMapView(parent=self, animEntry=animEntry)
        if animEntry:
            animations.FadeTo(self.header, 0.0, 1.0, duration=1.0, timeOffset=empireSelectionConst.ENTRY_ANIMATION_DURATION, callback=self.PlayEmpireSelectRenderedSound)
            animations.FadeTo(self.empireSelectMenu, 0.0, 1.0, duration=1.0, timeOffset=empireSelectionConst.ENTRY_ANIMATION_DURATION + 1.0, callback=self.empireSelectMenu.Enable)
        else:
            self.header.opacity = 1.0
            self.empireSelectMenu.opacity = 1.0
            self.empireSelectMenu.Enable()
        PlaySound(soundConst.BACKGROUND_LOOP)

    @staticmethod
    def PlayEmpireSelectRenderedSound():
        PlaySound(soundConst.RACE_BAR)

    def IsSchoolSelected(self):
        controller = uicore.layer.charactercreation.controller
        if controller:
            return bool(controller.schoolID)
        else:
            return False

    def OnEmpireFactionSelected(self, factionID):
        animations.MorphScalar(self.empireSelectMenu, 'top', self.empireSelectMenu.top, 0.9, duration=MINIMIZE_ANIMATION_DURATION)
        animations.MorphScalar(self.empireSelectMenu, 'height', self.empireSelectMenu.height, 100, duration=MINIMIZE_ANIMATION_DURATION)
        animations.MorphScalar(self.empireSelectMenu, 'width', self.empireSelectMenu.width, 0.5, duration=MINIMIZE_ANIMATION_DURATION)

    def Close(self):
        PlaySound(soundConst.BACKGROUND_LOOP_STOP)
        super(EmpireSelectionStep, self).Close()


class EmpireSelectionTestWindow(Window):
    default_windowID = 'EmpireSelectionTestWindow'
    default_minSize = (1024, 768)

    def ApplyAttributes(self, attributes):
        super(EmpireSelectionTestWindow, self).ApplyAttributes(attributes)
        EmpireSelectionStep(parent=self.sr.main)
