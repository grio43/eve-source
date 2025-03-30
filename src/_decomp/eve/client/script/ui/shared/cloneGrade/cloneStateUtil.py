#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\cloneStateUtil.py
import carbonui.const as uiconst
from eve.client.script.ui.shared.cloneGrade.omegaTooltipPanelCell import OmegaTooltipPanelCell
from localization import GetByLabel

def GetTooltipHeader():
    if IsOmega():
        return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateOmega')
    else:
        return GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/CurrentCloneStateAlpha')


def LoadTooltipPanel(tooltipPanel, text = None, origin = None, reason = None):
    tooltipPanel.state = uiconst.UI_NORMAL
    tooltipPanel.LoadGeneric2ColumnTemplate()
    tooltipPanel.margin = (12, 8, 12, 8)
    tooltipPanel.AddLabelLarge(text=GetTooltipHeader(), colSpan=2)
    if not IsOmega():
        if text is None:
            text = GetByLabel('UI/CloneState/RequiresOmegaClone')
        tooltipPanel.AddCell(cellPadding=(0, 4, 0, 0), colSpan=tooltipPanel.columns)
        tooltipPanel.AddRow(rowClass=OmegaTooltipPanelCell, text=text, cellPadding=(0, 4, 0, 4), origin=origin, reason=reason)
    else:
        tooltipPanel.AddLabelMedium(text=text, colSpan=2, cellPadding=(0, 4, 0, 0))


def IsOmega():
    return sm.GetService('cloneGradeSvc').IsOmega()
