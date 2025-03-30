#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\destructibleEffectBeacon.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from inventorycommon.const import TYPES_THAT_ALWAYS_FACE_THE_SUN

class DestructibleEffectBeacon(SpaceObject):

    def Assemble(self):
        self.SetStaticRotation()
