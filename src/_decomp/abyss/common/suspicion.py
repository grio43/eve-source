#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\common\suspicion.py
__all__ = ['FILAMENT_ACTIVATION_NOT_ALLOWED', 'FILAMENT_ACTIVATION_UNRESTRICTED', 'get_max_allowed_tier_by_security_level']
FILAMENT_ACTIVATION_NOT_ALLOWED = -405
FILAMENT_ACTIVATION_UNRESTRICTED = 200
_MAX_TIER_ALLOWED_BY_DECA_SECURITY_RANGE = {10: FILAMENT_ACTIVATION_NOT_ALLOWED,
 9: FILAMENT_ACTIVATION_NOT_ALLOWED,
 8: 3,
 7: 4,
 6: 5,
 5: 6}

def _deca_security_range(security_float):
    if 0.0 < security_float < 0.05:
        security_float = 0.05
    return int(round(security_float, 1) * 10)


def get_max_allowed_tier_by_security_level(security_level):
    return _MAX_TIER_ALLOWED_BY_DECA_SECURITY_RANGE.get(_deca_security_range(security_level), FILAMENT_ACTIVATION_UNRESTRICTED)
