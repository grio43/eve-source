#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\security.py
from eveuniverse.security import SecurityClassFromLevel, securityClassHighSec, securityClassLowSec, securityClassZeroSec

def is_in_high_sec(task):
    return get_local_security_level(task) == securityClassHighSec


def is_in_low_sec(task):
    return get_local_security_level(task) == securityClassLowSec


def is_in_zero_sec(task):
    return get_local_security_level(task) == securityClassZeroSec


def get_local_security_level(task):
    return get_security_level_for_system(task.context.solarSystemId)


def get_security_level_for_system(solar_system_id):
    return SecurityClassFromLevel(cfg.mapSystemCache[solar_system_id].securityStatus)


def get_spawnlist_by_group_owner_and_security_level(task):
    ownerToSpawnlistMapping = get_spawnlist_by_owner_map_by_security(task)
    return ownerToSpawnlistMapping.get(task.GetGroupOwnerId())


def get_spawnlist_by_owner_map_by_security(task):
    if is_in_high_sec(task):
        return task.attributes.highSecOwnerToSpawnlistMapping
    elif is_in_low_sec(task):
        return task.attributes.lowSecOwnerToSpawnlistMapping
    else:
        return task.attributes.zeroSecOwnerToSpawnlistMapping
