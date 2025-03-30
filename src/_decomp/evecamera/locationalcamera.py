#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecamera\locationalcamera.py
import evecamera
from eveuniverse.solar_systems import is_orbit_camera_range_limited, is_orbit_camera_range_limited_moderate, is_tactical_camera_suppressed, is_pov_camera_suppressed

def get_orbit_camera_by_solar_system(solar_system_id):
    if is_orbit_camera_range_limited(solar_system_id):
        if is_orbit_camera_range_limited_moderate(solar_system_id):
            return evecamera.CAM_SHIPORBIT_HAZARD
        return evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE
    return evecamera.CAM_SHIPORBIT


def get_corrected_camera_id(camera_id, solar_system_id):
    if camera_id in (evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE, evecamera.CAM_SHIPORBIT_HAZARD) and not is_orbit_camera_range_limited(solar_system_id):
        return evecamera.CAM_SHIPORBIT
    elif camera_id == evecamera.CAM_SHIPORBIT and is_orbit_camera_range_limited(solar_system_id):
        if is_orbit_camera_range_limited_moderate(solar_system_id):
            return evecamera.CAM_SHIPORBIT_HAZARD
        return evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE
    elif camera_id == evecamera.CAM_TACTICAL and is_tactical_camera_suppressed(solar_system_id):
        return get_orbit_camera_by_solar_system(solar_system_id)
    elif camera_id == evecamera.CAM_SHIPPOV and is_pov_camera_suppressed(solar_system_id):
        return get_orbit_camera_by_solar_system(solar_system_id)
    else:
        return camera_id
