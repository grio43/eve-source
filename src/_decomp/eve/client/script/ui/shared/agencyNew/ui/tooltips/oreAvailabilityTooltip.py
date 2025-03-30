#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\oreAvailabilityTooltip.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import ICON_SIZE_RESOURCE
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.agencyNew.ui.tooltips.tooltipsUtil import ConstructTextualSecurityStatusFillLabel
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from evedungeons.client.oreTypesInDungeons.const import ORE_TYPES_BY_SEC_STATUS
from localization import GetByLabel

def ExtraOreTooltip(tooltipPanel, typeIDs, *args):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    for typeID in typeIDs:
        sprite = Sprite(name='%s_icon' % evetypes.GetName(typeID).lower(), height=ICON_SIZE_RESOURCE, width=ICON_SIZE_RESOURCE, hint=evetypes.GetName(typeID))
        sm.GetService('photo').GetIconByType(sprite, typeID, size=ICON_SIZE_RESOURCE)
        tooltipPanel.AddSpriteLabel(sprite.texturePath, evetypes.GetName(typeID))


class OreAvailabilityTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric5ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/Map/SecurityStatus'), align=uiconst.CENTERLEFT, cellPadding=(10, 0, 10, 0))
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Common/Ore'), align=uiconst.CENTERLEFT, cellPadding=(10, 0, 10, 0))
        for secStatus, ores in ORE_TYPES_BY_SEC_STATUS.iteritems():
            self.tooltipPanel.AddDivider()
            secLabel = ConstructTextualSecurityStatusFillLabel(secStatus)
            self.tooltipPanel.AddCell(secLabel, cellPadding=(10, 0, 0, 0))
            oreTypesContainer = ContainerAutoSize(align=uiconst.TOPLEFT, height=50, alignMode=uiconst.TOLEFT)
            Line(parent=oreTypesContainer, align=uiconst.TOLEFT_NOPUSH)
            for oreTypeID in ores:
                TypeEntry(parent=oreTypesContainer, typeID=oreTypeID, align=uiconst.TOLEFT, left=4)

            self.tooltipPanel.AddCell(oreTypesContainer, cellPadding=(4, 4, 4, 4))

        return self.tooltipPanel
