#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\effects\sideeffect.py
from dogma.effects import Effect

def GetSideEffectClassByTypeString(effectType):
    if effectType == 'EffectStopper':
        return _GetEffectStopper


def _GetEffectStopper(modifier):
    return EffectStopper(modifier.effectID)


class EffectStopper(Effect):

    def __init__(self, effectID):
        self.effectID = effectID

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.StopEffect(self.effectID, targetID, forced=True)
