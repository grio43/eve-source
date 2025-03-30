#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\pirateStrongholdMechanicsTooltip.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from localization import GetByLabel

class PirateStrongholdMechanicsTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/Encounters/PirateStrongholds/PirateStrongholdMechanics'), wrapWidth=tooltipConst.LABEL_WRAP_WIDTH)
        fleetInfoContainer = ContainerAutoSize(align=uiconst.CENTERLEFT)
        Sprite(name='groupContentSprite', parent=fleetInfoContainer, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/agency/iconGroupActivity.png', width=32, height=32)
        EveLabelMedium(parent=fleetInfoContainer, align=uiconst.CENTERLEFT, left=40, text=GetByLabel('UI/Agency/Tooltips/FleetActivity'), color=Color.WHITE, maxWidth=tooltipConst.LABEL_WRAP_WIDTH)
        self.tooltipPanel.AddCell(fleetInfoContainer, cellPadding=(0, 10, 0, 0))
        return self.tooltipPanel
