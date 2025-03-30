#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\dungeonHelper.py
import blue
from eve.client.script.parklife import dungeonEditorTools
import math
from ballparkCommon.ballRadius import ComputeRadiusFromQuantity, ComputeQuantityFromRadius
import trinity
import geo2

def IsJessicaOpen():
    return '/jessica' in blue.pyos.GetArg()


def IsObjectLocked(objectID):
    return (False, [])


def SetObjectPosition(objectID, x = None, y = None, z = None):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    dX = 0
    if x is not None:
        dX = x - slimItem.dunX
        slimItem.dunX = x
    dY = 0
    if y is not None:
        dY = y - slimItem.dunY
        slimItem.dunY = y
    dZ = 0
    if z is not None:
        dZ = z - slimItem.dunZ
        slimItem.dunZ = z
    targetModel = getattr(targetBall, 'model', None)
    if targetModel:
        targetModel.translationCurve.x += dX
        targetModel.translationCurve.y += dY
        targetModel.translationCurve.z += dZ
    scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_TRANSLATION)


def SetObjectRotation(objectID, yaw = None, pitch = None, roll = None):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    try:
        mYaw, mPitch, mRoll = geo2.QuaternionRotationGetYawPitchRoll(targetModel.rotationCurve.value)
    except:
        mYaw, mPitch, mRoll = targetBall.yaw, targetBall.pitch, targetBall.roll

    if yaw is None:
        yaw = mYaw
    if pitch is None:
        pitch = mPitch
    if roll is None:
        roll = mRoll
    targetBall.typeData['dunRotation'] = (yaw, pitch, roll)
    targetBall.SetStaticRotation()
    scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_ROTATION)


def SetObjectRadius(objectID, radius):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    if slimItem.categoryID == const.categoryAsteroid or slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
        godma = sm.GetService('godma')
        computedQuantity = ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, radius, godma)
        SetObjectQuantity(objectID, computedQuantity)


def SetObjectQuantity(objectID, quantity):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    if slimItem.categoryID == const.categoryAsteroid or slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
        godma = sm.GetService('godma')
        computedRadius = ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, quantity, godma)
        if hasattr(targetModel, 'modelScale'):
            targetModel.modelScale = computedRadius
        elif hasattr(targetModel, 'scaling'):
            scaleVector = trinity.TriVector(computedRadius, computedRadius, computedRadius)
            targetModel.scaling = scaleVector
        else:
            raise RuntimeError('Model has neither modelScale nor scaling')
        slimItem.dunRadius = quantity
        scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_SCALE)
    else:
        raise RuntimeError("Can't scale type %d" % slimItem.categoryID)


def GetObjectPosition(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    return (slimItem.dunX, slimItem.dunY, slimItem.dunZ)


def GetObjectRotation(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel or not targetModel.rotationCurve or not hasattr(targetModel.rotationCurve, 'value'):
        return (None, None, None)
    return (x * 180.0 / math.pi for x in geo2.QuaternionRotationGetYawPitchRoll(targetModel.rotationCurve.value))


def GetObjectQuantity(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    if hasattr(targetModel, 'scaling') or hasattr(targetModel, 'modelScale'):
        if not getattr(slimItem, 'dunRadius', None):
            slimItem.dunRadius = targetBall.radius
        if slimItem.categoryID == const.categoryAsteroid:
            return slimItem.dunRadius
        if slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
            return slimItem.dunRadius


def GetObjectRadius(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    if hasattr(targetModel, 'scaling') or hasattr(targetModel, 'modelScale'):
        godma = sm.GetService('godma')
        if not getattr(slimItem, 'dunRadius', None):
            slimItem.dunRadius = ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, targetBall.radius, godma)
        if slimItem.categoryID == const.categoryAsteroid:
            return ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma)
        if slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
            return ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma)
