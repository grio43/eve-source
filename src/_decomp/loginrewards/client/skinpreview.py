#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\loginrewards\client\skinpreview.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from eve.client.script.ui.control.scenecontainer import SceneContainer, SceneContainerBaseNavigation
from eve.client.script.environment.sofService import GetSofService
import evegraphics.utils as gfxutils
import trinity
import uthread
import math
import evetypes

class ShipPreviewSceneContainer(SceneContainer):

    def LoadShipType(self, typeID, materialSetID = None):
        dna = gfxutils.BuildSOFDNAFromTypeID(typeID, materialSetID=materialSetID)
        spaceObjectFactory = GetSofService().spaceObjectFactory
        model = spaceObjectFactory.BuildFromDNA(dna)
        uthread.new(self.LoadShipModel, model)

    def LoadShipModel(self, model, animate = True):
        if self.destroyed:
            return
        with self._reloadLock:
            newModel = self.CreateShipModel(model)
            if not newModel:
                return
            newModel.FreezeHighDetailMesh()
            trinity.WaitForResourceLoads()
            self.ModifyCameraToFitShip(animate, newModel)
            self.AddToScene(newModel)
            self.AnimEntry()

    def ModifyCameraToFitShip(self, animate, shipModel):
        camera = self.camera
        rad = shipModel.GetBoundingSphereRadius()
        minZoom = rad + camera.nearClip
        alpha = camera.fov / 2.0
        maxZoom = min(self.backClip - rad, rad * (1 / math.tan(alpha)) * 2)
        oldZoomDistance = self.minZoom + (self.maxZoom - self.minZoom) * self.zoom
        defaultZoom = minZoom / (maxZoom - minZoom)
        self.SetMinMaxZoom(minZoom, maxZoom)
        if animate or oldZoomDistance < minZoom or oldZoomDistance > maxZoom:
            self.SetZoom(defaultZoom)

    def CreateShipModel(self, model):
        if not model:
            return
        if hasattr(model, 'ChainAnimationEx'):
            model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        model.display = 1
        model.name = 'ActiveShipModel'
        return model


class ShipsView(Container):

    def ApplyAttributes(self, attributes):
        super(ShipsView, self).ApplyAttributes(attributes)
        self.shipPreviewContainer = None
        self.cosmeticsSvc = sm.GetService('cosmeticsSvc')

    def GetShipTypeToShow(self, skinTypeID):
        skinMaterial = self.cosmeticsSvc.GetSkinByLicenseType(skinTypeID)
        return skinMaterial.types[0]

    def PreviewSkin(self, skinTypeID):
        if self.shipPreviewContainer and not self.shipPreviewContainer.destroyed:
            self.shipPreviewContainer.Close()
        self.shipPreviewContainer = ShipPreviewSceneContainer(align=uiconst.TOALL, parent=self, state=uiconst.UI_HIDDEN)
        self.shipPreviewContainer.PrepareSpaceScene()
        self.shipPreviewContainer.DisplaySpaceScene(blendMode=trinity.TR2_SBM_ADD)
        shipType = self.GetShipTypeToShow(skinTypeID)
        skinMaterial = self.cosmeticsSvc.GetSkinByLicenseType(skinTypeID)
        materialSetID = skinMaterial.materialSetID
        self.shipPreviewContainer.LoadShipType(shipType, materialSetID)
        self.sceneNavigation = SceneContainerBaseNavigation(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL)
        self.sceneNavigation.Startup(self.shipPreviewContainer)
        self.shipPreviewContainer.Show()


class SkinPreviewWindow(Window):
    __guid__ = 'skinpreview.SkinPreviewWindow'
    default_windowID = 'skinpreview.SkinPreviewWindow'
    default_minSize = (420, 320)

    def ApplyAttributes(self, attributes):
        super(SkinPreviewWindow, self).ApplyAttributes(attributes)
        Container(parent=self.sr.header, bgColor=(0.0, 0.0, 0.0, 1.0), align=uiconst.TOALL)
        intermediary = Container(parent=self.sr.main, align=uiconst.TOALL)
        self.preview = ShipsView(parent=intermediary, align=uiconst.TOALL)
        self.PreviewSkin(attributes.skinTypeID)

    def PreviewSkin(self, skinTypeID):
        self.SetCaption(evetypes.GetName(skinTypeID))
        self.preview.PreviewSkin(skinTypeID)
