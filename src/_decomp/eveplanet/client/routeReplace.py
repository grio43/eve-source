#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveplanet\client\routeReplace.py
import mathext

def GetRouteToDeleteAndNewRouteData(newSchematicID, pins, getSchematicFunc, getSourceRoutesForPin, getDestinationRoutesForPin):
    newSchematicData = getSchematicFunc(newSchematicID)
    newOutput = newSchematicData.outputs[0]
    resultsByPinID = {}
    for p in pins:
        pinResults = ReplacementResultsForPin(p.id)
        if p.schematicID is None:
            resultsByPinID[p.id] = pinResults
            continue
        oldSchematicData = getSchematicFunc(p.schematicID)
        oldOutputsByTypeID = {x.typeID:x for x in oldSchematicData.outputs}
        oldInputsByTypeID = {x.typeID:x for x in oldSchematicData.inputs}
        newOutputByOldOutputTypeID, newInputByOldInputTypeID = _GetMappingOldNewInputsOutputs(newSchematicData, oldSchematicData)
        leftToRoute = newOutput.quantity
        routesFrom = getSourceRoutesForPin(p.id)
        for route in routesFrom:
            qtyPercentage = float(route.commodityQuantity) / oldOutputsByTypeID[route.commodityTypeID].quantity
            newOutput = newOutputByOldOutputTypeID.get(route.commodityTypeID)
            newQty = mathext.clamp(int(round(qtyPercentage * newOutput.quantity)), 0, leftToRoute)
            leftToRoute -= newQty
            pinResults.outputRouteIDsToDelete.add(route.routeID)
            pinResults.newOutputRouteData.append((newOutput.typeID, newQty, route.path[:]))

        routesTo = getDestinationRoutesForPin(p.id)
        for route in routesTo:
            newInput = newInputByOldInputTypeID.get(route.commodityTypeID)
            if route.commodityQuantity == oldInputsByTypeID[route.commodityTypeID].quantity:
                newQty = newInput.quantity
            else:
                qtyPercentage = float(route.commodityQuantity) / oldInputsByTypeID[route.commodityTypeID].quantity
                newQty = mathext.clamp(int(round(qtyPercentage * newInput.quantity)), 0, newInput.quantity)
            pinResults.inputRouteIDsToDelete.add(route.routeID)
            pinResults.newInputRouteData.append((newInput.typeID, newQty, route.path[:]))

        resultsByPinID[p.id] = pinResults

    return resultsByPinID


def _GetMappingOldNewInputsOutputs(newSchematicData, oldSchematicData):
    newOutputByOldOutputTypeID = {o.typeID:n for o, n in zip(oldSchematicData.outputs, newSchematicData.outputs)}
    newInputByOldInputTypeID = {o.typeID:n for o, n in zip(sorted(oldSchematicData.inputs, key=lambda x: x.typeID), sorted(newSchematicData.inputs, key=lambda x: x.typeID))}
    return (newOutputByOldOutputTypeID, newInputByOldInputTypeID)


class ReplacementResultsForPin(object):

    def __init__(self, pinID):
        self.pinID = pinID
        self.newOutputRouteData = []
        self.outputRouteIDsToDelete = set()
        self.newInputRouteData = []
        self.inputRouteIDsToDelete = set()
