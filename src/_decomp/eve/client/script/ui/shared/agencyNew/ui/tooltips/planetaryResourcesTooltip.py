#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\tooltips\planetaryResourcesTooltip.py
import evetypes
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.control import tooltipConst
from eve.client.script.ui.shared.agencyNew.ui.typeEntry import TypeEntry
from eve.client.script.ui.shared.planet import planetConst
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from fsdBuiltData.common.planet import iter_resource_type_ids_by_planet_type_id
from localization import GetByLabel
ICON_SIZE = 48
LINE_PADDING = (5, 0, 5, 0)

class PlanetaryResourcesTooltip(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric3ColumnTemplate()
        self.tooltipPanel.SetState(uiconst.UI_NORMAL)
        self.tooltipPanel.margin = tooltipConst.TOOLTIP_MARGIN
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/PlanetaryProduction/planetTypes'))
        line = Line(align=uiconst.TOLEFT)
        self.tooltipPanel.AddCell(line, cellPadding=LINE_PADDING)
        self.tooltipPanel.AddLabelMedium(text=GetByLabel('UI/PI/Common/ResourcesContained'))
        for planetTypeID, resourceTypeIDs in iter_resource_type_ids_by_planet_type_id():
            self.tooltipPanel.AddDivider()
            planetIconLabelContainer = ContainerAutoSize(align=uiconst.CENTERLEFT, height=ICON_SIZE)
            planetIcon = Sprite(parent=Container(parent=planetIconLabelContainer, align=uiconst.TOLEFT, width=48), align=uiconst.CENTER, height=ICON_SIZE, width=ICON_SIZE, hint=evetypes.GetName(planetTypeID))
            sm.GetService('photo').GetIconByType(planetIcon, planetTypeID)
            EveLabelMedium(parent=ContainerAutoSize(parent=planetIconLabelContainer, align=uiconst.TOLEFT, left=5), align=uiconst.CENTER, text=GetByLabel(planetConst.PLANETTYPE_NAMES[planetTypeID]))
            self.tooltipPanel.AddCell(planetIconLabelContainer)
            line = Line(align=uiconst.TOLEFT)
            self.tooltipPanel.AddCell(line, cellPadding=LINE_PADDING)
            resourceGridContainer = GridContainer(align=uiconst.CENTER, lines=2, columns=3, width=520 * fontconst.fontSizeFactor, height=65)
            for resourceTypeID in resourceTypeIDs:
                typeContainer = Container(parent=resourceGridContainer)
                TypeEntry(parent=typeContainer, align=uiconst.CENTERLEFT, typeID=resourceTypeID)

            self.tooltipPanel.AddCell(resourceGridContainer)

        return self.tooltipPanel
