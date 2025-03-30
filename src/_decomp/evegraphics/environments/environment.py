#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\environment.py
import geo2
from evegraphics.environments.distanceField import DistanceField
from evegraphics.environments.environmentItemFactory import CreateEnvironmentItem
from fsdBuiltData.client.environmentTemplates import GetAllEnvironmentModifiers, AVAILABLE_ATTRIBUTES, GetEnvironmentTemplate
import logging
log = logging.getLogger(__name__)

class Environment(object):

    def __init__(self, name, solarsystemId, center, anchorRadius = 0, anchorTranslationCurve = None):
        self.name = name
        self.center = center
        self.solarsystemId = solarsystemId
        self._subEnvironmentTypes = []
        self._audio = None
        self._distanceField = None
        self._postProcess = None
        self._cloudField = None
        self._staticParticleField = None
        self._cameraAttachments = None
        self._nebulaOverrides = None
        self._graphicIDAttachments = None
        self._radius = 0
        self._radiusSq = 0
        self._isActive = False
        self._templateID = -1
        self._debugObject = None
        self._anchorRadius = anchorRadius
        self._anchorTranslationCurves = [anchorTranslationCurve] if anchorTranslationCurve else []
        self._anchorIDs = set()
        self._systemWide = False
        self._subEnvironmentObjects = []

    def CreateFromTemplate(self, templateID):
        log.info("Creating environment %s up from template '%s'", self.name, templateID)
        self._templateID = templateID
        if isinstance(templateID, (int, long)):
            template = GetEnvironmentTemplate(templateID)
        else:
            template = templateID
        self._systemWide = template.isSystemWide
        self.radius = template.activationRadius
        self.subEnvironmentTypeIDs = template.subEnvironmentTypeIDs
        environmentTypes = GetAllEnvironmentModifiers(template)
        for environmentType, environmentValue in environmentTypes.iteritems():
            if not hasattr(self, environmentType):
                log.warning("Environment: cannot create environment of type '%s'", environmentType)
                continue
            setattr(self, environmentType, CreateEnvironmentItem(environmentType, environmentValue))

    @property
    def anchorRadius(self):
        return self._anchorRadius

    @anchorRadius.setter
    def anchorRadius(self, v):
        self._anchorRadius = v
        if self._distanceField is not None:
            self._distanceField.SetAnchorRadius(self._anchorRadius)

    @property
    def subEnvironmentTypeIDs(self):
        return self._subEnvironmentTypes

    @subEnvironmentTypeIDs.setter
    def subEnvironmentTypeIDs(self, v):
        self._subEnvironmentTypes = v

    @property
    def templateID(self):
        return self._templateID

    @property
    def systemWide(self):
        return self._systemWide

    @systemWide.setter
    def systemWide(self, v):
        if not isinstance(v, bool):
            raise TypeError("Environment: systemWide must be a 'bool', got %s" % v)
        self._systemWide = v

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, v):
        if not isinstance(v, (float, int)):
            raise TypeError("Environment: radius must be a 'float', got %s" % v)
        v = float(v)
        self._radius = v
        self._radiusSq = v * v

    @property
    def isActive(self):
        return self._isActive

    @property
    def staticParticleField(self):
        return self._staticParticleField

    @staticParticleField.setter
    def staticParticleField(self, v):
        self._staticParticleField = v

    @property
    def audioTriggers(self):
        return self._audio

    @audioTriggers.setter
    def audioTriggers(self, environmentAudio):
        self._audio = environmentAudio

    @property
    def distanceField(self):
        return self._distanceField

    @distanceField.setter
    def distanceField(self, environmentDistanceField):
        if environmentDistanceField is not None and not isinstance(environmentDistanceField, DistanceField):
            raise TypeError("DistanceField must be of type None or %s, not '%s'" % (str(DistanceField), str(environmentDistanceField.__class__)))
        self._distanceField = environmentDistanceField
        if self._distanceField is not None:
            self._distanceField.SetAnchorRadius(self._anchorRadius)

    @property
    def cloudField(self):
        return self._cloudField

    @cloudField.setter
    def cloudField(self, environmentCloudField):
        self._cloudField = environmentCloudField

    @property
    def postProcess(self):
        return self._postProcess

    @postProcess.setter
    def postProcess(self, environmentPostProcess):
        self._postProcess = environmentPostProcess

    @property
    def cameraAttachments(self):
        return self._cameraAttachments

    @cameraAttachments.setter
    def cameraAttachments(self, cameraAttachments):
        self._cameraAttachments = cameraAttachments

    @property
    def nebulaOverrides(self):
        return self._nebulaOverrides

    @nebulaOverrides.setter
    def nebulaOverrides(self, nebulaOverrides):
        self._nebulaOverrides = nebulaOverrides

    @property
    def graphicIDAttachments(self):
        return self._graphicIDAttachments

    @graphicIDAttachments.setter
    def graphicIDAttachments(self, graphicIDAttachments):
        self._graphicIDAttachments = graphicIDAttachments

    @property
    def anchorIDs(self):
        return self._anchorIDs

    def Update(self, cameraPos):
        self._isActive = self.InRange(cameraPos)

    def DistanceFrom(self, pos):
        return geo2.Vec3Distance(pos, self.center)

    def DistanceSqFrom(self, pos):
        return geo2.Vec3DistanceSq(pos, self.center)

    def InRange(self, pos):
        if pos is None:
            return False
        return self.systemWide or geo2.Vec3DistanceSq(pos, self.center) < self._radiusSq

    def AddEnvironmentAnchorID(self, anchorID, anchorTranslationCurve):
        self._anchorIDs.add(anchorID)
        if anchorTranslationCurve:
            self._anchorTranslationCurves.append(anchorTranslationCurve)

    def RemoveEnvironmentAnchorID(self, anchorID):
        if anchorID in self._anchorIDs:
            self._anchorIDs.remove(anchorID)

    def AddEnvironmentObjects(self, environmentObjects):
        if not self.isActive:
            return []
        newEnvironmentObjects = [ o for o in environmentObjects if self.InRange(o.position) and o.typeID in self.subEnvironmentTypeIDs ]
        self._subEnvironmentObjects.extend(newEnvironmentObjects)
        if self.staticParticleField is not None and self.distanceField is not None and self.staticParticleField.IsReady():
            self.staticParticleField.AddObjects(newEnvironmentObjects)
            self.staticParticleField.LinkToDistanceField(self.distanceField)
            log.debug('AddEnvironmentObjects: added %s environment objects to %s', len(newEnvironmentObjects), self.name)
            return self._subEnvironmentObjects
        return []

    def GetLockedAttributes(self):
        for environmentType in AVAILABLE_ATTRIBUTES:
            attribute = getattr(self, environmentType, None)
            if attribute is None:
                continue
            yield (environmentType, attribute.GetLockedAttributes())

    def SetIgnoredAttributes(self, ignoredAttributes):
        for environmentType, attributes in ignoredAttributes.iteritems():
            environmentObject = getattr(self, environmentType, None)
            if environmentObject:
                environmentObject.SetIgnoredAttributes(attributes)

    def Setup(self, camera, renderJob):
        log.info('Setting up environment %s', self.name)
        for environmentType in AVAILABLE_ATTRIBUTES:
            if getattr(self, environmentType, None) is None:
                continue
            environmentItem = getattr(self, environmentType)
            if environmentItem.IsDisabled():
                log.info('%s is disabled' % environmentType)
                continue
            environmentItem.SetEnvironmentPosition(self.center)
            environmentItem.SetEnvironmentTranslationCurves(self._anchorTranslationCurves)
            environmentItem.SetEnvironmentRadius(self.radius)
            environmentItem.Setup()
            environmentItem.ApplyToCamera(camera)
            environmentItem.ApplyToRenderJob(renderJob)
            environmentItem.ApplyToScene()

        if self.distanceField is not None:
            if self.cloudField is not None:
                self.cloudField.LinkToDistanceField(self.distanceField)
            if self.postProcess is not None:
                self.postProcess.LinkToDistanceField(self.distanceField)
            if self.staticParticleField is not None:
                self.staticParticleField.AddObjects(self._subEnvironmentObjects)
                self.staticParticleField.LinkToDistanceField(self.distanceField)
            for curve in self._anchorTranslationCurves:
                self.distanceField.AddBallToField(curve)

        elif self.postProcess is not None:
            self.postProcess.ApplyLerpValues()

    def TearDown(self):
        log.info('Tearing down environment %s', self.name)
        for environmentType in AVAILABLE_ATTRIBUTES:
            if getattr(self, environmentType, None) is not None:
                getattr(self, environmentType).TearDown()

        self._subEnvironmentObjects = []

    def CreateFromExisting(self, existingEnvironment):
        log.info("Creating environment %s up from existing item '%s'", self.name, existingEnvironment.name)
        self._templateID = existingEnvironment.templateID
        self._systemWide = existingEnvironment.systemWide
        self.radius = existingEnvironment.radius
        self.subEnvironmentTypeIDs = existingEnvironment.subEnvironmentTypeIDs
        for attribute in AVAILABLE_ATTRIBUTES:
            setattr(self, attribute, getattr(existingEnvironment, attribute, None))


class EnvironmentObject(object):

    def __init__(self, typeID, position, radius, ball = None):
        self.typeID = typeID
        self.position = position
        self.radius = radius
        self.ball = ball
