#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_planetary_pin.py
import trinity
from utils_scene import *
from utils_renderer import RenderToBitmapFromScene
from renderer_base import IconRenderer
from iconrendering2.const import Language
from iconrendering2.utils import Pump

class PlanetaryPinIconRenderer(IconRenderer):

    def __init__(self, objectPath, language = Language.ENGLISH):
        super(PlanetaryPinIconRenderer, self).__init__(language)
        self._objectPath = objectPath
        self._scene = None
        self._object = None
        self._shaderModel = trinity.GetShaderModel()

    def __str__(self):
        return 'Planetary Pin Icon Renderer <%s>' % hex(id(self))

    def _PrepareRender(self):
        self._shaderModel = trinity.GetShaderModel()
        trinity.SetShaderModel('SM_3_0_DEPTH')
        FreezeTime()
        self._scene = trinity.EveSpaceScene()
        self._object = blue.resMan.LoadObject(self._objectPath)
        blue.resMan.Wait()
        Pump()
        if self._object:
            self._InitializeObject()
            self._scene.objects.append(self._object)

    def _FinishRender(self):
        del self._object
        self._object = None
        del self._scene
        self._scene = None
        trinity.SetShaderModel(self._shaderModel)

    def _Render(self, renderInfo):
        if not self._scene or not self._object or not renderInfo:
            return
        view, projection = self._PrepareSceneForRender()
        self._DoRendering(renderInfo, view, projection)

    def _DoRendering(self, renderInfo, view, projection):
        bitmap = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, postProcessingQuality=2)
        bitmap.Save(renderInfo.outputPath)

    def _InitializeObject(self):
        if hasattr(self._object, 'curveSets'):
            self._object.curveSets.removeAt(-1)

    def _PrepareSceneForRender(self):
        self._scene.sunDirection = (-0.5, -0.5, -0.6)
        bBoxMin = (0.0, 0.0, 0.0)
        bBoxMax = (0.0, 0.0, 0.0)
        for i in range(self._object.mesh.geometry.GetMeshAreaCount(0)):
            boundingBoxMin, boundingBoxMax = self._object.mesh.geometry.GetAreaBoundingBox(0, i)
            if abs(boundingBoxMax[1] - boundingBoxMin[1]) > 0.005:
                if geo2.Vec3Length(bBoxMin) < geo2.Vec3Length(boundingBoxMin):
                    bBoxMin = boundingBoxMin
                if geo2.Vec3Length(bBoxMax) < geo2.Vec3Length(boundingBoxMax):
                    bBoxMax = boundingBoxMax

        return GetViewAndProjectionUsingBoundingBox(bBoxMin, bBoxMax)
