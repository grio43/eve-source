#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\cloudField.py
import trinity
from evegraphics.environments import BaseEnvironmentObject
import evegraphics.settings as gfxsettings
import logging
DEFAULT_CLOUDFIELD_PATH = 'res:/dx9/scene/asteroidcloudfield.red'
CF_COLOR2_EFFECT_PARAMETER = 'Color2'
log = logging.getLogger(__name__)

class CloudField(BaseEnvironmentObject):

    def __init__(self, cloudFieldResPath):
        super(CloudField, self).__init__(cloudFieldResPath)
        self.cloudField = None
        self.cloudFieldResPath = cloudFieldResPath

    def IsDisabled(self):
        return gfxsettings.Get(gfxsettings.UI_ASTEROID_ATMOSPHERICS) == 0

    def ApplyToScene(self):
        if self.IsDisabled():
            return
        self.scene.cameraAttachments.append(self.cloudField)

    def Setup(self):
        log.debug("Creating a cloudfield with path='%s'", self.cloudFieldResPath)
        self.cloudField = self.Load(self.cloudFieldResPath)

    def LinkToDistanceField(self, distanceFieldEnvironmentItem):
        if self.IsDisabled():
            return
        if self.cloudField is None:
            log.debug('Could not link cloudfield to distancecurve, cloudField is None')
            return
        for each in self.cloudField.Find('trinity.Tr2Vector4Parameter'):
            if each.name == 'Color2':
                distanceFieldEnvironmentItem.AddTriBinding('CloudfieldIntensity', each, 'value.w', distanceFieldEnvironmentItem.distanceCurve, 'currentValue')
                break

    def TearDown(self):
        log.debug('Tearing down cloudfield')
        if self.scene is None:
            return
        self.scene.cameraAttachments.fremove(self.cloudField)
        del self.cloudField
        self.cloudField = None
        self.scene = None
