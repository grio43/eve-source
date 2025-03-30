#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingControllerUtil.py
import evetypes
from eve.client.script.ui.shared.fitting.fittingController import StructureFittingController, ShipFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GetTypeIDForController

def GetFittingController(itemID, ghost = False):
    typeID = GetTypeIDForController(itemID)
    if _IsInStructureCategory(typeID):
        return StructureFittingController(itemID, typeID)
    else:
        return ShipFittingController(itemID)


def _IsInStructureCategory(typeID):
    return evetypes.GetCategoryID(typeID) == const.categoryStructure
