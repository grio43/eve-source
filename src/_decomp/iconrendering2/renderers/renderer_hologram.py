#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_hologram.py
import blue
from renderer_spaceobject import SpaceObjectIconRenderer
from utils_scene import *
from iconrendering2.const import Language

class HologramIconRenderer(SpaceObjectIconRenderer):

    def __init__(self, sofFactory, dna, language = Language.ENGLISH):
        super(HologramIconRenderer, self).__init__(sofFactory, None, dna, language)

    def __str__(self):
        return 'Hologram Icon Renderer <%s>' % hex(id(self))

    def _PrepareRender(self):
        super(HologramIconRenderer, self)._PrepareRender()
        ApplyIsisEffect(self._object)

    def _PrepareSceneForRender(self, renderInfo):
        view = projection = None
        boundingSphereRadius = self._object.GetBoundingSphereRadius()
        angle = (-1.5708, 0, 0)
        if self._object.mesh is not None:
            geometry = self._object.mesh.geometry
            boundingSphereCenter = self._object.GetBoundingSphereCenter()
            view, projection = GetViewAndProjectionUsingMeshGeometry(geometry, scene=self._scene, boundingSphereRadius=boundingSphereRadius, boundingSphereCenter=boundingSphereCenter, cameraAngle=angle)
        return (view, projection)


def ApplyIsisEffect(ship):
    if not ship:
        return
    isSkinned = getattr(ship, 'isAnimated', False)

    def getIsisEffect():
        if isSkinned:
            isisEffect = blue.resMan.LoadObject('res:/dx9/model/ui/isisEffectSkinned.red')
        else:
            isisEffect = blue.resMan.LoadObject('res:/dx9/model/ui/isisEffect.red')
        blue.resMan.Wait()
        return isisEffect

    def getNormalMapPath(area):
        normalMapParam = [ res for res in area.effect.resources if res.name == 'NormalMap' or res.name == 'NoMap' ][0]
        if normalMapParam is None:
            return
        normalMapPath = normalMapParam.resourcePath
        return normalMapPath

    blue.resMan.Wait()
    areaCount = ship.mesh.geometry.GetMeshAreaCount(0)
    del ship.attachments[:]
    del ship.decals[:]
    del ship.effectChildren[:]
    sourceAreas = []
    for area in ship.mesh.opaqueAreas:
        sourceAreas.append(area)

    for area in ship.mesh.transparentAreas:
        sourceAreas.append(area)

    del ship.mesh.opaqueAreas[:]
    del ship.mesh.depthAreas[:]
    del ship.mesh.transparentAreas[:]
    del ship.mesh.additiveAreas[:]
    del ship.mesh.decalAreas[:]
    del ship.mesh.distortionAreas[:]
    depthArea = trinity.Tr2MeshArea()
    depthArea.count = areaCount
    depthArea.effect = trinity.Tr2Effect()
    paintMaskMap = trinity.TriTextureParameter()
    paintMaskMap.name = 'PaintMaskMap'
    paintMaskMap.resourcePath = 'res:/texture/global/black.dds'
    depthArea.effect.resources.append(paintMaskMap)
    if isSkinned:
        depthArea.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpaceObject/V5/Skinned_DepthOnlyV5.fx'
    else:
        depthArea.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpaceObject/V5/DepthOnlyV5.fx'
    ship.mesh.depthAreas.append(depthArea)
    for sourceArea in sourceAreas:
        normalMapPath = getNormalMapPath(sourceArea)
        if normalMapPath is None:
            continue
        area = trinity.Tr2MeshArea()
        area.index = sourceArea.index
        area.count = sourceArea.count
        area.effect = getIsisEffect()
        normalMap = [ res for res in area.effect.resources if res.name == 'NormalMap' or res.name == 'NoMap' ][0]
        normalMap.resourcePath = normalMapPath
        ship.mesh.additiveAreas.append(area)
