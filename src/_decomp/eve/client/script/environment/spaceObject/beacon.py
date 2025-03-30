#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\beacon.py
import trinity
from spaceObject import SpaceObject
import evegraphics.settings as gfxsettings

class Beacon(SpaceObject):

    def LoadModel(self, fileName = None, loadedModel = None):
        if not self.typeData.get('graphicID', None) or gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED) == 0:
            model = trinity.EveRootTransform()
            SpaceObject.LoadModel(self, fileName, loadedModel=model)
        else:
            SpaceObject.LoadModel(self, fileName, loadedModel)
            self.SetupAmbientAudio()
