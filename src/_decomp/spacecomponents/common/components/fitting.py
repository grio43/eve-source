#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\components\fitting.py
from ..componentConst import FITTING_CLASS
from spacecomponents.common.helper import HasFittingComponent
from spacecomponents.common.helper import IsActiveComponent
from spacecomponents.common.helper import IsReinforcedComponent
from ..data import get_space_component_for_type

def IsShipWithinFittingRange(shipSlimItem, componentSlimItem, ballPark):
    if shipSlimItem is None:
        return False
    if not hasattr(componentSlimItem, 'typeID'):
        return False
    ball = ballPark.GetBall(componentSlimItem.itemID)
    itemIsDead = not ball or ball.isMoribund
    componentTypeID = componentSlimItem.typeID
    if shipSlimItem.ownerID != componentSlimItem.ownerID:
        return False
    if itemIsDead:
        return False
    if not HasFittingComponent(componentTypeID):
        return False
    if not IsActiveComponent(ballPark.componentRegistry, componentTypeID, componentSlimItem.itemID):
        return False
    if IsReinforcedComponent(ballPark.componentRegistry, componentTypeID, componentSlimItem.itemID):
        return False
    fittingRange = get_space_component_for_type(componentTypeID, FITTING_CLASS).range
    shipDistanceFromComponent = ballPark.GetSurfaceDist(shipSlimItem.itemID, componentSlimItem.itemID)
    return shipDistanceFromComponent <= fittingRange
