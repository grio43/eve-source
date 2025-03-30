#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\__init__.py
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionMapCamera import EmpireSelectionMapCamera
_CAMERA_CLASS_BY_ID = None

def get_camera_class(camera_id):
    global _CAMERA_CLASS_BY_ID
    if _CAMERA_CLASS_BY_ID is None:
        _CAMERA_CLASS_BY_ID = _get_camera_class_by_id_index()
    return _CAMERA_CLASS_BY_ID[camera_id]


def _get_camera_class_by_id_index():
    import evecamera
    from eve.client.script.ui.camera.cameraOld import CameraOld
    from eve.client.script.ui.camera.capitalHangarCamera import CapitalHangarCamera
    from eve.client.script.ui.camera.deathSceneCamera import DeathSceneCamera
    from eve.client.script.ui.camera.debugCamera import DebugCamera
    from eve.client.script.ui.camera.enterSpaceCamera import EnterSpaceCamera
    from eve.client.script.ui.camera.explosionCamera import ExplosionCamera
    from eve.client.script.ui.camera.hangarCamera import HangarCamera
    from eve.client.script.ui.camera.jumpCamera import JumpCamera
    from eve.client.script.ui.camera.loginCamera import LoginCamera
    from eve.client.script.ui.camera.mapCamera import MapCamera
    from eve.client.script.ui.camera.insurgencyMapCamera import InsurgencyMapCamera
    from eve.client.script.ui.camera.miniMapCamera import MiniMapCamera
    from eve.client.script.ui.camera.modularHangarCamera import ModularHangarCamera
    from eve.client.script.ui.camera.modularHangarCapitalCamera import ModularHangarCapitalCamera
    from eve.client.script.ui.camera.planetCamera import PlanetCamera
    from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera
    from eve.client.script.ui.camera.shipOrbitAbyssalSpaceCamera import ShipOrbitAbyssalSpaceCamera
    from eve.client.script.ui.camera.shipOrbitHazardCamera import ShipOrbitHazardSpaceCamera
    from eve.client.script.ui.camera.shipOrbitRestrictedCamera import RestrictedShipOrbitCamera
    from eve.client.script.ui.camera.shipPOVCamera import ShipPOVCamera
    from eve.client.script.ui.camera.solarSystemMapCamera import SolarSystemMapCamera
    from eve.client.script.ui.camera.starmapCamera import StarmapCamera
    from eve.client.script.ui.camera.structureCamera import StructureCamera
    from eve.client.script.ui.camera.systemMapCamera2 import SystemMapCamera2
    from eve.client.script.ui.camera.tacticalCamera import TacticalCamera
    from eve.client.script.ui.camera.undockCamera import UndockCamera
    from eve.client.script.ui.camera.vcsConsumerCamera import VCSConsumerCamera
    return {evecamera.CAM_SHIPORBIT: ShipOrbitCamera,
     evecamera.CAM_HANGAR: HangarCamera,
     evecamera.CAM_CAPITALHANGAR: CapitalHangarCamera,
     evecamera.CAM_MODULARHANGAR: ModularHangarCamera,
     evecamera.CAM_MODULARHANGAR_CAPITAL: ModularHangarCapitalCamera,
     evecamera.CAM_PLANET: PlanetCamera,
     evecamera.CAM_STARMAP: StarmapCamera,
     evecamera.CAM_SYSTEMMAP: SystemMapCamera2,
     evecamera.CAM_TACTICAL: TacticalCamera,
     evecamera.CAM_SHIPPOV: ShipPOVCamera,
     evecamera.CAM_JUMP: JumpCamera,
     evecamera.CAM_DEBUG: DebugCamera,
     evecamera.CAM_DEATHSCENE: DeathSceneCamera,
     evecamera.CAM_LOGIN: LoginCamera,
     evecamera.CAM_UNDOCK: UndockCamera,
     evecamera.CAM_ENTERSPACE: EnterSpaceCamera,
     evecamera.CAM_EXPLOSION: ExplosionCamera,
     evecamera.CAM_STRUCTURE: StructureCamera,
     evecamera.CAM_SOLARSYSTEMMAP: SolarSystemMapCamera,
     evecamera.CAM_MAP: MapCamera,
     evecamera.CAM_MINIMAP: MiniMapCamera,
     evecamera.CAM_SHIPORBIT_ABYSSAL_SPACE: ShipOrbitAbyssalSpaceCamera,
     evecamera.CAM_SHIPORBIT_HAZARD: ShipOrbitHazardSpaceCamera,
     evecamera.CAM_SHIPORBIT_RESTRICTED: RestrictedShipOrbitCamera,
     evecamera.CAM_EMPIRESELECTIONMAP: EmpireSelectionMapCamera,
     evecamera.CAM_VCS_CONSUMER: VCSConsumerCamera,
     evecamera.CAM_INSURGENCY_MAP: InsurgencyMapCamera}
