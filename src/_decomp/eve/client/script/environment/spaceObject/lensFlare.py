#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\lensFlare.py
import evetypes
import trinity
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from fsdBuiltData.common.graphicIDs import GetGraphicFile, GetAlbedoColor

class LensFlare(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.lensflare = None

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        graphicID = evetypes.GetGraphicID(self.typeID)
        self.lensflare = trinity.Load(GetGraphicFile(graphicID))
        scene = self.spaceMgr.GetScene()
        if self.lensflare and scene:
            self.lensflare.translationCurve = self
            scene.lensflares.append(self.lensflare)
        if scene.sunBall is None:
            scene.sunBall = self
            if GetAlbedoColor(graphicID) is not None:
                sunColor = tuple(GetAlbedoColor(graphicID))
                scene.sunDiffuseColor = sunColor

    def Release(self, origin = None):
        if self.released:
            return
        scene = self.spaceMgr.GetScene()
        if scene:
            if scene.sunBall == self:
                scene.sunBall = None
            if self.lensflare and self.lensflare in scene.lensflares:
                scene.lensflares.fremove(self.lensflare)
        self.lensflare = None
        SpaceObject.Release(self, 'Sun')
