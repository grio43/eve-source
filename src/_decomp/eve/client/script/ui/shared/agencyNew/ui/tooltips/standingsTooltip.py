#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\standingsTooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class StandingsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Agents/StandingsSystem'), wrapWidth=250)
        self.tooltipPanel.AddSpacer(height=5)
        button = Button(name='openFwButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/charactersheet.png', label=GetByLabel('UI/Standings/openCharacterStandings'), func=lambda x: CharacterSheetWindow.OpenStandings())
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        return self.tooltipPanel
