#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\paperDoll\paperDollSculpting.py
import trinity
import blue
import uthread
import struct
import math
import geo2
from carbon.client.script.animation.animationController import AnimationController
import telemetry
import legacy_r_drive
from eve.common.script.paperDoll.paperDollCommonFunctions import Yield
from .commonClientFunctions import MoveAreas
from eve.common.script.paperDoll.paperDollDefinitions import BLENDSHAPE_CATEGORIES, BODY_BLENDSHAPE_ZONES, DOLL_EXTRA_PARTS, HEAD_BLENDSHAPE_ZONES, HEAD_CATEGORIES
from eve.common.script.paperDoll.yamlPreloader import LoadYamlFileNicely

class PaperDollSculpting:

    def GetProjectionAndViewMatrix(self):
        return (self.camera.projectionMatrix, self.camera.viewMatrix)

    def OnInvalidate(self, dev):
        self.Stop()

    def OnCreate(self, dev):
        self.PreloadZoneMaps(self.doll)
        self.Reset(self.doll, self.avatar, mode=self.mode, camera=self.camera, callback=self.callback, pickCallback=self.pickCallback, inactiveZones=self.inactiveZones)
        self.ready = True

    @telemetry.ZONE_METHOD
    def GetMaskAtPixel(self, x, y):
        self.zoneSize = (self.zoneMap.width, self.zoneMap.height)
        self.bodyZoneSize = (self.bodyZoneMap.width, self.bodyZoneMap.height)
        if self.zoneSize[0] == 0 or self.bodyZoneSize[0] == 0:
            return (0,
             0,
             [0, 0],
             0,
             True)
        mask = 0
        dev = trinity.device
        cameraProj, cameraView = self.GetProjectionAndViewMatrixFunc()
        if self.pickScene:
            self.pickAvatar.rotation = self.avatar.rotation
        backbuffer = self.backbuffer or trinity.device.GetRenderContext().GetDefaultBackBuffer()
        viewport = trinity.TriViewport(0, 0, backbuffer.width, backbuffer.height)
        pick = None
        if hasattr(self.pickScene, 'PickObject'):
            pick = self.pickScene.PickPointAndObject(x, y, cameraProj, cameraView, viewport)
        if not pick:
            return (0,
             0,
             [0, 0],
             0,
             True)
        if not hasattr(self.pickScene, 'PickObjectUV') or pick[0].__typename__ != 'Tr2IntSkinnedObject':
            return (0,
             pick[0],
             [0, 0],
             pick[1],
             True)
        pickedPixelUV = self.pickScene.PickObjectUV(x, y, cameraProj, cameraView, viewport)
        isHead = True
        self.pickedSide = 'right'
        midpoint = 0.5
        if pickedPixelUV[0] > 0.5:
            self.pickedMesh = 'head'
            pickedPixelUV = [(pickedPixelUV[0] - 0.5) * 2.0, pickedPixelUV[1] * 2.0]
            if pickedPixelUV[0] < 0.0 or pickedPixelUV[0] > 1.0 or pickedPixelUV[1] < 0.0 or pickedPixelUV[1] > 1.0:
                return (0,
                 pick[0],
                 pickedPixelUV,
                 pick[1],
                 isHead)
            pixel = [int(pickedPixelUV[0] * self.zoneSize[0]), int(pickedPixelUV[1] * self.zoneSize[1])]
            buffer = self.zoneMap.GetRawData()
            color = struct.unpack_from('=BBBB', buffer[0], pixel[0] * 4 + pixel[1] * buffer[3])
            mask = color[0]
        else:
            isHead = False
            self.pickedMesh = 'body'
            pickedPixelUV = [pickedPixelUV[0] * 2.0, pickedPixelUV[1]]
            pixel = [int(pickedPixelUV[0] * self.bodyZoneSize[0]), int(pickedPixelUV[1] * self.bodyZoneSize[1])]
            buffer = self.bodyZoneMap.GetRawData()
            color = struct.unpack_from('=BBBB', buffer[0], pixel[0] * 4 + pixel[1] * buffer[3])
            mask = color[0]
            zone = self.ConvertMaskToZone(mask)
            if zone in (0, 2, 5) or zone == 1 and pickedPixelUV[0] < 0.37:
                midpoint = 0.2
        if pickedPixelUV[0] > midpoint:
            self.pickedSide = 'left'
        return (mask,
         pick[0],
         pickedPixelUV,
         pick[1],
         isHead)

    def ConvertMaskToZone(self, mask):
        return int(mask / 10.0 - 1)

    def RightDown(self, x, y):
        self.rightClick = True
        self.PickWrapper(x, y)

    def RightUp(self, x, y):
        self.EndMotion(x, y)

    @telemetry.ZONE_METHOD
    def PickWrapper(self, x, y):
        xy = (x, y)
        dev = trinity.device
        self.markerCorrection = [0.0, 0.0]
        mask, pick, uv, xyz, isHead = self.GetMaskAtPixel(x, y)
        if mask > 0:
            if self.mode == 'sculpt':
                self.avatar.animationUpdater.TogglePauseAnimations(True)
            self.startXY = [x, y]
            camera = self.camera
            cPos = camera.GetPosition()
            cInt = camera.GetPointOfInterest()
            avatarRotation = self.avatar.rotation
            vector = [cPos[0] - cInt[0], cPos[1] - cInt[1], cPos[2] - cInt[2]]
            invRotation = geo2.QuaternionInverse(avatarRotation)
            vector = geo2.QuaternionTransformVector(invRotation, vector)
            if abs(vector[0]) > abs(vector[2]):
                if vector[0] > 0.0:
                    self.direction = 'right'
                else:
                    self.direction = 'left'
            else:
                self.direction = 'front'
            self.zone = self.ConvertMaskToZone(mask)
            if self.zone not in self.inactiveZones:
                if self.pickCallback:
                    self.pickCallback(self.zone)
            if self.useHighlighting:
                if self.highlightGhost.IsActive():
                    self.highlightGhost.Stop()
                if self.bodyHighlightGhost.IsActive():
                    self.bodyHighlightGhost.Stop()
        else:
            self.zone = -1
            self.direction = None
            self.startXY = None
        self.rightClick = False
        return self.zone

    @telemetry.ZONE_METHOD
    def MotionWrapper(self, x, y):
        if self.handlingMotion:
            return
        if self.stopInteraction:
            return
        currentFrameCounter = trinity.GetCurrentFrameCounter()
        if self.lastFrameSculpted == currentFrameCounter:
            return
        self.lastFrameSculpted = currentFrameCounter
        self.handlingMotion = True
        if self.startXY:
            delta = [self.startXY[0] - x, self.startXY[1] - y]
            if sum(delta) == 0:
                self.handlingMotion = False
                return
            if self.mode == 'sculpt':
                result = self.UpdateField(delta)
                self.UpdateBlendShapes(result)
            elif self.mode == 'animation':
                result = self.UpdateFieldAnimation(delta)
                if result:
                    self.UpdateAnimation(result)
        else:
            mask, pick, uv, xyz, isHead = self.GetMaskAtPixel(x, y)
            zone = self.ConvertMaskToZone(mask)
            isFront = True
            camera = self.camera
            cPos = camera.GetPosition()
            cInt = camera.GetPointOfInterest()
            vector = [cPos[0] - cInt[0], cPos[1] - cInt[1], cPos[2] - cInt[2]]
            if abs(vector[0]) > abs(vector[2]):
                isFront = False
            if zone not in self.inactiveZones:
                if self.callback:
                    self.callback(zone, isFront, isHead)
            if self.useHighlighting:
                if self.highlightGhost.IsActive() and not isHead:
                    self.highlightGhost.Stop()
                if self.bodyHighlightGhost.IsActive() and isHead:
                    self.bodyHighlightGhost.Stop()
                if mask == 0:
                    if self.highlightGhost.IsActive() and not self.previewingHighlight:
                        self.highlightGhost.Stop()
                    if self.bodyHighlightGhost.IsActive() and not self.previewingHighlight:
                        self.bodyHighlightGhost.Stop()
                    self.handlingMotion = False
                    return
                if not self.highlightGhost.IsActive() and isHead and not self.mode == 'bodyselect':
                    uthread.new(self.highlightGhost.Start, pick)
                if not self.bodyHighlightGhost.IsActive() and not isHead and (self.mode == 'sculpt' or self.mode == 'bodyselect'):
                    uthread.new(self.bodyHighlightGhost.Start, pick)
                if isHead:
                    if self.highlightGhost.IsActive():
                        if not self.overrideMousePos:
                            self.highlightGhost.SetMousePos(xyz, 0.05)
                        else:
                            self.highlightGhost.SetMousePos(self.overrideMousePosXYZ, 0.05)
                        if zone not in self.inactiveZones:
                            self.KillHighlightPreview()
                            self.highlightGhost.SetActiveZoneColor((1.0,
                             1.0,
                             1.0,
                             mask / 255.0))
                elif self.bodyHighlightGhost.IsActive():
                    if not self.overrideMousePos:
                        self.highlightGhost.SetMousePos(xyz, 0.15)
                    else:
                        self.highlightGhost.SetMousePos(self.overrideMousePosXYZ, 0.15)
                    if zone not in self.inactiveZones:
                        self.KillHighlightPreview()
                        self.bodyHighlightGhost.SetActiveZoneColor((1.0,
                         1.0,
                         1.0,
                         mask / 255.0))
        self.handlingMotion = False

    @telemetry.ZONE_METHOD
    def OverrideMousePosWithJoint(self, joint_name):
        bpos = (0.0, 0.0, 0.0)
        if self.avatar is not None and self.avatar.animationUpdater is not None:
            joint = self.avatar.GetBoneIndex(joint_name)
            if joint == 4294967295L:
                bpos = (0.0, 0.0, 0.0)
            else:
                bpos = self.avatar.GetBonePosition(joint)
        self.OverrideMousePos(bpos[0], bpos[1], bpos[2])

    @telemetry.ZONE_METHOD
    def OverrideMousePos(self, x, y, z):
        self.overrideMousePos = True
        self.overrideMousePosXYZ = (x, y, z)

    @telemetry.ZONE_METHOD
    def ReleaseOverrideMousePos(self):
        self.overrideMousePos = False
        self.overrideMousePosXYZ = (0.0, 0.0, 0.0)

    @telemetry.ZONE_METHOD
    def HighlightPreview(self, isMale = True):
        import time
        self.previewingHighlight = True
        start = time.time()
        self.highlightGhost.Start(self.avatar)
        self.bodyHighlightGhost.Start(self.avatar)
        if self.mode == 'sculpt':
            sequence = [10.1,
             11.1,
             17,
             13,
             1,
             15,
             2,
             3,
             4,
             12,
             18,
             5,
             14.1,
             7,
             9.1,
             8,
             6]
            for i, each in enumerate(sequence):
                self.highlightGhost.SetActiveZoneColor((2.0,
                 2.0,
                 2.0,
                 each * 10 / 255.0))
                while time.time() < start + (i + 1) / 3.0:
                    Yield(frameNice=False)

        else:
            numZones = 0
            if self.mode == 'hair':
                numZones = 2
                if isMale:
                    numZones = 3
            elif self.mode == 'bodyselect':
                numZones = 5
            elif self.mode == 'makeup':
                numZones = 3
            for i in range(numZones + 1):
                if self.mode == 'bodyselect':
                    self.bodyHighlightGhost.SetActiveZoneColor((1.0,
                     1.0,
                     1.0,
                     i * 10 / 255.0))
                else:
                    self.highlightGhost.SetActiveZoneColor((2.0,
                     2.0,
                     2.0,
                     i * 10 / 255.0))
                while time.time() < start + i / 3.0:
                    Yield(frameNice=False)

        self.highlightGhost.Stop()
        self.bodyHighlightGhost.Stop()
        self.previewingHighlight = False

    def KillHighlightPreview(self):
        self.previewingHighlight = False
        if self.highlightThread is not None:
            self.highlightThread.kill()

    def RunHighlightPreview(self, isMale = True):
        self.KillHighlightPreview()
        if self.useHighlighting:
            self.highlightThread = uthread.new(self.HighlightPreview, isMale)

    @telemetry.ZONE_METHOD
    def EndMotion(self, x, y):
        self.stopInteraction = False
        if self.mode == 'sculpt':
            self.avatar.animationUpdater.TogglePauseAnimations(False)
        for f in self.fieldResetData:
            pos = self.fieldResetData[f]
            field = None
            if self.mode == 'sculpt':
                if f in self.fieldData['Fields']:
                    field = self.fieldData['Fields'][f]
            elif self.mode == 'animation':
                if f in self.fieldDataAnimation['Fields']:
                    field = self.fieldDataAnimation['Fields'][f]
            if field:
                field['MarkerPosition'] = pos

        self.fieldResetData = {}
        self.startXY = None

    @telemetry.ZONE_METHOD
    def UpdateAnimation(self, values):
        doll = self.doll
        av = self.avatar
        if self.animationController is None or self.animationController.animationNetwork.avatar != av:
            self.animationController = AnimationController(av)
        for v in values:
            if v.endswith('_X') or v.endswith('_Y') or v.endswith('_Z'):
                baseName = v[:-2]
                self.animationController.SetControlParameter(baseName, (values[baseName + '_X'], values[baseName + '_Y'], values[baseName + '_Z']))
                break
            rightVersion = v.replace('Left', 'Right')
            if rightVersion != v:
                if self.poseSymmetric:
                    self.animationController.SetControlParameter(v, values[v])
                    self.animationController.SetControlParameter(rightVersion, values[v])
                elif self.pickedSide == 'left':
                    self.animationController.SetControlParameter(v, values[v])
                else:
                    self.animationController.SetControlParameter(rightVersion, values[v])
            else:
                self.animationController.SetControlParameter(v, values[v])

    @telemetry.ZONE_METHOD
    def UpdateBlendShapes(self, values, doUpdate = True):
        doll = self.doll
        mods = []
        for blendshapeCategory in BLENDSHAPE_CATEGORIES:
            modifiersByCategory = doll.buildDataManager.GetModifiersByCategory(blendshapeCategory)
            mods.extend(modifiersByCategory)

        cleanValues = {}
        valueThreshold = 0.0001
        if doll:
            av = self.avatar
            for v in iter(values):
                mod = (v + 'shape').lower()
                cleanValues[mod] = values[v]
                limit = doll.buildDataManager.modifierLimits.get(mod)
                if limit:
                    if cleanValues[mod] > limit[1]:
                        cleanValues[mod] = limit[1]
                    elif cleanValues[mod] < limit[0]:
                        cleanValues[mod] = limit[0]
                foundMod = False
                for m in iter(mods):
                    if mod == m.name:
                        m.weight = values[v]
                        foundMod = True
                        if values[v] < valueThreshold:
                            resPath = '{0}/{1}'.format(m.categorie, m.name)
                            doll.RemoveResource(resPath, self.factory)
                        break

                if not foundMod:
                    for zone in BODY_BLENDSHAPE_ZONES:
                        if zone.lower() in mod and cleanValues[mod] > valueThreshold:
                            resPath = '{0}/{1}'.format(DOLL_EXTRA_PARTS.BODYSHAPES, mod)
                            doll.AddResource(resPath, cleanValues[mod], self.factory)
                            foundMod = True
                            break

                if not foundMod:
                    for zone in HEAD_BLENDSHAPE_ZONES:
                        if zone.lower() in mod and cleanValues[mod] > valueThreshold:
                            resPath = '{0}/{1}'.format(HEAD_CATEGORIES.FACEMODIFIERS, mod)
                            doll.AddResource(resPath, cleanValues[mod], self.factory)
                            break

            if doUpdate:
                doll.Update(self.factory, avatar=av)
            for m in mods:
                if m.weight > 0 and m not in cleanValues:
                    limit = doll.buildDataManager.modifierLimits.get(m.name)
                    cleanValues[m.name] = m.weight
                    if limit:
                        if cleanValues[m.name] > limit[1]:
                            cleanValues[m.name] = limit[1]
                        elif cleanValues[m.name] < limit[0]:
                            cleanValues[m.name] = limit[0]

        pickAvatar = self.pickAvatar
        if pickAvatar:
            self.UpdatePickBlendshapes(pickAvatar, cleanValues)

    @telemetry.ZONE_METHOD
    def UpdatePickBlendshapes(self, avatar, values):
        meshGeometryResPaths = {}
        modifierList = self.doll.buildDataManager.GetSortedModifiers()
        for m in self.pickExtraMods:
            modifierList.append(m)

        for modifier in iter(modifierList):
            meshGeometryResPaths.update(modifier.meshGeometryResPaths)

        meshGeometryResPaths.update(self.pickAvatarPaths)
        meshes = avatar.Find('Trinity.Tr2Mesh')
        uthread.new(self.factory.ApplyMorphTargetsToMeshes, meshes, values, self.pickAvatarCache, meshGeometryResPaths)

    @telemetry.ZONE_METHOD
    def LoadMapping(self):
        self.mapping = {}
        self.mapping[0] = 'Nose'
        self.mapping[1] = 'NoseTip'
        self.mapping[2] = 'Nostrils'
        self.mapping[3] = 'CheeksUpper'
        self.mapping[4] = 'Jaw'
        self.mapping[5] = 'Chin'
        self.mapping[6] = 'MouthCorner'
        self.mapping[7] = 'LowerLip'
        self.mapping[8] = 'UpperLip'
        self.mapping[9] = 'InnerBrow'
        self.mapping[10] = 'OuterBrow'
        self.mapping[11] = 'Ears'
        self.mapping[12] = 'Eyes'
        self.mapping[13] = 'CheeksMiddle'
        self.mapping[14] = 'Nosebone'
        self.mapping[15] = 'EyesInner'
        self.mapping[16] = 'EyesOuter'
        self.mapping[17] = 'JawCheek'
        self.bodyMapping = {}
        self.bodyMapping[0] = 'Legs'
        self.bodyMapping[1] = 'Abs'
        self.bodyMapping[2] = 'Pelvis'
        self.bodyMapping[3] = 'Shoulders'
        self.bodyMapping[4] = 'Chest'
        self.bodyMapping[5] = 'Feet'
        self.bodyMapping[6] = 'Neck'

    def OnSculptFace(self, evt):
        self.mode = 'sculpt'

    def OnPoseFace(self, evt):
        self.mode = 'animation'
        self.poseSymmetric = True

    def OnPoseAsymFace(self, evt):
        self.mode = 'animation'
        self.poseSymmetric = False

    @telemetry.ZONE_METHOD
    def __init__(self, avatar = None, doll = None, scene = None, camera = None, factory = None, callback = None, viewProjCallback = None, mode = 'sculpt', pickCallback = None, inactiveZones = [], backbuffer = None):
        self.avatar = avatar
        self.doll = doll
        self.scene = scene
        self.head = ''
        self.gender = ''
        self.pickScene = None
        self.pickAvatar = None
        self.pickExtraMods = []
        self.pickAvatarCache = {}
        self.pickAvatarPaths = {}
        self.updateRenderjob = None
        self.backbuffer = backbuffer
        self.ready = False
        if camera:
            self.camera = camera
            self.GetProjectionAndViewMatrixFunc = self.GetProjectionAndViewMatrix
        if viewProjCallback:
            self.GetProjectionAndViewMatrixFunc = viewProjCallback
        self.factory = factory
        self.callback = callback
        self.pickCallback = pickCallback
        self.inactiveZones = inactiveZones
        self.keysDown = set()
        self.handlingMotion = False
        self.lastFrameSculpted = 0
        self.rightClick = False
        self.mode = None
        self.startXY = None
        self.direction = None
        self.pickedSide = None
        self.pickedMesh = 'head'
        self.zone = -1
        self.mapping = {}
        self.fieldData = None
        self.fieldDataAnimation = None
        self.stopInteraction = False
        self.finalAttrs = {}
        self.fieldResetData = {}
        self.fieldLKG = {}
        self.fieldLKGPos = {}
        self.markerCorrection = [0.0, 0.0]
        self.dirDict = {}
        self.LoadMapping()
        self.LoadFieldData()
        self.FillInFieldData()
        self.lightSettings = []
        self.poseSymmetric = False
        self.useHighlighting = True
        self.previewingHighlight = False
        self.highlightGhost = None
        self.highlightThread = None
        self.overrideMousePos = False
        self.overrideMousePosXYZ = (0.0, 0.0, 0.0)
        self.animationController = None
        self.PreloadZoneMaps(doll)
        self.Reset(doll, avatar, mode=mode, camera=camera, callback=callback, pickCallback=pickCallback, inactiveZones=inactiveZones)
        self.ready = True
        trinity.device.RegisterResource(self)

    @telemetry.ZONE_METHOD
    def PreloadZoneMaps(self, doll):
        textureRoot = 'R:/'
        textureSuffix = '.tga'
        if not legacy_r_drive.loadFromContent:
            textureRoot = 'res:/'
            textureSuffix = '.png'
        self.zoneMaps = {}
        self.highlightMaps = {}
        for each in ('hair', 'makeup', 'bodyselect', 'animation', 'default'):
            zonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/SculptZones' + textureSuffix
            headGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/male_head_fx' + textureSuffix
            bodyGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/male_body_fx' + textureSuffix
            if doll.gender == 'female':
                headGridPath = headGridPath.replace('male_', 'female_')
                bodyGridPath = bodyGridPath.replace('male_', 'female_')
            if headGridPath not in self.highlightMaps:
                self.highlightMaps[headGridPath] = blue.resMan.GetResource(headGridPath)
            if bodyGridPath not in self.highlightMaps:
                self.highlightMaps[bodyGridPath] = blue.resMan.GetResource(bodyGridPath)
            bodyZonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/BodySculptZones' + textureSuffix
            headTiling = 1
            bodyTiling = 1
            if each == 'hair':
                zonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/HairZones' + textureSuffix
                bodyZonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/EmptyZone' + textureSuffix
                headGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                bodyGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                headTiling = 40
                bodyTiling = 40
            elif each == 'makeup':
                zonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/MakeupZones' + textureSuffix
                bodyZonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/EmptyZone' + textureSuffix
                headGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                bodyGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                headTiling = 40
                bodyTiling = 40
            elif each == 'bodyselect':
                zonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/EmptyZone' + textureSuffix
                bodyZonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/BodySelectZones' + textureSuffix
                headGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                bodyGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/SelectGrid' + textureSuffix
                headTiling = 40
                bodyTiling = 40
            elif each == 'animation':
                zonePath = textureRoot + 'Graphics/Character/Global/FaceSetup/AnimZones' + textureSuffix
                headGridPath = textureRoot + 'Graphics/Character/Global/FaceSetup/male_head_Profile_fx' + textureSuffix
                if doll.gender == 'female':
                    headGridPath = headGridPath.replace('male_', 'female_')
                headTiling = 1
            zoneMap = trinity.Tr2HostBitmap()
            zoneMap.CreateFromFile(zonePath)
            bodyZoneMap = trinity.Tr2HostBitmap()
            bodyZoneMap.CreateFromFile(bodyZonePath)
            zoneSize = (0, 0)
            bodyZoneSize = (0, 0)
            self.zoneMaps[each] = (zonePath,
             headGridPath,
             bodyGridPath,
             headTiling,
             bodyTiling,
             bodyZonePath,
             zoneMap,
             zoneSize,
             bodyZoneMap,
             bodyZoneSize)

    def IsReady(self):
        return self.ready

    def IsDollDifferent(self, doll, avatar):
        retVal = False
        if avatar != self.avatar:
            self.avatar = avatar
            retVal = True
        head = doll.buildDataManager.GetModifiersByCategory('head')
        if not head == self.head:
            self.head = head
            retVal = True
        if not self.gender == doll.gender:
            self.gender = doll.gender
            retVal = True
        return retVal

    @telemetry.ZONE_METHOD
    def Reset(self, doll, avatar, camera = None, mode = 'sculpt', callback = None, pickCallback = None, inactiveZones = [], skipPickSceneReset = False):
        dollUpdated = self.IsDollDifferent(doll, avatar)
        self.doll = doll
        if self.pickAvatar:
            self.pickAvatar.animationUpdater = avatar.animationUpdater
        if self.mode == mode and not dollUpdated:
            return
        if camera is not None:
            self.camera = camera
        if (dollUpdated or not self.pickScene or mode != self.mode) and not skipPickSceneReset:
            self.SetupPickScene()
        self.avatar = avatar
        self.mode = mode
        self.inactiveZones = inactiveZones
        if pickCallback:
            self.pickCallback = pickCallback
        if callback:
            self.callback = callback
        if mode in self.zoneMaps:
            zonePath, headGridPath, bodyGridPath, headTiling, bodyTiling, bodyZonePath, self.zoneMap, self.zoneSize, self.bodyZoneMap, self.bodyZoneSize = self.zoneMaps[mode]
        else:
            zonePath, headGridPath, bodyGridPath, headTiling, bodyTiling, bodyZonePath, self.zoneMap, self.zoneSize, self.bodyZoneMap, self.bodyZoneSize = self.zoneMaps['default']
        self.zoneSize = (self.zoneMap.width, self.zoneMap.height)
        self.bodyZoneSize = (self.bodyZoneMap.width, self.bodyZoneMap.height)
        if self.useHighlighting:
            from eve.client.script.paperDoll.PaperdollSculptingGhost import PaperdollSculptingGhost
            self.highlightGhost = PaperdollSculptingGhost(zonePath=zonePath, texturePath=headGridPath, noisePath='res:/Texture/Global/noise.png', meshFilter=['head'], tiling=headTiling)
            self.bodyHighlightGhost = PaperdollSculptingGhost(zonePath=bodyZonePath, texturePath=bodyGridPath, noisePath='res:/Texture/Global/noise.png', meshFilter=['topinner',
             'bottominner',
             'hands',
             'feet',
             'dependantsnude'], ignoreZ=True, tiling=bodyTiling)

    @telemetry.ZONE_METHOD
    def Stop(self):
        self.mode = None
        if self.updateRenderjob:
            self.updateRenderjob.UnscheduleRecurring()
        self.updateRenderjob = None
        self.pickScene = None
        self.pickAvatar = None
        self.pickExtraMods = []
        self.pickAvatarCache = {}

    @telemetry.ZONE_METHOD
    def SetupPickScene(self, doUpdate = True):
        self.pickScene = trinity.Tr2InteriorScene()
        if hasattr(self.pickScene, 'updateShadowCubeMap'):
            self.pickScene.updateShadowCubeMap = False
        self.pickAvatarCache = {}
        self.pickAvatar = self.avatar.CopyTo()
        foundUpperNude = False
        foundLowerNude = False
        foundHead = False
        torsoClickable = False
        for meshIx in range(len(self.avatar.visualModel.meshes)):
            mesh = self.avatar.visualModel.meshes[meshIx]
            self.pickAvatar.visualModel.meshes[meshIx].SetGeometryRes(mesh.geometry)
            if mesh.name.startswith('topinner'):
                foundUpperNude = True
                if len(mesh.opaqueAreas):
                    torsoClickable |= True
            if mesh.name.startswith('bottominner'):
                foundLowerNude = True
            if mesh.name.startswith('head'):
                foundHead = True

        deleteList = []
        for mesh in self.pickAvatar.visualModel.meshes:
            if mesh.name.startswith('feet') or mesh.name.startswith('hands'):
                deleteList.append(mesh)

        for d in deleteList:
            self.pickAvatar.visualModel.meshes.remove(d)

        self.pickExtraMods = []
        if not foundUpperNude or not torsoClickable:
            deleteList = []
            for mesh in self.pickAvatar.visualModel.meshes:
                if mesh.name.startswith('topinner'):
                    deleteList.append(mesh)

            for d in deleteList:
                self.pickAvatar.visualModel.meshes.remove(d)

            torsoMod = self.factory.CollectBuildData(self.doll.gender, 'topinner/torso_nude')
            self.pickExtraMods.append(torsoMod)
            item = blue.resMan.LoadObject(torsoMod.redfile)
            if item:
                index = 1
                for m in item.meshes:
                    m.name = 'topinner' + str(index)
                    self.pickAvatar.visualModel.meshes.append(m)
                    torsoMod.meshGeometryResPaths[m.name] = m.geometryResPath
                    self.pickAvatarPaths[m.name] = m.geometryResPath
                    index += 1

        index = 1
        for armPart in ['dependants/sleeveslower/standard', 'dependants/sleevesupper/standard']:
            armMod = self.factory.CollectBuildData(self.doll.gender, armPart)
            self.pickExtraMods.append(armMod)
            item = blue.resMan.LoadObject(armMod.redfile)
            if item:
                for m in item.meshes:
                    m.name = 'dependantsnude' + str(index)
                    self.pickAvatar.visualModel.meshes.append(m)
                    armMod.meshGeometryResPaths[m.name] = m.geometryResPath
                    self.pickAvatarPaths[m.name] = m.geometryResPath
                    index += 1

        if not foundLowerNude:
            legMod = self.factory.CollectBuildData(self.doll.gender, 'bottominner/legs_nude')
            self.pickExtraMods.append(legMod)
            item = blue.resMan.LoadObject(legMod.redfile)
            if item:
                index = 1
                for m in item.meshes:
                    m.name = 'bottominner' + str(index)
                    self.pickAvatar.visualModel.meshes.append(m)
                    legMod.meshGeometryResPaths[m.name] = m.geometryResPath
                    self.pickAvatarPaths[m.name] = m.geometryResPath
                    index += 1

        if not foundHead:
            headMod = self.factory.CollectBuildData(self.doll.gender, 'head/head_generic')
            self.pickExtraMods.append(headMod)
            item = blue.resMan.LoadObject(headMod.redfile)
            if item:
                index = 1
                for m in item.meshes:
                    m.name = 'head' + str(index)
                    self.pickAvatar.visualModel.meshes.append(m)
                    headMod.meshGeometryResPaths[m.name] = m.geometryResPath
                    self.pickAvatarPaths[m.name] = m.geometryResPath
                    index += 1

        handMod = self.factory.CollectBuildData(self.doll.gender, 'hands/hands_nude')
        self.pickExtraMods.append(handMod)
        item = blue.resMan.LoadObject(handMod.redfile)
        if item:
            index = 1
            for m in item.meshes:
                m.name = 'hands' + str(index)
                self.pickAvatar.visualModel.meshes.append(m)
                handMod.meshGeometryResPaths[m.name] = m.geometryResPath
                self.pickAvatarPaths[m.name] = m.geometryResPath
                index += 1

        feetMod = self.factory.CollectBuildData(self.doll.gender, 'feet/feet_nude')
        self.pickExtraMods.append(feetMod)
        item = blue.resMan.LoadObject(feetMod.redfile)
        if item:
            index = 1
            for m in item.meshes:
                m.name = 'feet' + str(index)
                self.pickAvatar.visualModel.meshes.append(m)
                feetMod.meshGeometryResPaths[m.name] = m.geometryResPath
                self.pickAvatarPaths[m.name] = m.geometryResPath
                index += 1

        for mesh in self.pickAvatar.visualModel.meshes:
            MoveAreas(mesh.decalAreas, mesh.opaqueAreas)

        self.pickAvatar.animationUpdater = self.avatar.animationUpdater
        self.pickAvatar.worldTransformUpdater = self.avatar.worldTransformUpdater

        def Filter(mesh):
            for f in ['head',
             'topinner',
             'bottominner',
             'hands',
             'feet',
             'dependantsnude']:
                if mesh.name.lower().startswith(f):
                    return True

            return False

        index = 0
        remList = []
        for mesh in self.pickAvatar.visualModel.meshes:
            if not Filter(mesh):
                remList.append(mesh)

        for m in remList:
            self.pickAvatar.visualModel.meshes.remove(m)

        self.pickScene.AddDynamic(self.pickAvatar)
        self.pickScene.RebuildSceneData()
        cameraProj, cameraView = self.GetProjectionAndViewMatrixFunc()
        rj = trinity.CreateRenderJob('ProdPickScene')
        RT = trinity.Tr2RenderTarget(32, 32, 1, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
        depth = trinity.Tr2DepthStencil(32, 32, trinity.DEPTH_STENCIL_FORMAT.D24S8)
        rj.PushRenderTarget(RT)
        rj.PushDepthStencil(depth)
        rj.SetStdRndStates(trinity.RM_PICKING)
        rj.SetView(cameraView)
        rj.SetProjection(cameraProj)
        rj.Update(self.pickScene)
        rj.RenderScene(self.pickScene)
        rj.PopDepthStencil()
        rj.PopRenderTarget()
        rj.ScheduleOnce()
        trinity.renderJobs.UnscheduleByName('PickSceneUpdate')
        self.updateRenderjob = trinity.CreateRenderJob('PickSceneUpdate')
        self.updateRenderjob.SetView(cameraView)
        self.updateRenderjob.SetProjection(cameraProj)
        self.updateRenderjob.Update(self.pickScene)
        self.updateRenderjob.ScheduleRecurring()
        self.UpdateBlendShapes([], doUpdate=doUpdate)

    def KeyUpWrapper(self, key):
        self.keysDown.discard(key)

    def KeyDownWrapper(self, key):
        self.keysDown.add(key)

    @telemetry.ZONE_METHOD
    def LoadFieldData(self):
        self.fieldData = LoadYamlFileNicely('res:/Graphics/Character/Global/FaceSetup/TriangleFields.trif')
        self.fieldDataAnimation = LoadYamlFileNicely('res:/Graphics/Character/Global/FaceSetup/TriangleFieldsAnimation.trif')

    @telemetry.ZONE_METHOD
    def FillInFieldData(self):
        defaultFields = LoadYamlFileNicely('res:/Graphics/Character/Global/FaceSetup/DefaultFields.trif')
        import copy

        def FillInFields(mapping):
            for m in mapping:
                for var in ['Front', 'Side']:
                    fieldName = mapping[m] + '_' + var
                    if fieldName not in self.fieldData['Fields']:
                        defaultField = copy.deepcopy(defaultFields['Fields']['Default_' + var])
                        newAttr = []
                        for a in defaultField['Attributes']:
                            newAttr.append(a.replace('XXX', mapping[m]))

                        defaultField['Attributes'] = newAttr
                        for v in defaultField['VertData']:
                            for pair in defaultField['VertData'][v]:
                                pair[0] = pair[0].replace('XXX', mapping[m])

                        if False:
                            print 'New Field:'
                            print defaultField
                            print '-----------------------------------'
                        self.fieldData['Fields'][fieldName] = defaultField

        FillInFields(self.mapping)
        FillInFields(self.bodyMapping)

    @telemetry.ZONE_METHOD
    def CalcBaryCentric2DTriangle(self, corners, position):
        x = [position[0],
         corners[0][0],
         corners[1][0],
         corners[2][0]]
        y = [position[1],
         corners[0][1],
         corners[1][1],
         corners[2][1]]
        b0 = (x[2] - x[1]) * (y[3] - y[1]) - (x[3] - x[1]) * (y[2] - y[1])
        b1 = ((x[2] - x[0]) * (y[3] - y[0]) - (x[3] - x[0]) * (y[2] - y[0])) / b0
        b2 = ((x[3] - x[0]) * (y[1] - y[0]) - (x[1] - x[0]) * (y[3] - y[0])) / b0
        b3 = ((x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])) / b0
        return (b1, b2, b3)

    @telemetry.ZONE_METHOD
    def ProjectToTriangle(self, p, a, b, c):
        import geo2
        ab = geo2.Vec3Subtract(b, a)
        ac = geo2.Vec3Subtract(c, a)
        ap = geo2.Vec3Subtract(p, a)
        d1 = geo2.Vec3Dot(ab, ap)
        d2 = geo2.Vec3Dot(ac, ap)
        if d1 <= 0 and d2 <= 0:
            return (a, (1, 0, 0))
        bp = geo2.Vec3Subtract(p, b)
        d3 = geo2.Vec3Dot(ab, bp)
        d4 = geo2.Vec3Dot(ac, bp)
        if d3 >= 0 and d4 <= d3:
            return (b, (0, 1, 0))
        vc = d1 * d4 - d3 * d2
        if vc <= 0 and d1 >= 0 and d3 <= 0:
            v = d1 / (d1 - d3)
            vab = geo2.Vec3Scale(ab, v)
            return (geo2.Vec3Add(a, vab), (1.0 - v, v, 0))
        cp = geo2.Vec3Subtract(p, c)
        d5 = geo2.Vec3Dot(ab, cp)
        d6 = geo2.Vec3Dot(ac, cp)
        if d6 >= 0 and d5 <= d6:
            return (c, (0, 0, 1))
        vb = d5 * d2 - d1 * d6
        if vb <= 0 and d2 >= 0 and d6 <= 0:
            w = d2 / (d2 - d6)
            wac = geo2.Vec3Scale(ac, w)
            return (geo2.Vec3Add(a, wac), (1.0 - w, 0, w))
        va = d3 * d6 - d5 * d4
        if va <= 0 and d4 - d3 >= 0 and d5 - d6 >= 0:
            w = (d4 - d3) / (d4 - d3 + (d5 - d6))
            bc = geo2.Vec3Subtract(c, b)
            wcb = geo2.Vec3Scale(bc, w)
            return (geo2.Vec3Add(b, wcb), (0, 1.0 - w, w))
        denom = 1.0 / (va + vb + vc)
        v = vb * denom
        w = vc * denom
        abv = geo2.Vec3Scale(ab, v)
        acw = geo2.Vec3Scale(ac, w)
        r = geo2.Vec3Add(a, abv)
        r = geo2.Vec3Add(r, acw)
        return (r, (1.0 - v - w, v, w))

    @telemetry.ZONE_METHOD
    def CalculateClosestPosInField(self, position, field):

        def CalcDistance(v1, v2):
            val = math.sqrt(pow(v1[0] - v2[0], 2) + pow(v1[1] - v2[1], 2))
            return val

        pos = [position[0], position[2]]
        ret = None
        shortestDistance = 1000000.0
        for t in field['Tris']:
            internalPos = self.ProjectToTriangle(pos, t[0][1], t[1][1], t[2][1])[0]
            dist = CalcDistance(pos, internalPos)
            if dist < shortestDistance:
                shortestDistance = dist
                ret = internalPos

        return ret

    @telemetry.ZONE_METHOD
    def UpdateFields(self, fieldName, field, secondaryFieldName, secField, delta):
        threshold = 0.0001
        markerPos = field['MarkerPosition']
        if not len(markerPos) == 3:
            print 'Warning: Field ' + fieldName + ' passing in a 2D coordinate, not a 3D one: ' + str(markerPos)
            return {}
        moveScale = 0.03
        actualMarkerPos = [markerPos[0], markerPos[1], markerPos[2]]
        actualMarkerPos[0] += delta[0] * moveScale
        actualMarkerPos[2] += delta[1] * moveScale
        newMarkerPos = [actualMarkerPos[0], actualMarkerPos[1], actualMarkerPos[2]]
        newMarkerPos[0] += self.markerCorrection[0]
        newMarkerPos[2] += self.markerCorrection[1]
        tris = field['Tris']
        result = []
        for t in tris:
            points2D = [t[0][1], t[1][1], t[2][1]]
            a, b, c = self.CalcBaryCentric2DTriangle(points2D, (newMarkerPos[0], newMarkerPos[2]))
            if a >= 0 - threshold and b >= 0 - threshold and c >= 0 - threshold:
                result = [[t[0][0], a], [t[1][0], b], [t[2][0], c]]
                self.fieldLKG[fieldName] = result
                self.fieldLKGPos[fieldName] = newMarkerPos
                break

        if result != []:
            self.fieldResetData[fieldName] = newMarkerPos
        else:
            closestPos = self.CalculateClosestPosInField(newMarkerPos, field)
            for t in tris:
                points2D = [t[0][1], t[1][1], t[2][1]]
                a, b, c = self.CalcBaryCentric2DTriangle(points2D, closestPos)
                if a >= 0 - threshold and b >= 0 - threshold and c >= 0 - threshold:
                    result = [[t[0][0], a], [t[1][0], b], [t[2][0], c]]
                    self.fieldLKG[fieldName] = result
                    self.fieldLKGPos[fieldName] = closestPos
                    break

            self.fieldResetData[fieldName] = [closestPos[0], 0.0, closestPos[1]]
            self.markerCorrection = [closestPos[0] - actualMarkerPos[0], closestPos[1] - actualMarkerPos[2]]
        finalAttrs = {}
        newAttrs = {}
        for r in result:
            if r[0] in field['VertData']:
                attrs = field['VertData'][r[0]]
                weight = r[1]
                for a in attrs:
                    if a[0] in field['Attributes']:
                        if a[0] not in newAttrs:
                            newAttrs[a[0]] = weight * a[1]
                        else:
                            newAttrs[a[0]] += weight * a[1]

        for newAttr in newAttrs:
            finalAttrs[newAttr] = newAttrs[newAttr]

        if secField:
            secMarkerPos = list(secField['MarkerPosition'])
            if len(secMarkerPos) == 3:
                secMarkerPos[2] = newMarkerPos[2]
                tris = secField['Tris']
                result = []
                for t in tris:
                    points2D = [t[0][1], t[1][1], t[2][1]]
                    a, b, c = self.CalcBaryCentric2DTriangle(points2D, (secMarkerPos[0], secMarkerPos[2]))
                    if a >= 0 - threshold and b >= 0 - threshold and c >= 0 - threshold:
                        result = [[t[0][0], a], [t[1][0], b], [t[2][0], c]]
                        self.fieldLKG[secondaryFieldName] = result
                        self.fieldLKGPos[secondaryFieldName] = secMarkerPos

                if result != []:
                    self.fieldResetData[secondaryFieldName] = secMarkerPos
                elif secondaryFieldName in self.fieldLKG:
                    result = self.fieldLKG[secondaryFieldName]
                    self.fieldResetData[secondaryFieldName] = self.fieldLKGPos[secondaryFieldName]
                else:
                    print "Warning: Can't find secondary field in LKG!"
                secFinalAttrs = {}
                for r in result:
                    if r[0] in secField['VertData']:
                        attrs = secField['VertData'][r[0]]
                        weight = r[1]
                        for a in attrs:
                            if a[0] in secField['Attributes']:
                                if a[0] not in secFinalAttrs:
                                    secFinalAttrs[a[0]] = weight * a[1]
                                else:
                                    secFinalAttrs[a[0]] += weight * a[1]

                if secFinalAttrs != {}:
                    for a in secFinalAttrs:
                        if a in finalAttrs:
                            finalAttrs[a] = (finalAttrs[a] + secFinalAttrs[a]) / 2.0
                        else:
                            finalAttrs[a] = secFinalAttrs[a]

                else:
                    print 'Secondary out of range'
            else:
                print 'Warning: Secondary marker coordinate not 3 values.'
        return finalAttrs

    @telemetry.ZONE_METHOD
    def UpdateFieldAnimation(self, delta):
        mirror = True
        delta[0] = -delta[0]
        if self.pickedMesh == 'head':
            fieldName = self.mapping[self.zone]
        else:
            fieldName = 'Body'
        animFieldName = ''
        if fieldName == 'OuterBrow':
            animFieldName = 'EyebrowOuter'
        elif fieldName == 'InnerBrow':
            animFieldName = 'EyebrowInner'
        elif fieldName == 'Chin':
            animFieldName = 'Jaw'
            mirror = False
        elif fieldName == 'MouthCorner':
            animFieldName = 'MouthCorner'
        elif fieldName in ('EyesInner', 'EyesOuter'):
            animFieldName = 'EyeClose'
        elif fieldName == 'Eyes':
            animFieldName = 'EyeRotation'
            mirror = False
        elif fieldName == 'CheeksUpper':
            animFieldName = 'CheeksUpper'
        elif fieldName == 'UpperLip':
            animFieldName = 'UpperLip'
        elif fieldName == 'Jaw' or fieldName == 'JawCheek' or fieldName == 'Ears':
            animFieldName = 'Forehead'
            mirror = False
        elif fieldName == 'Body':
            animFieldName = 'Torso'
            mirror = False
        else:
            animFieldName = 'HeadLookAt'
            mirror = False
        if mirror and self.pickedSide == 'right':
            delta[0] = -delta[0]
        if animFieldName in self.fieldDataAnimation['Fields']:
            field = self.fieldDataAnimation['Fields'][animFieldName]
            secField = None
            attrs = self.UpdateFields(animFieldName, field, None, secField, delta)
            return attrs
        else:
            return

    @telemetry.ZONE_METHOD
    def UpdateField(self, delta):
        if self.zone not in self.mapping:
            return {}
        if self.pickedMesh == 'head':
            fieldName = self.mapping[self.zone]
        else:
            fieldName = 'Body'
            if self.zone in self.bodyMapping:
                fieldName = self.bodyMapping[self.zone]
        secondaryFieldName = ''
        if self.direction == 'left' or self.direction == 'right':
            secondaryFieldName = fieldName + '_Front'
            fieldName = fieldName + '_Side'
            if self.direction == 'left':
                delta[0] = -delta[0]
        else:
            secondaryFieldName = fieldName + '_Side'
            fieldName += '_Front'
            if self.pickedSide == 'left':
                delta[0] = -delta[0]
        if fieldName in self.fieldData['Fields']:
            field = self.fieldData['Fields'][fieldName]
            secField = None
            if secondaryFieldName in self.fieldData['Fields']:
                secField = self.fieldData['Fields'][secondaryFieldName]
            attrs = self.UpdateFields(fieldName, field, secondaryFieldName, secField, delta)
            return attrs
        return {}

    @telemetry.ZONE_METHOD
    def UpdateFieldsBasedOnExistingValues(self, doll):
        if not doll:
            return
        mods = doll.buildDataManager.GetModifiersAsList()
        fieldGroups = {}
        for m in mods:
            if len(m.name.split('_')) > 1:
                if m.categorie == 'facemodifiers' or m.categorie == 'bodyshapes':
                    group = m.name.split('_')[0]
                    if group not in fieldGroups:
                        fieldGroups[group] = {}
                    axisName = m.name.split('_')[1][:-5]
                    fieldGroups[group][axisName] = m.weight

        for f in self.fieldData['Fields']:
            type = f.split('_')[0].lower()
            direction = f.split('_')[1].lower()
            field = self.fieldData['Fields'][f]
            if type in fieldGroups:
                attrs = fieldGroups[type]
                x = 0.0
                y = 0.0
                for a in attrs:
                    if a == 'up':
                        y = attrs[a] * 2
                    elif a == 'down':
                        y = -attrs[a] * 2
                    elif a == 'left' and direction == 'front':
                        x = -attrs[a] * 2
                    elif a == 'right' and direction == 'front':
                        x = attrs[a] * 2
                    elif a == 'forward' and direction == 'side':
                        x = attrs[a] * 2
                    elif a == 'back' and direction == 'side':
                        x = -attrs[a] * 2

                newPos = [x, 0.0, y]
                field['MarkerPosition'] = newPos
                self.fieldResetData[f] = newPos
            else:
                newPos = [0, 0, 0]
                field['MarkerPosition'] = newPos
                self.fieldResetData[f] = newPos

        for meshPicked in ['head', 'body']:
            self.pickedMesh = meshPicked
            for z in range(20):
                self.zone = z
                self.UpdateField([0, 0])

        self.zone = 0
        result = self.UpdateField([0, 0])
