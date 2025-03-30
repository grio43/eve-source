#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\cameraLimitation.py
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import logging
import math
from spacecomponents.client.messages import MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
from spacecomponents.common.components.component import Component
import uthread2
logger = logging.getLogger(__name__)

class CameraLimitation(Component):

    def __init__(self, item_id, type_id, attributes, component_registry):
        Component.__init__(self, item_id, type_id, attributes, component_registry)
        logger.debug('adding CameraLimitation component to item=%s of type=%s', item_id, type_id)
        self._set_pitch(attributes)
        self._set_zoom(attributes)
        self._set_controls(attributes)
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self._on_added_to_space)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self._on_removed_from_space)
        self.sceneManager = sm.GetService('sceneManager')

    def _set_pitch(self, attributes):
        topPitchClampAngle = getattr(attributes, 'topPitchClampAngle', None)
        if topPitchClampAngle is None:
            self.minPitch = BaseSpaceCamera.kMinPitch
        else:
            self.minPitch = topPitchClampAngle / 180.0 * math.pi
        bottomPitchClampAngle = getattr(attributes, 'bottomPitchClampAngle', None)
        if bottomPitchClampAngle is None:
            self.maxPitch = BaseSpaceCamera.kMaxPitch
        else:
            self.maxPitch = (180 - bottomPitchClampAngle) / 180.0 * math.pi

    def _set_zoom(self, attributes):
        self.minZoom = getattr(attributes, 'minZoom', None)
        self.maxZoom = getattr(attributes, 'maxZoom', None)

    def _set_controls(self, attributes):
        self.isRotationEnabled = getattr(attributes, 'isRotationEnabled', True)

    def _switch_to_restricted_camera(self):
        self.sceneManager.SwitchToRestrictedCamera(self.minZoom, self.maxZoom, self.minPitch, self.maxPitch, self.isRotationEnabled)

    def _switch_from_restricted_camera(self):
        self.sceneManager.SwitchFromRestrictedCamera()

    def _on_added_to_space(self, slimItem):
        uthread2.start_tasklet(self._switch_to_restricted_camera)

    def _on_removed_from_space(self):
        uthread2.start_tasklet(self._switch_from_restricted_camera)
