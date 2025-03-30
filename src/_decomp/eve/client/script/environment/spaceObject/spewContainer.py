#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\spewContainer.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class SpewContainer(SpaceObject):

    def Assemble(self):
        self.UnSync()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupSharedAmbientAudio()
        self.SetStaticRotation()
