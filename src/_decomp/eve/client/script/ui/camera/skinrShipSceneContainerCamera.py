#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\skinrShipSceneContainerCamera.py
import blue
import geo2
import math
from bisect import bisect_left
from carbonui import const as uiconst
from carbonui.uicore import uicore
from cosmetics.client.ships.skins.live_data import current_skin_design
from cosmetics.common.ships.skins.static_data.slot_name import PATTERN_SLOT_IDS, PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.camera.sceneContainerCamera import SceneContainerCamera
from eve.client.script.ui.cosmetics.ship.pages.studio import studioSettings
from eve.client.script.ui.cosmetics.ship.pages.studio.studioSettings import pattern_rotation_follow_camera_setting
ROLL_SNAP_STEP = 15

class YawPitchCamera(Camera):
    kOrbitSpeed = 10.0
    kMinPitch = 0.001
    kMaxPitch = math.pi - kMinPitch


class SkinrShipSceneContainerCamera(SceneContainerCamera):
    kFovSpeed = 7.0
    roll_snap_angles = [ x for x in range(-180, 180 + ROLL_SNAP_STEP, ROLL_SNAP_STEP) ]
    roll_snap_delay = 50.0
    roll_snap_timestamp = blue.os.GetSimTime()

    def __init__(self):
        SceneContainerCamera.__init__(self)
        self.kFovSpeed = 5.0
        self.cameraBasedProjectionThread = None
        self.patternTwist = 0.0
        self.model = None
        self.currentModKeyOrbitalModeHorizontal = True
        self.inputConsistencyCounter = 5.0
        self.yaw_pitch_camera = YawPitchCamera()
        self.yaw_pitch_camera.on_eye_position_changed.connect(self.on_yaw_pitch_camera_eye_position_changed)
        self.yaw_pitch_camera.on_orbit_end.connect(self.on_yaw_pitch_camera_orbit_end)
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnMouseDown)
        studioSettings.pattern_rotation_follow_camera_setting.on_change.connect(self.on_pattern_rotation_follow_camera_setting)

    def on_yaw_pitch_camera_orbit_end(self):
        current_skin_design.add_to_undo_history()

    def Update(self):
        super(SkinrShipSceneContainerCamera, self).Update()
        self.yaw_pitch_camera.Update()

    def on_yaw_pitch_camera_eye_position_changed(self, value):
        component_instance = self.get_pattern_component_instance()
        if component_instance:
            yaw_ratio = -self.yaw_pitch_camera.yaw / math.pi
            pitch_ratio = 1.0 - 2 * (self.yaw_pitch_camera.pitch / math.pi)
            component_instance.yaw = yaw_ratio
            component_instance.pitch = pitch_ratio

    def on_pattern_rotation_follow_camera_setting(self, value):
        if value:
            self.reset_pattern_uv_offset()
        current_skin_design.add_to_undo_history()

    def OnMouseDown(self, button, eventID, vKeyAndFlag, *args):
        updatingPattern = uicore.uilib.Key(uiconst.VK_CONTROL) or pattern_rotation_follow_camera_setting.is_enabled()
        activeWindow = uicore.registry.GetActive()
        if updatingPattern and activeWindow is not None and len(vKeyAndFlag) > 0:
            if activeWindow.name == 'ShipSKINRWindow':
                if vKeyAndFlag[0] == uiconst.MOUSELEFT:
                    uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
                    uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnTestLeftMouseUp)
                if vKeyAndFlag[0] == uiconst.MOUSERIGHT:
                    uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
                    uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnTestRightMouseUp)
        return True

    def OnTestRightMouseUp(self, obj, eventID, vk_flag):
        vkey, flag = vk_flag
        if vkey == uiconst.MOUSERIGHT:
            if not uicore.uilib.leftbtn:
                uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)
        else:
            return True

    def OnTestLeftMouseUp(self, obj, eventID, vk_flag):
        vkey, flag = vk_flag
        if vkey == uiconst.MOUSELEFT:
            if not uicore.uilib.rightbtn:
                uicore.uilib.SetCursor(uiconst.UICURSOR_DEFAULT)
        else:
            return True

    def reset_pattern_uv_offset(self):
        component_instance = self.get_pattern_component_instance()
        if component_instance:
            component_instance.offset_u_ratio = component_instance.offset_v_ratio = 0.0

    def SetZoom(self, proportion):
        if not pattern_rotation_follow_camera_setting.is_enabled():
            direction = self.GetLookAtDirection()
            distance = self.GetZoomDistanceByZoomProportion(proportion)
            zoomVec = geo2.Vec3Scale(direction, distance)
            self.SetEyePosition(geo2.Vec3Add(self.GetZoomToPoint(), zoomVec))

    def Orbit(self, dx = 0, dy = 0):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            self._modify_pattern_attributes(dx, dy)
        else:
            super(SkinrShipSceneContainerCamera, self).Orbit(dx, dy)

    def _modify_pattern_attributes(self, dx, dy):
        if uicore.uilib.rightbtn and not uicore.uilib.leftbtn:
            self.modify_offset(dx, dy)
        elif uicore.uilib.leftbtn and not uicore.uilib.rightbtn:
            self.modify_yaw_pitch(dx, dy)

    def modify_yaw_pitch(self, dx, dy):
        if not self.yaw_pitch_camera.orbitUpdateThread:
            component_instace = self.get_pattern_component_instance()
            if component_instace:
                self.yaw_pitch_camera.yaw = -component_instace.yaw * math.pi
                self.yaw_pitch_camera.pitch = -math.pi * (component_instace.pitch - 1.0) / 2.0
        k = 0.03 if uicore.uilib.Key(uiconst.VK_SHIFT) else 0.3
        self.yaw_pitch_camera.Orbit(-k * dx, -2 * k * dy)

    def modify_offset(self, dx, dy):
        k = 0.01 if uicore.uilib.Key(uiconst.VK_SHIFT) else 0.1
        if uicore.uilib.Key(uiconst.VK_MENU):
            pass
        else:
            component_instance = self.get_pattern_component_instance()
            if component_instance:
                dx, dy = self._rotate_offset_to_face_camera(component_instance, dx, dy)
                component_instance.offset_u_ratio += k * dx
                component_instance.offset_v_ratio += k * dy
                current_skin_design.add_to_undo_history_batch_up()

    def _rotate_offset_to_face_camera(self, component_instance, dx, dy):
        yaw = self.yaw + component_instance.yaw * math.pi
        if component_instance.pitch > 0:
            yaw *= -1
        dx, _, dy = geo2.QuaternionTransformVector(geo2.QuaternionRotationSetYawPitchRoll(yaw, 0, 0), (dx, 0, -dy))
        return (dx, dy)

    def _Update(self):
        super(SkinrShipSceneContainerCamera, self)._Update()
        if pattern_rotation_follow_camera_setting.is_enabled():
            yaw_ratio = -self.GetYaw() / math.pi
            pitch_ratio = 1.0 - 2 * (self.GetPitch() / math.pi)
            component_instance = self.get_pattern_component_instance()
            if component_instance:
                component_instance.yaw = yaw_ratio
                component_instance.pitch = pitch_ratio

    def Zoom(self, dz):
        updatingPattern = uicore.uilib.Key(uiconst.VK_CONTROL) or pattern_rotation_follow_camera_setting.is_enabled()
        if not updatingPattern:
            return super(SceneContainerCamera, self).Zoom(dz)
        component_instance = self.get_pattern_component_instance()
        if not component_instance:
            return
        if uicore.uilib.rightbtn and uicore.uilib.leftbtn:
            k = 0.01 if uicore.uilib.Key(uiconst.VK_SHIFT) else 0.1
            component_instance.scaling_ratio += dz * k
            current_skin_design.add_to_undo_history_batch_up()
        elif uicore.uilib.Key(uiconst.VK_MENU):
            component_instance.roll = self.get_roll_snap_value(component_instance.roll, dz)
            current_skin_design.add_to_undo_history_batch_up()
        else:
            k = 0.01 if uicore.uilib.Key(uiconst.VK_SHIFT) else 0.1
            component_instance.roll += dz * k
            current_skin_design.add_to_undo_history_batch_up()

    def get_roll_snap_value(self, current_value, dz):
        now = blue.os.GetSimTime()
        delta = blue.os.TimeDiffInMs(self.roll_snap_timestamp, now)
        if delta < self.roll_snap_delay or dz == 0:
            return current_value
        self.roll_snap_timestamp = now
        current_angle = current_value * 180
        index = bisect_left(self.roll_snap_angles, current_angle)
        if dz > 0:
            if index == len(self.roll_snap_angles) - 1:
                index = 1
            else:
                index += 1
        elif index == 0:
            index = len(self.roll_snap_angles) - 2
        else:
            index -= 1
        return self.roll_snap_angles[index] / 180.0

    def get_pattern_component_instance(self):
        slot_id = current_skin_design.get_selected_slot_id()
        slot_id = PATTERN_SLOT_ID_BY_PATTERN_MATERIAL_ID.get(slot_id, slot_id)
        if slot_id in PATTERN_SLOT_IDS:
            return current_skin_design.get().get_fitted_component_instance(slot_id)

    def SetInnerBoundRadius(self, innerRadius):
        maxSideLength = max(innerRadius)
        paddingLength = 0.01 * maxSideLength + 5
        padding = (paddingLength, paddingLength, paddingLength)
        self.innerBoundRadius = geo2.Vec3Add(innerRadius, padding)

    def SetModelCenter(self, modelCenter):
        self._modelCenterOffset = modelCenter
        self.SetAtPosition(self._modelCenterOffset)
