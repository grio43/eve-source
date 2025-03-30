#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetUISvc.py
import math
import blue
import carbonui.const as uiconst
import evecamera
import evegraphics.settings as gfxsettings
import evetypes
import inventorycommon.typeHelpers
import localization
import log
import trinity
import uthread
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING, SERVICE_START_PENDING
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.environment.spaceObject.planet import Planet
from eve.client.script.ui.shared.dockedUI.lobbyWnd import LobbyWnd
from eve.client.script.ui.shared.planet.pinContainers.LinkContainer import LinkContainer
from eve.client.script.ui.shared.planet.pinContainers.containersByPinType import containerClsByPinType
from eve.client.script.ui.shared.planet.planetConst import SCALE_OTHERLINKS, SCALE_RUBBERLINK, SCALE_EXTRACTORLINKS, SCALE_LINKS
from eve.common.lib.PlanetResources import builder
from eve.common.script.planet.planetUtil import MATH_2PI
from eveexceptions import UserError
from localization import GetByLabel
from carbonui.control.window import Window
from eve.client.script.ui.shared.planet.curveLineDrawer import CurveLineDrawer
from eve.client.script.ui.shared.planet.eventManager import EventManager
from eve.client.script.ui.shared.planet.myPinManager import MyPinManager
from eve.client.script.ui.shared.planet.otherPinManager import OtherPinManager
from eve.client.script.ui.shared.planet.planetCommon import PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT
from eve.client.script.ui.shared.planet.planetCommon import PLANET_TEXTURE_SIZE, PLANET_SCALE
from eve.client.script.ui.shared.planet.importExportUI import PlanetaryImportExportUI
from eve.client.script.ui.shared.planet.orbitalMaterialUI import OrbitalMaterialUI
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow
from eve.client.script.ui.inflight.orbitalConfiguration import OrbitalConfigurationWindow
from eve.common.lib import appConst as const
SQRT_NUM_SAMPLES = 80
LINER_BLENDING_RATIO = 0.8
RESOURCE_BASE_COLOR = (1, 1, 1, 0.175)

class ResourceRenderAbortedError(Exception):
    pass


class PlanetUISvc(Service):
    __guid__ = 'svc.planetUI'
    __notifyevents__ = ['OnGraphicSettingsChanged',
     'OnUIRefresh',
     'ProcessUIRefresh',
     'OnPILaunchesChange']
    __exportedcalls__ = {}
    __servicename__ = 'planetUI'
    __displayname__ = 'Planet UI Client Service'
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        self.state = SERVICE_START_PENDING
        self.LogInfo('Starting Planet UI Client Svc')
        uicore.layer.planet.Flush()
        self.planetID = None
        self.oldPlanetID = None
        self.format = trinity.PIXEL_FORMAT.B8G8R8A8_UNORM
        self.busy = 0
        self.isLoadingResource = False
        self.selectedResourceTypeID = None
        self.minimizedWindows = []
        self.planetAccessRequired = None
        self.currSphericalHarmonic = None
        self.spherePinsPendingLoad = []
        self.spherePinLoadThread = None
        self.inEditMode = False
        self.launchsRowSet = None
        self.planetDimensions = 1000
        self.planet = None
        self.curveLineDrawer = CurveLineDrawer()
        self.myPinManager = None
        self.otherPinManager = None
        self.eventManager = None
        self.planetRoot = None
        self.trinityPlanet = None
        self.planetTransform = None
        self.resourceLayer = None
        self.pinTransform = None
        self.pinOthersTransform = None
        self.orbitalObjectTransform = None
        self.modeController = None
        self.scanController = None
        self.currentContainer = None
        self.planetNav = None
        self.planetUIContainer = Container(parent=uicore.layer.planet, name='planetUIContainer', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.state = SERVICE_RUNNING
        self.LogInfo('Planet UI Client Svc Started')

    def Stop(self, memStream = None):
        if trinity.device is None:
            return
        self.LogInfo('service is stopping')
        if self.spherePinLoadThread:
            self.spherePinLoadThread.kill()
            self.spherePinLoadThread = None
        self.Reset()

    def Reset(self):
        self.LogInfo('PlanetUISvc Reset')
        self.minimizedWindows = []
        self.CleanScene()
        sm.ScatterEvent('OnPlanetUIReset')

    def CleanScene(self):
        self.LogInfo('CleanScene')
        self.CloseCurrentlyOpenPinContainer()
        self.planetUIContainer.Flush()
        if self.planetTransform is not None:
            del self.planetTransform.children[:]
        if self.planetRoot is not None:
            del self.planetRoot.children[:]
        self.planetTransform = None
        self.pinTransform = None
        self.pinOthersTransform = None
        if self.trinityPlanet is not None:
            self.trinityPlanet.model = None
            self.trinityPlanet = None
        self.planetRoot = None
        self.planetNav = None
        if self.scanController is not None:
            self.scanController.Close()
            self.scanController = None
        self.resourceLayer = None
        self.isLoadingResource = False

    def RevertChanges(self):
        self.planet.RevertChanges()
        self.eventManager.SetStateNormal()

    def CleanView(self):
        if self.planetTransform is not None:
            self.planetTransform.children.remove(self.pinTransform)
            self.planetTransform.children.remove(self.pinOthersTransform)
        if self.eventManager:
            self.eventManager.OnPlanetViewClosed()
        if self.myPinManager:
            self.myPinManager.OnPlanetViewClosed()
        if self.otherPinManager:
            self.otherPinManager.OnPlanetViewClosed()
        self.eventManager.DeselectCurrentlySelected()
        self.planetUIContainer.Flush()
        self.busy = 0
        self.StopSpherePinLoadThread()
        del self.pinTransform
        self.pinTransform = None
        del self.pinOthersTransform
        self.pinOthersTransform = None
        if self.scanController is not None:
            self.scanController.Close()
            self.scanController = None
        self.resourceLayer = None

    def ProcessUIRefresh(self):
        self.oldPlanetID = None
        if sm.GetService('viewState').IsViewActive('planet'):
            self.oldPlanetID = self.planetID
            self.planetID = None
        self.Reset()

    def GetLaunches(self, force = 0):
        if self.launchsRowSet is None or force:
            self.launchsRowSet = sm.RemoteSvc('planetMgr').GetMyLaunchesDetails()
        return self.launchsRowSet

    def OnPILaunchesChange(self, *args):
        self.launchsRowSet = None
        sm.GetService('neocom').Blink('planets', GetByLabel('UI/Neocom/Blink/PlanetaryLaunch'))

    def OnUIRefresh(self):
        if self.oldPlanetID:
            self.Open(self.oldPlanetID)
            self.oldPlanetID = None

    def MinimizeWindows(self):
        lobby = LobbyWnd.GetIfOpen()
        if lobby and not lobby.destroyed and lobby.state != uiconst.UI_HIDDEN and not lobby.IsMinimized() and not lobby.IsCollapsed():
            lobby.Minimize()
            self.minimizedWindows.append(LobbyWnd.default_windowID)

    def Open(self, planetID):
        sm.GetService('viewState').ActivateView('planet', planetID=planetID)

    def ExitView(self):
        sm.GetService('viewState').CloseSecondaryView('planet')

    def _Open(self, planetID):
        mapSvc = sm.GetService('map')
        planetData = mapSvc.GetPlanetInfo(planetID)
        planetChanged = planetID != self.planetID
        oldPlanetID = self.planetID
        self.planetID = planetID
        self.typeID = planetData.typeID
        self.solarSystemID = planetData.solarSystemID
        try:
            self.InitUI(planetChanged)
        except:
            self.Stop()
            self.Run()
            raise

        sm.GetService('audio').SendUIEvent('msg_pi_general_opening_play')
        sm.ScatterEvent('OnPlanetViewChanged', planetID, oldPlanetID)
        self.planetAccessRequired = session.solarsystemid2 == self.solarSystemID or sm.GetService('planetSvc').IsPlanetColonizedByMe(planetID)

    def Close(self, clearAll = True):
        if getattr(self, 'busy', 0):
            return True
        self.busy = 1
        if len(self.minimizedWindows) > 0:
            for windowID in self.minimizedWindows:
                wnd = Window.GetIfOpen(windowID=windowID)
                if wnd and wnd.IsMinimized():
                    wnd.Maximize()

            self.minimizedWindows = []
        sm.GetService('sceneManager').SetRegisteredScenes('default')
        self.busy = 0
        if self.eventManager:
            self.eventManager.OnPlanetViewClosed()
        if self.myPinManager:
            self.myPinManager.OnPlanetViewClosed()
        if self.otherPinManager:
            self.otherPinManager.OnPlanetViewClosed()
        self.CleanScene()
        self.StopSpherePinLoadThread()
        sm.ScatterEvent('OnPlanetViewChanged', None, self.planetID)
        if self.planetAccessRequired is not None:
            self.planetAccessRequired = None
        self.planetID = None
        self.planet = None
        self.selectedResourceTypeID = None
        sm.GetService('audio').SendUIEvent('msg_pi_general_closing_play')
        if clearAll:
            self.cameraScene = None
            self.planetScene = None
            sm.GetService('sceneManager').UnregisterScene('planet')
        return True

    def InitUI(self, planetChanged):
        self.LogInfo('Initializing UI')
        self.StartLoadingBar('planet_ui_init', localization.GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), localization.GetByLabel('UI/PI/Common/LoadingPlanetResources'), 5)
        try:
            sm.GetService('planetSvc').GetPlanet(self.planetID)
        except UserError:
            self.StopLoadingBar('planet_ui_init')
            raise
        except Exception:
            eve.Message('PlanetLoadingFailed', {'planet': (const.UE_LOCID, self.planetID)})
            self.StopLoadingBar('planet_ui_init')
            log.LogException()
            return

        if not sm.GetService('viewState').IsViewActive('planet'):
            self.MinimizeWindows()
        newScene = False
        if self.planetRoot is None or planetChanged:
            self.CreateScene()
            newScene = True
        self.UpdateLoadingBar('planet_ui_init', localization.GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), localization.GetByLabel('UI/PI/Common/LoadingPlanetResources'), 1, 4)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.SetRegisteredScenes('planet')
        sm.GetService('sceneManager').SetSecondaryCamera(evecamera.CAM_PLANET)
        self.UpdateLoadingBar('planet_ui_init', localization.GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), localization.GetByLabel('UI/PI/Common/LoadingPlanetResources'), 2, 4)
        self.SetPlanet()
        self.UpdateLoadingBar('planet_ui_init', localization.GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), localization.GetByLabel('UI/PI/Common/LoadingPlanetResources'), 3, 4)
        self.LoadPI(newScene)
        self.UpdateLoadingBar('planet_ui_init', localization.GetByLabel('UI/InfoWindow/TabNames/PlanetaryProduction'), localization.GetByLabel('UI/PI/Common/LoadingPlanetResources'), 4, 4)
        self.StopLoadingBar('planet_ui_init')

    def LoadPI(self, newScene = True):
        self.InitTrinityTransforms()
        self.InitUIContainers()
        self.InitLinesets()
        if self.myPinManager:
            self.myPinManager.Close()
        self.myPinManager = MyPinManager()
        if self.otherPinManager:
            self.otherPinManager.Close()
        self.otherPinManager = OtherPinManager()
        if self.eventManager:
            self.eventManager.Close()
        self.eventManager = EventManager()
        self.planetNav.Startup()
        self.eventManager.OnPlanetViewOpened()
        self.myPinManager.OnPlanetViewOpened()
        self.otherPinManager.OnPlanetViewOpened()

    def SetModeController(self, modeController):
        self.modeController = modeController

    def InitUIContainers(self):
        self.pinInfoParent = Container(parent=self.planetUIContainer, name='pinInfoParent', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.planetNav = sm.GetService('viewState').GetView('planet').layer

    def InitTrinityTransforms(self):
        self.pinTransform = trinity.EveTransform()
        self.pinTransform.name = 'myPins'
        self.pinOthersTransform = trinity.EveTransform()
        self.pinOthersTransform.name = 'othersPins'
        self.planetTransform.children.append(self.pinTransform)
        self.planetTransform.children.append(self.pinOthersTransform)

    def InitLinesets(self):
        self.curveLineDrawer.CreateLineSet('links', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=SCALE_LINKS)
        self.curveLineDrawer.CreateLineSet('linksExtraction', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=SCALE_EXTRACTORLINKS)
        self.curveLineDrawer.CreateLineSet('rubberLink', self.pinTransform, 'res:/UI/Texture/Planet/link.dds', scale=SCALE_RUBBERLINK)
        self.curveLineDrawer.CreateLineSet('otherLinks', self.pinOthersTransform, 'res:/UI/Texture/Planet/link.dds', scale=SCALE_OTHERLINKS)

    def CreateRenderTarget(self):
        textureQuality = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        self.maxSizeLimit = size = PLANET_TEXTURE_SIZE >> textureQuality
        rt = None
        while rt is None or not rt.isValid:
            rt = trinity.Tr2RenderTarget(2 * size, size, 0, self.format)
            if not rt.isValid:
                if size < 2:
                    return
                self.maxSizeLimit = size = size / 2
                rt = None

        self.LogInfo('CreateRenderTarget textureQuality', textureQuality, 'size', size, 'maxSizeLimit', self.maxSizeLimit)
        return rt

    def CreateScene(self):
        self.LogInfo('CreateScene')
        self.planetScene = self.GetPlanetScene()
        self.planetScene.sunDirection = (0.0, 0.0, 1.0)
        self.planetScene.sunDiffuseColor = (1.0, 1.0, 1.0, 1.0)
        self.planetScene.planetScale = self.planetDimensions
        self.planetScene.planetCameraScale = self.planetDimensions
        self.planetRoot = trinity.EveRootTransform()
        self.planetRoot.name = 'planetRoot'
        self.planetScene.objects.append(self.planetRoot)
        self.LoadPlanet()
        sm.GetService('sceneManager').RegisterScene(self.planetScene, 'planet')

    def GetScene(self):
        _, regionID, constellationID, solarSystemID, _ = sm.GetService('map').GetParentLocationID(self.solarSystemID)
        scene = sm.GetService('sceneManager').GetScene(location=(solarSystemID, constellationID, regionID))
        return scene

    def GetPlanetScene(self):
        scenepath = self.GetScene()
        scene = trinity.Load(scenepath)
        scene.backgroundRenderingEnabled = True
        return scene

    def LoadPlanet(self):
        self.LogInfo('LoadPlanet planet', self.planetID, 'type', self.typeID, 'system', self.solarSystemID)
        planet = Planet()
        graphicFile = inventorycommon.typeHelpers.GetGraphicFile(self.typeID)
        planet.typeData['graphicFile'] = graphicFile
        planet.typeID = self.typeID
        planet.LoadPlanet(self.planetID, forPhotoService=True, rotate=False, hiTextures=True, notifyLoaded=False)
        self.trinityPlanet = planet
        if planet.model is None:
            return
        planet.name = 'planet'
        planet.model.scaling = tuple([self.planetDimensions] * 3)
        planet.model.radius = self.planetDimensions
        planet.model.translationCurve = None
        planet.model.rotationCurve = None
        planet.model.zOnlyModel = trinity.Load('res:/dx9/model/worldobject/planet/planetzonly.red').effectChildren[0]
        planet.model.zOnlyModel.scaling = (0.99, 0.99, 0.99)
        planetTransform = trinity.EveTransform()
        planetTransform.name = 'planet'
        planetTransform.scaling = (PLANET_SCALE, PLANET_SCALE, PLANET_SCALE)
        self.planetTransform = planetTransform
        self.planetRoot.children.append(self.planetTransform)
        self.planetScene.planets.append(planet.model)
        trinity.WaitForResourceLoads()
        self.evePlanet = planet.model

    def GetCurrentPlanet(self):
        if not self.planetID:
            return None
        return sm.GetService('planetSvc').GetPlanet(self.planetID)

    def StartLoadingBar(self, key, tile, action, total):
        if getattr(self, 'loadingBarActive', None) is None:
            sm.GetService('loading').ProgressWnd(tile, action, 0, total)
            self.loadingBarActive = key

    def UpdateLoadingBar(self, key, tile, action, part, total):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').ProgressWnd(tile, action, part, total)

    def StopLoadingBar(self, key):
        if getattr(self, 'loadingBarActive', None) == key:
            sm.GetService('loading').StopCycle()
            self.loadingBarActive = None

    def OnGraphicSettingsChanged(self, changes):
        changed = gfxsettings.GFX_TEXTURE_QUALITY in changes or gfxsettings.GFX_SHADER_QUALITY in changes
        if sm.GetService('viewState').IsViewActive('planet') and self.trinityPlanet is not None and changed:
            if self.selectedResourceTypeID is not None:
                self.ShowResource(self.selectedResourceTypeID)

    def ShowResource(self, resourceTypeID):
        self.LogInfo('ShowResource', resourceTypeID)
        oldResourceTypeID = self.selectedResourceTypeID
        self.selectedResourceTypeID = resourceTypeID
        if resourceTypeID is None:
            if self.resourceLayer is not None:
                self.resourceLayer.display = False
            self.otherPinManager.HideOtherPlayersExtractors()
            if self.IsModeControllerPresent():
                self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
        elif not getattr(self, 'isLoadingResource', False):
            if self.IsModeControllerPresent():
                self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
            self.isLoadingResource = True
            uthread.new(self._ShowResource, resourceTypeID)
            self.modeController.resourceControllerTab.ResourceSelected(resourceTypeID)
        elif oldResourceTypeID != resourceTypeID:
            while self.isLoadingResource:
                blue.pyos.synchro.SleepWallclock(50)

            if resourceTypeID == self.selectedResourceTypeID:
                self.ShowResource(resourceTypeID)

    def _ShowResource(self, resourceTypeID):
        self.LogInfo('_ShowResource', resourceTypeID)
        inRange = False
        try:
            inRange, texture = self.GetResourceAndRender(resourceTypeID)
            if self.planetTransform is not None:
                self.EnableResourceLayer()
                self.SetResourceTexture(texture)
        except ResourceRenderAbortedError:
            pass
        finally:
            self.isLoadingResource = False
            if self.IsModeControllerPresent():
                self.modeController.resourceControllerTab.StopLoadingResources(resourceTypeID)
            if self.otherPinManager is not None and inRange:
                self.otherPinManager.RenderOtherPlayersExtractors(resourceTypeID)

    def IsModeControllerPresent(self):
        return self.modeController is not None and hasattr(self.modeController, 'resourceControllerTab') and self.modeController.resourceControllerTab is not None

    def IsColonyPresent(self):
        if not self.planet:
            return False
        return session.charid in self.planet.colonies

    def EnableResourceLayer(self):
        if self.planetTransform is not None:
            if self.resourceLayer is None:
                self.LogInfo('_ShowResource no resourceLayer found. Loading resource layer')
                self.resourceLayer = trinity.Load('res:/dx9/model/worldobject/planet/uiplanet.red')
                trinity.WaitForResourceLoads()
                effect = self.resourceLayer.mesh.transparentAreas[0].effect
                for resource in effect.resources:
                    if resource.name == 'ColorRampMap':
                        resource.resourcePath = 'res:/dx9/model/worldobject/planet/resource_colorramp.dds'

                for param in effect.parameters:
                    if param.name == 'MainColor':
                        param.value = RESOURCE_BASE_COLOR
                    elif param.name == 'ResourceTextureInfo':
                        param.value = (PLANET_RESOURCE_TEX_WIDTH,
                         PLANET_RESOURCE_TEX_HEIGHT,
                         0,
                         0)

                offset = trinity.Tr2FloatParameter()
                offset.name = 'HeatOffset'
                offset.value = 0.0
                effect.parameters.append(offset)
                stretch = trinity.Tr2FloatParameter()
                stretch.name = 'HeatStretch'
                stretch.value = 1.0
                effect.parameters.append(stretch)
                self.planetTransform.children.append(self.resourceLayer)
            else:
                self.resourceLayer.display = True
            low, hi = self.GetResourceDisplayRange()
            self.SetResourceDisplayRange(low, hi)

    def GetResourceTexture(self):
        effect = self.resourceLayer.mesh.transparentAreas[0].effect
        for resource in effect.resources:
            if resource.name == 'ResourceDistMap':
                return resource

    def GetResourceAndRender(self, resourceTypeID):
        self.LogInfo('GetResourceAndRender resourceTypeID', resourceTypeID)
        planet = sm.GetService('planetSvc').GetPlanet(self.planetID)
        inRange, sh = planet.GetResourceData(resourceTypeID)
        self.currSphericalHarmonic = sh
        sh = builder.CopySH(sh)
        builder.ScaleSH(sh, 1.0 / const.planetResourceMaxValue)
        bmp = self.ChartResourceLayer(sh)
        texture = trinity.TriTextureRes()
        texture.CreateFromHostBitmap(bmp)
        return (inRange, texture)

    def GetCurrentResourceValueAt(self, phi, theta):
        if not self.currSphericalHarmonic:
            return None
        return builder.GetValueAt(self.currSphericalHarmonic, phi, theta)

    def GenerateSamplePoints(self, sqrtNumSamples):
        self.LogInfo('GenerateSamplePoints creating', sqrtNumSamples ** 2, 'samples for chart generation')
        thetaSamples = []
        phiSamples = []
        scale = 1.0 / (sqrtNumSamples - 1)
        for b in xrange(sqrtNumSamples):
            theta = math.pi * b * scale
            thetaSamples.append(theta)

        for a in xrange(sqrtNumSamples):
            phi = MATH_2PI * a * scale
            phiSamples.append(phi)

        return (thetaSamples, phiSamples)

    def ChartResourceLayer(self, resSH):
        if not hasattr(self, 'thetaSamples'):
            self.thetaSamples, self.phiSamples = self.GenerateSamplePoints(SQRT_NUM_SAMPLES)
        data = []
        for t in self.thetaSamples:
            for p in self.phiSamples:
                value = builder.GetValueAt(resSH, p, t)
                data.append(value)

        maxValue = max(data)
        minValue = min(data)
        d = maxValue - minValue
        maxIntensity = min(max(maxValue, 0.0), 255.0) / 255.0
        if d == 0.0:
            d = 1.0
        data = map(lambda x: maxIntensity * (x - minValue) / d, data)
        bmp = trinity.Tr2HostBitmap(PLANET_RESOURCE_TEX_WIDTH, PLANET_RESOURCE_TEX_HEIGHT, 1, trinity.PIXEL_FORMAT.A8_UNORM)
        bmp.CreateFromHeightData(data, len(self.phiSamples), len(self.thetaSamples))
        return bmp

    def SetResourceTexture(self, texture):
        effect = self.resourceLayer.mesh.transparentAreas[0].effect
        for resource in effect.resources:
            if resource.name == 'ResourceDistMap':
                resource.SetResource(texture)

    def GetResourceDisplayRange(self):
        defaultResourceDisplayRange = settings.char.ui.Get('planet_resource_display_range', (0.0, 0.5))
        return settings.char.ui.Get('planet_resource_display_range_{}'.format(self.planetID), defaultResourceDisplayRange)

    def SetResourceDisplayRange(self, low, hi):
        settings.char.ui.Set('planet_resource_display_range', (low, hi))
        settings.char.ui.Set('planet_resource_display_range_{}'.format(self.planetID), (low, hi))
        stretch = 1.0 / (hi - low)
        offset = -low * stretch
        if self.planetTransform is not None:
            if self.resourceLayer is not None:
                effect = self.resourceLayer.mesh.transparentAreas[0].effect
                for param in effect.parameters:
                    if param.name == 'HeatStretch':
                        param.value = stretch
                    elif param.name == 'HeatOffset':
                        param.value = offset

    def OpenPlanetCustomsOfficeImportWindow(self, customsOfficeID, spaceportPinID = None):
        wnd = PlanetaryImportExportUI.GetIfOpen()
        if wnd:
            if wnd.customsOfficeID != customsOfficeID or wnd.spaceportPinID != spaceportPinID:
                wnd.CloseByUser()
                wnd = None
            else:
                wnd.Maximize()
        if not wnd:
            PlanetaryImportExportUI.Open(customsOfficeID=customsOfficeID, spaceportPinID=spaceportPinID)

    def OpenUpgradeWindow(self, orbitalID):
        wnd = OrbitalMaterialUI.GetIfOpen()
        if wnd:
            if wnd.orbitalID != orbitalID:
                wnd.CloseByUser()
                wnd = None
            else:
                wnd.Maximize()
        if not wnd:
            OrbitalMaterialUI.Open(orbitalID=orbitalID)

    def OpenConfigureWindow(self, orbitalItem):
        wnd = OrbitalConfigurationWindow.GetIfOpen()
        if wnd:
            if getattr(wnd, 'orbitalID', None) != orbitalItem.itemID:
                wnd.CloseByUser()
                wnd = None
            else:
                wnd.Maximize()
        if not wnd:
            if getattr(orbitalItem, 'locationID', None) is None:
                orbitalItem.locationID = session.solarsystemid
            OrbitalConfigurationWindow.Open(orbitalItem=orbitalItem)

    def GetSurveyWindow(self, ecuPinID):
        wnd = SurveyWindow.Open(ecuPinID=ecuPinID)
        if wnd.ecuPinID != ecuPinID:
            self.CloseSurveyWindow()
            self.myPinManager.EnterSurveyMode(ecuPinID)
        else:
            self.EnterSurveyMode(ecuPinID)
        return SurveyWindow.GetIfOpen()

    def EnterSurveyMode(self, ecuPinID):
        if self.IsModeControllerPresent():
            self.modeController.resourceControllerTab.EnterSurveyMode()

    def ExitSurveyMode(self):
        if self.IsModeControllerPresent():
            self.modeController.resourceControllerTab.ExitSurveyMode()
        self.myPinManager.LockHeads()

    def CloseSurveyWindow(self):
        SurveyWindow.CloseIfOpen()

    def GMShowResource(self, resourceTypeID, layer):
        self.LogInfo('GMShowResource', resourceTypeID, layer)
        planet = sm.GetService('planetSvc').GetPlanet(self.planetID)
        data = planet.remoteHandler.GMGetCompleteResource(resourceTypeID, layer)
        sh = builder.CreateSHFromBuffer(data.data, data.numBands)
        self.ShowSH(sh, scaleIt=layer == 'base')

    def ShowSH(self, sh, scaleIt = True):
        if scaleIt:
            builder.ScaleSH(sh, 1.0 / const.planetResourceMaxValue)
        bmp = self.ChartResourceLayer(sh)
        texture = trinity.TriTextureRes()
        texture.CreateFromHostBitmap(bmp)
        if self.planetTransform is not None:
            self.EnableResourceLayer()
            self.SetResourceTexture(texture)

    def GMCreateNuggetLayer(self, typeID):
        self.planet.remoteHandler.GMCreateNuggetLayer(self.planetID, typeID)
        self.GMShowResource(typeID, 'nuggets')

    def SetPlanet(self, planetID = None):
        pID = planetID
        if pID is None:
            pID = self.planetID
        self.planet = sm.GetService('planetSvc').GetPlanet(pID)
        self.planet.StartTicking()

    def OpenContainer(self, pin, panelID = None):
        containerCls = self._GetPinContainerClass(pin.typeID)
        self.currentContainer = containerCls(pin=pin, panelID=panelID)

    def _GetPinContainerClass(self, typeID):
        groupID = evetypes.GetGroupID(typeID)
        containerCls = containerClsByPinType[groupID]
        return containerCls

    def GetCurrContainerPanelID(self):
        if not self.currentContainer:
            return
        return self.currentContainer.GetPanelID()

    def OpenContainerLink(self, link, panelID = None):
        self.currentContainer = LinkContainer(pin=link, panelID=panelID)

    def CloseCurrentlyOpenPinContainer(self):
        if not self.currentContainer:
            return
        panelID = self.GetCurrContainerPanelID()
        self.currentContainer.updateInfoContTimer.KillTimer()
        self.currentContainer.Close()
        self.currentContainer = None
        return panelID

    def CloseCurrentlyOpenPinContainerIfOpen(self, pinID):
        if self.currentContainer and self.currentContainer.GetID() == pinID:
            self.CloseCurrentlyOpenPinContainer()

    def FocusCameraOnCommandCenter(self):
        self.planetNav.OrbitToCommandCenter()

    def OnPlanetZoomChanged(self, zoom):
        self.curveLineDrawer.ChangeLineSetWidth('links', 1.1 - zoom)

    def VerifySimulation(self):
        self.planet.GMVerifySimulation()

    def GetLocalDistributionReport(self, surfacePoint):
        report = self.planet.GetLocalDistributionReport(surfacePoint)
        reportRows = []
        for k in report['base'].keys():
            reportRows.append(localization.GetByLabel('UI/PI/Planet/LocalDistributionReportRow', item=k, itemID=k, base=report['base'][k], quality=report['quality'][k], deplete=report['deplete'][k], final=report['final'][k], raw=report['raw'][k]))

        txtMsg = localization.GetByLabel('UI/PI/Planet/LocalDistributionReport', latitude=math.degrees(surfacePoint.phi), longitude=math.degrees(surfacePoint.theta), reportRows='<br>'.join(reportRows))
        uthread.new(eve.Message, 'CustomInfo', {'info': txtMsg}).context = 'gameui.ServerMessage'

    def AddDepletionPoint(self, point):
        self.myPinManager.AddDepletionPoint(point)

    def CancelInstallProgram(self, pinID, pinData):
        currentPlanet = self.GetCurrentPlanet()
        if currentPlanet is None:
            return
        pin = currentPlanet.CancelInstallProgram(pinID, pinData)
        if pin is not None:
            self.myPinManager.ReRenderPin(pin)
        self.eventManager.SetStateNormal()

    def LoadSpherePinResources(self, spherePin, textureName):
        self.spherePinsPendingLoad.append((spherePin, textureName))
        if not self.spherePinLoadThread:
            self.spherePinLoadThread = uthread.new(self._LoadSpherePinResources)

    def _LoadEffectResource(self, effect):
        if effect.effectResource.isPrepared:
            return
        if not effect.effectResource.isLoading:
            effect.effectResource.Reload()
        while not effect.effectResource.isPrepared:
            blue.synchro.Yield()

    def _LoadSpherePinResources(self):
        while self.spherePinsPendingLoad:
            spherePin, textureName = self.spherePinsPendingLoad.pop()
            self._LoadEffectResource(spherePin.pinEffect)
            spherePin.pinEffect.PopulateParameters()
            for res in spherePin.pinEffect.resources:
                if res.name == 'Layer1Map':
                    res.resourcePath = textureName
                elif res.name == 'Layer2Map':
                    res.resourcePath = 'res:/dx9/texture/UI/pinCircularRamp.dds'

            self._LoadEffectResource(spherePin.pickEffect)
            spherePin.pickEffect.PopulateParameters()
            for res in spherePin.pickEffect.resources:
                if res.name == 'Layer1Map':
                    res.resourcePath = textureName

            spherePin.pinColor = spherePin.pinColor
            spherePin.geometryResPath = 'res:/dx9/model/worldobject/planet/PlanetSphere.gr2'

        self.spherePinLoadThread = None

    def StopSpherePinLoadThread(self):
        if self.spherePinLoadThread:
            self.spherePinLoadThread.kill()
            self.spherePinLoadThread = None

    def EnteredEditMode(self, planetID):
        if self.planetID != planetID:
            return
        self.inEditMode = True
        if self.myPinManager is not None:
            self.myPinManager.OnPlanetEnteredEditMode()

    def ExitedEditMode(self, planetID):
        if self.planetID != planetID:
            return
        self.inEditMode = False
        if self.myPinManager is not None:
            self.myPinManager.OnPlanetExitedEditMode()
