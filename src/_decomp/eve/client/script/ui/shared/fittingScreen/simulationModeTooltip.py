#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\simulationModeTooltip.py
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fittingScreen import OFFLINE_COLOR, ONLINE_COLOR, ACTIVE_COLOR, OVERHEATED_COLOR, PASSIVE_COLOR
from localization import GetByLabel
import carbonui.const as uiconst
SLOT_SIZE = 24

def LoadSimulationModuleModeTooltip(tooltipPanel, *args):
    wrapWidth = 250
    tooltipPanel.LoadGeneric2ColumnTemplate()
    tooltipPanel.cellSpacing = (10, 2)
    tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fitting/FittingWindow/ModuleMode'), bold=True, colSpan=tooltipPanel.columns, wrapWidth=wrapWidth)
    tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fitting/FittingWindow/ModuleModeHint'), colSpan=tooltipPanel.columns, wrapWidth=wrapWidth)
    slotInfo = [(OFFLINE_COLOR, 'UI/Fitting/FittingWindow/ModuleModeOfflineShort'),
     (ONLINE_COLOR, 'UI/Fitting/FittingWindow/ModuleModeOnlineShort'),
     (ACTIVE_COLOR, 'UI/Fitting/FittingWindow/ModuleModeActiveShort'),
     (OVERHEATED_COLOR, 'UI/Fitting/FittingWindow/ModuleModeOverheatedShort')]
    for eachColor, labelPath in slotInfo:
        cont = LayoutGrid(parent=tooltipPanel, columns=2)
        _GetSlotSprite(cont, eachColor)
        AddLabel(cont, labelPath, eachColor)

    cont = LayoutGrid(parent=tooltipPanel, columns=2)
    _GetSlotSprite(cont, PASSIVE_COLOR, texturePath='res:/UI/Texture/classes/Fitting/slotPassive_Small.png')
    AddLabel(cont, 'UI/Fitting/FittingWindow/ModuleModePassiveShort', PASSIVE_COLOR)


def LoadSimulationIconTooltip(tooltipPanel, isSimulated = False, *args):
    wrapWidth = 250
    tooltipPanel.LoadGeneric2ColumnTemplate()
    tooltipPanel.cellSpacing = (10, 2)
    if isSimulated:
        headerText = GetByLabel('UI/Fitting/FittingWindow/ExitSimulationMode')
        bodyText = GetByLabel('Tooltips/FittingWindow/ExitSimulationModeDescription')
    else:
        headerText = GetByLabel('UI/Fitting/FittingWindow/SimulateShipFitting')
        bodyText = GetByLabel('Tooltips/FittingWindow/SimulateShipFittingDescription')
    tooltipPanel.AddLabelMedium(text=headerText, bold=True, colSpan=tooltipPanel.columns, wrapWidth=wrapWidth)
    tooltipPanel.AddLabelMedium(text=bodyText, colSpan=tooltipPanel.columns, wrapWidth=wrapWidth, color=(0.6, 0.6, 0.6, 1))


def AddLabel(parent, labelPath, color):
    textColor = color[:3] + (0.75,)
    EveLabelMedium(parent=parent, text=GetByLabel(labelPath), align=uiconst.CENTERLEFT, color=textColor)


def _GetSlotSprite(parent, color, texturePath = None):
    if texturePath is None:
        texturePath = 'res:/UI/Texture/classes/Fitting/slotActive_Small.png'
    slot = Sprite(parent=parent, name='moduleSlotFill', align=uiconst.CENTER, state=uiconst.UI_DISABLED, pos=(0,
     0,
     SLOT_SIZE,
     SLOT_SIZE), texturePath=texturePath)
    slot.SetRGBA(*color)
