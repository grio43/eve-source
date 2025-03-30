#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\cloud.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import evegraphics.settings as gfxsettings

class Cloud(SpaceObject):

    def LoadModel(self, fileName = None, loadedModel = None):
        if not gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED):
            return
        SpaceObject.LoadModel(self, fileName, loadedModel)

    def Assemble(self):
        self.SetStaticRotation()
        self.SetRadius(self.radius)
        self.SetupAmbientAudio()

    def SetRadius(self, r):
        s = 2.0
        if self.model is not None and hasattr(self.model, 'scaling'):
            self.model.scaling = (s * r, s * r, s * r)
