#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destructionEffect\destructionType.py
NONE = 0
EXPLOSION_OVERRIDE = 1
DISSOLVE = 2
EXPLOSION = 3
REVERSE_EJECT = 4
DURATION_BY_DESTRUCTION_TYPE = {DISSOLVE: 33000,
 REVERSE_EJECT: 11000}

def isExplosionOrOverride(identifier):
    return identifier == EXPLOSION or identifier == EXPLOSION_OVERRIDE
