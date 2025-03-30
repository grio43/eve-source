#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\factionWarfare\enlistmentTooltip.py
from carbonui import uiconst
from carbonui.control.button import Button
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.common.script.sys.idCheckers import IsNPCCorporation
from localization import GetByLabel
WRAP_WIDTH = 320

class FactionWarfareEnlistmentTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/SoloEnlistment'), wrapWidth=WRAP_WIDTH)
        button = Button(name='standingsButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/charactersheet.png', label=GetByLabel('UI/Standings/openCharacterStandings'), func=lambda x: CharacterSheetWindow.OpenStandings())
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/CorpAllianceEnlistment'), wrapWidth=WRAP_WIDTH)
        if IsNPCCorporation(session.corpid):
            buttonFunc = lambda x: ShowQuickMessage(GetByLabel('UI/Standings/npcCorpStandingsError'))
        else:
            buttonFunc = lambda x: sm.GetService('corpui').Show(CorpPanel.NPC_STANDINGS)
        button = Button(name='standingsButton', align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/corporation.png', label=GetByLabel('UI/Standings/openCorporationStandings'), func=buttonFunc)
        self.tooltipPanel.AddCell(button, cellPadding=(0, 10, 0, 10))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/FactionWarfare/EnlistmentWarnings'), wrapWidth=WRAP_WIDTH)
        return self.tooltipPanel
