#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\postProcess.py
import copy
import logging
import blue
import evegraphics.settings as gfxsettings
import trinity
import uthread2
from evegraphics.environments import BaseEnvironmentObject
from fsdBuiltData.common.graphicIDs import GetAlbedoColor
log = logging.getLogger(__name__)
FOG_PARAMETER = 'fog'
INTENSITY_THRESHOLD = 1e-06
FOG_FADE_IN_TIME_MS = 1500.0
READ_ONLY_POSTPROCESS_MEMBERS = ['luts',
 'whiteTemperature',
 'whiteTint',
 'colorSaturation',
 'colorContrast',
 'colorGamma',
 'colorGain',
 'colorOffset']

class PostProcess(BaseEnvironmentObject):
    __defaultValues__ = None
    __postProcessParameters__ = None

    def __init__(self, postProcess, unsetPostprocess, lerpValues, useSunColor):
        super(PostProcess, self).__init__()
        self._postProcess = postProcess
        self._unsetPostprocess = unsetPostprocess
        self._intensity = 0
        self._setup = False
        self._size = (0, 0, 0)
        self._midpoint = (0, 0, 0)
        self._fadeTaskelt = None
        self._lerpValues = lerpValues
        lerpParameters = [ name for name in self._lerpValues.keys() ]
        self._lerpParameters = {}
        self.usedPostProcessParameters = self._FindUsedPostProcessParameters(lerpParameters, lerpValues)
        self._usedLerpParameters = self._lerpParameters
        self._useSunColor = useSunColor

    @property
    def postProcess(self):
        return self._postProcess

    @postProcess.setter
    def postProcess(self, value):
        self._postProcess = value
        self._updateLerpParamsAndValues()

    def _updateLerpParamsAndValues(self):
        from evegraphics.environments.environmentItemFactory import CreateLerpFromPostProcess
        self._resetUnsetPostProcess()
        self._lerpValues = CreateLerpFromPostProcess(self._unsetPostprocess, self._postProcess)
        self._lerpParameters = {}
        self.usedPostProcessParameters = self._FindUsedPostProcessParameters(self._lerpValues.keys(), self._lerpValues)
        self._usedLerpParameters = self._lerpParameters

    def _resetUnsetPostProcess(self):
        unsetPostprocess = trinity.Tr2PostProcess2()
        for parameter in PostProcess.GetTr2PostProcess2Members():
            if getattr(self._postProcess, parameter, None) is not None:
                setattr(unsetPostprocess, parameter, type(getattr(self._postProcess, parameter))())

        self._unsetPostprocess = unsetPostprocess

    def Setup(self):
        pass

    def IsDisabled(self):
        return gfxsettings.Get(gfxsettings.GFX_POST_PROCESSING_QUALITY) == 0

    def GetDefaultValues(self):
        if PostProcess.__defaultValues__ is None:
            PostProcess.__defaultValues__ = trinity.Load('res:/dx9/postprocess/DefaultPostProcessingSettings.red')
        return PostProcess.__defaultValues__

    @classmethod
    def GetTr2PostProcess2Members(cls):
        if PostProcess.__postProcessParameters__ is None:
            pp = trinity.Tr2PostProcess2()
            PostProcess.__postProcessParameters__ = [ attr for attr in pp.__members__ if not attr.startswith('_') and attr not in READ_ONLY_POSTPROCESS_MEMBERS ]
        return PostProcess.__postProcessParameters__

    def ApplyLerpValues(self):
        if self._usedLerpParameters and self.postProcess is not None and self.scenePostProcess is not None:
            for key, value in self._lerpValues.iteritems():
                if value is None:
                    continue
                member = getattr(self.scenePostProcess, key)
                if member is None:
                    continue
                for subKey, subValue in value.iteritems():
                    if subValue is None:
                        continue
                    min, max = subValue
                    if max is not None:
                        setattr(member, subKey, max)

    def ApplyToScene(self):
        if self.scenePostProcess is not None:
            if self.IsDisabled():
                return
            if self.postProcess.godRays is not None and self._useSunColor and self.InClientMode():
                flareGraphicID = cfg.mapSystemCache[session.solarsystemid].sunFlareGraphicID
                rayColor = GetAlbedoColor(flareGraphicID)
                self.postProcess.godRays.godRayColor = (rayColor[0],
                 rayColor[1],
                 rayColor[2],
                 rayColor[3])
            for member in self.GetTr2PostProcess2Members():
                try:
                    if member not in self.usedPostProcessParameters:
                        continue
                    newPPVal = getattr(self.postProcess, member, None)
                    if newPPVal is not None:
                        setattr(self.scenePostProcess, member, newPPVal.CopyTo())
                except ValueError as ex:
                    log.error('Error when applying post processing to scene' + ex.message)

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, v):
        self.testWrapper(v)

    def testWrapper(self, v):
        if self._setup and abs(self._intensity - v) < INTENSITY_THRESHOLD:
            return
        self._intensity = v
        for parentKey, parentValue in self._usedLerpParameters.iteritems():
            for postProcessObjectKey in parentValue:
                minValue, maxValue = self._lerpValues[parentKey][postProcessObjectKey]
                if minValue is None or maxValue is None:
                    continue
                value = minValue + self._intensity * (maxValue - minValue)
                postProcessMember = getattr(self.scenePostProcess, parentKey)
                if postProcessMember is not None:
                    setattr(postProcessMember, postProcessObjectKey, value)

        self._setup = True

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, v):
        if all([ old == new for old, new in zip(self._size, v) ]):
            return
        self._size = v
        setattr(self.scenePostProcess.fog, 'areaSize', (self._size[0], self._size[1], self._size[2]))

    @property
    def midpoint(self):
        return self._midpoint

    @midpoint.setter
    def midpoint(self, v):
        if all([ old == new for old, new in zip(self._midpoint, v) ]):
            return
        self._midpoint = v
        setattr(self.scenePostProcess.fog, 'areaCenter', self._midpoint)

    def GetLockedAttributes(self):
        lockedAttributes = dict()
        lockedAttributes['lockedLerp'] = copy.deepcopy(self._lerpParameters)
        lockedPostProcess = []
        for member in self.GetTr2PostProcess2Members():
            if getattr(self.postProcess, member, None) is None:
                continue
            lockedPostProcess.append(member)

        lockedAttributes['lockedPostProcess'] = lockedPostProcess
        if FOG_PARAMETER in self._lerpParameters and len(self._lerpParameters['fog']) > 0:
            lockedAttributes['lockedLerp']['fog'] += ['areaCenter', 'areaSize', 'intensity']
        return lockedAttributes

    @property
    def scenePostProcess(self):
        return getattr(self.scene, 'postprocess', None)

    def SetIgnoredAttributes(self, attributes):
        usedPostProcessParameters = list()
        for member in self.GetTr2PostProcess2Members():
            memVal = getattr(self.postProcess, member, None)
            if memVal is None or member in attributes['lockedPostProcess']:
                continue
            usedPostProcessParameters.append(member)

        self.usedPostProcessParameters = usedPostProcessParameters
        usedLerpParameters = dict()
        lockedLerpAttributes = attributes['lockedLerp']
        for k, v in self._lerpParameters.iteritems():
            if k not in lockedLerpAttributes:
                usedLerpParameters[k] = v
                continue
            lockedValuesForKey = lockedLerpAttributes[k]
            for value in v:
                if value not in lockedValuesForKey:
                    if k not in usedLerpParameters:
                        usedLerpParameters[k] = []
                    usedLerpParameters[k].append(value)

        self._usedLerpParameters = usedLerpParameters

    def LinkToDistanceField(self, distanceFieldEnvironmentItem):
        if self.IsDisabled() or self.scenePostProcess is None:
            return
        distanceFieldEnvironmentItem.AddPyBinding('Intensity', self, 'intensity', distanceFieldEnvironmentItem.distanceCurve, 'currentValue')
        if FOG_PARAMETER in self.usedPostProcessParameters:
            distanceFieldEnvironmentItem.AddPyBinding('FogCenter', self, 'midpoint', distanceFieldEnvironmentItem.distanceField, 'midpoint')
            distanceFieldEnvironmentItem.AddPyBinding('FogSize', self, 'size', distanceFieldEnvironmentItem.distanceField, 'dimensions')
            self._fadeTaskelt = uthread2.start_tasklet(self._DoFogFadeIn)

    def _DoFogFadeIn(self):
        time0 = blue.os.GetSimTime()
        fadeIn = 0.0
        if not hasattr(self.scenePostProcess, 'fog') or not hasattr(self.postProcess, 'fog'):
            log.error('Missing fog postprocess member when attempting to start fog fade in ')
        self.scenePostProcess.fog.intensity = 0.0
        maxFogValue = min(1.0, self.postProcess.fog.intensity)
        while fadeIn < maxFogValue:
            blue.synchro.Yield()
            timeNow = blue.os.GetSimTime()
            diff = blue.os.TimeDiffInMs(time0, timeNow)
            fadeIn = max(0.0, min(1.0, diff / FOG_FADE_IN_TIME_MS))
            fadeIn = fadeIn * fadeIn * (3 - 2 * fadeIn)
            if self.scenePostProcess is not None and hasattr(self.scenePostProcess, 'fog'):
                self.scenePostProcess.fog.intensity = fadeIn
            else:
                raise AttributeError('Missing fog on scene post process when fading in')

        self._fadeTaskelt = None

    def Refresh(self):
        if self.IsDisabled():
            return
        for key, value in self.usedPostProcessParameters.iteritems():
            setattr(self.scenePostProcess, key, value)

    def TearDown(self):
        if self.postProcess and self.scenePostProcess is not None:
            defaultValues = self.GetDefaultValues()
            for member in self.GetTr2PostProcess2Members():
                try:
                    if member not in self.usedPostProcessParameters:
                        continue
                    guard = 'GUARD_VALUE'
                    defaultPPMember = getattr(defaultValues, member, guard)
                    if defaultPPMember is guard:
                        continue
                    if self.scenePostProcess is not None:
                        setattr(self.scenePostProcess, member, defaultPPMember)
                except ValueError as ex:
                    log.error('Error when tearing down post processing and setting them to default values with ex ' + ex.message)

        self._intensity = 0
        self._setup = False
        self._size = (0, 0, 0)
        self._midpoint = (0, 0, 0)
        if self._fadeTaskelt is not None:
            self._fadeTaskelt.kill()
            self._fadeTaskelt = None
        self.scene = None

    def _FindUsedPostProcessParameters(self, lerpParameters, lerpValues):
        for k in lerpParameters:
            self._lerpParameters[k] = []
            for key in lerpValues[k].keys():
                self._lerpParameters[k].append(key)

        usedPostProcessParameters = list()
        for member in self.GetTr2PostProcess2Members():
            memVal = getattr(self.postProcess, member, None)
            if memVal is None:
                continue
            usedPostProcessParameters.append(member)

        return usedPostProcessParameters
