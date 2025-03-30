#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\scanningTooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupCareerAgents
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class ScanningTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/OreSites/Scanning'), wrapWidth=250)
        button = Button(name='openFwButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Icons/probe_scan.png', label=GetByLabel('UI/Inflight/Scanner/ProbeScanner'), func=uicore.cmd.OpenProbeScanner)
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/OreSites/ScanningSuggestion'), wrapWidth=250)
        buttonContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=25)
        EveLabelMedium(parent=ContainerAutoSize(parent=buttonContainer, align=uiconst.TOLEFT), align=uiconst.CENTER, text=GetByLabel('UI/Agency/jumpTo'))
        from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
        Button(name='signaturesButton', parent=buttonContainer, align=uiconst.TOLEFT, label=GetByLabel('UI/Agency/ContentGroups/ContentGroupCareerAgents'), func=lambda x: AgencyWndNew.OpenAndShowContentGroup(contentGroupCareerAgents), left=5)
        self.tooltipPanel.AddCell(buttonContainer, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/OreSites/ScanningRequirements'), state=uiconst.UI_NORMAL)
        return self.tooltipPanel
