#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\scanHologramHandler.py
import math
import inventorycommon.const as invconst
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.uianimations import animations
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import GetScanRangeInMeters
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
from evegraphics.utils import BuildSOFDNAFromTypeID
import geo2
import blue
import uthread
import trinity
import dogma.const as dogmaconst
from eve.client.script.environment.sofService import GetSofService
IGNORE_CATEOGORIES = (invconst.categoryStarbase,
 invconst.categoryAsteroid,
 invconst.categoryOrbital,
 invconst.categorySovereigntyStructure,
 invconst.categoryStation,
 invconst.categoryStructure)
IGNORE_GROUPS = (invconst.groupStargate,)
DURATION = 0.2
THRESHOLD_LARGE = 2000
THRESHOLD_SMALL = 240.0
SIZE_SMALL = 1
SIZE_MEDIUM = 2
SIZE_LARGE = 3
MAX_IN_GROUP = {SIZE_SMALL: 5,
 SIZE_MEDIUM: 3,
 SIZE_LARGE: 1}
MAX_GROUPS = 3

class ScanHologramHandler(object):

    def __init__(self, scene, camera):
        self.scene = scene
        self.camera = camera
        self.hologramModels = []
        self.dScanResultIDs = []

    def RenderHolograms(self, results, egoPos, direction):
        typeIDs = self.GetTypeIDsToDisplay(results)
        if not typeIDs:
            return
        self.CleanUpHolograms()
        typeIDs.sort(key=self.GetTypeRadius, reverse=True)
        typeIDGroups = self.GetTypeIDGroups(typeIDs)
        blue.synchro.SleepWallclock(500)
        for typeIDGroup in typeIDGroups:
            PlaySound('msg_newscan_directional_scan_hologram_appear_play')
            models = self.ConstructAndPositionModels(typeIDGroup, egoPos, direction)
            for i, typeID in enumerate(typeIDGroup):
                model = models[i]
                uthread.new(self.AnimEnterHologram, model, direction, duration=DURATION)

            blue.synchro.SleepWallclock(1000 * (DURATION + 0.3))

    def RenderHologram(self, typeID, egoPos, direction, duration = DURATION):
        if not self.IsValidTypeID(typeID):
            return
        typeIDGroup = [typeID]
        models = self.ConstructAndPositionModels(typeIDGroup, egoPos, direction)
        self.AnimAppear(direction, models[0], animPos=False)

    def HideHologram(self):
        self.CleanUpHolograms()

    def GetTypeIDGroups(self, typeIDs):
        ret = []
        j = 0
        currGroup = None
        currSize = None
        for typeID in typeIDs:
            if currGroup is None:
                currGroup = []
                radius = self.GetTypeRadius(typeID)
                currSize = self.GetSize(radius)
            currGroup.append(typeID)
            if len(currGroup) == MAX_IN_GROUP[currSize]:
                ret.append(currGroup)
                currGroup = None
            if len(ret) == MAX_GROUPS:
                break

        if currGroup:
            ret.append(currGroup)
        return ret

    def GetSize(self, radius):
        if radius > THRESHOLD_LARGE:
            return SIZE_LARGE
        elif radius > THRESHOLD_SMALL:
            return SIZE_MEDIUM
        else:
            return SIZE_SMALL

    def IsValidTypeID(self, typeID):
        if evetypes.GetCategoryID(typeID) in IGNORE_CATEOGORIES:
            return False
        if evetypes.GetGroupID(typeID) in IGNORE_GROUPS:
            return False
        if not BuildSOFDNAFromTypeID(typeID):
            return False
        return True

    def GetTypeIDsToDisplay(self, results):
        resultIDs = [ result.id for result in results ]
        typeIDs = [ result.typeID for result in results if self.IsNewResult(result) and self.IsValidTypeID(result.typeID) ]
        self.dScanResultIDs = resultIDs
        return typeIDs

    def IsNewResult(self, result):
        return result.id not in self.dScanResultIDs

    def GetTypeRadius(self, typeID):
        godma = sm.GetService('godma')
        return godma.GetTypeAttribute(typeID, dogmaconst.attributeRadius)

    def ConstructAndPositionModels(self, typeIDGroup, egoPos, direction):
        models = [ self.ConstructHologramModel(typeID) for typeID in typeIDGroup ]
        numModels = len(models)
        xDir = geo2.Vec3Normalize(geo2.Vec3Cross(direction, (0, 1, 0)))
        yDir = geo2.Vec3Normalize(geo2.Vec3Cross(direction, xDir))
        for i, model in enumerate(models):
            self.SetModelRotation(model, direction)
            pos = self.GetModelPosition(model, direction, i, numModels, xDir, yDir)
            model.translationCurve.value = geo2.Vec3Add(egoPos, pos)

        return models

    def GetModelPosition(self, model, direction, i, numModels, xDir, yDir):
        shipRadius = model.GetBoundingSphereRadius()
        shipRadius = max(shipRadius, 18)
        p0 = geo2.Vec3Scale(direction, 13 + shipRadius + GetScanRangeInMeters() * SOLARSYSTEM_SCALE)
        offset = self.GetPositionOffset(i, numModels, 10 + 0.8 * shipRadius, xDir, yDir)
        if offset:
            p0 = geo2.Vec3Add(p0, offset)
        return p0

    def GetPositionOffset(self, i, numModels, r, xDir, yDir):
        if numModels == 1:
            return None
        else:
            theta = float(i) / numModels * 2 * math.pi
            x = geo2.Vec3Scale(xDir, r * math.cos(theta))
            y = geo2.Vec3Scale(yDir, r * math.sin(theta))
            return geo2.Vec3Add(x, y)

    def AnimEnterHologram(self, model, direction, duration = 1.0):
        self.AnimAppear(direction, model)
        blue.synchro.SleepWallclock(duration * 1000)
        self.AnimDisappear(direction, model)
        self.RemoveHologram(model)

    def AnimAppear(self, direction, model, animPos = True):
        if animPos:
            animDiff = geo2.Vec3Scale(direction, 5.0)
            pos = geo2.Vec3Add(model.translationCurve.value, animDiff)
            animations.MorphVector3(model.translationCurve, 'value', pos, model.translationCurve.value, duration=0.1)
        animations.MorphScalar(model, 'modelScale', 0.0, model.modelScale, duration=0.05)
        for j in xrange(2):
            animations.MorphScalar(model, 'activationStrength', 2.0, 1.3, duration=0.15, sleep=True)

    def AnimDisappear(self, direction, model):
        animDiff = geo2.Vec3Scale(direction, 30.0)
        pos = geo2.Vec3Subtract(model.translationCurve.value, animDiff)
        duration = 0.15
        animations.MorphVector3(model.translationCurve, 'value', model.translationCurve.value, pos, duration=duration)
        animations.MorphScalar(model, 'modelScale', model.modelScale, 0.0, duration=duration)
        animations.MorphScalar(model, 'activationStrength', 2.0, 0.0, duration=duration, sleep=True)

    def ConstructHologramModel(self, typeID):
        dna = BuildSOFDNAFromTypeID(typeID)
        if dna:
            sof = GetSofService().spaceObjectFactory
            model = sof.BuildFromDNA(dna + ':variant?dscan_hologram:class?mobile')
            model.translationCurve = trinity.Tr2TranslationAdapter()
            model.modelScale = 3.5 / model.boundingSphereRadius ** 0.6
            model.rotationCurve = trinity.Tr2RotationAdapter()
            model.activationStrength = 0.0
            self.scene.objects.append(model)
            self.hologramModels.append(model)
            return model

    def SetModelRotation(self, model, direction):
        quat = geo2.QuaternionRotationArc((0, 0, -1), direction)
        yaw, pitch, _ = geo2.QuaternionRotationGetYawPitchRoll(quat)
        quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0.0)
        model.rotationCurve.value = quat

    def CleanUpHolograms(self):
        for model in self.hologramModels:
            self.RemoveHologram(model)

        self.hologramModels = []

    def RemoveHologram(self, model):
        self.scene.objects.fremove(model)
