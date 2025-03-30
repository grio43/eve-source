#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\structure\components\previewScene.py
import trinity
import uthread
from carbonui.primitives.container import Container
from carbonui import const as uiconst
from cosmetics.common.structures.const import StructurePaintSlot
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.ui.control.scenecontainer import SceneContainer, SceneContainerBaseNavigation
from eve.client.script.environment.spaceObject.spaceObject import modify_dna
from eve.client.script.ui.cosmetics.structure import paintToolSelections
from evegraphics import utils as gfxutils
from paints.data import dataLoader as paintsDataLoader
import evetypes
from fsdBuiltData.common.graphicIDs import GetAnimationStateObjects
from eve.client.script.environment.spaceObject.structure import STATE_VULNERABLE_ACTIVE
TRANSITION_ZOOM_DEFAULT = 0.3
MINIMUM_ZOOM_DISTANCE_DEFAULT = 5000
ZOOM_RANGE = [1.6, 10.0]

class PreviewPanel(Container):

    def __init__(self, **kw):
        super(PreviewPanel, self).__init__(**kw)
        self._construct_layout()
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.connect(self._on_structure_selection_changed)
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.connect(self._on_structure_selection_changed)
        self._on_structure_selection_changed(paintToolSelections.SELECTED_STRUCTURE_TYPE.get())

    def Close(self):
        super(PreviewPanel, self).Close()
        paintToolSelections.SELECTED_STRUCTURE_TYPE.on_change.disconnect(self._on_structure_selection_changed)

    def _construct_layout(self):
        self.preview_container = Container(name='preview_container', parent=self, align=uiconst.TOALL)
        self._live_preview = PaintPreviewSceneContainer(name='preview_scene', parent=self.preview_container, align=uiconst.TOALL)
        self.sceneNavigation = SceneContainerBaseNavigation(name='preview_navigation', parent=self.preview_container, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL, pickRadius=0)
        self.sceneNavigation.Startup(self._live_preview)

    def _on_structure_selection_changed(self, type_id):
        self.update(type_id)

    def update(self, type_id, fit_in_view = True):
        base_dna = gfxutils.BuildSOFDNAFromTypeID(type_id)
        model_dna = modify_dna(base_dna=base_dna, mat1=self._get_material_for_slot(StructurePaintSlot.PRIMARY), mat2=self._get_material_for_slot(StructurePaintSlot.SECONDARY), mat3=self._get_material_for_slot(StructurePaintSlot.DETAILING), isStructure=True)
        self._live_preview.preview_type(type_id, model_dna, fit_to_view=fit_in_view)

    def _get_material_for_slot(self, slot_id):
        paint_id = paintToolSelections.SELECTED_PAINTWORK.get_slot(slot_id)
        if paint_id is None:
            return
        return paintsDataLoader.get_paint_material_name(paint_id)


class PaintPreviewSceneContainer(SceneContainer):
    _model_dna = None
    _type_id = None
    _fit_to_view = True

    def __init__(self, **kwargs):
        super(PaintPreviewSceneContainer, self).__init__(**kwargs)
        self.PrepareSpaceScene(scenePath='res:/dx9/scene/universe/c05_cube.red')
        self.fadeObject = None
        if hasattr(self.camera, 'SetAdvancedInspectionMode'):
            self.camera.SetAdvancedInspectionMode(True)

    def PrepareSpaceScene(self, scenePath = None):
        if scenePath is None:
            scenePath = 'res:/dx9/scene/wormholes/wormhole_class_01.red'
        super(PaintPreviewSceneContainer, self).PrepareSpaceScene(scenePath=scenePath)
        if not self.scene.postprocess:
            self.scene.postprocess = trinity.Tr2PostProcess2()
        self.scene.sunDirection = (0.6198, -0.1016, -0.7781)
        self.scene.nebulaIntensity = 1.25
        self.scene.reflectionIntensity = 1.55
        self.scene.sunDiffuseColor = (1.0,
         205.0 / 255.0,
         170.0 / 255.0,
         1.0)
        self.scene.postprocess.taa = None

    def preview_type(self, type_id, model_dna, fit_to_view = True):
        self._type_id = type_id
        self._model_dna = model_dna
        self._fit_to_view = fit_to_view
        uthread.new(self._reload_model)

    def _reload_model(self):
        if self.destroyed:
            return
        with self._reloadLock:
            if self.fadeObject is None:
                self.fadeObject = sm.GetService('sceneManager').GetFadeObject(scene=self.scene, create=True)
            space_object_factory = GetSofService().spaceObjectFactory
            self.model = space_object_factory.BuildFromDNA(self._model_dna)
            typeID = paintToolSelections.SELECTED_STRUCTURE_TYPE.get()
            graphicsID = evetypes.GetGraphicID(typeID)
            state_objects = GetAnimationStateObjects(graphicsID)
            dnaToLoad = state_objects[STATE_VULNERABLE_ACTIVE]
            self.stateObject = space_object_factory.BuildFromDNA(dnaToLoad)
            if self.stateObject is not None:
                self.stateObject.SetControllerVariable('BuildDuration', 0)
                self.stateObject.SetControllerVariable('BuildElapsedTime', 0)
                self.stateObject.SetControllerVariable('IsBuilt', 1)
            if self.model is not None:
                self.model.SetControllerVariable('BuildDuration', 0)
                self.model.SetControllerVariable('BuildElapsedTime', 0)
                self.model.SetControllerVariable('IsBuilt', 1)
                self.model.SetControllerVariable('ActivationState', 2)
                self.model.StartControllers()
            while len(self.model.observers) > 0:
                self.model.observers.pop()

            self.model.FreezeHighDetailMesh()
            trinity.WaitForResourceLoads()
            self.ClearScene()
            if self._fit_to_view:
                self._fit_model_in_view(self.model)
            if self.scene:
                self.AddToScene(self.model)
                self.AddToScene(self.stateObject, clear=0)
            self.stateObject.rotationCurve = self.model.rotationCurve
            self.stateObject.StartControllers()

    def _fit_model_in_view(self, model):
        if model is None:
            return
        if hasattr(model, 'GetBoundingSphereCenter'):
            rad = model.GetBoundingSphereRadius()
        else:
            rad = MINIMUM_ZOOM_DISTANCE_DEFAULT
        maxRenderDist = self.camera.farClip or 400000.0
        min_zoom = ZOOM_RANGE[0] * rad
        max_zoom = min(ZOOM_RANGE[1] * rad, maxRenderDist - 2 * rad)
        self.SetMinMaxZoom(min_zoom, max_zoom)
        self.SetZoom(TRANSITION_ZOOM_DEFAULT)
        if hasattr(self.camera, 'SetInnerBoundRadius') and self.model.shapeEllipsoidRadius is not None:
            self.camera.SetInnerBoundRadius(self.model.shapeEllipsoidRadius)
            if hasattr(self.camera, 'SetModelCenter'):
                self.camera.SetModelCenter(self.model.shapeEllipsoidCenter)

    def OrbitParent(self, dx, dy):
        self.StopAnimations()
        fov = self.camera.fov
        cameraSpeed = 0.02
        self.camera.Orbit(dx * fov * cameraSpeed, dy * fov * cameraSpeed)
