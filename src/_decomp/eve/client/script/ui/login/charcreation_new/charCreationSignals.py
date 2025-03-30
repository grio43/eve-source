#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\charCreationSignals.py
from signals import Signal
onDollSelectionDollClicked = Signal(signalName='onDollSelectionDollClicked')
onDollSelectionDollHovered = Signal(signalName='onDollSelectionDollHovered')
onDollSelectionDollSelected = Signal(signalName='onDollSelectionDollSelected')
onDollSelectionRandomizeStarting = Signal(signalName='onDollSelectionRandomizeStarting')
onDollSelectionDollRandomized = Signal(signalName='onDollSelectionDollRandomized')
onEmpireFactionButtonClicked = Signal(signalName='onEmpireFactionButtonClicked')
onEmpireFactionSelected = Signal(signalName='onEmpireFactionSelected')
onEmpireSchoolButtonClicked = Signal(signalName='onEmpireSchoolButtonClicked')
onEmpireSchoolSelected = Signal(signalName='onEmpireSchoolSelected')
onStepSwitched = Signal(signalName='onStepSwitched')
onNameInputChanged = Signal(signalName='onNameInputChanged')

def OnEmpireFactionSelected(factionID):
    onEmpireSchoolSelected(None)


onEmpireFactionSelected.connect(OnEmpireFactionSelected)
