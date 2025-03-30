#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\environmentItemFactory.py
import trinity
from evegraphics.environments.graphicIDAttachments import GraphicIDAttachments
from evegraphics.environments.nebulaOverrides import NebulaOverrides
from fsdBuiltData.client.environmentTemplates import CLOUD_FIELD, POST_PROCESS, ENVIRONMENT_AUDIO, STATIC_PARTICLE_FIELD, DISTANCE_FIELD, CAMERA_ATTACHMENTS, NEBULA_OVERRIDES, GRAPHIC_ID_ATTACHMENTS
from evegraphics.environments.cloudField import CloudField
from evegraphics.environments.distanceField import DistanceField
from evegraphics.environments.postProcess import PostProcess, READ_ONLY_POSTPROCESS_MEMBERS
from evegraphics.environments.staticParticleField import StaticParticleField
from evegraphics.environments.environmentAudio import EnvironmentAudio
from evegraphics.environments.cameraAttachments import CameraAttachments
from fsd.schemas.loaders import VectorLoader
import logging
log = logging.getLogger(__name__)
POST_PROCESS_LERP_PARAMETERS = {'fog': ['minFogAmount',
         'maxFogAmount',
         'colorInfluence',
         'nebulaInfluence',
         'backgroundOcclusion',
         'brightnessAdjustmentAmount'],
 'godRays': ['intensity']}

def CreateStaticParticleField(staticParticleData):
    staticParticleField = StaticParticleField(staticParticleData.transformFile, staticParticleData.maxParticleCount, staticParticleData.particleMinSize, staticParticleData.particleMaxSize, staticParticleData.density, staticParticleData.staticClusters)
    return staticParticleField


def CreateCloudField(cloudFieldData):
    cloudField = CloudField(cloudFieldData)
    return cloudField


def CreateDistanceField(distanceFieldData):
    dimensions = getattr(distanceFieldData, 'dimensions', None)
    anchorBallDimensionMultiplication = getattr(distanceFieldData, 'anchorBallDimensionMultiplication', None)
    minDistance = getattr(distanceFieldData, 'minDistance', None)
    maxDistance = getattr(distanceFieldData, 'maxDistance', None)
    if dimensions:
        dimensions = tuple(dimensions)
    if anchorBallDimensionMultiplication:
        anchorBallDimensionMultiplication = tuple(anchorBallDimensionMultiplication)
    distanceField = DistanceField(distanceFieldData.distanceThreshold, distanceFieldData.timeAdjustmentSecondsIn, distanceFieldData.timeAdjustmentSecondsOut, position=(0, 0, 0), dimensions=dimensions, dynamicDimensions=distanceFieldData.dynamicDimensions, anchorBallDimensionMultiplication=anchorBallDimensionMultiplication, maxDistance=maxDistance, minDistance=minDistance)
    return distanceField


def GetParameterName(baseName, fsdName):
    return '%s%s' % (baseName, fsdName[0].upper() + fsdName[1:])


def GetPostProcessParameters(baseName, dataObject, ignoredAttributes):
    postProcessParameters = {}
    for parameterName in [ pn for pn in dir(dataObject) if not pn.startswith('_') and pn not in ignoredAttributes and pn not in READ_ONLY_POSTPROCESS_MEMBERS ]:
        value = getattr(dataObject, parameterName)
        if isinstance(value, VectorLoader):
            value = tuple(value)
        ppParameterName = GetParameterName(baseName, parameterName)
        log.debug('Setting PostProcessParemeter %s to %s', ppParameterName, str(value))
        postProcessParameters[ppParameterName] = value

    return postProcessParameters


def LerpExtractionMap():
    map = {'fog': ['colorInfluence',
             'nebulaInfluence',
             'backgroundOcclusion',
             'brightnessAdjustmentAmount'],
     'godRays': ['intensity'],
     'lut': ['influence'],
     'bloom': ['brightness', 'grimeWeight'],
     'dynamicExposure': ['exposureAdjust']}
    return map


def CreateLerpFromPostProcess(unsetPostProcess, postProcess):
    extraction = LerpExtractionMap()
    lerpDict = {}
    for k, v in extraction.iteritems():
        lerpDict[k] = {}
        p = getattr(postProcess, k, None)
        u = getattr(unsetPostProcess, k, None)
        if p is not None:
            if u is None:
                raise Exception('Unset post processing members should exist if it exists on loaded postprocess')
            for member in extraction[k]:
                max = None
                min = None
                if hasattr(p, member):
                    max = getattr(p, member)
                elif hasattr(u, member):
                    max = getattr(u, member)
                if hasattr(u, member):
                    min = getattr(u, member)
                if min is None and max is not None:
                    min = 0.0
                lerpDict[k][member] = (min, max)

    return lerpDict


def CreatePostProcess(postProcessData):
    if postProcessData.path is None:
        log.warning('The path for the post process has not been authored')
        return
    postprocess = trinity.Load(postProcessData.path, nonCached=PostProcess.DEBUG_MODE)
    if postprocess is None:
        log.warning("For some reason a loaded post process was None, it's path is: " + postProcessData.path)
        return
    unsetPostprocess = trinity.Tr2PostProcess2()
    for parameter in PostProcess.GetTr2PostProcess2Members():
        if getattr(postprocess, parameter, None) is not None:
            setattr(unsetPostprocess, parameter, type(getattr(postprocess, parameter))())

    lerpValues = CreateLerpFromPostProcess(unsetPostprocess, postprocess)
    ranges = postProcessData.ranges
    if ranges:
        if 'fog' in lerpValues and ranges.fog is not None:
            fogRange = ranges.fog
            lerpValues['fog']['totalAmount'] = (fogRange.min, fogRange.max)
        if 'bloom' in lerpValues and ranges.bloom is not None:
            bloomRange = ranges.bloom
            lerpValues['bloom']['brightness'] = (bloomRange.min, bloomRange.max)
    pp = PostProcess(postprocess, unsetPostprocess, lerpValues, getattr(postProcessData, 'useGodRaysSunColor', True))
    return pp


def CreateEnvironmentAudio(audioTriggers):
    audio = EnvironmentAudio(audioTriggers)
    return audio


def CreateCameraAttachments(camAttachmentsResPaths):
    camAttachments = CameraAttachments(camAttachmentsResPaths)
    return camAttachments


def CreateNebulaOverrides(nebulaOverrideInfo):
    return NebulaOverrides(nebulaOverrideInfo)


def CreateGraphicIDAttachements(graphicIDAttachement):
    foregroundGraphics = [ item.graphicID for item in graphicIDAttachement if not item.background ]
    backgroundGraphics = [ item.graphicID for item in graphicIDAttachement if item.background ]
    return GraphicIDAttachments(foregroundGraphics, backgroundGraphics)


ENVIRONMENT_FACTORY_OBJECTS = {STATIC_PARTICLE_FIELD: CreateStaticParticleField,
 CLOUD_FIELD: CreateCloudField,
 DISTANCE_FIELD: CreateDistanceField,
 POST_PROCESS: CreatePostProcess,
 ENVIRONMENT_AUDIO: CreateEnvironmentAudio,
 CAMERA_ATTACHMENTS: CreateCameraAttachments,
 NEBULA_OVERRIDES: CreateNebulaOverrides,
 GRAPHIC_ID_ATTACHMENTS: CreateGraphicIDAttachements}

def CreateEnvironmentItem(environmentType, environmentFsdInfo):
    if environmentType not in ENVIRONMENT_FACTORY_OBJECTS:
        raise KeyError("EnvironmentType '%s' does not map to a factory method" % environmentType)
    return ENVIRONMENT_FACTORY_OBJECTS[environmentType](environmentFsdInfo)
