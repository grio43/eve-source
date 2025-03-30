#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\iceReprocessingTooltip.py
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from evedungeons.client.iceTypesInDungeon.const import ISOTOPES_BY_ICE_TYPE
from localization import GetByLabel
import inventorycommon.const as invConst

class IceReprocessingTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/IceReprocessing'), colSpan=2, wrapWidth=320)
        self.tooltipPanel.AddDivider()
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/allIceTypes'), rowSpan=3, align=uiconst.CENTERLEFT)
        typesFromAllIce = [invConst.typeHeavyWater, invConst.typeLiquidOzone, invConst.typeStrontiumClathrates]
        for typeID in typesFromAllIce:
            typeEntryContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=35, alignMode=uiconst.CENTERLEFT)
            Line(parent=typeEntryContainer, align=uiconst.TOLEFT_NOPUSH)
            TypeEntry(parent=typeEntryContainer, typeID=typeID, align=uiconst.CENTERLEFT, opacity=1, left=4)
            self.tooltipPanel.AddCell(typeEntryContainer, cellPadding=(0, 5, 0, 0))

        self.tooltipPanel.AddDivider()
        self.tooltipPanel.AddSpacer(height=5, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/additionalFactionIce'), colSpan=2, wrapWidth=300)
        self.tooltipPanel.AddDivider()
        for iceTypeID, materialTypeID in ISOTOPES_BY_ICE_TYPE.iteritems():
            iceTypeEntry = TypeEntry(typeID=iceTypeID, align=uiconst.CENTERLEFT, opacity=1)
            self.tooltipPanel.AddCell(iceTypeEntry)
            typeEntryContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=35, alignMode=uiconst.CENTERLEFT)
            Line(parent=typeEntryContainer, align=uiconst.TOLEFT_NOPUSH)
            TypeEntry(parent=typeEntryContainer, typeID=materialTypeID, align=uiconst.CENTERLEFT, opacity=1, left=4)
            self.tooltipPanel.AddCell(typeEntryContainer)
            self.tooltipPanel.AddDivider()

        return self.tooltipPanel
