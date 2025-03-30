#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\stargate\client\emanationLockVisualization.py
import logging
from carbon.common.script.sys.serviceManager import ServiceManager
logger = logging.getLogger(__name__)

class EmanationLockVisualization(object):

    @staticmethod
    def clear_blocked_gate_visuals(solar_system_id):
        EmanationLockVisualization.update_blocked_gate_visuals(solar_system_id, -1)

    @staticmethod
    def update_blocked_gate_visuals(solar_system_id, emanation_lock_gate_id):
        logger.info('Emanation Lock - EmanationLockVisualization.update_blocked_gate_visuals({solar_system_id}, {emanation_lock_gate_id})'.format(solar_system_id=solar_system_id, emanation_lock_gate_id=emanation_lock_gate_id))
        service_manager = ServiceManager.Instance()
        michelle = service_manager.GetService('michelle')

        def update_visuals_for_gate(gate_id):
            is_emanation_locked = False
            if gate_id != emanation_lock_gate_id and emanation_lock_gate_id > 0:
                is_emanation_locked = True
            michelle.SetControllerVariableOnBall(gate_id, 'emanationLock', is_emanation_locked)

        map_service = service_manager.GetService('map')
        map_service.ForEachStarGateIDInSolarSystem(solar_system_id, update_visuals_for_gate)

    @staticmethod
    def update_gate_space_object_visuals(gate_space_object, emanation_lock_gate_id):
        logger.info('Emanation Lock - EmanationLockVisualization.update_gate_space_object_visuals(%s, %s)', gate_space_object, emanation_lock_gate_id)
        slimItem = gate_space_object.typeData.get('slimItem')
        if not slimItem:
            return
        is_emanation_locked = False
        if slimItem.itemID != emanation_lock_gate_id and emanation_lock_gate_id > 0:
            is_emanation_locked = True
        gate_space_object.SetControllerVariable('emanationLock', is_emanation_locked)
