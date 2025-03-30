#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\planet.py
import random
import datetime
import math
import blue
import evetypes
import trinity
import uthread
import pytelemetry.zoning as telemetry
import eve.common.lib.appConst as appConst
import carbon.common.lib.const as const
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.parklife.environmentSvc import GetEnvironmentService
from eve.common.script.sys.idCheckers import IsEmpireSystem
import inventorycommon.typeHelpers
from fsdBuiltData.common.graphicIDs import GetGraphicFile
import evegraphics.effects as gfxeffects
from moonmining.const import MOON_CRATER_SLIMITEM_NAME
from sovereignty.resource.shared.planetary_resources_cache import DataUnavailableError
AURORA_PERIOD = (302400.0, 561600.0)
AURORA_DURATION = (510.0, 930.0)

def _FindAuroraCurveSet(model):
    for cs in model.Find('trinity.TriCurveSet'):
        if cs.name == 'PlayAurora':
            return cs


def _StartAurora(model, rand, length, offset):
    cs = _FindAuroraCurveSet(model)
    if not cs:
        return
    seedCurve = cs.curves.FindByName('AuroraSeed')
    if seedCurve:
        seedCurve.value = (rand.random(),
         rand.random(),
         rand.random(),
         rand.random())
    cs.scale = 1.0 / length
    cs.PlayFrom(offset * cs.scale)


def _AuroraTasklet(itemID, model):
    if not _FindAuroraCurveSet(model.object):
        return
    r = random.Random()
    r.seed(itemID)
    period = blue.os.TimeFromDouble(r.uniform(*AURORA_PERIOD))
    while model.object:
        t = blue.os.GetWallclockTime()
        phase = t % period
        r.seed(itemID + t / period)
        duration = blue.os.TimeFromDouble(r.uniform(*AURORA_DURATION))
        if phase < duration:
            _StartAurora(model.object, r, blue.os.TimeAsDouble(duration), blue.os.TimeAsDouble(phase))
        wait = blue.os.TimeAsDouble(period - phase)
        blue.synchro.Sleep(min(wait, 82800) * 1000)


def GetTimeUntilNextAurora(itemID):
    r = random.Random()
    r.seed(itemID)
    period = blue.os.TimeFromDouble(r.uniform(*AURORA_PERIOD))
    t = blue.os.GetWallclockTime()
    phase = t % period
    r.seed(itemID + t / period)
    duration = blue.os.TimeFromDouble(r.uniform(*AURORA_DURATION))
    if phase < duration:
        return 0.0
    return blue.os.TimeAsDouble(period - phase)


UNLOADED = 0
TEXTURES_UNLOADED = 1
LOADED = 2

class Planet(SpaceObject):
    __notifyevents__ = ['OnSlimItemUpdated']

    def __init__(self):
        SpaceObject.__init__(self)
        self.isInflightPlanet = True
        self.attributes = None
        self.largeTextures = False
        self._crater = None
        self.itemID = None
        self.impactDirection = (0, 0, 0)
        self.impactStartTime = 0
        self.chunk = None
        self._auroraTasklet = None
        if not hasattr(self, 'typeData'):
            self.typeData = {}
        self.OnSlimItemUpdated(self.typeData.get('slimItem'))
        sm.RegisterNotify(self)

    def OnSlimItemUpdated(self, item):
        celestialEffect = getattr(item, 'celestialEffect', None)
        if celestialEffect is not None:
            effectGuid, graphicInfo = celestialEffect
            self.logger.debug('Planet.OnSlimItemUpdated found celestialEffect %s %s', effectGuid, graphicInfo)
            sm.ScatterEvent('OnSpecialFX', self.id, None, None, None, None, effectGuid, False, 1, True, graphicInfo=graphicInfo)
        if getattr(item, MOON_CRATER_SLIMITEM_NAME, None) is not None:
            self.impactDirection, self.impactStartTime, chunkID = getattr(item, MOON_CRATER_SLIMITEM_NAME)
            self.chunk = sm.GetService('michelle').GetBall(chunkID)
            if self.chunk is None or not hasattr(self.chunk, 'GetModel'):
                return
            if self.chunk.GetModel() is None:
                self.chunk.RegisterForModelLoad(self._SpawnImpactCraterFromSlimItemUpdate)
            else:
                self._SpawnImpactCraterFromSlimItemUpdate()

    def Display(self, display = 1, canYield = True):
        pass

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        uthread.new(self.LoadPlanet)

    def _IsMoon(self):
        return evetypes.GetGroupID(self.typeID) == appConst.groupMoon

    def _ApplyPlanetRotation(self, model):
        if self._IsMoon():
            return
        rotationDirection = 1
        if self.id % 2:
            rotationDirection = -1
        r = random.Random()
        r.seed(self.id)
        rotationTime = r.random() * 2000 + 3000
        curve = trinity.Tr2CurveEulerRotation()
        curve.SetExtrapolation(trinity.Tr2CurveExtrapolation.CYCLE)
        curve.yaw.AddKey(0.0, math.radians(1.0), trinity.Tr2CurveInterpolation.LINEAR)
        curve.yaw.AddKey(rotationTime, math.radians(rotationDirection * 360.0), trinity.Tr2CurveInterpolation.LINEAR)
        tilt = r.random() * 60.0 - 30.0
        curve.pitch.AddKey(0.0, math.radians(1.0))
        curve.pitch.AddKey(6000.0, math.radians(tilt))
        curve.pitch.AddKey(12000.0, 0.0)
        model.rotationCurve = trinity.Tr2RotationAdapter()
        model.rotationCurve.curve = curve

    def _GetModelPath(self):
        graphicFile = self.typeData.get('graphicFile')
        if self.largeTextures:
            graphicFile = graphicFile.replace('.red', '_HI.red')
        return graphicFile

    @telemetry.ZONE_METHOD
    def LoadPlanet(self, itemID = None, forPhotoService = False, rotate = True, hiTextures = False, notifyLoaded = True):
        if itemID is None:
            itemID = self.id
        self.itemID = itemID
        fsdData = cfg.mapSolarSystemContentCache.celestials[self.itemID]
        if self.attributes is None:
            self.attributes = fsdData.planetAttributes
        if hasattr(fsdData, 'environmentTemplateID'):
            GetEnvironmentService().AddBallEnvironment(self, fsdData.environmentTemplateID)
        self.largeTextures = hiTextures
        self.isInflightPlanet = not forPhotoService
        self.model = trinity.Load(self._GetPresetPath())
        if self.model is None:
            self.logger.error('No planet was loaded! %s', self._GetPresetPath())
            return
        self._SetupPlanet(planet=self.model, itemID=itemID, rotate=rotate)
        self.model.StartControllers()
        if self.isInflightPlanet:
            scene = self.spaceMgr.GetScene()
            if scene is not None:
                scene.planets.append(self.model)
        if notifyLoaded:
            self.NotifyModelLoaded()

    def GetTimeUntilNextAurora(self):
        return GetTimeUntilNextAurora(self.itemID)

    def ForceAuroraNow(self):
        if self._auroraTasklet:
            self._auroraTasklet.kill()
            self._auroraTasklet = None
        duration = random.uniform(*AURORA_DURATION)
        _StartAurora(self.model, random, duration, duration / 4.0)

    def _SetupTraffic(self, itemID):
        bp = getattr(self, 'ballpark', None)
        populationLevel = 1.0
        if bp is None or self.model is None:
            return
        solarSystemId = bp.solarsystemID
        if IsEmpireSystem(solarSystemId):
            populationLevel = 10.0
        else:
            try:
                colonyResourcesSvc = sm.GetService('sovereigntyResourceSvc')
                workforce = colonyResourcesSvc.GetPlanetWorkforceProduction(itemID)
                if workforce > 0 and workforce is not None:
                    workforceConfigurations = colonyResourcesSvc.GetAllPlanetWorkforceProduction()
                    max_workforce = max(workforceConfigurations.values())
                    if max_workforce > 0:
                        populationLevel = float(workforce) / float(max_workforce) * 10
                elif itemID % 100 > 0:
                    populationLevel = itemID % 100 / 10
            except DataUnavailableError as e:
                self.logger.warning('planet._SetupTraffic failed to get colony data')

        if self.model is not None and hasattr(self.model, 'SetControllerVariable'):
            self.model.SetControllerVariable('populationLevel', int(populationLevel))

    @telemetry.ZONE_METHOD
    def _SetupPlanet(self, planet, itemID, rotate):
        if rotate:
            self._ApplyPlanetRotation(planet)
        planet.translationCurve = self
        planet.scaling = (self.radius, self.radius, self.radius)
        planet.radius = self.radius
        planet.name = '%d' % itemID
        self.model.SetControllerVariable('radius', self.radius)
        if self.typeID == appConst.typePlanetOcean or self.typeID == appConst.typePlanetSandstorm or self.typeID == appConst.typePlanetEarthlike:
            uthread.new(self._SetupTraffic, itemID)
        gfx = inventorycommon.typeHelpers.GetGraphic(self.typeID)
        if hasattr(gfx, 'albedoColor') and gfx.albedoColor:
            planet.albedoColor = tuple(gfx.albedoColor)
        if hasattr(gfx, 'emissiveColor') and gfx.emissiveColor:
            planet.emissiveColor = tuple(gfx.emissiveColor)
        self._ModifyPlanetShader()
        self.SetEffectParameters()
        sm.GetService('audio').SetupPlanet3DAudio(planet, self.typeID)
        self._auroraTasklet = uthread.new(_AuroraTasklet, itemID, blue.BluePythonWeakRef(planet))

    def Release(self, origin = None):
        if self._auroraTasklet:
            self._auroraTasklet.kill()
            self._auroraTasklet = None
        scene = self.spaceMgr.GetScene()
        if scene:
            scene.planets.fremove(self.model)
        SpaceObject.Release(self, 'Planet')

    def RemoveFromScene(self, model, scene = None):
        pass

    @staticmethod
    def GetPlanetByID(itemID, typeID):
        planet = Planet()
        planet.logger.debug('GetPlanetByID called')
        planet.typeID = typeID
        planet.LoadPlanet(itemID, True, notifyLoaded=False)
        return planet

    def SetEffectParameters(self):
        planetParent = self._GetPlanetParent()
        if not planetParent:
            return
        for effect in planetParent.Find('trinity.Tr2Effect'):
            param1 = trinity.TriTextureParameter()
            param1.name = 'NormalHeight1'
            param1.resourcePath = GetGraphicFile(self._GetHeightMap1())
            effect.resources.append(param1)
            param2 = trinity.TriTextureParameter()
            param2.name = 'NormalHeight2'
            param2.resourcePath = GetGraphicFile(self._GetHeightMap2())
            effect.resources.append(param2)
            param3 = trinity.Tr2FloatParameter()
            param3.name = 'Random'
            param3.value = float(self.itemID % 100)
            effect.parameters.append(param3)
            ind = -1
            for r in range(0, len(effect.resources)):
                resource = effect.resources[r]
                if resource.name.lower() == 'heightmap':
                    ind = r

            if ind > 0:
                effect.resources.removeAt(ind)

    def _GetAttribute(self, name):
        if self.attributes is None:
            raise RuntimeError('Planet was not loaded. Can not get population of an unloaded planet.')
        try:
            return getattr(self.attributes, name)
        except:
            self.logger.exception('Could not get attribute population. %s', str(self.attributes))

    def _GetPopulation(self):
        return self._GetAttribute('population')

    def _GetShaderPreset(self):
        return self._GetAttribute('shaderPreset')

    def _GetPresetPath(self):
        presetPath = self._GetModelPath() if self._GetShaderPreset() is None else GetGraphicFile(self._GetShaderPreset())
        return presetPath

    def _GetHeightMap1(self):
        return self._GetAttribute('heightMap1')

    def _GetHeightMap2(self):
        return self._GetAttribute('heightMap2')

    def _GetPlanetParent(self):
        return self.model.effectChildren.FindByName('Planet')

    def _GetPlanetShaderResources(self, paramName = ''):
        retList = []
        if not self.model:
            return retList
        planetParent = self.model
        if planetParent is not None:
            for param in planetParent.Find('trinity.TriTextureParameter'):
                if paramName == param.name or paramName == '':
                    retList.append(param)

        return retList

    def _ModifyPlanetShaderParameter(self, paramName, x = None, y = None, z = None, w = None):
        if not self.model:
            return
        planetParent = self._GetPlanetParent()
        if not planetParent:
            return
        for effect in planetParent.Find('trinity.Tr2Effect'):
            for i, param in enumerate(effect.constParameters):
                name, value = param
                if name == paramName:
                    value = list(value)
                    if x is not None:
                        value[0] = x
                    if y is not None:
                        value[1] = y
                    if z is not None:
                        value[2] = z
                    if w is not None:
                        value[3] = w
                    effect.constParameters.removeAt(i)
                    effect.constParameters.append((name, tuple(value)))
                    effect.RebuildCachedData()
                    break

            for param in effect.parameters:
                if param.name == paramName:
                    if isinstance(param, trinity.Tr2FloatParameter):
                        if x is not None:
                            param.value = x
                    else:
                        if x is not None:
                            param.x = x
                        if y is not None:
                            param.y = y
                        if z is not None:
                            param.z = z
                        if w is not None:
                            param.w = w
                    break

    def _ModifyPlanetShader(self):
        if self.typeID == appConst.typePlanetEarthlike or self.typeID == appConst.typePlanetSandstorm:
            self.RandomizeShaderClouds()
        if self.typeID is appConst.typePlanetOcean or self.typeID is appConst.typePlanetEarthlike:
            self.AdjustShaderPopulation()

    def AdjustShaderPopulation(self):
        if self._GetPopulation() == 0:
            for textureParamName in ['CityLight', 'CityDistributionTexture', 'CityDistributionMask']:
                textureParamList = self._GetPlanetShaderResources(textureParamName)
                for textureParam in textureParamList:
                    textureParam.resourcePath = ''

            self._ModifyPlanetShaderParameter('CoverageFactors', w=0.0)

    def RandomizeShaderClouds(self):
        now = datetime.datetime.now()
        r = random.Random()
        r.seed(now.year + now.month * 30 + now.day + self.itemID)
        val = r.randint(1, 5)
        useDense = val % 5 == 0
        if self.typeID == appConst.typePlanetEarthlike:
            if useDense:
                cloudMapIDs = (3857, 3858, 3859, 3860)
                cloudCapMapIDs = (3861, 3862, 3863, 3864)
            else:
                cloudMapIDs = (3848, 3849, 3851, 3852)
                cloudCapMapIDs = (3853, 3854, 3855, 3856)
        else:
            cloudMapIDs = (3956, 3957, 3958, 3959)
            cloudCapMapIDs = (3960, 3961, 3962, 3963)
        cloudMapIdx = r.randint(0, 3)
        cloudCapMapIdx = r.randint(0, 3)
        cloudCapTexResPath = GetGraphicFile(cloudCapMapIDs[cloudCapMapIdx])
        cloudTexResPath = GetGraphicFile(cloudMapIDs[cloudMapIdx])
        cloudCapParamList = self._GetPlanetShaderResources('CloudCapTexture')
        for cloudCapParam in cloudCapParamList:
            cloudCapParam.resourcePath = cloudCapTexResPath

        cloudParamList = self._GetPlanetShaderResources('CloudsTexture')
        for cloudParam in cloudParamList:
            cloudParam.resourcePath = cloudTexResPath

        cloudsBrightness = r.random() * 0.4 + 0.6
        cloudsTransparency = r.random() * 2.0 + 1.0
        self._ModifyPlanetShaderParameter('CloudsFactors', y=cloudsBrightness, z=cloudsTransparency)

    def SpawnImpactCrater(self, direction, size, timeFromStart):
        uthread.new(self._SpawnImpactCrater, direction, size, timeFromStart)

    def _SpawnImpactCrater(self, direction, size, timeFromStart):
        self.RemoveImpactCrater()
        radians = None
        if size is not None:
            size = max(0.0, min(1.0, 0.5 * size / self.radius))
            radians = math.asin(size) * 2
        pin = trinity.Load('res:/fisfx/structure/moonmining/moonmining_surfacecrater_01a.red')
        pin.centerNormal = direction
        if radians is not None:
            pin.pinRadius = radians
            pin.pinMaxRadius = radians
        self._crater = pin
        while self.GetModel() is None or len(self.GetModel().effectChildren) < 1:
            blue.synchro.Sleep(100)

        for curveSet in self._crater.curveSets:
            curveSet.PlayFrom(timeFromStart)

        self.GetModel().effectChildren.append(self._crater)

    def RemoveImpactCrater(self):
        model = self.GetModel()
        if model is not None and self._crater is not None:
            if self._crater in model.effectChildren:
                model.effectChildren.remove(self._crater)
            self._crater = None

    def _SpawnImpactCraterFromSlimItemUpdate(self):
        currentSimTime = blue.os.GetSimTime()
        size = 2.0 * self.chunk.GetModel().boundingSphereRadius
        self.SpawnImpactCrater(self.impactDirection, size, float((currentSimTime - self.impactStartTime) / const.SEC))

    def _ApplyCraterEffectAttributes(self):
        if not self.model:
            return
        planetParent = self._GetPlanetParent()
        if not planetParent:
            return
        for effect in planetParent.Find('trinity.Tr2Effect'):
            gfxeffects.ApplyEffectOverride(self._crater.pinEffect, effect)

    def SetImpactIntensity(self, value):
        if self._crater is None:
            return
        effect = self._crater.pinEffect
        gfxeffects.SetParameterComponentValue(effect, 'IntensityParameters', value, componentIndex=0)
