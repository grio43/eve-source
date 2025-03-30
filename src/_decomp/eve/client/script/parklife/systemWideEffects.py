#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\systemWideEffects.py


class SystemWideEffects(object):

    def __init__(self):
        self._systemWideEffects = {}

    def ResetSystemWideEffects(self):
        self._systemWideEffects.clear()

    def OnSystemWideEffectStart(self, effectID, sourceItemID, sourceTypeID):
        if not self.hasAddedEffect(sourceItemID, sourceTypeID):
            self._systemWideEffects[sourceItemID, sourceTypeID] = {effectID}
        else:
            self._systemWideEffects[sourceItemID, sourceTypeID].add(effectID)

    def OnSystemWideEffectStop(self, effectID, sourceItemID, sourceTypeID):
        if (sourceItemID, sourceTypeID) in self._systemWideEffects:
            self._systemWideEffects[sourceItemID, sourceTypeID].discard(effectID)
            if self.hasNoEffects(sourceItemID, sourceTypeID):
                self._systemWideEffects.pop((sourceItemID, sourceTypeID))

    def OnUpdateSystemWideEffectInfo(self, systemWideEffectsOnShip):
        self._systemWideEffects = systemWideEffectsOnShip

    def GetSystemWideEffectsOnShip(self):
        return self._systemWideEffects

    def hasAddedEffect(self, sourceItemID, sourceTypeID):
        return (sourceItemID, sourceTypeID) in self._systemWideEffects

    def hasNoEffects(self, sourceItemID, sourceTypeID):
        if (sourceItemID, sourceTypeID) not in self._systemWideEffects:
            return True
        return len(self._systemWideEffects[sourceItemID, sourceTypeID]) is 0
