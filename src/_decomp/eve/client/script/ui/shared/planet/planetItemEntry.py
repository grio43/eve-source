#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetItemEntry.py
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.shared.planet import planetCommon

class PlanetItemEntry(Item):

    def LoadTooltipPanel(self, tooltipPanel, *args):
        typeID = self.sr.node.typeID
        amount = self.sr.node.amount
        planetCommon.LoadProductTooltipPanel(tooltipPanel, typeID, amount)
