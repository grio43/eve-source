#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\distanceField.py
import trinity
from evegraphics.environments import BaseEnvironmentObject
import logging
DEFAULT_DISTANCE_FIELD_PATH = 'res:/dx9/scene/asteroidDistanceField.red'
DF_BINDING_FOG_AMOUNT = 'FogAmount'
DF_BINDING_FOG_CENTER = 'FogCenter'
DF_BINDING_FOG_SIZE = 'FogSize'
DF_BINDING_GOD_RAY_INTENSITY = 'GodRayIntensity'
DF_BINDING_CLOUD_FIELD_INTENSITY = 'CloudfieldIntensity'
log = logging.getLogger(__name__)

class DistanceField(BaseEnvironmentObject):

    def __init__(self, distanceThreshold, timeAdjustmentSecondsIn, timeAdjustmentSecondsOut, position = (0, 0, 0), dimensions = None, dynamicDimensions = False, anchorBallDimensionMultiplication = None, maxDistance = None, minDistance = None):
        super(DistanceField, self).__init__()
        self.distanceField = None
        self.distanceCurve = None
        self.distanceThreshold = distanceThreshold
        self.timeAdjustmentSecondsIn = timeAdjustmentSecondsIn
        self.timeAdjustmentSecondsOut = timeAdjustmentSecondsOut
        self.dimensions = dimensions
        self.dynamicDimensions = dynamicDimensions
        self.distanceFieldOffset = position
        self.anchorBallDimensionMultiplication = anchorBallDimensionMultiplication
        self.maxDistance = maxDistance
        self.minDistance = minDistance

    def SetAnchorRadius(self, radius):
        if self.anchorBallDimensionMultiplication is not None:
            self.dimensions = tuple([ radius * i for i in self.anchorBallDimensionMultiplication ])

    def Setup(self):
        log.debug('Setting up distance field')
        self.distanceField = trinity.EveDistanceField()
        if self.dynamicDimensions:
            self.distanceField.SetupDynamicDistanceField(self.distanceThreshold, self.timeAdjustmentSecondsOut, self.timeAdjustmentSecondsIn)
        else:
            distanceFieldPosition = tuple([ x + y for x, y in zip(self.distanceFieldOffset, self.GetLocalEnvironmentPosition()) ])
            self.distanceField.SetupStaticDistanceField(self.dimensions or (0.0, 0.0, 0.0), distanceFieldPosition, self.distanceThreshold, self.timeAdjustmentSecondsOut, self.timeAdjustmentSecondsIn)
        if self.maxDistance is not None:
            self.distanceField.maxDistance = self.maxDistance
        else:
            self.distanceField.maxDistance = self.environmentRadius * 0.7
        if self.minDistance is not None:
            self.distanceField.minDistance = self.minDistance
        self.distanceCurve = self.distanceField.curveSet.curves.FindByName('DistanceCurve')

    def ApplyToCamera(self, camera):
        self.distanceField.cameraView = camera.viewMatrix

    def ApplyToScene(self):
        self.scene.distanceFields.append(self.distanceField)

    def AddPyBinding(self, bindingName, destinationObject, destinationAttribute, sourceObject, sourceAttribute):
        self._AddBinding(bindingName, destinationObject, destinationAttribute, sourceObject, sourceAttribute, trinity.Tr2PyValueBinding)

    def AddTriBinding(self, bindingName, destinationObject, destinationAttribute, sourceObject, sourceAttribute):
        self._AddBinding(bindingName, destinationObject, destinationAttribute, sourceObject, sourceAttribute, trinity.TriValueBinding)

    def _AddBinding(self, bindingName, destinationObject, destinationAttribute, sourceObject, sourceAttribute, bindingType):
        binding = self.distanceField.curveSet.bindings.FindByName(bindingName)
        needToAddBinding = binding is None
        if needToAddBinding:
            binding = bindingType()
            binding.name = bindingName
        binding.sourceObject = sourceObject
        binding.sourceAttribute = sourceAttribute
        binding.destinationObject = destinationObject
        binding.destinationAttribute = destinationAttribute
        if needToAddBinding:
            self.distanceField.curveSet.bindings.append(binding)

    def AddBallToField(self, ball):
        if ball and self.distanceField and ball not in self.distanceField.objects:
            self.distanceField.objects.append(ball)

    def TearDown(self):
        log.debug('Tearing down distance field')
        if self.scene and self.distanceField in self.scene.distanceFields:
            self.scene.distanceFields.remove(self.distanceField)
        if self.distanceField and self.distanceField.curveSet:
            while len(self.distanceField.curveSet.curves) > 0:
                self.distanceField.curveSet.curves.pop()

            while len(self.distanceField.curveSet.bindings) > 0:
                self.distanceField.curveSet.bindings.pop()

        del self.distanceField
        self.distanceField = None
        self.scene = None
