#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_spaceobject.py
import trinity
import eveSpaceObject.spaceobjanimation as soanimation
import iconrendering2.const
from iconrendering2.const import Language, IconViewMode, IconRenderFormat, VIEW_MODE_CAMERA_ANGLES, VIEW_MODE_SUN_DIRECTIONS
from utils_scene import *
from utils_renderer import RenderToBitmapFromScene
from renderer_base import IconRenderer, RenderException

class SpaceObjectIconRenderer(IconRenderer):

    def __init__(self, sofFactory, scenePath, dna, language = Language.ENGLISH):
        super(SpaceObjectIconRenderer, self).__init__(language)
        self._sofFactory = sofFactory
        self._scenePath = scenePath
        self._dna = dna
        self._scene = None
        self._object = None
        self._shaderModel = trinity.GetShaderModel()

    def __str__(self):
        return 'Space Object Icon Renderer <%s>' % hex(id(self))

    def _PrepareRender(self):
        self._shaderModel = trinity.GetShaderModel()
        trinity.SetShaderModel('SM_3_0_DEPTH')
        trinity.GetVariableStore().RegisterVariable('EveSpaceSceneShadowMap', trinity.TriTextureRes())
        if self._scenePath:
            self._scene = blue.resMan.LoadObject(self._scenePath)
        else:
            self._scene = trinity.EveSpaceScene()
        self._object = self._sofFactory.BuildFromDNA(self._dna)
        self._initialScale = None
        if self._object:
            self._InitializeObject()
            self._scene.objects.append(self._object)
            WaitForGeometryLoad(self._object, context=self._dna)
            self._scene.UpdateScene(blue.os.GetTime())

    def _FinishRender(self):
        del self._object
        self._object = None
        del self._scene
        self._scene = None
        trinity.SetShaderModel(self._shaderModel)

    def _Render(self, renderInfo):
        if not self._scene or not self._object:
            raise RenderException('Could not render icon %s' % renderInfo.outputPath, renderInfo.outputPath)
        view, projection = self._PrepareSceneForRender(renderInfo)
        self._PrepareObjectForRender(renderInfo)
        self._DoRendering(renderInfo, view, projection)

    def _DoRendering(self, renderInfo, view, projection):
        supersampleQuality = 1
        outlineColor = renderInfo.outlineColor if iconrendering2.const.OUTLINE_THICKNESS > 0 else None
        if renderInfo.renderFormat == IconRenderFormat.JPG or renderInfo.background == None and not renderInfo.backgroundTransparent:
            outlineColor = None
        originalSize = renderInfo.renderSize
        originalBackground = renderInfo.background
        if outlineColor:
            supersampleQuality = 0
            renderInfo.background = None
            renderInfo.backgroundTransparent = True
        waitTime = 0 if not renderInfo.metadata else renderInfo.metadata.get('animationOffset', 0)
        if renderInfo.backgroundTransparent:
            prevColor = renderInfo.backgroundColor
            renderInfo.backgroundColor = (1.0, 0.0, 0.0)
            bitmapR = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, waitTime=waitTime)
            renderInfo.backgroundColor = (0.0, 1.0, 0.0)
            bitmapG = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, waitTime=waitTime)
            renderInfo.backgroundColor = (0.0, 0.0, 1.0)
            bitmapB = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, waitTime=waitTime)
            renderInfo.backgroundColor = prevColor
            bitmap = _CreateAlpha(bitmapR, bitmapG, bitmapB)
            bitmap.Save(renderInfo.outputPath)
        else:
            bitmap = RenderToBitmapFromScene(renderInfo, self._scene, view, projection, waitTime=waitTime, supersampleQuality=supersampleQuality)
            bitmap.Save(renderInfo.outputPath)
        if renderInfo.metadata and renderInfo.metadata.get('viewMode', IconViewMode.FREE) == IconViewMode.TOP:
            from PIL import Image
            img = Image.open(renderInfo.outputPath)
            img = img.rotate(90.0)
            img.save(renderInfo.outputPath)
        if outlineColor:
            from utils_renderer import ApplyOutline
            backgroundPath = blue.paths.ResolvePath(originalBackground) if originalBackground else None
            ApplyOutline(renderInfo.outputPath, originalSize, outlineColor, iconrendering2.const.OUTLINE_THICKNESS, iconrendering2.const.OUTLINE_HARDLINES, backgroundPath)

    def _InitializeObject(self):
        if hasattr(self._object, 'FreezeHighDetailMesh'):
            self._object.FreezeHighDetailMesh()
        perlinCurves = self._object.Find('trinity.TriPerlinCurve')
        for curve in perlinCurves:
            curve.scale = 0.0

        if hasattr(self._object, 'modelRotationCurve'):
            self._object.modelRotationCurve = None
        if hasattr(self._object, 'modelTranslationCurve'):
            self._object.modelTranslationCurve = None
        if hasattr(self._object, 'rotationCurve'):
            self._object.rotationCurve = None
        if hasattr(self._object, 'translationCurve'):
            self._object.translationCurve = None
        if hasattr(self._object, 'boosters'):
            self._object.boosters = None
        if hasattr(self._object, 'scaling'):
            self._initialScale = self._object.scaling

    def _PrepareObjectForRender(self, renderInfo):
        if renderInfo.metadata:
            controllerVariables = renderInfo.metadata.get('stateControllerVariables', [])
            if len(controllerVariables) > 0 and hasattr(self._object, 'SetControllerVariable'):
                for var, value in controllerVariables.iteritems():
                    self._object.SetControllerVariable(var, value)

            playCurveSets = renderInfo.metadata.get('playCurveSets', False)
            if playCurveSets:
                curveSets = self._object.Find('trinity.TriCurveSet')
                for curveSet in curveSets:
                    if not curveSet.isPlaying:
                        curveSet.Play()
                    curveSet.scaledTime = 0.0

            if hasattr(self._object, 'scaling') and self._initialScale:
                scaleFactor = renderInfo.metadata.get('scaleFactor', 1.0)
                if scaleFactor != 1.0:
                    self._object.scaling = (self._initialScale[0] * scaleFactor, self._initialScale[1] * scaleFactor, self._initialScale[2] * scaleFactor)
        soanimation.TriggerDefaultStates(self._object)

    @staticmethod
    def GetDefaultSunDirection(obj, view):
        from iconrendering2.metadata import DEFAULT_SUN_DIRECTION
        sunDirection = DEFAULT_SUN_DIRECTION
        if isinstance(obj, (trinity.EveStation2, trinity.EveMobile)):
            eyePos = (view.transform[0][3], view.transform[1][3], view.transform[2][3])
            lookAt = (view.transform[0][2], view.transform[1][2], view.transform[2][2])
            sunDirection = geo2.Vec3Normalize(geo2.Vec3Subtract(eyePos, lookAt))
        return sunDirection

    def _PrepareSceneForRender(self, renderInfo):
        view, projection = GetViewProjectionForObject(self._object, self._scene)
        sunDirection = None
        if renderInfo.metadata:
            viewMode = renderInfo.metadata.get('viewMode', IconViewMode.FREE)
            if viewMode == IconViewMode.FREE:
                sunDirection = renderInfo.metadata.get('sunDirection', None)
                if all((x in renderInfo.metadata for x in ['projection', 'view'])):
                    projData = renderInfo.metadata['projection']
                    projection.PerspectiveFov(projData['fov'], projData['aspectRatio'], projData['zn'], projData['zf'])
                    view.SetLookAtPosition(renderInfo.metadata['view']['eye'], renderInfo.metadata['view']['at'], renderInfo.metadata['view']['up'])
            else:
                angle = VIEW_MODE_CAMERA_ANGLES[viewMode]
                sunDirection = VIEW_MODE_SUN_DIRECTIONS[viewMode]
                boundingSphereRadius = self._object.GetBoundingSphereRadius()
                if self._object.mesh is not None:
                    geometry = self._object.mesh.geometry
                    boundingSphereCenter = self._object.GetBoundingSphereCenter()
                    view, projection = GetViewAndProjectionUsingMeshGeometry(geometry, scene=self._scene, boundingSphereRadius=boundingSphereRadius, boundingSphereCenter=boundingSphereCenter, cameraAngle=angle)
        if sunDirection is None:
            sunDirection = self.GetDefaultSunDirection(self._object, view)
        self._scene.sunDirection = sunDirection
        self._scene.backgroundRenderingEnabled = not renderInfo.backgroundTransparent
        return (view, projection)


def _CreateAlpha(rBmp, gBmp, bBmp):
    outputBmp = trinity.Tr2HostBitmap(rBmp.width, rBmp.height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
    rTriCol = trinity.TriColor()
    gTriCol = trinity.TriColor()
    bTriCol = trinity.TriColor()
    BLACKALPHA0 = 0
    HUERANGE = 60
    REDHUE = 0
    GREENHUE = 120
    BLUEHUE = 240
    for px in range(rBmp.width):
        for py in range(rBmp.height):
            rPixelValue = rBmp.GetPixel(px, py)
            gPixelValue = gBmp.GetPixel(px, py)
            bPixelValue = bBmp.GetPixel(px, py)
            rTriCol.FromInt(rPixelValue)
            gTriCol.FromInt(gPixelValue)
            bTriCol.FromInt(bPixelValue)
            rh, rs, rv = rTriCol.GetHSV()
            gh, gs, gv = gTriCol.GetHSV()
            bh, bs, bv = bTriCol.GetHSV()
            if (rTriCol.r, rTriCol.g, rTriCol.b) == (1.0, 0.0, 0.0) and (gTriCol.r, gTriCol.g, gTriCol.b) == (0.0, 1.0, 0.0) and (bTriCol.r, bTriCol.g, bTriCol.b) == (0.0, 0.0, 1.0):
                outputBmp.SetPixel(px, py, BLACKALPHA0)
            elif GREENHUE - HUERANGE < gh < GREENHUE + HUERANGE and (360 - HUERANGE < rh <= 360 or REDHUE <= rh < REDHUE + HUERANGE) and BLUEHUE - HUERANGE < bh < BLUEHUE + HUERANGE:
                if gv == 1.0 and bv == 1.0 and rv == 1.0:
                    gTriCol.SetRGB(gTriCol.r, rTriCol.g, gTriCol.b, 1.0)
                    ch, cs, cv = gTriCol.GetHSV()
                    gTriCol.a = cv
                    if cv != 0:
                        gTriCol.r = min(1.0, gTriCol.r * 1.0 / cv)
                        gTriCol.g = min(1.0, gTriCol.g * 1.0 / cv)
                        gTriCol.b = min(1.0, gTriCol.b * 1.0 / cv)
                    else:
                        gTriCol.r = 1.0
                        gTriCol.g = 1.0
                        gTriCol.b = 1.0
                    outputBmp.SetPixel(px, py, gTriCol.AsInt())
                else:
                    gTriCol.SetRGB(gTriCol.r, rTriCol.g, gTriCol.b, 1.0 - gv)
                    outputBmp.SetPixel(px, py, gTriCol.AsInt())
            else:
                gTriCol.a = 1.0
                outputBmp.SetPixel(px, py, gTriCol.AsInt())

    return outputBmp
