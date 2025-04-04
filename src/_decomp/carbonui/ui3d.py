#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\ui3d.py
import logging
import trinity
import geo2
from carbonui.primitives.desktop import UIRoot
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)

class InSceneContainer(UIRoot):
    __guid__ = 'ui3d.InSceneContainer'
    TRACKTYPE_BALL = 1
    TRACKTYPE_TRANSFORM = 2
    default_trackType = TRACKTYPE_BALL
    default_faceCamera = False

    def __init__(self, *args, **kwargs):
        trinity.device.RegisterResource(self)
        self.renderScene = kwargs['scene']
        self.sceneParent = kwargs.get('sceneParent', self.renderScene.objects)
        self._camera = kwargs.get('camera', None)
        self.trackType = kwargs.get('trackType', self.default_trackType)
        self.initialized = False
        self.sceneManager = sm.GetService('sceneManager')
        self.name = kwargs['name']
        self.faceCamera = kwargs.get('faceCamera', self.default_faceCamera)
        self.parentTransform = kwargs.get('parentTransform', None)
        try:
            super(InSceneContainer, self).__init__(**kwargs)
            self.Create3DRender()
            uicore.uilib.AddRootObject(self)
            self.initialized = True
        except Exception as e:
            logger.exception(e)
        finally:
            if not self.initialized:
                self.Close()

    def Create3DRender(self):
        self.renderTexture = trinity.TriTextureParameter()
        self.renderTexture.name = 'DiffuseMap'
        self.renderColor = trinity.Tr2Vector4Parameter()
        self.renderColor.name = 'DiffuseColor'
        self.renderColor.value = (1, 1, 1, 1)
        self.renderEffect = trinity.Tr2Effect()
        self.renderEffect.options.append(('DEPTH_MAP_OCCLUSION', 'DEPTH_MAP_OCCLUSION_YES'))
        self.renderEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        self.renderEffect.resources.append(self.renderTexture)
        self.renderEffect.parameters.append(self.renderColor)
        self.renderArea = trinity.Tr2MeshArea()
        self.renderArea.effect = self.renderEffect
        self.renderMesh = trinity.Tr2Mesh()
        self.renderMesh.name = 'orbitalBombardmentTarget'
        self.renderMesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
        self.renderMesh.transparentAreas.append(self.renderArea)
        if self.trackType == self.TRACKTYPE_BALL:
            self.transform = trinity.EveRootTransform()
        else:
            self.transform = trinity.EveTransform()
        if self.faceCamera:
            self.transform.modifier = 1
        self.transform.mesh = self.renderMesh
        if self.parentTransform:
            self.parentTransform.children.append(self.transform)
        else:
            self.sceneParent.append(self.transform)
        self.transform.name = self.name
        self.renderJob = trinity.CreateRenderJob()
        self.renderJob.Update(self.renderObject)
        self.renderObject = self.GetRenderObject()
        self.renderObject.is2dPick = False
        self.create_render_target()
        self.renderJob.PushRenderTarget(self.renderTarget)
        self.renderJob.RenderScene(self.renderObject)
        self.renderJob.PopRenderTarget()
        self.renderJob.ScheduleRecurring(insertFront=True)
        self.renderTexture.SetResource(trinity.TriTextureRes(self.renderTarget))
        self.disable_render_steps()

    def create_render_target(self):
        self.renderTarget = trinity.Tr2RenderTarget(self.width, self.height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)

    def disable_render_steps(self):
        self.renderSteps[-1].enabled = False

    def Close(self):
        if getattr(self, 'renderJob', None) is not None:
            self.renderJob.UnscheduleRecurring()
        if getattr(self, 'transform', None) is not None and getattr(self, 'renderScene', None) is not None:
            if self.transform in self.sceneParent:
                self.sceneParent.remove(self.transform)
        UIRoot.Close(self)
        uicore.uilib.RemoveRootObject(self)

    def OnInvalidate(self, device):
        pass

    def OnCreate(self, level):
        self.renderTexture.SetResource(trinity.TriTextureRes(self.renderTarget))

    def PickObject(self, x, y):
        if self.sceneManager.GetActiveScene() != self.renderScene:
            return
        rescale = 1.0 / 10000.0
        projection = trinity.TriProjection()
        projection.PerspectiveFov(trinity.GetFieldOfView(), trinity.GetAspectRatio(), trinity.GetFrontClip(), trinity.GetBackClip())
        view = trinity.TriView()
        view.transform = trinity.GetViewTransform()
        scaling, rotation, translation = geo2.MatrixDecompose(self.transform.worldTransform)
        pZ = geo2.Vec3Transform((0, 0, 1), self.transform.worldTransform)
        surfaceNormal = geo2.Subtract(pZ, translation)
        cameraZ = geo2.Vector(view.transform[0][2], view.transform[1][2], view.transform[2][2])
        if geo2.Vec3Dot(surfaceNormal, cameraZ) < 0:
            return
        self.renderObject.translation = geo2.Vec3Scale(translation, rescale)
        self.renderObject.rotation = rotation
        self.renderObject.scaling = geo2.Vec3Scale(scaling, rescale)
        scaling, rotation, translation = geo2.MatrixDecompose(view.transform)
        translation = geo2.Vec3Scale(translation, rescale)
        view.transform = geo2.MatrixTransformation(None, None, scaling, None, rotation, translation)
        return self.renderObject.PickObject(x, y, projection, view, trinity.device.viewport)

    def _GetColor(self):
        return self.renderColor.value

    def _SetColor(self, value):
        self.renderColor.value = value

    color = property(_GetColor, _SetColor)

    def _GetRed(self):
        return self.renderColor.value[0]

    def _SetRed(self, value):
        self.renderColor.value = (value,
         self.renderColor.value[1],
         self.renderColor.value[2],
         self.renderColor.value[3])

    red = property(_GetRed, _SetRed)

    def _GetBlue(self):
        return self.renderColor.value[1]

    def _SetBlue(self, value):
        self.renderColor.value = (self.renderColor.value[0],
         value,
         self.renderColor.value[2],
         self.renderColor.value[3])

    blue = property(_GetBlue, _SetBlue)

    def _GetGreen(self):
        return self.renderColor.value[2]

    def _SetGreen(self, value):
        self.renderColor.value = (self.renderColor.value[0],
         self.renderColor.value[1],
         value,
         self.renderColor.value[3])

    green = property(_GetGreen, _SetGreen)

    def _GetAlpha(self):
        return self.renderColor.value[3]

    def _SetAlpha(self, value):
        self.renderColor.value = (self.renderColor.value[0],
         self.renderColor.value[1],
         self.renderColor.value[2],
         value)

    alpha = property(_GetAlpha, _SetAlpha)
