#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\iceAvailabilityTooltip.py
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveIcon import LogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.agencyNew.ui.tooltips.tooltipsUtil import ConstructNumericSecurityStatusFillLabel
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from evedungeons.client.iceTypesInDungeon.const import UNIQUE_ICE_BY_FACTION, UNIQUE_ICE_BY_SEC_STATUS
from inventorycommon.const import typeFaction, typeDarkGlitter
from localization import GetByLabel

class IceAvailabilityTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric2ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/UniqueIceTypes'), colSpan=2, wrapWidth=300)
        self.tooltipPanel.AddDivider()
        for factionID, iceTypeID in UNIQUE_ICE_BY_FACTION.iteritems():
            factionIconContainer = Container(align=uiconst.CENTER, width=160 * fontconst.fontSizeFactor, height=30)
            LogoIcon(parent=factionIconContainer, align=uiconst.CENTERLEFT, iconAlign=uiconst.TOLEFT, itemID=factionID, size=32, isSmall=True, ignoreSize=True)
            factionName = cfg.eveowners.Get(factionID).ownerName
            EveLabelMedium(parent=factionIconContainer, align=uiconst.CENTERLEFT, left=40, state=uiconst.UI_NORMAL, text='<url=showinfo:%s//%s>%s</url>' % (typeFaction, factionID, factionName))
            Line(parent=factionIconContainer, align=uiconst.TORIGHT_NOPUSH)
            self.tooltipPanel.AddCell(factionIconContainer)
            typeEntry = TypeEntry(typeID=iceTypeID, align=uiconst.CENTERLEFT, opacity=1)
            self.tooltipPanel.AddCell(typeEntry, cellPadding=(10, 0, 0, 0))
            self.tooltipPanel.AddDivider()

        self.tooltipPanel.AddSpacer(height=10, colSpan=2)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/IceTypesInLowSec'), colSpan=2, wrapWidth=300)
        self.tooltipPanel.AddDivider()
        for securityStatus, iceTypeIDs in UNIQUE_ICE_BY_SEC_STATUS.iteritems():
            secContainer = ConstructNumericSecurityStatusFillLabel(securityStatus)
            self.tooltipPanel.AddCell(secContainer, cellPadding=(5, 0, 0, 0))
            iceTypesContainer = ContainerAutoSize(align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=160 * fontconst.fontSizeFactor)
            Line(parent=iceTypesContainer, align=uiconst.TOLEFT_NOPUSH)
            for iceTypeID in iceTypeIDs:
                TypeEntry(parent=iceTypesContainer, align=uiconst.TOTOP, typeID=iceTypeID, opacity=1, left=10)
                if iceTypeID == typeDarkGlitter:
                    EveLabelMedium(parent=iceTypesContainer, align=uiconst.TOPLEFT, text='*', left=5)

            self.tooltipPanel.AddCell(iceTypesContainer)
            self.tooltipPanel.AddDivider()

        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Tooltips/ResourceHarvesting/IceBelts/DarkGlitterNote'), colSpan=2, wrapWidth=300)
        return self.tooltipPanel
