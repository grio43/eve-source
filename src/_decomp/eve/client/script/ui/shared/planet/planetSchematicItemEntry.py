#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetSchematicItemEntry.py
import evetypes
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.shared.planet import planetCommon
from eve.common.lib import appConst

class PlanetSchematicItemEntry(Item):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        typeID = self.sr.node.typeID
        if evetypes.GetCategoryID(typeID) == appConst.categoryPlanetaryCommodities:
            schematicID = planetCommon.GetSchematicByOutput(typeID=typeID)
            schematic = planetCommon.GetSchematicDataForID(schematicID)
            planetCommon.LoadSchematicTooltipPanel(tooltipPanel, schematic)
