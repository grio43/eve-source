#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_sun.py
from utils_scene import *
from utils_renderer import RenderToBitmapFromScene
from renderer_base import IconRenderer
from iconrendering2.const import Language
from platformtools.compatibility.exposure.artpipeline.tools.utils.PlanetUtils import BuildPlanet, ConvertPlanetToEffectRoot

class SunIconRenderer(IconRenderer):

    def __init__(self, objectPath, language = Language.ENGLISH):
        super(SunIconRenderer, self).__init__(language)
        self._objectPath = objectPath
        self._scene = None
        self._object = None
        self._shaderModel = trinity.GetShaderModel()

    def __str__(self):
        return 'Sun Icon Renderer <%s>' % hex(id(self))

    def _PrepareRender(self):
        self._shaderModel = trinity.GetShaderModel()
        trinity.SetShaderModel('SM_3_0_DEPTH')
        self._scene = trinity.EveSpaceScene()
        self._scene.postprocess = trinity.Tr2PostProcess2()
        self._scene.postprocess.dynamicExposure = trinity.Tr2PPDynamicExposureEffect()
        self._scene.postprocess.dynamicExposure.influence = 0.0
        self._scene.postprocess.dynamicExposure.adjustment = -0.5
        self._object = BuildPlanet(self._objectPath, None, None, 0)
        self._initialScale = None
        if self._object:
            self._InitializeObject()
            self._scene.objects.append(self._object)
        self._object.FreezeHighDetailMesh()
        FreezeTime()

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
        self._PrepareObjectForRender(renderInfo)
        self._DoRendering(renderInfo, view, projection)

    def _DoRendering(self, renderInfo, view, projection):
        bitmap = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, postProcessingQuality=2)
        bitmap.Save(renderInfo.outputPath)

    def _InitializeObject(self):
        if hasattr(self._object, 'curveSets'):
            self._object.curveSets.removeAt(-1)
        self._object.scaling = (20, 20, 20)
        self._initialScale = self._object.scaling

    def _PrepareSceneForRender(self):
        self._scene.sunDirection = (-0.5, -0.5, -0.6)
        projection = trinity.TriProjection()
        projection.PerspectiveFov(GETPHOTO_FOV, 1.0, 0.0001, 1000)
        view = trinity.TriView()
        view.transform = ((0.9110742211341858, 0.2911122441291809, 0.2918860614299774, 0.0),
         (0.0, 0.7080447673797607, -0.7061676383018494, 0.0),
         (-0.41224241256713867, 0.6433711051940918, 0.6450812816619873, 0.0),
         (4.290776252746582, -4.666899681091309, -13.901455879211426, 1.0))
        return (view, projection)

    def _PrepareObjectForRender(self, renderInfo):
        if renderInfo.metadata:
            controllerVariables = renderInfo.metadata.get('stateControllerVariables', [])
            if len(controllerVariables) > 0 and hasattr(self._object, 'SetControllerVariable'):
                for var, value in controllerVariables.iteritems():
                    self._object.SetControllerVariable(var, value)

                self._object.StartControllers()
            scaleFactor = renderInfo.metadata.get('scaleFactor', 1.0)
            if scaleFactor != 1.0:
                self._object.scaling = (self._initialScale[0] * scaleFactor, self._initialScale[1] * scaleFactor, self._initialScale[2] * scaleFactor)
