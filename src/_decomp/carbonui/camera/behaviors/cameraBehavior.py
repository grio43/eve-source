#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\camera\behaviors\cameraBehavior.py


class CameraBehavior(object):

    def __init__(self):
        self.gameWorld = None
        self._LoadGameWorld()

    def _LoadGameWorld(self):
        pass

    def ProcessCameraUpdate(self, camera, now, frameTime):
        pass

    def _GetEntity(self, entID):
        return sm.GetService('entityClient').FindEntityByID(entID)

    def _GetEntityModel(self, entID):
        entity = sm.GetService('entityClient').FindEntityByID(entID)
        if entity and entity.HasComponent('paperdoll'):
            return entity.GetComponent('paperdoll').doll.avatar

    def Reset(self):
        pass

    def OnBehaviorAdded(self, camera):
        pass
