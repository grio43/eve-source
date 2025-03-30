#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\omegaTooltipPanelCell.py
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGridRow
from carbonui.uicore import uicore
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.shared.cloneGrade.button import CloneGradeButtonMedium
from carbonui.uicore import uicore

class OmegaTooltipPanelCell(LayoutGridRow):
    default_name = 'OmegaTooltipPanelCell'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.NOALIGN

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.origin = attributes.origin
        self.reason = attributes.reason
        text = attributes.text
        leftCont = ContainerAutoSize(align=uiconst.CENTERLEFT, padRight=16)
        self.AddCell(leftCont)
        EveLabelMediumBold(parent=leftCont, text=text, color=COLOR_OMEGA_ORANGE, width=256)
        self.icon = CloneGradeButtonMedium(align=uiconst.CENTERRIGHT, left=4, onClick=self._OnClick)
        self.AddCell(self.icon)

    def _OnClick(self, *args):
        return uicore.cmd.OpenCloneUpgradeWindow(self.origin, self.reason)
