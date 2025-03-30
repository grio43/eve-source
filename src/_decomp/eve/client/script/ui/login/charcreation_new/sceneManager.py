#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\sceneManager.py
import trinity
import telemetry
import blue
import geo2
import math
import eve.client.script.ui.login.charcreation_new.ccUtil as ccUtil
import charactercreator.const as ccConst
from eve.client.script.ui.camera.charCreationCamera import CharCreationCamera
from fsdBuiltData.common.graphicIDs import GetGraphicFile
ccSceneManager = None

def GetCharacterCreationSceneManager():
    global ccSceneManager
    if ccSceneManager is None:
        ccSceneManager = CharacterCreationSceneManager()
    return ccSceneManager


class CharacterCreationSceneManager(object):

    def __init__(self):
        self.scene = None
        self.avatarScene = None
        self.sceneManagerSvc = None
        self.camera = None
        self.cameraUpdateJob = None
        self.storedPortraitCameraSettings = None
        self.cameraPoi = None
        self.cameraPos = None
        self.cameraFov = None
        self.lightingID = ccConst.LIGHT_SETTINGS_ID[0]
        self.lightColorID = ccConst.LIGHT_COLOR_SETTINGS_ID[0]
        self.lightIntensity = 0.5

    def Initialize(self):
        self.sceneManagerSvc = sm.GetService('sceneManager')

    def TearDown(self):
        self.scene = None
        self.avatarScene = None
        self.cameraUpdateJob = None
        self.ClearCamera()

    def Cleanup(self):
        self.scene = None
        self.sceneManagerSvc.UnregisterScene('characterCreation')
        self.ClearCamera()

    @telemetry.ZONE_METHOD
    def SetAvatarScene(self, info):
        isNewScene = False
        if self.avatarScene is None:
            self.SetupScene(ccConst.SCENE_PATH_CUSTOMIZATION)
            self.avatarScene = self.scene
            self.floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR1)
            self.floor2 = trinity.Load(ccConst.CUSTOMIZATION_FLOOR2)
            self.scene.dynamics.append(self.floor)
            self.scene.dynamics.append(self.floor2)
            trinity.WaitForResourceLoads()
            if info.genderID:
                origin1 = self.floor.placeableRes.visualModel.meshes[0].opaqueAreas[0].effect.parameters.FindByName('Origin')
                origin2 = self.floor2.placeableRes.visualModel.meshes[0].opaqueAreas[0].effect.parameters.FindByName('Origin')
                origin1_list = list(origin1.value)
                origin2_list = list(origin2.value)
                origin1_list[2] = 2.2
                origin2_list[2] = 2.3
                origin1.value = tuple(origin1_list)
                origin2.value = tuple(origin2_list)
            isNewScene = True
        else:
            self.scene = self.avatarScene
        self.sceneManagerSvc.SetActiveScene(self.scene, sceneKey='characterCreation')
        return isNewScene

    @telemetry.ZONE_METHOD
    def SetupScene(self, path):
        scene = trinity.Load(path)
        blue.resMan.Wait()
        if ccUtil.IsSlowMachine():
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
            if hasattr(scene, 'ssao') and hasattr(scene.ssao, 'enable'):
                scene.ssao.enable = False
            if hasattr(scene, 'ambientColor'):
                scene.ambientColor = (0.25, 0.25, 0.25)
        elif scene:
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
        self.scene = scene
        self.sceneManagerSvc.RegisterScene(scene, 'characterCreation')
        self.sceneManagerSvc.SetRegisteredScenes('characterCreation')

    def SetupForPortraitStep(self, avatar):
        if self.camera is None:
            self.SetupCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
        else:
            self.camera.ToggleMode(ccConst.CAMERA_MODE_PORTRAIT, avatar=avatar, transformTime=500.0)
        if self.cameraPos and self.cameraPoi:
            self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
            xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(self.cameraPos, self.cameraPoi)
            self.camera.xFactor = self.camera.xTarget = xFactor
            self.camera.yFactor = self.camera.yTarget = yFactor
        self.RestorePortraitCameraSettings()
        self.UpdateLights()

    def SetupCamera(self, avatar, cameraMode, callback = None, frontClip = None, backClip = None, controlStyle = None):
        self.camera = CharCreationCamera(avatar, cameraMode)
        if frontClip is not None:
            self.camera.frontClip = frontClip
        if backClip is not None:
            self.camera.backclip = backClip
        if controlStyle is not None:
            self.camera.controlStyle = controlStyle
        self.SetupCameraUpdateJob()
        self.camera.SetMoveCallback(callback)

    def SetUpNamingStepCamera(self, avatar):
        self.SetupCamera(avatar, ccConst.CAMERA_MODE_DEFAULT, frontClip=3.5, backClip=100.0)
        self.camera.fieldOfView = 0.3
        self.camera.distance = 8.0
        self.camera.SetPointOfInterest((0.0, self.camera.avatarEyeHeight / 2.0, 0.0))

    @telemetry.ZONE_METHOD
    def SetupCameraUpdateJob(self):
        self.sceneManagerSvc.RefreshJob(self.camera)
        if self.cameraUpdateJob is None:
            self.cameraUpdateJob = trinity.renderJob.CreateRenderJob('cameraUpdate')
            r = trinity.TriStepPythonCB()
            r.SetCallback(self.UpdateCamera)
            self.cameraUpdateJob.steps.append(r)
        self.sceneManagerSvc.characterRenderJob.SetCameraUpdate(self.cameraUpdateJob)

    @telemetry.ZONE_METHOD
    def UpdateCamera(self):
        if self.camera is not None:
            self.camera.Update()

    @telemetry.ZONE_METHOD
    def ClearCamera(self):
        if self.camera is not None:
            for priority, behavior in self.camera.cameraBehaviors:
                behavior.camera = None

            del self.camera.cameraBehaviors[:]
            self.camera.avatar = None
            self.camera = None

    def ShouldMoveCamera(self, newPos, newPoi):
        newDirection = geo2.Subtract(newPos, newPoi)
        distanceDiff = abs(self.camera.distance - geo2.Vec3Length(newDirection))
        direction2 = geo2.Vec3Normalize(newDirection)
        yaw = math.acos(direction2[0])
        yawDiff = abs(self.camera.yaw - yaw)
        pitch = math.asin(direction2[1]) + math.pi / 2.0
        pitchDiff = math.sqrt(math.pow(self.camera.pitch - pitch, 2))
        diffPos = geo2.Vec3Distance(self.camera.GetPosition(), newPos)
        if distanceDiff < 5e-07 and yawDiff < 5e-05 and pitchDiff < 5e-05 and diffPos < 0.05:
            return False
        return True

    @telemetry.ZONE_METHOD
    def StorePortraitCameraSettings(self):
        if self.camera is not None:
            self.storedPortraitCameraSettings = {'poi': self.camera.poi,
             'pitch': self.camera.pitch,
             'yaw': self.camera.yaw,
             'distance': self.camera.distance,
             'xFactor': self.camera.xFactor,
             'yFactor': self.camera.yFactor,
             'fieldOfView': self.camera.fieldOfView}

    def RestorePortraitCameraSettings(self):
        if self.storedPortraitCameraSettings:
            self.camera.SetPointOfInterest(self.storedPortraitCameraSettings['poi'])
            self.camera.pitch = self.storedPortraitCameraSettings['pitch']
            self.camera.yaw = self.storedPortraitCameraSettings['yaw']
            self.camera.distance = self.storedPortraitCameraSettings['distance']
            self.camera.xFactor = self.storedPortraitCameraSettings['xFactor']
            self.camera.yFactor = self.storedPortraitCameraSettings['yFactor']
            self.camera.fieldOfView = self.storedPortraitCameraSettings['fieldOfView']

    def GetDoll(self, charID):
        for obj in self.scene.dynamics:
            if obj.name == 'doll_%s' % charID:
                return obj

    @telemetry.ZONE_METHOD
    def SetLighting(self, lightScenePath):
        self.SetLightScene(lightScenePath)
        if ccUtil.IsSlowMachine():
            self.ReduceLights()

    def SetSingleDollLighting(self):
        self.SetLighting('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')

    def SetSingleDollCloseupLighting(self, genderID):
        self.SetLighting('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/OneDollCloseup.red')
        light = self.GetLightByName('FrontMain')
        if light:
            if genderID:
                light.coneDirection = (-0.2813, -0.3778, -0.7448)
            else:
                light.coneDirection = (-0.2813, -0.59375, -0.7448)

    def SetTwoDollsLighting(self):
        self.SetLighting('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal_TwoDolls.red')

    @telemetry.ZONE_METHOD
    def UpdateLights(self):
        lightsPath = GetGraphicFile(self.lightingID)
        lightColorPath = GetGraphicFile(self.lightColorID)
        lightScene = trinity.Load(lightsPath)
        lightColorScene = trinity.Load(lightColorPath)
        ccUtil.SetupLighting(self.scene, lightScene, lightColorScene, self.lightIntensity)
        if ccUtil.IsSlowMachine():
            self.ReduceLights()

    @telemetry.ZONE_METHOD
    def ReduceLights(self):
        scene = self.scene
        if hasattr(scene, 'lights'):
            lightsToRemove = []
            for each in scene.lights:
                if each.name != 'FrontMain':
                    lightsToRemove.append(each)

            for each in lightsToRemove:
                scene.lights.remove(each)

    @telemetry.ZONE_METHOD
    def SetLightScene(self, lightPath, scene = None):
        scene = scene or self.scene
        lightScene = trinity.Load(lightPath)
        if scene:
            lightList = []
            for l in scene.lights:
                lightList.append(l)

            for l in lightList:
                scene.RemoveLightSource(l)

            for l in lightScene.lights:
                scene.AddLightSource(l)

    @telemetry.ZONE_METHOD
    def SetLights(self, lightID):
        self.lightingID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLight(self):
        return self.lightingID

    def GetLightByName(self, name):
        if not self.scene:
            return
        for light in self.scene.lights:
            if light.name == name:
                return light

    @telemetry.ZONE_METHOD
    def SetLightColor(self, lightID):
        self.lightColorID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightColor(self):
        return self.lightColorID

    @telemetry.ZONE_METHOD
    def SetLightsAndColor(self, lightID, colorID):
        self.lightingID = lightID
        self.lightColorID = colorID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def SetLightIntensity(self, intensity):
        self.lightIntensity = intensity
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightIntensity(self):
        return self.lightIntensity
