#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveSpaceObject\spaceobjanimation.py


def SetShipAnimationStance(ship, stanceID):
    if ship and stanceID is not None:
        ship.SetControllerVariable('ShipStance', stanceID)
        return True
    return False


def SetControllerVariable(model, name, value):
    try:
        model.SetControllerVariable(name, float(value))
    except AttributeError:
        pass


def TriggerDefaultStates(model):
    if hasattr(model, 'StartControllers'):
        model.StartControllers()
