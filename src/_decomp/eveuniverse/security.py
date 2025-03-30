#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveuniverse\security.py
securityClassZeroSec = 0
securityClassLowSec = 1
securityClassHighSec = 2
SECURITY_CLASS_TO_TEXT = {securityClassZeroSec: 'Null Security',
 securityClassLowSec: 'Low Security',
 securityClassHighSec: 'High Security'}
UNKNOWN_SECURITY_CLASS = 'Unknown Security Class'

def SecurityClassFromLevel(level):
    if level <= 0.0:
        return securityClassZeroSec
    elif level < 0.45:
        return securityClassLowSec
    else:
        return securityClassHighSec


def get_solar_system_security_level(solar_system_id):
    return cfg.mapSystemCache[solar_system_id].securityStatus


def get_solar_system_security_class(solar_system_id):
    security_level = get_solar_system_security_level(solar_system_id)
    return SecurityClassFromLevel(security_level)


def get_security_class_text(security_class):
    return SECURITY_CLASS_TO_TEXT.get(security_class, UNKNOWN_SECURITY_CLASS)


def is_high_security_class(security_class):
    return security_class == securityClassHighSec


def is_low_security_class(security_class):
    return security_class == securityClassLowSec


def is_zero_security_class(security_class):
    return security_class == securityClassZeroSec


def is_high_security_solar_system(solar_system_id):
    return is_high_security_class(get_solar_system_security_class(solar_system_id))


def is_low_security_solar_system(solar_system_id):
    return is_low_security_class(get_solar_system_security_class(solar_system_id))


def is_zero_security_solar_system(solar_system_id):
    return is_zero_security_class(get_solar_system_security_class(solar_system_id))
