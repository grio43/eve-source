#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\factionWarfare\systemCaptureMechanicsTooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.uicore import uicore
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel
WRAP_WIDTH = 320

class FactionWarfareSystemCaptureMechanicsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/SystemCaptureMechanics'), wrapWidth=WRAP_WIDTH)
        button = Button(name='standingsButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Icons/probe_scan.png', label=GetByLabel('UI/Inflight/Scanner/ProbeScanner'), func=lambda x: uicore.cmd.OpenProbeScanner())
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/AdvantageSystem'), wrapWidth=WRAP_WIDTH)
        objectivesInformationButton = Button(name='objectivesButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/factionalwarfare.png', label=GetByLabel('UI/FactionWarfare/frontlinesDashboard/objectives/objectives'), func=lambda x: uicore.cmd.OpenFWInfoTab())
        self.tooltipPanel.AddCell(objectivesInformationButton, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/Systems/CapturingComplexes'), wrapWidth=WRAP_WIDTH)
        return self.tooltipPanel
