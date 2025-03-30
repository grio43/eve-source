#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\ui\states.py
from eve.common.script.sys.idCheckers import IsNewbieShip
import inventorycommon.typeHelpers
from reprocessing.ui.const import STATE_RESTRICTED, STATE_SUSPICIOUS

class States(object):

    def __init__(self, quotes):
        self.quotes = quotes

    def GetState(self, item):
        materials = self.quotes.GetClientMaterial(item.itemID)
        if not materials or self._HasNewbieShipRestriction(item):
            return STATE_RESTRICTED
        valueOfInput = self._GetAveragePrice(item.typeID) * item.stacksize
        valueOfOutput = sum((self._GetAveragePrice(typeID) * qty for typeID, qty in materials.iteritems()))
        if valueOfOutput * 2 < valueOfInput:
            return STATE_SUSPICIOUS

    def _HasNewbieShipRestriction(self, item):
        return IsNewbieShip(item.groupID)

    def _GetAveragePrice(self, typeID):
        price = inventorycommon.typeHelpers.GetAveragePrice(typeID)
        if price is None:
            return 0.0
        return price
