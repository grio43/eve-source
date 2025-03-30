#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\iconrendering2\renderers\renderer_apparel.py
import os
import wx
import dogma.data as dogma_data
import trinity
import blue
import imageutils
import PIL.Image as PILImage
import charactercreator.client.animparams as animparams
import charactercreator.const as ccConst
import eve.client.script.ui.login.charcreation.ccUtil as ccUtil
import eve.common.script.paperDoll.paperDollDataManagement as pdDm
from eve.client.script.paperDoll.paperDollImpl import Doll
from eve.client.script.paperDoll.paperDollSpawnWrappers import PaperDollCharacter
from eve.common.script.paperDoll.paperDollDefinitions import LOD_SKIN
from eve.common.script.util.paperDollBloodLineAssets import bloodlineAssets
import evegraphics.settings as settings
import types
import log
from charactercreator.client.characterDollUtilities import CharacterDollUtilities
from eve.client.script.ui.camera.charCreationCamera import CharCreationCamera
from eve.client.script.ui.login.charcreation.assetRendererConst import DRESSCODE, SETUP, TUCKINDEX, EXAGGERATE, SCARGROUPS, SCARCAMERASETINGS, MALE_MANNEQUIN, FEMALE_MANNEQUIN, LIGHTLOCATION, PIERCINGRIGHTGROUPS, PIERCINGLEFTGROUPS, PIERCINGPAIRGROUPS, NORMAL_LIGHT_SETTINGS, DRESSCODE_CUSTOM_BY_CATEGORY, DRESSCODE_FEMALE_DEFAULT, DRESSCODE_MALE_DEFAULT, DRESSCODE_CATEGORIES, DOLL_MODIFIERS

def GetNESDirectory():
    try:
        up = os.path.join(os.environ['USERPROFILE'])
        return os.path.join(up, 'Desktop', 'CharacterIconOutput')
    except:
        return ''


def GetNESIconPath(path, genderID):
    directory = GetNESDirectory()
    if not os.path.exists(directory):
        os.mkdir(directory)
    directory += '\\Male' if genderID == ccConst.GENDERID_MALE else '\\Female'
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory + '\\' + os.path.basename(path)


CLIENT_OUTPUT_ROOT = 'res:\\UI\\Asset\\'
CLEAR_COLOR = (0.9,
 0.9,
 0.9,
 0.0)
BACKGROUND_PATH = 'res:/UI/Texture/CharacterCreation/assetBackground.png'
RENDER_SIZE = 2048
NES_ICON_SIZE = 512
CLIENT_ICON_SIZE = 128

class ApparelRenderer(object):

    def __init__(self, outputSuffix = ''):
        self.scene = None
        self.lightScene = None
        self.camera = None
        self.characterSvc = sm.GetService('character')
        self.paperDollClient = sm.GetService('paperDollClient')
        self.sceneMgr = sm.GetService('sceneManager')
        self.factory = self.characterSvc.factory
        self.resolution = ccConst.TEXTURE_RESOLUTIONS[0]
        self.genClientIcon = True
        self.genNESIcon = True
        self.charID = 0
        self.renderJob = None
        self.doll = None
        self.avatar = None
        self.cdu = CharacterDollUtilities()
        self.mannequin = None
        self.backBuffer = None
        self.floor = None
        self.rt = None
        self.clear_step = None
        self.outputSuffix = outputSuffix

    def SetupScene(self, gender = False, bloodlineID = None):
        settings.Set(settings.GFX_ANTI_ALIASING, settings.AA_QUALITY_DISABLED)
        self.scene = trinity.Load(ccConst.SCENE_PATH_CUSTOMIZATION)
        self.lightScene = trinity.Load(NORMAL_LIGHT_SETTINGS)
        ccUtil.SetupLighting(self.scene, self.lightScene, self.lightScene)
        self.camera = CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.frontClip = 0.1
        self.camera.backclip = 100.0
        if bloodlineID is not None:
            gender_name = 'female'
            if gender:
                gender_name = 'male'
            self.mannequin = self.PrepareBloodlineDoll(bloodlineID, gender_name, self.scene)
            self.avatar = self.mannequin.avatar
        else:
            self.avatar, self.mannequin = self.CreateAndLoadMannequin(gender, self.scene)
        self.renderJob = self.CreateCharacterRenderJob('testing')
        self.SetShadow(self.avatar, self.scene)
        self.scene.UpdateScene(blue.os.GetSimTime())
        blue.resMan.Wait()

    def CreateCharacterRenderJob(self, name):
        size = RENDER_SIZE
        rt = trinity.Tr2RenderTarget(size, size, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        rt.name = 'MyRT'
        ds = trinity.Tr2DepthStencil(size, size, trinity.DEPTH_STENCIL_FORMAT.AUTO)
        ds.name = 'MyDS'
        self.rt = rt
        rj = trinity.CreateRenderJob('TakeSnapShot')
        rj.PushRenderTarget(rt)
        rj.PushDepthStencil(ds)
        self.clear_step = rj.Clear((0.0, 0.0, 0.0, 0.0), 1.0)
        rj.SetView(self.camera.viewMatrix)
        rj.SetProjection(self.camera.projectionMatrix)
        rj.RenderScene(self.scene)
        trinity.WaitForResourceLoads()
        rj.PopDepthStencil()
        rj.PopRenderTarget()
        return rj

    def CreateAndLoadMannequin(self, genderID, scene):
        mannequin = PaperDollCharacter(self.factory)
        mannequin.doll = Doll('mannequin', gender=ccUtil.GenderIDToPaperDollGender(genderID))
        doll = mannequin.doll
        mannequin.avatar = trinity.Tr2IntSkinnedObject()
        self.doll = doll
        if genderID == ccConst.GENDERID_MALE:
            doll.Load(MALE_MANNEQUIN, self.factory)
        else:
            doll.Load(FEMALE_MANNEQUIN, self.factory)
        self.WaitForDoll(doll)
        doll.overrideLod = LOD_SKIN
        doll.textureResolution = self.resolution
        grannyPath = 'res:/Animation/PortraitCreator/Male/CharacterCreation/Mannequin.gr2'
        if doll.gender == 'female':
            grannyPath = 'res:/Animation/PortraitCreator/Female/CharacterCreation/Mannequin.gr2'
        self.factory.CreateGrannyAnimation(mannequin.avatar, grannyPath)
        mannequin.Spawn(scene, updateDoll=True)
        mannequin.WaitForUpdate()
        return (mannequin.avatar, mannequin)

    def WaitForDoll(self, doll):
        while doll.busyUpdating:
            blue.synchro.Yield()

    def WaitForDollAndScene(self, doll, scene):
        while len(scene.dynamics) < 1:
            blue.synchro.Yield()

        blue.synchro.Yield()
        self.WaitForDoll(doll)

    def FreezeCharacter(self, avatar):
        network = animparams.GetParamsPerAvatar(avatar)
        network.SetControlParameter('ControlParameters|isAlive', 0)
        network.update = False
        blue.synchro.Yield()

    def SetCameraAndLightPiercings(self, category, typeInfo, character, camera, scene):
        typeName, a, b = typeInfo
        if typeName.endswith('left', 0, -1):
            dictToUse = PIERCINGLEFTGROUPS
        elif typeName.endswith('right', 0, -1):
            dictToUse = PIERCINGRIGHTGROUPS
        else:
            dictToUse = PIERCINGPAIRGROUPS
        self.SetUpCamera(camera, category, character, dictToUse, scene)

    def SetCameraForScar(self, typeInfo, character, camera, scene):
        group = SCARGROUPS.get(typeInfo, None)
        if group is None:
            print 'couldnt find the group, return'
            return
        self.SetUpCamera(camera, group, character, SCARCAMERASETINGS, scene)

    def SetCamera(self, camera, poi, distance, yaw, pitch):
        camera.SetPointOfInterest(poi)
        camera.distance = distance
        camera.SetFieldOfView(0.3)
        camera.SetYaw(yaw)
        camera.SetPitch(pitch)
        camera.Update()

    def SetUpCamera(self, camera, category, character, categoryList = SETUP, scene = None, genderID = None):
        if (category, genderID) in categoryList:
            options = categoryList[category, genderID]
        else:
            options = categoryList.get(category, None)
        if options:
            log.LogNotice('+ category = %s' % category)
            boneName, offset, lightSetting = options
            if lightSetting:
                path = '%s%s.red' % (LIGHTLOCATION, lightSetting)
                lightScene = trinity.Load(path)
                ccUtil.SetupLighting(scene, lightScene, lightScene)
            log.LogNotice('before joint')
            joint = 4294967295L
            while joint == 4294967295L:
                log.LogNotice('joint = %s' % joint)
                log.LogNotice('boneName = %s' % boneName)
                joint = character.avatar.GetBoneIndex(boneName)
                log.LogNotice('j = %s' % joint)
                blue.synchro.Yield()
                log.LogNotice('done waiting')

            log.LogNotice('-- joint = %s' % joint)
            poi = character.avatar.GetBonePosition(joint)
            distance, yOffset, xOffset, yaw, pitch = offset
            x, y, z = poi
            if yOffset:
                y += yOffset
            if xOffset:
                x += xOffset
            poi = (x, y, z)
            log.LogNotice('before poi')
            if category in (ccConst.bottomouter, ccConst.feet):
                poi = (0.0, y, z)
            log.LogNotice('before setting camera')
            self.SetCamera(camera, poi, distance, yaw, pitch)
            log.LogNotice('after setting camera')
            return (distance,
             yaw,
             pitch,
             poi)
        else:
            return

    def GetCategoriesFromPath(self, typeID, genderID):
        asset = GetPaperDollResource(typeID, genderID)
        path = '/' + asset.resPath
        rv = []
        categs = SETUP.keys()
        categs.sort()
        categs.reverse()
        for each in categs:
            if isinstance(each, types.StringTypes):
                pathstr = '/%s/' % each
                if pathstr in path.lower():
                    rv.append(each)

        return rv

    def PrepareBloodlineDoll(self, bloodlineID, paperdollGender, scene):
        self.characterSvc.RemoveCharacter(self.charID)
        self.SetupCharacter(bloodlineID, scene, paperdollGender)
        character = self.characterSvc.GetSingleCharacter(self.charID)
        character.avatar.translation = (0.0, 0.0, 0.0)
        grannyPath = 'res:/Animation/PortraitCreator/Male/CharacterCreation/Mannequin.gr2'
        if character.doll.gender == 'female':
            grannyPath = 'res:/Animation/PortraitCreator/Female/CharacterCreation/Mannequin.gr2'
        self.factory.CreateGrannyAnimation(character.avatar, grannyPath)
        self.WaitForDollAndScene(character.doll, scene)
        trinity.WaitForResourceLoads()
        return character

    def SetupCharacter(self, bloodlineID, scene, paperdollGender):
        self.characterSvc.AddCharacterToScene(self.charID, scene, paperdollGender, bloodlineID=bloodlineID, raceID=None, noRandomize=True)
        doll = self.characterSvc.GetSingleCharactersDoll(self.charID)
        self.WaitForDoll(doll)
        doll.overrideLod = LOD_SKIN
        doll.textureResolution = self.resolution
        self.characterSvc.SetDollBloodline(self.charID, bloodlineID)
        self.characterSvc.ApplyItemToDoll(self.charID, 'head', bloodlineAssets[bloodlineID], doUpdate=False)
        if paperdollGender == 'female':
            modifier = doll.AddResource('hair/hair_shortcut_03', 1.0, self.factory)
            modifier.SetColorVariation('20_a')
            doll.AddResource('makeup/eyebrows/eyebrows_01', 1.0, self.factory)
        else:
            modifier = doll.AddResource('hair/hair_stubble_01', 1.0, self.factory)
            modifier.SetColorVariation('20_a')
            doll.AddResource('makeup/eyebrows/eyebrows_01', 1.0, self.factory)
        self.characterSvc.UpdateDoll(self.charID, fromWhere='RenderLoop')

    def DoRenderNormalAssetType(self, typeID, genderID, bloodlineID = 7, genClientIcon = False, genNESIcon = False):
        camera = self.camera
        character = self.mannequin
        scene = self.scene
        doll = character.doll
        for category in self.GetCategoriesFromPath(typeID, genderID):
            typeData = [typeID]
            log.LogNotice('before dresscode')
            if category in DRESSCODE:
                removeDcModifers = self.EnforceDresscode(bloodlineID, category, doll, genderID, character)
            log.LogNotice('go render type')
            for itemType in typeData:
                wasRendered = self.RenderNormalType(bloodlineID, camera, category, character, genderID, itemType, scene, genClientIcon=genClientIcon, genNESIcon=genNESIcon)

    def DoRenderMannequinAssetType(self, typeID, genderID, category, avatar = None, mannequin = None, scene = None, genNESIcon = False, genClientIcon = False):
        if avatar is None:
            avatar = self.avatar
        if mannequin is None:
            mannequin = self.mannequin
        if scene is None:
            scene = self.scene
        self.SetUpCamera(self.camera, category, mannequin, scene=scene)
        mannequin.doll.buildDataManager.SetAllAsDirty()
        if category == ccConst.bottommiddle:
            pantsModifiers = mannequin.doll.buildDataManager.GetModifiersByCategory(ccConst.bottomouter)
            for pm in pantsModifiers:
                mannequin.doll.RemoveResource(pm.GetResPath(), self.factory)

        modifierList = []
        asset = GetPaperDollResource(typeID, genderID)
        doll = mannequin.doll
        path = asset.resPath
        modifier = doll.SetItemType(self.factory, path, weight=1.0)
        if modifier:
            modifierList.append(modifier)
        mannequin.Update()
        blue.pyos.synchro.SleepWallclock(500)
        mannequin.WaitForUpdate()
        if not modifierList:
            return False
        self.SetShadow(avatar, scene)
        outputPath = self.GetOutputPath(assetPath=path, genderID=genderID, useMannequin=True, category=category, typeID=typeID)
        scene.UpdateScene(blue.os.GetSimTime())
        blue.resMan.Wait()
        if genClientIcon:
            self.CheckoutFile(outputPath)
            self.SaveScreenShot(outputPath, CLIENT_ICON_SIZE, True)
        if genNESIcon:
            outputPath = GetNESIconPath(outputPath, genderID)
            self.SaveScreenShot(outputPath, NES_ICON_SIZE, False)
        for modifier in modifierList:
            doll.RemoveResource(modifier.GetResPath(), self.factory)

        mannequin.Update()
        mannequin.WaitForUpdate()
        return True

    def RenderNormalType(self, bloodlineID, camera, category, character, genderID, itemType, scene, genClientIcon = False, genNESIcon = False):
        type_res_path = None
        for resource in cfg.paperdollResources:
            if resource.typeID == itemType and (resource.resGender == genderID or resource.resGender is None):
                type_res_path = resource.resPath

        if type_res_path is None:
            raise ValueError('Type ID not found! %d' % itemType)
        doll = character.doll
        doll.buildDataManager.SetAllAsDirty()
        modifier = doll.SetItemType(self.factory, type_res_path, weight=1.0)
        if 'tattoo/head' in type_res_path.lower() and modifier:
            modifier.SetColorVariation('default_a')
        if not modifier:
            return False
        typeInfo = self.GetCategoriesFromPath(itemType, genderID)
        self.ApplyTuckingIfNeeded(category)
        self.TrySetColor(bloodlineID, category, genderID, typeInfo)
        if (category, genderID) in EXAGGERATE:
            if getattr(modifier, 'weight', None) is not None:
                modifier.weight = 1.5 * modifier.weight
        character.Update()
        blue.pyos.synchro.SleepWallclock(500)
        character.WaitForUpdate()
        blue.resMan.Wait()
        trinity.WaitForResourceLoads()
        self.SetShadow(character.avatar, scene)
        outputPath = self.GetOutputPath(assetPath=type_res_path, genderID=genderID, category=category, bloodlineID=bloodlineID, typeID=itemType)
        if genderID == ccConst.GENDERID_FEMALE:
            character.avatar.animationUpdater.boneOffset.ClearTransforms()
        scene.UpdateScene(blue.os.GetSimTime())
        blue.resMan.Wait()
        if genClientIcon:
            self.CheckoutFile(outputPath)
            self.SaveScreenShot(outputPath, CLIENT_ICON_SIZE, True)
        if genNESIcon:
            outputPath = GetNESIconPath(outputPath, genderID)
            self.SaveScreenShot(outputPath, NES_ICON_SIZE, False)
        return True

    def EnforceDresscode(self, bloodlineID, category, doll, genderID, character):
        if category in DRESSCODE_CUSTOM_BY_CATEGORY:
            dressCode = DRESSCODE_CUSTOM_BY_CATEGORY[category][genderID]
        elif genderID == ccConst.GENDERID_FEMALE:
            dressCode = DRESSCODE_FEMALE_DEFAULT
        else:
            dressCode = DRESSCODE_MALE_DEFAULT
        removeDcModifers = []
        for dcCategory in DRESSCODE_CATEGORIES:
            if dcCategory == category:
                continue
            dcTypeData = self.characterSvc.GetAvailableTypesByCategory(dcCategory, genderID, bloodlineID, None, forceAllTypes=True)
            if not dcTypeData:
                continue
            for itemType in dcTypeData:
                assetID = itemType[0]
                if assetID in dressCode:
                    if dcCategory == ccConst.hair:
                        var = self.GetHairColor(genderID, bloodlineID)
                    else:
                        var = None
                    asset = GetPaperDollResource(itemType, genderID)
                    type_res_path = asset.resPath
                    dcModifier = doll.SetItemType(self.factory, type_res_path, weight=1.0)
                    character.Update()
                    character.WaitForUpdate()
                    if dcModifier:
                        removeDcModifers.append(dcModifier.GetResPath())
                    self.WaitForDoll(doll)
                    blue.resMan.Wait()
                    break

        return removeDcModifers

    def ApplyTuckingIfNeeded(self, category):
        if category not in TUCKINDEX:
            return
        tuckPath, requiredModifier, subKey = ccConst.TUCKMAPPING[category]
        tuckModifier = sm.GetService('character').GetModifierByCategory(self.charID, tuckPath)
        if tuckModifier:
            tuckVariations = tuckModifier.GetVariations()
            tuckStyle = tuckModifier.GetResPath().split('/')[-1]
            self.characterSvc.ApplyItemToDoll(self.charID, category, tuckStyle, variation=tuckVariations[TUCKINDEX[category]])

    def TrySetColor(self, bloodlineID, category, genderID, typeInfo):
        if category in (ccConst.beard, ccConst.hair, ccConst.eyebrows):
            category = ccConst.hair
        try:
            if typeInfo[1] or typeInfo[2]:
                return
            categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, genderID, None)
            if not categoryColors:
                return
            primary, secondary = categoryColors
            primaryVal = (primary[1][0], primary[1][2])
            if primary and secondary:
                secondaryVal = (secondary[1][0], secondary[1][2])
                self.characterSvc.SetColorValueByCategory(self.charID, category, primaryVal, secondaryVal)
            else:
                self.characterSvc.SetColorValueByCategory(self.charID, category, primaryVal, None)
        except:
            pass
        finally:
            if category == ccConst.hair:
                sm.GetService('character').SetHairDarkness(0, 0.5)

    def SetShadow(self, avatar, scene):
        scene.shadowSize = 2048

    def GetHairColor(self, genderID, bloodlineID):
        colorsA, colorsB = sm.GetService('character').GetAvailableColorsForCategory(ccConst.hair, genderID, None)
        colorA = []
        colorB = []
        var = None
        color1Value, color1Name, color2Name, variation = (None, None, None, None)
        if len(colorsA) > 0:
            indexA = int(len(colorsA) * 0.3)
            colorA = colorsA[indexA]
            colorB = None
            if len(colorsB) > 0:
                colorB = colorsB[0]
            color1Value, color1Name, color2Name, variation = sm.GetService('character').GetColorsToUse(colorA, colorB)
        if color1Value:
            return var
        if colorB:
            var = variation
        elif len(colorA) > 0:
            var = colorA[1]
        return var

    @staticmethod
    def CheckoutFile(path):
        import ccpp4
        p4 = ccpp4.P4Init()
        try:
            if p4.EditOrAdd(path, False):
                return True
        except:
            pass

        return False

    def GetScreenshotRenderTarget(self, rt):
        readable = trinity.Tr2RenderTarget(rt.width, rt.height, 1, rt.format)
        if not readable.isValid:
            raise RuntimeError('out of video memory')
        rt.Resolve(readable)
        return readable

    def Tr2HostBitmapToPILImage(self, hostBitmap):
        import tempfile
        if not hostBitmap:
            return
        fd, path = tempfile.mkstemp(suffix='.png')
        hostBitmap.Save(path)
        bitmap = PILImage.open(path)
        bitmap.load()
        os.close(fd)
        os.remove(path)
        return bitmap

    def SaveScreenShot(self, outputPath, targetRes = 512, applyBackground = False):
        import imageutils
        from PIL import Image as PILImage
        print 'SaveScreenShot', outputPath
        blue.resMan.Wait()
        self.render_frame(self.renderJob)
        backbuffer = self.rt
        image = self.CreateAlphaPreservingScreenShot(backbuffer, self.renderJob, clearStep=self.clear_step)
        if applyBackground:
            background = PILImage.open(blue.paths.ResolvePath(BACKGROUND_PATH))
            background.load()
            if background.size[0] != RENDER_SIZE:
                background = background.resize((RENDER_SIZE, RENDER_SIZE), PILImage.ANTIALIAS)
            image = PILImage.composite(image, background, image)
        if targetRes != RENDER_SIZE:
            image = image.resize((targetRes, targetRes), PILImage.ANTIALIAS)
        imageutils.from_pil(image).save(outputPath)

    def GetOutputPath(self, assetPath, genderID, useMannequin = False, category = None, bloodlineID = -1, typeID = None):
        assetResPath = self.ReformatAssetPath(assetPath)
        categoryPath = self.ReformatAssetPath(category)
        subFolder = 'mannequin/' + categoryPath + '/'
        ccUtil.CreateCategoryFolderIfNeeded(blue.paths.ResolvePath(CLIENT_OUTPUT_ROOT), subFolder)
        outputPath = blue.paths.ResolvePath(CLIENT_OUTPUT_ROOT) + subFolder
        suffix = 'png'
        if self.outputSuffix != '':
            suffix = '%s.' % self.outputSuffix + suffix
        if typeID:
            if genderID == ccConst.GENDERID_MALE:
                gender = 'male'
            else:
                gender = 'female'
            outputPath = outputPath + '%s_%s_%s.%s' % (typeID,
             gender,
             assetResPath,
             suffix)
        elif bloodlineID < 0:
            outputPath = outputPath + '%s_g%s.%s' % (assetResPath, genderID, suffix)
        else:
            outputPath = outputPath + '%s_g%s_b%s.%s' % (assetResPath,
             genderID,
             bloodlineID,
             suffix)
        return outputPath

    @staticmethod
    def ReformatAssetPath(path):
        assetResPath = path.replace('/', '_').replace('.type', '')
        return assetResPath

    def GetClearColor(self):
        return self.clear_step.color

    def SetClearColor(self, newColor):
        self.clear_step.color = newColor

    def FreezeRenderJob(self, rj):
        try:
            rj.scene.object.update = False
            rj.scene.object.backgroundRenderingEnabled = False
        except:
            pass

        trinity.device.animationTimeScale = 0

    def ThawRenderJob(self, rj):
        try:
            rj.scene.object.update = True
            rj.scene.object.backgroundRenderingEnabled = True
        except:
            pass

    def CreateRGPCompositeEffect(self, shotA, shotAColor, shotB, shotBColor, finalImage):
        effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/graphics/Effect/Managed/Space/System/BlueScreenMatting.fx'
        param = trinity.TriTextureParameter()
        param.name = 'ShotA'
        res = trinity.TriTextureRes()
        res.SetFromRenderTarget(shotA)
        param.SetResource(res)
        effect.resources.append(param)
        param = trinity.Tr2Vector4Parameter()
        param.name = 'shotABackgroundColor'
        param.value = shotAColor
        effect.parameters.append(param)
        param = trinity.TriTextureParameter()
        param.name = 'ShotB'
        res = trinity.TriTextureRes()
        res.SetFromRenderTarget(shotB)
        param.SetResource(res)
        effect.resources.append(param)
        param = trinity.Tr2Vector4Parameter()
        param.name = 'shotBBackgroundColor'
        param.value = shotBColor
        effect.parameters.append(param)
        param = trinity.TriTextureParameter()
        param.name = 'FinalImage'
        res = trinity.TriTextureRes()
        res.SetFromRenderTarget(finalImage)
        param.SetResource(res)
        effect.resources.append(param)
        return effect

    def RunRGBCompositeEffect(self, effect, width, height):
        rt = trinity.Tr2RenderTarget(width, height, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        rj = trinity.CreateRenderJob('rj')
        rj.steps.append(trinity.TriStepPushRenderTarget(rt))
        rj.steps.append(trinity.TriStepClear((0, 0, 0, 0)))
        rj.steps.append(trinity.TriStepSetStdRndStates(trinity.RM_FULLSCREEN))
        rj.steps.append(trinity.TriStepPushDepthStencil(None))
        rj.steps.append(trinity.TriStepRenderEffect(effect))
        rj.steps.append(trinity.TriStepPopRenderTarget())
        rj.steps.append(trinity.TriStepPopDepthStencil())
        trinity.WaitForResourceLoads()
        rj.ScheduleOnce()
        rj.WaitForFinish()
        return trinity.Tr2HostBitmap(rt)

    def CreateAlphaPreservingScreenShot(self, backBuffer, rj, clearStep = None):
        originalClearColor = self.GetClearColor()
        try:
            bloom = True
            try:
                bloom = rj.postProcess.Bloom
                rj.postProcess.Bloom = False
            except:
                pass

            self.FreezeRenderJob(rj)
            colorA = (1.0, 0.0, 1.0, 1.0)
            self.SetClearColor(colorA)
            self.render_frame(rj)
            shotA = self.GetScreenshotRenderTarget(backBuffer)
            imA = trinity.Tr2HostBitmap(shotA)
            colorB = (0.0, 1.0, 0.0, 0.0)
            self.SetClearColor(colorB)
            self.render_frame(rj)
            shotB = self.GetScreenshotRenderTarget(backBuffer)
            imB = trinity.Tr2HostBitmap(shotB)
            try:
                rj.postProcess.Bloom = bloom
            except:
                pass

            self.SetClearColor((0, 0, 0, 0))
            self.render_frame(rj)
            final = self.GetScreenshotRenderTarget(backBuffer)
            imFinal = trinity.Tr2HostBitmap(final)
            effect = self.CreateRGPCompositeEffect(shotA, colorA, shotB, colorB, final)
            bmp = self.RunRGBCompositeEffect(effect, backBuffer.width, backBuffer.height)
            return self.Tr2HostBitmapToPILImage(bmp)
        except:
            import traceback
            traceback.print_exc()
            return
        finally:
            self.SetClearColor(originalClearColor)
            self.ThawRenderJob(rj)
            trinity.device.animationTimeScale = 1.0

    def render_frame(self, rj):
        rj.ScheduleOnce()
        rj.WaitForFinish()


def GetValidPaperDollGenders(typeID):
    genders = []
    for each in cfg.paperdollResources:
        if each.typeID == typeID:
            if each.resGender is not None:
                genders.append(each.resGender)
            else:
                genders.append(0)
                genders.append(1)

    return genders


def GetPaperDollCategory(typeID, genderID):
    for each in cfg.paperdollResources:
        if each.typeID == typeID:
            asset = GetPaperDollResource(typeID, genderID)
            path = '/' + asset.resPath
            rv = []
            categs = SETUP.keys()
            categs.sort()
            categs.reverse()
            for each in categs:
                if isinstance(each, types.StringTypes):
                    pathstr = '/%s/' % each
                    if pathstr in path.lower():
                        rv.append(each)

            return rv


def GetPaperDollResource(typeID, genderID):
    assets = []
    for each in cfg.paperdollResources:
        if type(typeID) is int and each.typeID == typeID:
            assets.append(each)
        elif type(typeID) is tuple and typeID[1][0] in each.resPath.lower():
            assets.append(each)

    if len(assets) == 1:
        return assets[0]
    if len(assets) > 1:
        for asset in assets:
            if genderID == asset.resGender:
                return asset

    log.LogError('PreviewWnd::PreviewType - No asset matched the typeID: %d' % typeID)


def IsValidType(typeID):
    for each in cfg.paperdollResources:
        if each.typeID == typeID:
            return True

    return False


def OpenTrinityWindow():
    mainFrame = wx.GetApp().GetTopWindow()
    tp = mainFrame.windowManager.GetWindow('Trinity Panel')


class RenderCharacter(object):

    def __init__(self, doll, avatar):
        self.doll = doll
        self.avatar = avatar


def setup_cfg():
    import fsdBuiltData.common.character as fsdchar
    charSvc = sm.GetService('character')
    charSvc.assetsToIDs = {'male': None,
     'female': None}
    paperdollModifierLocations = fsdchar.GetModifierLocationRows()
    paperdollResources = fsdchar.GetResourceRows()
    paperdollSculptingLocations = fsdchar.GetSculptingLocationRows()
    paperdollColors = fsdchar.GetColorLocationRows()
    paperdollColorNames = fsdchar.GetColorNameRows()
    paperdollPortraitResources = fsdchar.GetPortraitResourceRows()
    cfg.paperdollModifierLocations = paperdollModifierLocations
    cfg.paperdollResources = paperdollResources
    cfg.paperdollSculptingLocations = paperdollSculptingLocations
    cfg.paperdollColors = paperdollColors
    cfg.paperdollColorNames = paperdollColorNames
    cfg.paperdollPortraitResources = paperdollPortraitResources
    dogma_data.get_all_attributes = lambda : []
    dogma_data.get_all_effects = lambda : []
    charSvc.PopulateModifierLocationDicts(True)


def RenderClientIcon(typenum, gender, outputSuffix = ''):
    if outputSuffix == '' or outputSuffix == 'EN':
        blue.os.languageID = 'EN'
    elif outputSuffix == 'ZH':
        blue.os.languageID = 'ZH'
    if not IsValidType(typenum):
        print '*****  Type %d does not match a paperdoll resource. *****' % typenum
        return False
    pdDm.ClearAllCachedMaps()
    aprenderer = ApparelRenderer(outputSuffix)
    OpenTrinityWindow()
    if GetPaperDollCategory(typenum, gender)[0] in DOLL_MODIFIERS:
        curr_bloodline = 1
        aprenderer.SetupScene(gender, bloodlineID=curr_bloodline)
        aprenderer.mannequin.doll.buildDataManager.SetAllAsDirty()
        aprenderer.SetUpCamera(aprenderer.camera, GetPaperDollCategory(typenum, gender)[0], aprenderer.mannequin, scene=aprenderer.scene)
        aprenderer.DoRenderNormalAssetType(typenum, gender, bloodlineID=curr_bloodline, genClientIcon=True)
    else:
        aprenderer.SetupScene(gender)
        aprenderer.SetUpCamera(aprenderer.camera, GetPaperDollCategory(typenum, gender)[0], aprenderer.mannequin, scene=aprenderer.scene)
        aprenderer.DoRenderMannequinAssetType(typenum, gender, GetPaperDollCategory(typenum, gender)[0], genClientIcon=True)


def RenderNESIcon(typenum, gender, outputSuffix = ''):
    if outputSuffix == '' or outputSuffix == 'EN':
        blue.os.languageID = 'EN'
    elif outputSuffix == 'ZH':
        blue.os.languageID = 'ZH'
    if not IsValidType(typenum):
        print '*****  Type %d does not match a paperdoll resource. *****' % typenum
        return False
    pdDm.ClearAllCachedMaps()
    aprenderer = ApparelRenderer(outputSuffix)
    OpenTrinityWindow()
    if GetPaperDollCategory(typenum, gender)[0] in DOLL_MODIFIERS:
        curr_bloodline = 1
        aprenderer.SetupScene(gender, bloodlineID=curr_bloodline)
        aprenderer.SetUpCamera(aprenderer.camera, GetPaperDollCategory(typenum, gender)[0], aprenderer.mannequin, scene=aprenderer.scene)
        aprenderer.DoRenderNormalAssetType(typenum, gender, bloodlineID=curr_bloodline, genNESIcon=True)
    else:
        aprenderer.SetupScene(gender)
        aprenderer.SetUpCamera(aprenderer.camera, GetPaperDollCategory(typenum, gender)[0], aprenderer.mannequin, scene=aprenderer.scene)
        aprenderer.DoRenderMannequinAssetType(typenum, gender, GetPaperDollCategory(typenum, gender)[0], genNESIcon=True)


def ProcessTypes(typeslist, genClientIconCB, genNESIconCB, outputSuffix = ''):
    print '**************  STARTING APPAREL RENDER  *************************'
    types_string = str(typeslist)
    types = [ int(t) for t in types_string.split(',') ]
    for typenum in types:
        genders = GetValidPaperDollGenders(typenum)
        for gender in genders:
            if genClientIconCB:
                print 'Rendering %s Client Icon for type %d gender %d' % (outputSuffix, typenum, gender)
                RenderClientIcon(typenum, gender, outputSuffix)
            if genNESIconCB:
                print 'Rendering %s NES Icon for type %d gender %d' % (outputSuffix, typenum, gender)
                RenderNESIcon(typenum, gender, outputSuffix)


TYPES_TEXT_CONTROL = None
GEN_CLIENT_ICON_CB = None
GEN_NES_ICON_CB = None
RESOURCE_LANGUAGE_DROPDOWN = False

class RenderIconDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(RenderIconDialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((400, 300))
        self.SetTitle('Apparel Icon Render')

    def InitUI(self):
        global TYPES_TEXT_CONTROL
        global GEN_NES_ICON_CB
        global RESOURCE_LANGUAGE_DROPDOWN
        global GEN_CLIENT_ICON_CB
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(pnl, label='Render Parameters')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        GEN_CLIENT_ICON_CB = wx.CheckBox(pnl, label='Generate Client Icon')
        sbs.Add(GEN_CLIENT_ICON_CB)
        GEN_NES_ICON_CB = wx.CheckBox(pnl, label='Generate NES Icon')
        sbs.Add(GEN_NES_ICON_CB)
        sbs.Add(wx.StaticText(pnl, -1, 'Resource Language'))
        RESOURCE_LANGUAGE_DROPDOWN = wx.ComboBox(pnl, value='EN', choices=['EN', 'ZH'], style=wx.CB_READONLY)
        sbs.Add(RESOURCE_LANGUAGE_DROPDOWN)
        sbs.Add(wx.StaticText(pnl, -1, 'Types'))
        TYPES_TEXT_CONTROL = wx.TextCtrl(pnl, size=(300, -1))
        sbs.Add(TYPES_TEXT_CONTROL, flag=wx.LEFT, border=5)
        pnl.SetSizer(sbs)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)
        vbox.Add(pnl, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)
        self.SetSizer(vbox)
        okButton.Bind(wx.EVT_BUTTON, self.OnOk)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnClose(self, e):
        self.Destroy()

    def OnOk(self, e):
        typeslist = TYPES_TEXT_CONTROL.GetValue()
        genClientIconCB = GEN_CLIENT_ICON_CB.GetValue()
        genNESIconCB = GEN_NES_ICON_CB.GetValue()
        self.Destroy()
        ProcessTypes(typeslist, genClientIconCB, genNESIconCB, outputSuffix=RESOURCE_LANGUAGE_DROPDOWN.GetValue().replace('EN', ''))


def start():
    setup_cfg()
    cdDialog = RenderIconDialog(None, title='Apparel Icon Render')
    cdDialog.ShowModal()
