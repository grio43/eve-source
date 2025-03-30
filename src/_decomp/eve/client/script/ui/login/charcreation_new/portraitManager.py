#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\portraitManager.py
import uthread
import telemetry
import utillib
from eve.common.script.util import paperDollUtil
import blue
import math
import geo2
from carbon.common.script.util import mathUtil
import eve.common.lib.appConst as const
from carbonui import uiconst
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.uicore import uicore
import evegraphics.settings as gfxsettings
import charactercreator.const as ccConst
import charactercreator.client.animparams as animparams
from eve.client.script.ui.login.charcreation_new.portraitMaker import PortraitMaker
from eve.client.script.ui.login.charcreation_new import ccUtil
from eve.client.script.ui.login.charcreation_new.sceneManager import GetCharacterCreationSceneManager
ccPortraitManager = None

def GetCharacterCreationPortraitManager():
    global ccPortraitManager
    if ccPortraitManager is None:
        ccPortraitManager = CharacterCreationPortraitManager()
    return ccPortraitManager


class CharacterCreationPortraitManager(object):

    def __init__(self):
        self.characterSvc = sm.GetService('character')
        self.animateToStoredPortraitThread = None
        self.animatingToPortraitID = None
        self.portraitInfo = {}
        self.facePortraits = {}
        self.activePortraitIndex = 0
        self.activePortrait = None
        self.backdropPath = None
        self.alreadyLoadedOldPortraitData = False
        self.poseID = 0

    def Initialize(self):
        self.alreadyLoadedOldPortraitData = False

    def TearDown(self):
        self.animateToStoredPortraitThread = None
        self.animatingToPortraitID = None

    def Cleanup(self):
        pass

    @telemetry.ZONE_METHOD
    def ClearFacePortrait(self, *args):
        self.facePortraits = [None] * ccConst.NUM_PORTRAITS
        self.portraitInfo = [None] * ccConst.NUM_PORTRAITS
        self.activePortraitIndex = 0
        self.activePortrait = None

    @telemetry.ZONE_METHOD
    def GetPortraitInfo(self, portraitID):
        return self.portraitInfo[portraitID]

    @telemetry.ZONE_METHOD
    def SetActivePortrait(self, portraitNo, *args):
        self.activePortraitIndex = portraitNo
        self.activePortrait = self.facePortraits[portraitNo]

    @telemetry.ZONE_METHOD
    def GetActivePortrait(self):
        return self.activePortrait

    @telemetry.ZONE_METHOD
    def GetActivePortraitInfo(self):
        return self.portraitInfo[self.activePortraitIndex]

    @telemetry.ZONE_METHOD
    def SetFacePortrait(self, photo, portraitNo, *args):
        self.facePortraits[portraitNo] = photo
        self.SetActivePortrait(portraitNo)

    @telemetry.ZONE_METHOD
    def SetBackdrop(self, backdropPath):
        self.backdropPath = backdropPath

    @telemetry.ZONE_METHOD
    def GetBackdrop(self):
        return self.backdropPath

    @telemetry.ZONE_METHOD
    def SetPoseID(self, poseID):
        self.poseID = poseID

    @telemetry.ZONE_METHOD
    def GetPoseID(self):
        return self.poseID

    @telemetry.ZONE_METHOD
    def CapturePortrait(self, portraitID, camera, poseData, lightingID, lightColorID, lightIntensity):
        self.portraitInfo[portraitID] = utillib.KeyVal(cameraPosition=camera.GetPosition(), cameraFieldOfView=camera.fieldOfView, cameraPoi=camera.GetPointOfInterest(), backgroundID=self.GetCurrentBackgroundID(), lightID=lightingID, lightColorID=lightColorID, lightIntensity=lightIntensity, poseData=poseData)
        maker = PortraitMaker(camera, self.backdropPath)
        self.activePortrait = maker.GetPortraitTexture(portraitID)
        return self.activePortrait

    @telemetry.ZONE_METHOD
    def GetPortraitSnapshotPath(self, portraitID):
        return blue.paths.ResolvePathForWriting(u'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid))

    def AnimateToStoredPortrait(self, newPortraitID, charID):
        if self.portraitInfo[newPortraitID] is None:
            return
        if self.animateToStoredPortraitThread and self.animateToStoredPortraitThread.alive:
            if self.animatingToPortraitID == newPortraitID:
                return
            self.animateToStoredPortraitThread.kill()
        self.animateToStoredPortraitThread = uthread.new(self.AnimateToStoredPortrait_thread, newPortraitID, charID)

    def AnimateToStoredPortrait_thread(self, newPortraitID, charID):
        portraitInfo = self.portraitInfo[newPortraitID]
        if portraitInfo is None:
            return
        newParams = self.GetControlParametersFromPortraitID(newPortraitID, charID)
        if newParams is None:
            return
        oldParams = self.GetControlParametersFromPortraitID(None, charID)
        if len(oldParams) < 1 or len(newParams) < 1:
            return
        sceneManager = GetCharacterCreationSceneManager()
        self.animatingToPortraitID = newPortraitID
        thereIsCamera = sceneManager.camera is not None
        oldCameraPos = None
        oldCameraPoi = None
        if thereIsCamera:
            oldCameraPos = sceneManager.camera.cameraPosition
            oldCameraPoi = sceneManager.camera.poi
        start, ndt = blue.os.GetWallclockTime(), 0.0
        moveCamera = sceneManager.ShouldMoveCamera(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
        while ndt != 1.0:
            timeValue = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 250.0, 1.0)
            ndt = math.sin(timeValue * math.pi - math.pi / 2.0) / 2.0 + 0.5
            params = []
            for shortKey, keyAndValue in oldParams.iteritems():
                longKey, value = keyAndValue
                if shortKey == 'HeadLookTarget':
                    lerpedValue = geo2.Lerp(value, newParams[shortKey][1], ndt)
                elif shortKey == 'PortraitPoseNumber':
                    continue
                else:
                    lerpedValue = mathUtil.Lerp(value, newParams[shortKey][1], ndt)
                params.append([longKey, lerpedValue])

            self.characterSvc.SetControlParametersFromList(params, charID)
            if thereIsCamera and moveCamera:
                posValue = geo2.Lerp(oldCameraPos, portraitInfo.cameraPosition, ndt)
                poiValue = geo2.Lerp(oldCameraPoi, portraitInfo.cameraPoi, ndt)
                sceneManager.cameraPos = posValue
                sceneManager.cameraPoi = poiValue
                sceneManager.camera.PlacePortraitCamera(sceneManager.cameraPos, sceneManager.cameraPoi)
            blue.pyos.synchro.Yield()

        xFactor, yFactor = sceneManager.camera.GetCorrectCameraXandYFactors(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
        sceneManager.camera.xFactor = sceneManager.camera.xTarget = xFactor
        sceneManager.camera.yFactor = sceneManager.camera.yTarget = yFactor
        sceneManager.lightingID = portraitInfo.lightID
        sceneManager.lightIntensity = portraitInfo.lightIntensity
        sceneManager.lightColorID = portraitInfo.lightColorID
        shouldSnapPortrait = False
        path = self.GetBackgroundPathFromID(portraitInfo.backgroundID)
        if path in self.GetAvailableBackgroundsPaths():
            self.backdropPath = path
        elif not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            shouldSnapPortrait = True
        self.poseID = int(portraitInfo.poseData['PortraitPoseNumber'])
        self.characterSvc.SetControlParametersFromList([['ControlParameters|PortraitPoseNumber', float(self.poseID)]], charID)
        self.UpdateBackdrop()
        sceneManager.UpdateLights()
        sm.ScatterEvent('OnPortraitPicked')
        if shouldSnapPortrait and uicore.layer.charactercreation.controller.step:
            uicore.layer.charactercreation.controller.step.CapturePortrait(newPortraitID)

    def GetControlParametersFromPortraitID(self, portraitID, charID):
        PREFIX = 'ControlParameters|'
        params = {}
        if portraitID is not None:
            portraitInfo = self.portraitInfo[portraitID]
            if portraitInfo is None:
                return {}
            return self.GetControlParametersFromPoseData(portraitInfo.poseData)
        avatar = self.characterSvc.GetSingleCharactersAvatar(charID)
        if avatar is None:
            return {}
        for controlParameter in paperDollUtil.FACIAL_POSE_PARAMETERS.__dict__.iterkeys():
            if controlParameter.startswith('_'):
                continue
            longKey = PREFIX + controlParameter
            network = animparams.GetParamsPerAvatar(avatar, charID)
            value = network.GetControlParameterValue(longKey)
            params[controlParameter] = (longKey, value)

        return params

    def GetControlParametersFromPoseData(self, poseData, fromDB = False):
        if poseData is None:
            return {}
        if fromDB:
            allParameterKeys = poseData.__keys__
        else:
            allParameterKeys = poseData.keys()
        params = {}
        PREFIX = 'ControlParameters|'
        for key in allParameterKeys:
            if key in ('headLookTargetX', 'headLookTargetY', 'headLookTargetZ', 'cameraX', 'cameraY', 'cameraZ'):
                continue
            value = poseData[key]
            if fromDB:
                key = key.replace(key[0], key[0].upper(), 1)
            params[key] = (PREFIX + key, value)

        if fromDB:
            params['HeadLookTarget'] = (PREFIX + 'HeadLookTarget', (poseData['headLookTargetX'], poseData['headLookTargetY'], poseData['headLookTargetZ']))
        return params

    @telemetry.ZONE_METHOD
    def GetBackgroundPathFromID(self, bgID):
        if bgID < const.NCC_MIN_NORMAL_BACKGROUND_ID:
            return 'res:/UI/Texture/CharacterCreation/backdrops/Background_' + str(bgID) + '.dds'
        resourceRow = cfg.paperdollPortraitResources.Get(bgID)
        if resourceRow:
            return resourceRow.resPath

    def GetAvailableBackgroundsPaths(self):
        bgOptions = []
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            bgOptions += ccConst.greenscreenBackgroundOptions
        authoredBackgrounds = self.characterSvc.GetAvailableBackgrounds()
        for eachResource in authoredBackgrounds:
            path = eachResource.resPath
            bgOptions.append(path)

        return bgOptions

    @telemetry.ZONE_METHOD
    def GetCurrentBackgroundID(self):
        authoredBackground = self.characterSvc.GetPortraitResourceByPath(self.backdropPath)
        if authoredBackground:
            return authoredBackground.portraitResourceID
        ID = self.backdropPath.split('_')[-1].split('.')[0]
        try:
            ID = int(ID)
        except ValueError:
            return None

        return ID

    @telemetry.ZONE_METHOD
    def FetchOldPortraitData(self, charID):
        sceneManager = GetCharacterCreationSceneManager()
        PREFIX = 'ControlParameters|'
        cache = self.characterSvc.GetCachedPortraitInfo(charID)
        if cache is not None:
            sceneManager.lightingID = cache.lightID
            sceneManager.lightColorID = cache.lightColorID
            sceneManager.lightIntensity = cache.lightIntensity
            path = self.GetBackgroundPathFromID(cache.backgroundID)
            if path in self.GetAvailableBackgroundsPaths():
                self.SetBackdrop(path)
            self.poseID = cache.poseData['PortraitPoseNumber']
            sceneManager.cameraPos = cache.cameraPosition
            sceneManager.cameraPoi = cache.cameraPoi
            sceneManager.cameraFov = cache.cameraFieldOfView
            params = []
            for key in cache.poseData:
                params.append((PREFIX + key, cache.poseData[key]))

            if len(params):
                self.characterSvc.SetControlParametersFromList(params, charID)
        else:
            portraitData = sm.GetService('cc').GetPortraitData(charID)
            if portraitData is not None:
                sceneManager.lightingID = portraitData.lightID
                sceneManager.lightColorID = portraitData.lightColorID
                sceneManager.lightIntensity = portraitData.lightIntensity
                path = self.GetBackgroundPathFromID(portraitData.backgroundID)
                if path in self.GetAvailableBackgroundsPaths():
                    self.SetBackdrop(path)
                self.poseID = portraitData.portraitPoseNumber
                sceneManager.cameraPos = (portraitData.cameraX, portraitData.cameraY, portraitData.cameraZ)
                sceneManager.cameraPoi = (portraitData.cameraPoiX, portraitData.cameraPoiY, portraitData.cameraPoiZ)
                sceneManager.cameraFov = portraitData.cameraFieldOfView
                params = self.GetControlParametersFromPoseData(portraitData, fromDB=True).values()
                self.characterSvc.SetControlParametersFromList(params, charID)
        self.alreadyLoadedOldPortraitData = True

    @telemetry.ZONE_METHOD
    def UpdateBackdrop(self):
        uiRoot = sm.GetService('sceneManager').characterBackdropUIRoot
        if not uiRoot:
            return
        uiRoot.Flush()
        stepID = uicore.layer.charactercreation.controller.stepID
        if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
            Sprite(name='greenScreenSprite', parent=uiRoot, align=uiconst.TOALL, texturePath='res:/UI/Texture/CharacterCreation/backdrops/Background_1001_thumb.dds')
        elif stepID == ccConst.PORTRAITSTEP:
            activeBackdrop = self.GetBackdrop()
            if activeBackdrop:
                height, width = self.GetBackgroundWidthAndHeight(ratio=1.0)
                Sprite(name='bgSprite', parent=uiRoot, align=uiconst.CENTER, pos=(0,
                 0,
                 width,
                 height), texturePath=activeBackdrop)
        elif stepID == ccConst.CUSTOMIZATIONSTEP:
            videoPath = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/customizeBG.webm'
            self.ConstructBackgroundVideo(uiRoot, videoPath, ratio=16.0 / 9.0)
        elif stepID in (ccConst.NAMINGSTEP, ccConst.DOLLSTEP):
            videoPath = 'res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/backgroundVideo.webm'
            self.ConstructBackgroundVideo(uiRoot, videoPath, ratio=16.0 / 9.0)

    def ConstructBackgroundVideo(self, uiRoot, videoPath, ratio):
        height, width = self.GetBackgroundWidthAndHeight(ratio)
        StreamingVideoSprite(parent=uiRoot, align=uiconst.CENTER, pos=(0,
         0,
         width,
         height), videoPath=videoPath, videoLoop=True)

    def GetBackgroundWidthAndHeight(self, ratio):
        w, h = ccUtil.GetDpiScaledWidthAndHeight()
        if float(w) / h <= ratio:
            width = h * ratio
            height = h
        else:
            width = w
            height = w / ratio
        return (height, width)
