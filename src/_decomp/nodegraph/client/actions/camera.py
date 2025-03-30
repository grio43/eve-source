#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\camera.py
import os
import math
import trinity
import logging
import uthread2
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from .base import Action
logger = logging.getLogger(__name__)

class CameraLookAtObject(Action):
    atom_id = 118

    def __init__(self, item_id = None, distance = None, **kwargs):
        super(CameraLookAtObject, self).__init__(**kwargs)
        self.item_id = item_id
        self.distance = distance

    def start(self, **kwargs):
        super(CameraLookAtObject, self).start(**kwargs)
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if camera:
            camera.LookAt(self.item_id, objRadius=self.distance)

    @classmethod
    def get_subtitle(cls, distance = None, **kwargs):
        if distance:
            return 'Distance: {}'.format(FmtDist(distance))
        return 'Distance: Object Radius'


class CameraLookAtSelf(CameraLookAtObject):
    atom_id = 119

    def start(self, **kwargs):
        self.item_id = session.shipid
        super(CameraLookAtSelf, self).start(**kwargs)


class CameraTrackObject(Action):
    atom_id = 120

    def __init__(self, item_id = None, duration = None, **kwargs):
        super(CameraTrackObject, self).__init__(**kwargs)
        self.item_id = item_id
        self.duration = self.get_atom_parameter_value('duration', duration)

    def start(self, **kwargs):
        super(CameraTrackObject, self).start(**kwargs)
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if camera:
            camera.Track(self.item_id, duration=self.duration)

    @classmethod
    def get_subtitle(cls, duration = None, **kwargs):
        return 'Duration: {}sec'.format(cls.get_atom_parameter_value('duration', duration))


class CameraTrackSelf(CameraTrackObject):
    atom_id = 121

    def start(self, **kwargs):
        self.item_id = session.shipid
        super(CameraTrackSelf, self).start(**kwargs)


class RestrictedCamera(Action):
    atom_id = 148

    def __init__(self, min_zoom = None, max_zoom = None, top_pitch_clamp_angle = None, bottom_pitch_clamp_angle = None, rotation_enabled = None, initial_zoom_distance = None, **kwargs):
        super(RestrictedCamera, self).__init__(**kwargs)
        self.initial_zoom_distance = self.get_atom_parameter_value('initial_zoom_distance', initial_zoom_distance)
        self.min_zoom = self.get_atom_parameter_value('min_zoom', min_zoom)
        self.max_zoom = self.get_atom_parameter_value('max_zoom', max_zoom)
        self.top_pitch_clamp_angle = self.get_atom_parameter_value('top_pitch_clamp_angle', top_pitch_clamp_angle)
        self.bottom_pitch_clamp_angle = self.get_atom_parameter_value('bottom_pitch_clamp_angle', bottom_pitch_clamp_angle)
        self.rotation_enabled = self.get_atom_parameter_value('rotation_enabled', rotation_enabled)

    def start(self, **kwargs):
        super(RestrictedCamera, self).start(**kwargs)
        if self.top_pitch_clamp_angle:
            min_pitch = self.top_pitch_clamp_angle / 180.0 * math.pi
        else:
            min_pitch = BaseSpaceCamera.kMinPitch
        if self.bottom_pitch_clamp_angle:
            max_pitch = (180 - self.bottom_pitch_clamp_angle) / 180.0 * math.pi
        else:
            max_pitch = BaseSpaceCamera.kMaxPitch
        sm.GetService('sceneManager').SwitchToRestrictedCamera(minZoom=self.min_zoom, maxZoom=self.max_zoom, minPitch=min_pitch, maxPitch=max_pitch, isRotationEnabled=self.rotation_enabled, initialZoomDistance=self.initial_zoom_distance)

    def stop(self):
        super(RestrictedCamera, self).stop()
        sm.GetService('sceneManager').SwitchFromRestrictedCamera()


class RestrictedCameraOff(Action):
    atom_id = 149

    def start(self, **kwargs):
        super(RestrictedCameraOff, self).start(**kwargs)
        sm.GetService('sceneManager').SwitchFromRestrictedCamera()


class LoadVirtualCamera(Action):
    atom_id = 257

    def __init__(self, graphic_id = None, position_anchor_ids = None, point_of_interest_anchor_ids = None, position_anchor_id = None, point_of_interest_anchor_id = None, **kwargs):
        self.graphic_id = graphic_id
        self.position_anchor_ids = set(position_anchor_ids or [])
        self.point_of_interest_anchor_ids = set(point_of_interest_anchor_ids or [])
        self.position_anchor_id = position_anchor_id
        self.point_of_interest_anchor_id = point_of_interest_anchor_id
        super(LoadVirtualCamera, self).__init__(**kwargs)

    def start(self, **kwargs):
        super(LoadVirtualCamera, self).start()
        position_anchor_ids = self.position_anchor_ids
        if self.position_anchor_id:
            position_anchor_ids.add(self.position_anchor_id)
        point_of_interest_anchor_ids = self.point_of_interest_anchor_ids
        if self.point_of_interest_anchor_id:
            point_of_interest_anchor_ids.add(self.point_of_interest_anchor_id)
        sceneManager = sm.GetService('sceneManager')
        camera = sceneManager.GetVirtualCamera()
        res_path = GetGraphicFile(self.graphic_id)
        logger.debug('LoadVirtualCamera start graphic_id=%s position_anchor_ids=%s point_of_interest_anchor_ids=%s res_path=%s', self.graphic_id, position_anchor_ids, point_of_interest_anchor_ids, res_path)
        try:
            vc = camera.vcsInterface.AddCameraFromFile(res_path)
            if vc:
                camera.vcsInterface.SetAnchorsFromItemIDs(vc, position_anchor_ids, point_of_interest_anchor_ids)
                logger.debug("LoadVirtualCamera loading camera '%s'", vc.name)
                return {'camera_name': vc.name}
        except RuntimeError as e:
            logger.exception("Error trying to load graphic id {} as a virtual camera.\nThe virtual camera system isn't correctly configured:\n\t{}".format(self.graphic_id, e.message.replace('\n', '\t')))

    @classmethod
    def get_subtitle(cls, graphic_id = None, **kwargs):
        if graphic_id:
            res_path = GetGraphicFile(graphic_id)
            camera = trinity.Load(res_path)
            if camera and camera.name:
                return camera.name
            else:
                return os.path.basename(res_path)
        return ''


class TransitionToVirtualCamera(Action):
    atom_id = 235

    def __init__(self, camera_name = None, transition_time = None, animation_timeline_override = None, **kwargs):
        self.camera_name = camera_name
        self.transition_time = self.get_atom_parameter_value('transition_time', transition_time)
        self.animation_timeline_override = self.get_atom_parameter_value('animation_timeline_override', animation_timeline_override)
        super(TransitionToVirtualCamera, self).__init__(**kwargs)

    def start(self, **kwargs):
        super(TransitionToVirtualCamera, self).start()
        sceneManager = sm.GetService('sceneManager')
        camera = sceneManager.GetVirtualCamera()
        sceneManager.SwitchToVirtualCamera()
        logger.debug('TransitionToVirtualCamera start camera_name=%s transition_time=%s animation_timeline_override=%s', self.camera_name, self.transition_time, self.animation_timeline_override)
        try:
            vc = camera.vcsInterface.FindCameraByName(self.camera_name)
            if not vc:
                sceneManager.SwitchFromVirtualCamera()
                logger.exception('No VirtualCamera could be found matching the name; {}'.format(self.camera_name))
                return
            if self.animation_timeline_override:
                vc.animationTimelineLength = self.animation_timeline_override
            if self.transition_time > 0:
                camera.vcsInterface.LerpToCamera(vc, self.transition_time)
            else:
                camera.vcsInterface.CutToCamera(vc)
            if self._on_end_callback:
                uthread2.sleep(self.transition_time + vc.animationTimelineLength)
        except RuntimeError as e:
            sceneManager.SwitchFromVirtualCamera()
            logger.exception("Error trying to transition to camera: {}.\nThe virtual camera system isn't correctly configured:\n\t{}".format(self.camera_name, e.message.replace('\n', '\t')))

        if self._on_end_callback:
            self._on_end()

    def stop(self, **kwargs):
        super(TransitionToVirtualCamera, self).stop()
        sm.GetService('sceneManager').SwitchFromVirtualCamera()

    @classmethod
    def get_subtitle(cls, camera_name = None, **kwargs):
        if camera_name:
            return camera_name
        return ''


class StartVirtualCameraSystem(Action):
    atom_id = 256

    def __init__(self, graphic_id = None, **kwargs):
        super(StartVirtualCameraSystem, self).__init__(**kwargs)
        self.graphic_id = graphic_id

    def start(self, **kwargs):
        super(StartVirtualCameraSystem, self).start()
        sceneManager = sm.GetService('sceneManager')
        camera = sceneManager.GetVirtualCamera()
        logger.debug('StartVirtualCameraSystem start graphic_id=%s', self.graphic_id)
        if self.graphic_id:
            try:
                camera.LoadVirtualCameraSystem(self.graphic_id)
            except RuntimeError as e:
                logger.exception("Error trying to load graphic id {} as a virtual camera system.\nThe virtual camera system isn't correctly configured:\n\t{}".format(self.graphic_id, e.message.replace('\n', '\t')))

    def stop(self, **kwargs):
        super(StartVirtualCameraSystem, self).stop()
        sceneManager = sm.GetService('sceneManager')
        if sceneManager:
            camera = sceneManager.GetVirtualCamera()
            if camera:
                camera.vcsInterface.Deactivate()

    @classmethod
    def get_subtitle(cls, graphic_id = None, **kwargs):
        if graphic_id:
            res_path = GetGraphicFile(graphic_id)
            camera = trinity.Load(res_path)
            if camera and camera.name:
                return camera.name
            else:
                return os.path.basename(res_path)
        return ''


class StopVirtualCameraSystem(Action):
    atom_id = 236

    def __init__(self, transition_time = None, move_previous_camera_to_virtual = None, **kwargs):
        super(StopVirtualCameraSystem, self).__init__(**kwargs)
        self.transition_time = self.get_atom_parameter_value('transition_time', transition_time)
        self.move_previous_camera_to_virtual = self.get_atom_parameter_value('move_previous_camera_to_virtual', move_previous_camera_to_virtual)

    def start(self, **kwargs):
        super(StopVirtualCameraSystem, self).start()
        sceneManager = sm.GetService('sceneManager')
        camera = sceneManager.GetVirtualCamera()
        logger.debug('StopVirtualCameraSystem transition_time=%s move_previous_camera_to_virtual=%s', self.transition_time, self.move_previous_camera_to_virtual)
        try:
            if self.transition_time > 0:
                camera.vcsInterface.LerpToCamera(camera.vcsInterface.externalCamera, self.transition_time)
            else:
                camera.vcsInterface.CutToCamera(camera.vcsInterface.externalCamera)
            if self.move_previous_camera_to_virtual:
                sceneManager.SnapLastCameraToVirtualCamera()
            if self._on_end_callback:
                uthread2.sleep(self.transition_time)
        except RuntimeError as e:
            logger.exception('Error trying to transition from the virtual camera and stop the virtual camera system.\nMost likely a knock on from earlier errors:\n\t{}'.format(e.message.replace('\n', '\t')))

        sceneManager.SwitchFromVirtualCamera()
        if self._on_end_callback:
            self._on_end()

    def stop(self, **kwargs):
        super(StopVirtualCameraSystem, self).stop()
        sm.GetService('sceneManager').SwitchFromVirtualCamera()


class RotateAndZoomCamera(Action):
    atom_id = 472

    def __init__(self, **kwargs):
        super(RotateAndZoomCamera, self).__init__(**kwargs)

    def start(self, **kwargs):
        super(RotateAndZoomCamera, self).start(**kwargs)
        cmd_svc = sm.GetService('cmd')
        cmd_svc.CmdZoomIn()
        cmd_svc.CmdZoomOut()
        sm.ScatterEvent('OnClientMouseSpinInSpace')
