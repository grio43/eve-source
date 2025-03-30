#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ballparkCommon\ballRadius.py
import math
import evetypes
from dogma.const import attributeAsteroidRadiusUnitSize, attributeAsteroidRadiusGrowthFactor, attributeAsteroidMaxRadius
from inventorycommon.const import categoryAsteroid, groupHarvestableCloud
ASTEROID_EXP_SCALE = 4e-05

def ComputeRadiusFromQuantity(categoryID, groupID, typeID, quantity, dogma):
    if quantity < 0:
        quantity = 1
    if categoryID == categoryAsteroid:
        return AsteroidQuantityToRadius(typeID, quantity, dogma)
    if groupID == groupHarvestableCloud:
        return quantity * evetypes.GetRadius(typeID) / 10.0
    return quantity * evetypes.GetRadius(typeID)


def AsteroidQuantityToRadius(typeID, quantity, dogma):
    unitSize = dogma.GetTypeAttribute2(typeID, attributeAsteroidRadiusUnitSize)
    growthFactor = dogma.GetTypeAttribute2(typeID, attributeAsteroidRadiusGrowthFactor)
    maxRadius = dogma.GetTypeAttribute2(typeID, attributeAsteroidMaxRadius)
    quantity = max(1, quantity)
    radius = unitSize * math.exp(ASTEROID_EXP_SCALE * (quantity - 1) * growthFactor)
    return min(maxRadius, radius)


def ComputeQuantityFromRadius(categoryID, groupID, typeID, radius, dogma):
    if categoryID == categoryAsteroid:
        return AsteroidRadiusToQuantity(typeID, radius, dogma)
    if groupID == groupHarvestableCloud:
        quantity = radius * 10.0 / evetypes.GetRadius(typeID)
        return quantity
    return radius / evetypes.GetRadius(typeID)


def AsteroidRadiusToQuantity(typeID, radius, dogma):
    unitSize = dogma.GetTypeAttribute2(typeID, attributeAsteroidRadiusUnitSize)
    growthFactor = dogma.GetTypeAttribute2(typeID, attributeAsteroidRadiusGrowthFactor)
    quantity = 1 + math.log(radius / unitSize) * (1.0 / ASTEROID_EXP_SCALE / growthFactor)
    return quantity
