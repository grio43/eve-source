#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\sceneManager.py
import logging
import sys
import blue
import uthread
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager
from eve.client.script.parklife.sceneManagerConsts import SCENE_TYPE_CHARACTER_CREATION, SCENE_TYPE_SPACE, SYSTEM_WIDE_CLOUD_NAME
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge
from eve.common.script.sys import idCheckers
from evecamera import INSPACE_CAMERAS, CAM_SHIPORBIT_RESTRICTED, CAM_VCS_CONSUMER, INSPACE_CAMERA_MODES
from evecamera.locationalcamera import get_orbit_camera_by_solar_system
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
import evegraphics.settings as gfxsettings
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem, IsAbyssalSpaceSystem
from eve.client.script.ui.camera import get_camera_class
from eve.client.script.ui.camera.baseCamera import DestinyBallInvalid
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraBase import CameraBase
from eve.client.script.ui.view.viewStateConst import ViewState
from fsdBuiltData.common.graphicIDs import GetGraphicFile
import locks
import log
import telemetry
import trinity
from localization import GetByLabel
from trinity.sceneRenderJobSpace import DEFAULT_POSTPROCESS_PATH
stdlog = logging.getLogger(__name__)

class SceneContext():

    def __init__(self, scene = None, camera = None, sceneKey = 'default', sceneType = None, renderJob = None):
        self.scene = scene
        self.camera = camera
        self.sceneKey = sceneKey
        self.sceneType = sceneType
        self.renderJob = renderJob


def GetSceneManager():
    return sm.GetService('sceneManager')


class SceneManager(Service):
    __guid__ = 'svc.sceneManager'
    __exportedcalls__ = {'LoadScene': [],
     'GetScene': []}
    __startupdependencies__ = ['settings', 'device']
    __notifyevents__ = ['OnGraphicSettingsChanged',
     'OnSessionChanged',
     'OnCameraLookAt',
     'OnViewStateChanged']

    def Run(self, ms):
        Service.Run(self, ms)
        self.registeredScenes = {}
        self.registeredCameras = {}
        self.sceneLoadedEvents = {}
        self.cameraBeforeRestriction = None
        self.registeredJobs = []
        self.cameraOffsetOverride = None
        self.characterBackdropUIRoot = None
        self.ProcessImportsAndCreateScenes()
        self.primaryJob = SceneContext()
        self.secondaryJob = None
        self.loadingClearJob = trinity.CreateRenderJob()
        self.loadingClearJob.name = 'loadingClear'
        self.loadingClearJob.Clear((0, 0, 0, 1))
        self.loadingClearJob.enabled = False
        self.overlaySceneKeys = [ViewState.StarMap,
         ViewState.SystemMap,
         ViewState.StarMapNew,
         ViewState.SystemMapNew,
         ViewState.Planet,
         ViewState.ShipTree,
         ViewState.DockPanel]
        self.overlayForcePostProcessing = {ViewState.StarMap: 0,
         ViewState.SystemMap: 0}
        self._sharedResources = {}
        self.routeVisualizer = None
        self.podDeathScene = None
        self._persistedSpaceObjects = {}
        self._updateCameras = []
        if '/skiprun' not in blue.pyos.GetArg():
            self._EnableLoadingClear()
        limit = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY) * 30
        self.explosionManager = ExplosionManager(limit)
        self.currentFadeIntensity = 0.0
        self.currentDesaturateLevel = 1.0
        self.enable3DView = True

    def ProcessImportsAndCreateScenes(self):
        from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
        from trinity.sceneRenderJobCharacters import CreateSceneRenderJobCharacters
        self.fisRenderJob = CreateSceneRenderJobSpace('SpaceScenePrimary')
        self.characterRenderJob = CreateSceneRenderJobCharacters()
        self._CreateJobCharCreation()
        self._CreateJobFiS()

    def _UpdateSecondaryCameras(self):
        for camera in self._updateCameras:
            self._UpdateCamera(camera)

    def _UpdateActiveCamera(self):
        cam = self.GetActiveCamera()
        if cam:
            self._UpdateCamera(cam)
        self._UpdateSecondaryCameras()

    def _UpdateCamera(self, camera):
        try:
            camera._Update()
        except DestinyBallInvalid as e:
            log.LogWarn('DestinyBallInvalid while updating camera, e=', e)
        except Exception:
            stdlog.error('Unexpected exception raised from UpdateCamera', exc_info=1, extra={'sample_rate': 0.01})

    def RegisterForCameraUpdate(self, camera):
        if camera not in self._updateCameras:
            self._updateCameras.append(camera)

    def UnregisterForCameraUpdate(self, camera):
        if camera in self._updateCameras:
            self._updateCameras.remove(camera)

    def _EnableLoadingClear(self):
        if not self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = True
            trinity.renderJobs.recurring.insert(0, self.loadingClearJob)

    def _DisableLoadingClear(self):
        if self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = False
            trinity.renderJobs.recurring.remove(self.loadingClearJob)

    def RefreshJob(self, camera):
        sceneType = self.primaryJob.sceneType
        if sceneType == SCENE_TYPE_CHARACTER_CREATION:
            self.primaryJob.renderJob.SetActiveCamera(camera)
            uicore.uilib.SetSceneView(camera.viewMatrix, camera.projectionMatrix)

    def DeactivateFISCamera(self):
        currCam = self.GetActivePrimaryCamera()
        if currCam and hasattr(currCam, 'OnDeactivated'):
            currCam.OnDeactivated()

    def _CreateJobCharCreation(self):
        self.characterRenderJob.CreateBasicRenderSteps()
        self.characterRenderJob.EnableScatter(True)
        self.characterRenderJob.EnableSculpting(True)
        self.characterRenderJob.Set2DBackdropUIRoot(self.characterBackdropUIRoot)
        self.characterRenderJob.AddStep('UPDATE_SECONDARY_CAMERAS', trinity.TriStepPythonCB(self._UpdateSecondaryCameras))

    def _CreateJobFiS(self, rj = None):
        if rj is None:
            rj = self.fisRenderJob
        rj.CreateBasicRenderSteps()
        rj.SetCameraCallback(self._UpdateActiveCamera)

    def GetFisRenderJob(self):
        return self.fisRenderJob

    def GetFiSPostProcess(self):
        return self.fisRenderJob.postProcess

    def OnGraphicSettingsChanged(self, changes):
        if len(gfxsettings.GFX_SETTINGS.intersection(changes)) == 0:
            return
        self.fisRenderJob.SetSettingsBasedOnPerformancePreferences()
        self.characterRenderJob.SetSettingsBasedOnPerformancePreferences()
        activeScene = self.GetActiveScene()
        if activeScene is not None and isinstance(activeScene, trinity.EveSpaceScene):
            self.fisRenderJob.SetScene(activeScene)
        if self.HasSecondaryScene():
            self.secondaryJob.renderJob.SetSettingsBasedOnPerformancePreferences()
        for each in self.registeredJobs:
            each.object.SetSettingsBasedOnPerformancePreferences()

        if gfxsettings.GFX_LOD_QUALITY in changes:
            limit = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY) * 30
            self.explosionManager.SetLimit(limit)
        if gfxsettings.UI_CAMERA_OFFSET in changes:
            self.UpdateCameraOffset()
        if session.userid is not None:
            effectsEnabled = gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED)
            if gfxsettings.UI_TRAILS_ENABLED in changes or gfxsettings.UI_EFFECTS_ENABLED in changes:
                trailsEnabled = effectsEnabled and gfxsettings.Get(gfxsettings.UI_TRAILS_ENABLED)
                trinity.settings.SetValue('eveSpaceObjectTrailsEnabled', trailsEnabled)

    @telemetry.ZONE_METHOD
    def OnSessionChanged(self, isremote, session, change):
        if 'locationid' in change:
            newLocationID = change['locationid'][1]
            if idCheckers.IsSolarSystem(newLocationID) and self.primaryJob.sceneType != SCENE_TYPE_SPACE:
                log.LogWarn('SceneManager: I detected a session change into space but no one has bothered to update my scene type!')
                self.SetSceneType(SCENE_TYPE_SPACE)
        SpaceObjectExplosionManager.ClearWaiters()

    @telemetry.ZONE_METHOD
    def SetSceneType(self, sceneType):
        if self.primaryJob.sceneType == sceneType:
            return
        if sceneType != SCENE_TYPE_SPACE:
            self.DeactivateFISCamera()
        self.primaryJob = SceneContext(sceneType=sceneType)
        if sceneType == SCENE_TYPE_CHARACTER_CREATION:
            log.LogInfo('Setting up character creation scene rendering')
            self.primaryJob.renderJob = self.characterRenderJob
            self.fisRenderJob.SetActiveScene(None)
            self.fisRenderJob.Disable()
            self._DisableLoadingClear()
            self.characterRenderJob.Enable()
        elif sceneType == SCENE_TYPE_SPACE:
            log.LogInfo('Setting up space scene rendering')
            self.primaryJob.renderJob = self.fisRenderJob
            self.characterRenderJob.SetScene(None)
            self.characterRenderJob.Disable()
            for each in self.registeredJobs:
                if hasattr(each.object, 'UseFXAA'):
                    each.object.UseFXAA(False)

            self._DisableLoadingClear()
            if not self.HasSecondaryScene():
                self.fisRenderJob.Enable()

    @telemetry.ZONE_METHOD
    def Initialize(self, scene):
        self.primaryJob = SceneContext(scene=scene, renderJob=self.fisRenderJob)

    def CreateCharacterBackdropUIRoot(self):
        if self.characterBackdropUIRoot:
            return
        self.characterBackdropUIRoot = uicore.uilib.CreateRootObject(name='ccBackgroundUI', renderJob=None, state=uiconst.UI_DISABLED)
        self.characterRenderJob.Set2DBackdropUIRoot(self.characterBackdropUIRoot)

    def _ApplyCamera(self, jobContext, camera, **kwargs):
        if jobContext == self.primaryJob:
            currCam = self.GetActivePrimaryCamera()
        else:
            currCam = self.GetActiveSecondaryCamera()
        jobContext.camera = camera
        if jobContext.renderJob is not None:
            if isinstance(camera, CameraBase):
                jobContext.renderJob.SetActiveCamera(camera.GetTrinityCamera())
            elif isinstance(camera, trinity.EveCamera):
                jobContext.renderJob.SetActiveCamera(camera)
            else:
                jobContext.renderJob.SetActiveCamera(None, camera.viewMatrix, camera.projectionMatrix)
        if hasattr(camera, 'cameraID'):
            sm.ScatterEvent('OnActiveCameraChanged', camera.cameraID)
            if camera.cameraID in INSPACE_CAMERAS:
                self.UpdateSceneCameraReferences(camera)
        if hasattr(camera, 'OnActivated'):
            camera.OnActivated(lastCamera=currCam, **kwargs)
        if currCam and hasattr(currCam, 'OnDeactivated') and currCam != camera:
            currCam.OnDeactivated()
        self.UpdateBracketProjectionCamera()

    def OnCameraLookAt(self, isEgo, itemID):
        scene = self.GetRegisteredScene('default')
        if scene is None:
            return
        for each in scene.cameraAttachments:
            try:
                each.display = isEgo
            except AttributeError:
                pass

    def UpdateSceneCameraReferences(self, camera):
        scene = self.GetRegisteredScene('default')
        if not scene:
            return
        for distanceField in scene.distanceFields:
            distanceField.cameraView = camera.viewMatrix

    def UpdateBracketProjectionCamera(self):
        camera = self.GetActiveCamera()
        if camera:
            uicore.uilib.SetSceneCamera(camera)

    def SetPrimaryCamera(self, cameraID, force = False, **kwargs):
        activeCam = self.GetActivePrimaryCamera()
        if activeCam and activeCam.cameraID == cameraID and not force:
            return activeCam
        camera = self.GetOrCreateCamera(cameraID)
        self._ApplyCamera(self.primaryJob, camera, **kwargs)
        return camera

    def SetSecondaryCamera(self, cameraID, **kwargs):
        activeCam = self.GetActiveSecondaryCamera()
        if activeCam and activeCam.cameraID == cameraID:
            return activeCam
        camera = self.GetOrCreateCamera(cameraID)
        self._ApplyCamera(self.secondaryJob, camera, **kwargs)
        return camera

    def HasSecondaryScene(self):
        return self.secondaryJob is not None

    @telemetry.ZONE_METHOD
    def SetSecondaryScene(self, scene, sceneKey, sceneType):
        if sceneType == SCENE_TYPE_SPACE:
            newJob = not self.HasSecondaryScene()
            if newJob:
                from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
                self.secondaryJob = SceneContext(scene=scene, sceneKey=sceneKey, sceneType=sceneType)
                self.secondaryJob.renderJob = CreateSceneRenderJobSpace('SpaceSceneSecondary')
                self._CreateJobFiS(self.secondaryJob.renderJob)
            else:
                self.secondaryJob.scene = scene
                self.secondaryJob.sceneKey = sceneKey
            if sceneKey in self.overlayForcePostProcessing:
                self.secondaryJob.renderJob.OverrideSettings(gfxsettings.GFX_POST_PROCESSING_QUALITY, self.overlayForcePostProcessing[sceneKey])
                self.secondaryJob.renderJob.OverrideSettings('aaQuality', gfxsettings.AA_QUALITY_DISABLED)
            else:
                self.secondaryJob.renderJob.StopOverrideSettings(gfxsettings.GFX_POST_PROCESSING_QUALITY)
                self.secondaryJob.renderJob.StopOverrideSettings('aaQuality')
            if newJob:
                self.secondaryJob.renderJob.Enable()
            self.secondaryJob.renderJob.SetActiveScene(scene, sceneKey)

    def ClearSecondaryScene(self):
        if not self.HasSecondaryScene():
            return
        if self.secondaryJob.renderJob is not None:
            self.secondaryJob.renderJob.Disable()
        self.secondaryJob = None

    def SetActiveScene(self, scene, sceneKey = None):
        sceneType = SCENE_TYPE_CHARACTER_CREATION
        if getattr(scene, '__bluetype__', None) == 'trinity.EveSpaceScene':
            sceneType = SCENE_TYPE_SPACE
        if sceneKey in self.overlaySceneKeys:
            fadeObject = self.GetFadeObject(scene=self.primaryJob.scene)
            if fadeObject is not None:
                fadeObject.intensity = 0.0
            self.primaryJob.renderJob.SuspendRendering()
            self.SetSecondaryScene(scene, sceneKey, sceneType)
        elif sceneType == SCENE_TYPE_SPACE:
            self.primaryJob.sceneKey = sceneKey
            self.primaryJob.scene = scene
            self.primaryJob.renderJob.SetActiveScene(scene, sceneKey)
        else:
            self.primaryJob.scene = scene
            self.primaryJob.renderJob.SetScene(scene)
        self.UpdateBracketProjectionCamera()

    def RefreshSecondarySceneToRenderJob(self):
        self.secondaryJob.renderJob.SetScene(self.secondaryJob.scene)

    def RegisterJob(self, job):
        wr = blue.BluePythonWeakRef(job)

        def ClearDereferenced():
            self.registeredJobs.remove(wr)

        wr.callback = ClearDereferenced
        self.registeredJobs.append(wr)

    def GetRegisteredCamera(self, key):
        if key in self.registeredCameras:
            return self.registeredCameras[key]
        self.LogNotice('No camera registered for:', key, self.registeredCameras)

    def GetActiveSpaceCamera(self):
        return self.GetActivePrimaryCamera()

    def GetActivePrimaryCamera(self):
        return self.primaryJob.camera

    def GetActiveCamera(self):
        if self.HasSecondaryScene():
            return self.GetActiveSecondaryCamera()
        return self.GetActivePrimaryCamera()

    def GetActiveSecondaryCamera(self):
        return self.secondaryJob.camera

    def UnregisterCamera(self, key):
        if key in self.registeredCameras:
            self.LogNotice('sceneManager::UnregisterCamera', key, self.registeredCameras[key])
            cam = self.registeredCameras[key]
            if cam == self.GetActiveCamera():
                sm.ScatterEvent('OnActiveCameraChanged', None)
            if cam and hasattr(cam, 'OnDeactivated'):
                cam.OnDeactivated()
            del self.registeredCameras[key]

    def RegisterCamera(self, camera):
        cameraID = camera.cameraID
        if cameraID in self.registeredCameras:
            return
        self.LogNotice('sceneManager::RegisterCamera', cameraID, camera)
        self.registeredCameras[camera.cameraID] = camera
        camera.centerOffset = self.GetCameraOffset()

    def GetCameraOffset(self):
        if self.cameraOffsetOverride:
            return self.cameraOffsetOverride * -0.01
        elif gfxsettings.IsInitialized(gfxsettings.SETTINGS_GROUP_UI):
            return gfxsettings.Get(gfxsettings.UI_CAMERA_OFFSET) * -0.01
        else:
            return 0.0

    def SetCameraOffsetOverride(self, cameraOffsetOverride):
        self.cameraOffsetOverride = cameraOffsetOverride
        self.UpdateCameraOffset()

    def UpdateCameraOffset(self):
        offset = self.GetCameraOffset()
        for cam in self.registeredCameras.itervalues():
            cam.centerOffset = offset

        sm.ScatterEvent('OnSetCameraOffset', offset)

    def UnregisterScene(self, key, ignoreCamera = False):
        if key in self.registeredScenes:
            del self.registeredScenes[key]
            if not ignoreCamera and key == 'default':
                cam = self.GetActivePrimaryCamera()
                if cam:
                    cam.OnDeactivated()

    def RegisterScene(self, scene, key):
        self.registeredScenes[key] = scene
        self._Update3DViewDisplayState()

    def GetRegisteredScene(self, key, defaultOnActiveScene = False, allowBlocking = True):
        if key in self.registeredScenes:
            return self.registeredScenes[key]
        if self.IsLoadingScene(key) and allowBlocking:
            self.sceneLoadedEvents[key].wait()
            return self.registeredScenes[key]
        if defaultOnActiveScene:
            return self.primaryJob.scene

    def IsLoadingScene(self, key):
        return key in self.sceneLoadedEvents and not self.sceneLoadedEvents[key].is_set()

    def SetRegisteredScenes(self, key):
        if key == 'default' and 'transition' in self.registeredScenes:
            key = 'transition'
        if key in ('default', 'transition') and self.HasSecondaryScene():
            if self.primaryJob.renderJob.enabled:
                self.primaryJob.renderJob.Start()
            else:
                self.primaryJob.renderJob.Enable()
            self.ClearSecondaryScene()
        scene = self.registeredScenes.get(key, None)
        self.SetActiveScene(scene, key)

    def GetActiveScene(self):
        if self.HasSecondaryScene():
            return self.secondaryJob.scene
        return self.primaryJob.scene

    def Get2DBackdropScene(self):
        return self.characterBackdropUIRoot.GetRenderObject()

    @telemetry.ZONE_METHOD
    def Show2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = True
        if updateRenderJob:
            self.characterRenderJob.Set2DBackdropUIRoot(self.characterBackdropUIRoot)

    @telemetry.ZONE_METHOD
    def Hide2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = False
        if updateRenderJob:
            self.characterRenderJob.Set2DBackdropUIRoot(None)

    def GetScene(self, location = None):
        if location is None:
            location = (eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid)
        return self.GetResPathForLocation(location)

    def GetResPathForLocation(self, location):
        resPath = None
        if IsAbyssalSpaceSystem(location[0]):
            resPath = sm.GetService('abyss').get_nebula_res_path()
        if resPath is None:
            return cfg.GetNebula(*location)
        return resPath

    def GetSceneForSystem(self, solarSystemID):
        _, regionID, constellationID, _, _ = sm.GetService('map').GetParentLocationID(solarSystemID)
        return self.GetScene((solarSystemID, constellationID, regionID))

    def GetNebulaPathForSystem(self, solarSystemID):
        scene = trinity.Load(self.GetSceneForSystem(solarSystemID))
        return scene.envMapResPath

    def ReplaceNebulaFromResPath(self, nebulaGraphicsResPath):
        newScene = trinity.Load(nebulaGraphicsResPath)
        scene = self.GetRegisteredScene('default')
        scene.backgroundEffect = newScene.backgroundEffect
        scene.envMapResPath = newScene.envMapResPath
        scene.envMap1ResPath = newScene.envMap1ResPath
        scene.envMap2ResPath = newScene.envMap2ResPath

    def DeriveTextureFromSceneName(self, scenePath):
        scene = trinity.Load(scenePath)
        if scene is None:
            return {}
        d = {'envMap1ResPath': scene.envMap1ResPath,
         'lowQualityNebulaResPath': scene.lowQualityNebulaResPath,
         'lowQualityNebulaMixResPath': scene.lowQualityNebulaMixResPath}
        return d

    def CleanupSpaceResources(self):
        self._sharedResources = {}

    def RegisterPersistentUIObject(self, key, object):
        if key in self._persistedSpaceObjects:
            self.RemovePersistentUIObject(key)
        self._persistedSpaceObjects[key] = object
        scene = self.GetRegisteredScene('default', False)
        if scene is not None:
            scene.uiObjects.append(object)

    def GetPersistentUIObject(self, key):
        obj = None
        if key in self._persistedSpaceObjects:
            obj = self._persistedSpaceObjects[obj]
        return obj

    def RemovePersistentUIObject(self, key):
        obj = self._persistedSpaceObjects[key]
        scene = self.GetRegisteredScene('default', False)
        if scene is not None:
            scene.uiObjects.fremove(obj)
        del self._persistedSpaceObjects[key]

    def _GetSharedResource(self, path, key = None):
        comboKey = (path, key)
        if comboKey not in self._sharedResources:
            self._sharedResources[comboKey] = trinity.Load(path)
        return self._sharedResources[comboKey]

    def _PrepareBackgroundLandscapes(self, scene, solarSystemID, constellationID = None):
        starSeed = 0
        securityStatus = 1
        if constellationID is None:
            constellationID = sm.GetService('map').GetConstellationForSolarSystem(solarSystemID)
        if bool(solarSystemID) and bool(constellationID):
            starSeed = int(constellationID)
            securityStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
        scene.starfield = self._GetSharedResource('res:/dx9/scene/starfield/spritestars.red')
        if scene.starfield is not None:
            scene.starfield.seed = starSeed
            scene.starfield.minDist = 40
            scene.starfield.maxDist = 80
            if IsKnownSpaceSystem(solarSystemID):
                scene.starfield.numStars = 500 + int(250 * securityStatus)
            else:
                scene.starfield.numStars = 0

    def _SetupUniverseStars(self, scene, solarsystemID):
        if gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED) and solarsystemID is not None:
            universe = self._GetSharedResource('res:/dx9/scene/starfield/universe.red')
            scene.backgroundObjects.append(universe)
            here = sm.GetService('map').GetItem(solarsystemID)
            if here:
                scale = 10000000000.0
                position = (here.x / scale, here.y / scale, -here.z / scale)
                universe.children[0].translation = position

    def AddPersistentUIObjects(self, scene):
        for spaceObject in self._persistedSpaceObjects.values():
            if spaceObject not in scene.uiObjects:
                scene.uiObjects.append(spaceObject)

    def ApplySolarsystemAttributes(self, scene, solarsystemID = None):
        if solarsystemID is None:
            solarsystemID = session.solarsystemid
        if not scene.cameraAttachments.FindByName('dustfield'):
            dustfield = self._GetSharedResource('res:/dx9/scene/dustfield.red')
            dustfield.name = 'dustfield'
            scene.cameraAttachments.append(dustfield)
        scene.sunDiffuseColor = (1.5, 1.5, 1.5, 1.0)
        if hasattr(cfg.mapSolarSystemContentCache[solarsystemID], 'systemWideCloud'):
            systemWideCloudGID = cfg.mapSolarSystemContentCache[solarsystemID].systemWideCloud
            if systemWideCloudGID > 0:
                systemWideCloudGraphicPath = GetGraphicFile(systemWideCloudGID)
                systemWideCloud = self._GetSharedResource(systemWideCloudGraphicPath)
                if systemWideCloud is not None:
                    systemWideCloud.name = SYSTEM_WIDE_CLOUD_NAME
                    systemWideCloud.StartControllers()
                    scene.objects.append(systemWideCloud)
        self._SetupUniverseStars(scene, solarsystemID)
        self._PrepareBackgroundLandscapes(scene, solarsystemID)

    def ApplySceneInflightAttributes(self, scene, bp = None):
        if bp is None:
            bp = sm.GetService('michelle').GetBallpark()
        scene.ballpark = bp

    def SetVignette(self, vignette, vignetteSettings):
        index = 0
        if isinstance(vignette, trinity.Tr2PPVignetteEffect):
            index = 1
        for nametuple, value in vignetteSettings.iteritems():
            setattr(vignette, nametuple[index], value)

    def GetVignetteObject(self, vignetteSettings, scene = None, create = False):
        if scene is None:
            scene = self.GetActiveScene()
        if isinstance(scene, trinity.EveSpaceScene):
            if scene.postprocess is not None and scene.postprocess.vignette is not None:
                return scene.postprocess.vignette
            if create:
                if scene.postprocess is None:
                    scene.postprocess = trinity.Load(DEFAULT_POSTPROCESS_PATH)
                if scene.postprocess.vignette is None:
                    scene.postprocess.vignette = trinity.Tr2PPVignetteEffect()
                self.SetVignette(scene.postprocess.vignette, vignetteSettings)
                return scene.postprocess.vignette

    def GetFadeObject(self, scene = None, create = False):
        if scene is None:
            scene = self.GetActiveScene()
        if isinstance(scene, trinity.EveSpaceScene):
            if scene.postprocess is not None and scene.postprocess.fade is not None:
                return scene.postprocess.fade
            if create:
                if scene.postprocess is None:
                    scene.postprocess = trinity.Load(DEFAULT_POSTPROCESS_PATH)
                if scene.postprocess.fade is None:
                    scene.postprocess.fade = trinity.Tr2PPFadeEffect()
                return scene.postprocess.fade

    def GetDesaturateObject(self, scene = None, create = False):
        if scene is None:
            scene = self.GetActiveScene()
        if scene is None:
            return
        if isinstance(scene, trinity.EveSpaceScene):
            if scene.postprocess is not None and scene.postprocess.desaturate is not None:
                return scene.postprocess.desaturate
            if create:
                if scene.postprocess is None:
                    scene.postprocess = trinity.Load(DEFAULT_POSTPROCESS_PATH)
                if scene.postprocess.desaturate is None:
                    scene.postprocess.desaturate = trinity.Tr2PPDesaturateEffect()
                return scene.postprocess.desaturate

    def ApplyScene(self, scene, registerKey = None):
        fadeObject = self.GetFadeObject(scene=scene, create=True)
        desaturateObject = self.GetDesaturateObject(scene=scene, create=True)
        if fadeObject:
            fadeObject.intensity = self.currentFadeIntensity
        if desaturateObject:
            desaturateObject.intensity = self.currentDesaturateLevel
        if registerKey is not None:
            self.RegisterScene(scene, registerKey)
            self.SetActiveScene(scene, registerKey)
        else:
            self.SetActiveScene(scene, registerKey)
        sm.ScatterEvent('OnLoadScene', scene, registerKey)

    def GetOrCreateCamera(self, cameraID):
        if cameraID in self.registeredCameras:
            return self.GetRegisteredCamera(cameraID)
        else:
            return self._CreateAndRegisterCamera(cameraID)

    def _CreateAndRegisterCamera(self, key, **kwargs):
        cameraCls = get_camera_class(key)
        camera = cameraCls(**kwargs)
        self.RegisterCamera(camera)
        return camera

    @telemetry.ZONE_METHOD
    def LoadScene(self, scenefile, registerKey = None, applyScene = True):
        scene = None
        try:
            if registerKey:
                self.sceneLoadedEvents[registerKey] = locks.Event(registerKey)
            self.SetSceneType(SCENE_TYPE_SPACE)
            sceneFromFile = trinity.Load(scenefile)
            if sceneFromFile is None:
                return
            scene = sceneFromFile
            if applyScene:
                self.ApplyScene(scene, registerKey)
        except Exception:
            log.LogException('sceneManager::LoadScene')
            sys.exc_clear()
        finally:
            if registerKey and registerKey in self.sceneLoadedEvents:
                self.sceneLoadedEvents.pop(registerKey).set()

        return (scene, None)

    def ApplySpaceScene(self):
        scene = self.primaryJob.scene
        if not scene:
            return
        self.ApplySolarsystemAttributes(scene)
        self.ApplySceneInflightAttributes(scene)
        self.AddPersistentUIObjects(scene)

    def SwitchToRestrictedCamera(self, minZoom = None, maxZoom = None, minPitch = BaseSpaceCamera.kMinPitch, maxPitch = BaseSpaceCamera.kMaxPitch, isRotationEnabled = True, initialZoomDistance = None):
        lastCamera = self.GetActivePrimaryCamera()
        if lastCamera and lastCamera.cameraID != CAM_SHIPORBIT_RESTRICTED:
            if lastCamera.cameraID in INSPACE_CAMERAS:
                self.cameraBeforeRestriction = lastCamera.cameraID
        self.SetPrimaryCamera(CAM_SHIPORBIT_RESTRICTED, force=True)
        restrictedCam = self.GetActivePrimaryCamera()
        restrictedCam.Lock(minZoom, maxZoom, minPitch, maxPitch, isRotationEnabled)
        restrictedCam.LookAt(session.shipid)
        if initialZoomDistance is not None:
            restrictedCam.SetZoomDistance(initialZoomDistance)

    def SwitchFromRestrictedCamera(self):
        newCamera = get_orbit_camera_by_solar_system(session.solarsystemid)
        if self.cameraBeforeRestriction is not None and self.cameraBeforeRestriction in INSPACE_CAMERA_MODES:
            newCamera = self.cameraBeforeRestriction
        activeCamera = self.GetActivePrimaryCamera()
        activeCameraID = activeCamera.cameraID if activeCamera else None
        if activeCameraID == CAM_SHIPORBIT_RESTRICTED:
            activeCamera.Unlock()
            self.SetPrimaryCamera(newCamera)
        elif settings.char.ui.Get('spaceCameraID', None) == CAM_SHIPORBIT_RESTRICTED:
            settings.char.ui.Set('spaceCameraID', newCamera)
        self.cameraBeforeRestriction = None

    def GetVirtualCamera(self):
        return self.GetOrCreateCamera(CAM_VCS_CONSUMER)

    def SwitchToVirtualCamera(self):
        lastCamera = self.GetActivePrimaryCamera()
        if lastCamera and lastCamera.cameraID == CAM_VCS_CONSUMER:
            return
        self.cameraBeforeVirtual = lastCamera.cameraID
        self.SetPrimaryCamera(CAM_VCS_CONSUMER, force=True)

    def SwitchFromVirtualCamera(self):
        lastCamera = self.GetActivePrimaryCamera()
        if not lastCamera or lastCamera.cameraID != CAM_VCS_CONSUMER:
            self.cameraBeforeVirtual = None
            return
        if self.cameraBeforeVirtual is not None:
            camera = self.SetPrimaryCamera(self.cameraBeforeVirtual)
        else:
            orbitCamera = get_orbit_camera_by_solar_system(session.solarsystemid)
            camera = self.SetPrimaryCamera(orbitCamera)
        self.cameraBeforeVirtual = None

    def SnapLastCameraToVirtualCamera(self):
        if self.cameraBeforeVirtual:
            virtualCamera = self.GetVirtualCamera()
            camera = self.GetOrCreateCamera(self.cameraBeforeVirtual)
            camera.eyePosition = virtualCamera.eyePosition
            camera.atPosition = virtualCamera.atPosition

    def EnableRestrictedCameraRotation(self):
        activeCamera = self.GetActivePrimaryCamera()
        if activeCamera and activeCamera.cameraID == CAM_SHIPORBIT_RESTRICTED:
            activeCamera.EnableRotation()

    def FadeOut(self, duration, sleep = False):
        self.FadeTo(duration, fromValue=1.0, toValue=0.0, sleep=sleep)

    def FadeIn(self, duration, color = (0.0, 0.0, 0.0, 1.0), sleep = False):
        self.FadeTo(duration, color, fromValue=0.0, toValue=1.0, sleep=sleep)

    def FadeTo(self, duration, color = None, fromValue = 0.0, toValue = 1.0, sleep = False):
        fadeObject = self.GetFadeObject(create=True)
        self.currentFadeIntensity = toValue
        if fadeObject is not None:
            if color is not None:
                fadeObject.color = color
            uicore.animations.MorphScalar(fadeObject, 'intensity', startVal=fromValue, endVal=toValue, duration=duration, sleep=sleep)

    def FadeVignetteToIntensityAndOpacity(self, duration, vignetteSettings, color = None, fromIntensity = 0.0, toIntensity = 1.0, fromOpacity = 0.0, toOpacity = 1.0, sleep = False):
        vignetteObject = self.GetVignetteObject(vignetteSettings, create=True)
        self.currentFadeIntensity = toIntensity
        if vignetteObject is not None:
            if color is not None:
                vignetteObject.color = color
        uicore.animations.MorphScalar(vignetteObject, 'intensity', startVal=fromIntensity, endVal=toIntensity, duration=duration, sleep=sleep)
        uicore.animations.MorphScalar(vignetteObject, 'opacity', startVal=fromOpacity, endVal=toOpacity, duration=duration, sleep=sleep)

    def Saturate(self, duration, saturateLevel):
        uthread.new(self._Saturate, duration, saturateLevel)

    def _Saturate(self, duration, saturateLevel):
        effect = self.GetDesaturateObject(create=True)
        if effect is not None:
            level = effect.intensity
            self.currentDesaturateLevel = saturateLevel
            uicore.animations.MorphScalar(effect, 'intensity', startVal=level, endVal=saturateLevel, duration=duration)

    def ToggleEnable3DView(self):
        self.enable3DView = not self.enable3DView
        self._Update3DViewDisplayState()

    def _Update3DViewDisplayState(self):
        scenesToToggle = ['default', 'hangar', 'transition']
        for sceneName in scenesToToggle:
            if sceneName in self.registeredScenes:
                self.registeredScenes[sceneName].display = self.enable3DView

        if hasattr(self, 'hidden3DViewWarningContainer') and self.hidden3DViewWarningContainer is not None:
            self.hidden3DViewWarningContainer.Close()
            self.hidden3DViewWarningContainer = None
        if not self.enable3DView:
            self.hidden3DViewWarningContainer = Toggled3DViewWarning(parent=uicore.desktop, name='exterior_view_hider')
            self.hidden3DViewWarningContainer.Show()
            uicore.animations.FadeOut(self.hidden3DViewWarningContainer, 4.0, timeOffset=20.0, callback=self.hidden3DViewWarningContainer.Hide)

    def OnViewStateChanged(self, from_view, to_view):
        self._Update3DViewDisplayState()
        if from_view != ViewState.CharacterCreation and to_view == ViewState.CharacterSelector:
            self.SetActiveScene(trinity.EveSpaceScene())
            self.ClearSecondaryScene()

    def SwitchFromRestrictedCameraOnReset(self):
        self.cameraBeforeVirtual = None
        self.cameraBeforeRestriction = None
        self.SwitchFromRestrictedCamera()


class Toggled3DViewWarning(ContainerAutoSize):
    default_align = uiconst.CENTERTOP
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(Toggled3DViewWarning, self).ApplyAttributes(attributes)
        mainCont = ContainerAutoSize(parent=self, align=uiconst.CENTERTOP, alignMode=uiconst.TOTOP, top=230, width=400, bgColor=(0.1, 0.1, 0.1, 0.5))
        EveCaptionLarge(parent=mainCont, align=uiconst.TOTOP, text='<center>%s</center>' % GetByLabel('UI/Shared/ExteriorViewDisabled'), padding=(4, 4, 4, 4))
        command = uicore.cmd.commandMap.GetCommandByName('CmdToggle3DView')
        EveLabelLarge(parent=mainCont, align=uiconst.TOTOP, text='<center>%s</center>' % GetByLabel('UI/Shared/PressToRestoreView', shortcut=command.GetShortcutAsString()), padding=(4, 4, 4, 4))
