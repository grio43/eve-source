#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\empireSelectionMapCamera.py
import math
import geo2
import evecamera
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.camera.mapCamera import MapCamera

class EmpireSelectionMapCamera(MapCamera):
    cameraID = evecamera.CAM_EMPIRESELECTIONMAP
    maxZoom = 1.0
    minZoom = 50000.0
    default_fov = 1.1
    kMaxPitch = math.pi / 4
    kMinPitch = 0.01
    kMaxAspectRatio = 2.2

    def __init__(self):
        super(EmpireSelectionMapCamera, self).__init__()
        self.verticalOffset = 0.075

    def AnimEntry(self, atPosition, duration = None):
        self.atPosition = atPosition
        self.eyePosition = geo2.Vec3Add(self.atPosition, (0, -4000, 50))
        animations.MorphScalar(self, 'yaw', self.yaw, self.yaw + 2 * math.pi, duration=120.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        if duration:
            animations.MorphScalar(self, 'zoomLinear', 0.01, 0.75, duration=duration)
            animations.MorphScalar(self, 'pitch', self.kMinPitch, 0.65, duration=duration, sleep=True)
            animations.MorphScalar(self, 'maxZoom', self.maxZoom, 10000, duration=0.3)
        else:
            self.zoomLinear = 0.75
            self.pitch = 0.65
            self.maxZoom = 10000

    def AnimZoomIn(self):
        animations.StopAllAnimations(self)
        animations.MorphScalar(self, 'zoomLinear', self.zoomLinear, 0.1, duration=0.5)
