#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\mineralAvailabilityTooltip.py
from carbonui import uiconst
from carbonui.primitives.line import Line
from carbonui.util.color import Color
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from evedungeons.client.oreTypesInDungeons.const import ORE_TYPES_BY_VALUE
from typematerials.data import get_type_materials_by_id
from localization import GetByLabel

class MineralAvailabilityTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.columns = 7
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Common/Ore'), color=Color.WHITE)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Moonmining/Output'), colSpan=4, color=Color.WHITE)
        for oreTypeID in ORE_TYPES_BY_VALUE:
            oreType = TypeEntry(typeID=oreTypeID, align=uiconst.CENTERLEFT, height=32)
            self.tooltipPanel.AddDivider()
            self.tooltipPanel.AddCell(oreType, cellPadding=(10, 0, 0, 0))
            self.tooltipPanel.AddCell(Line(align=uiconst.TOLEFT), cellPadding=(5, 0, 5, 0))
            mineralOutputs = get_type_materials_by_id(oreTypeID)
            mineralOutputLength = len(mineralOutputs)
            for i, mineralOutput in enumerate(mineralOutputs):
                mineralTypeID = mineralOutput.materialTypeID
                mineralEntry = TypeEntry(typeID=mineralTypeID, align=uiconst.CENTERLEFT, height=32)
                self.tooltipPanel.AddCell(mineralEntry, cellPadding=(5, 0, 5, 0))
                if i == mineralOutputLength - 1:
                    self.tooltipPanel.FillRow()

        return self.tooltipPanel
