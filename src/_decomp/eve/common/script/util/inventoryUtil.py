#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\inventoryUtil.py
import evetypes
import log
from typematerials.data import get_type_materials_by_id

def GetComputedBasePrice(typeID, quantity = None):
    price = 0
    portionSize = evetypes.GetPortionSize(typeID)
    if portionSize == 0:
        log.LogError('GetComputedBasePrice - portionSize of item type:%s is 0' % typeID)
        portionSize = 1
    if quantity is None:
        quantity = portionSize
    materials = get_type_materials_by_id(typeID)
    if len(materials) > 0:
        for material in materials:
            portionSize = evetypes.GetPortionSize(material.materialTypeID)
            if portionSize == 0:
                log.LogError('GetComputedBasePrice - portionSize of material type:%s is 0' % material.materialTypeID)
                continue
            materialQuantityRequiredPerPortion = material.quantity
            materialCostPerMaterialUnitRequired = int(evetypes.GetBasePrice(material.materialTypeID) / portionSize)
            materialCostPerPortion = materialQuantityRequiredPerPortion * materialCostPerMaterialUnitRequired
            materialCost = materialCostPerPortion * (float(quantity) / float(portionSize))
            price += materialCost

    else:
        log.LogWarn('GetComputedBasePrice - MISSING RECIPE FOR type:%s is 0' % typeID)
        price = float(evetypes.GetBasePrice(typeID)) * (float(quantity) / float(portionSize))
    return int(price)
