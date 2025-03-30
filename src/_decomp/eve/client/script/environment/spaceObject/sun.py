#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\sun.py
import blue
import geo2
import uthread2
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import trinity
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs
import inventorycommon.typeHelpers

class Sun(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self._stopUpdate = False
        self.sunColorClose = (0, 0, 1.5)
        self.sunColorFar = (0, 0, 1.5)
        self.lensflare = None
        self.sceneManager = sm.GetService('sceneManager')

    def LoadModel(self, fileName = None, loadedModel = None):
        self.Reload(self.typeData.get('graphicFile', None), self.typeID)

    def Reload(self, sunGraphicFile, typeID):
        scene = self.spaceMgr.GetScene()
        if self.lensflare is not None and self.lensflare in scene.lensflares:
            scene.lensflares.remove(self.lensflare)
        sunFlareGraphicID = cfg.mapSystemCache[session.solarsystemid].sunFlareGraphicID
        self.lensflare = trinity.Load(fsdGraphicIDs.GetGraphicFile(sunFlareGraphicID))
        scene.sunBall = self
        self.model = trinity.Load(sunGraphicFile)
        if self.model is None:
            self.model = trinity.EvePlanet()
        self.model.translationCurve = self
        self.model.rotationCurve = self
        self.model.name = '%d' % self.id
        gfx = inventorycommon.typeHelpers.GetGraphic(typeID)
        sunColorClose = (1.5, 1.5, 1.5, 1.0)
        if hasattr(gfx, 'emissiveColor') and gfx.emissiveColor:
            sunColorClose = tuple(gfx.emissiveColor)
        self.sunColorClose = trinity.TriColor(*sunColorClose).GetHSV()
        if hasattr(gfx, 'albedoColor') and gfx.albedoColor:
            sunColorFar = tuple(gfx.albedoColor)
            self.sunColorFar = trinity.TriColor(*sunColorFar).GetHSV()
        else:
            self.sunColorFar = (self.sunColorClose[0], self.sunColorClose[1] * 0.5, 1.5)
        if abs(self.sunColorClose[0] - self.sunColorFar[0]) > 180:
            self.sunColorFar = (360 + self.sunColorFar[0], self.sunColorFar[1], self.sunColorFar[2])
        self._stopUpdate = False
        uthread2.StartTasklet(self._UpdateSunColor)
        self._UpdateController(sunGraphicFile)
        if self.model is not None and self.model not in scene.planets:
            scene.planets.append(self.model)
        if self.lensflare is not None:
            self.lensflare.translationCurve = self
            scene.lensflares.append(self.lensflare)
            godRaysColor = fsdGraphicIDs.GetAlbedoColor(sunFlareGraphicID)
            scene = self.sceneManager.fisRenderJob.GetScene()
            if scene.postprocess is None:
                scene.postprocess = trinity.Tr2PostProcess2()
            if scene.postprocess.godRays is None:
                scene.postprocess.godRays = trinity.Tr2PPGodRaysEffect()
            self.sceneManager.fisRenderJob.GetScene().postprocess.godRays.godRayColor = (godRaysColor[0],
             godRaysColor[1],
             godRaysColor[2],
             godRaysColor[3])
        self.SetupAmbientAudio()
        if self._audioEntity:
            self._audioEntity.SetAttenuationScalingFactor(self.radius)

    def _UpdateController(self, sunGraphicFile):
        isYellow = bool('yellow' in sunGraphicFile.lower())
        if isYellow:
            self.model.SetControllerVariable('star_is_yellow', 1.0)
        self.model.SetControllerVariable('radius', self.radius or 0)

    def _UpdateSunColor(self):
        triColor = trinity.TriColor()
        while not self._stopUpdate:
            try:
                distance = self.model.translationCurve.UpdateVector(blue.os.GetSimTime()).Length()
                ratio = 1.0 / max(1.0, distance / self.radius * 0.5)
                color = geo2.Vec3Lerp(self.sunColorFar, self.sunColorClose, ratio)
                triColor.SetHSV(*color)
                scene = self.spaceMgr.GetScene()
                if scene:
                    scene.sunDiffuseColor = (triColor.r,
                     triColor.g,
                     triColor.b,
                     1.0)
            except:
                pass

            uthread2.Sleep(0.1)

    def EnableGodRays(self, enable):
        self.sceneManager.fisRenderJob.postProcess.GodRaysIntensity = 1.0 if enable else 0.0

    def Assemble(self):
        self.model.radius = self.radius
        self.model.scaling = (self.radius, self.radius, self.radius)

    def Release(self, origin = None):
        if self.released:
            return
        self.ReleaseSun()
        SpaceObject.Release(self, 'Sun')

    def ReleaseSun(self):
        self._stopUpdate = True
        scene = self.spaceMgr.GetScene()
        if hasattr(self.model, 'children'):
            del self.model.children[:]
        if scene:
            scene.planets.fremove(self.model)
        if self.model is not None:
            self.model.translationCurve = None
            self.model.rotationCurve = None
            self.model = None
        self.lensflare = None
        if scene:
            scene.sunBall = None
            del scene.lensflares[:]


exports = {'spaceObject.Sun': Sun}
