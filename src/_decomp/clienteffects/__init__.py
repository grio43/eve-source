#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\clienteffects\__init__.py
EFFECT_METHOD = 'OnSpecialFX'

def SetEffect(sourceID, targetID, effectName, start, duration, repeat, graphicInfo = None):
    sm.ScatterEvent(EFFECT_METHOD, sourceID, None, None, targetID, None, effectName, 0, start, 0, duration, repeat, graphicInfo=graphicInfo)


def StartShipEffect(sourceID, effectName, duration, repeat, graphicInfo = None):
    SetEffect(sourceID, None, effectName, True, duration, repeat, graphicInfo=graphicInfo)


def StopShipEffect(sourceID, effectName, graphicInfo = None):
    SetEffect(sourceID, None, effectName, False, None, None, graphicInfo=graphicInfo)


def StartStretchEffect(sourceID, targetID, effectName, duration, repeat):
    SetEffect(sourceID, targetID, effectName, True, duration, repeat)


def StopStretchEffect(sourceID, targetID, effectName):
    SetEffect(sourceID, targetID, effectName, False, None, None)
