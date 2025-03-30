#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\solarsysteminterference\util.py
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem, IsVoidSpaceSystem, IsWormholeSystem, IsTriglavianSystem, IsLowSecSystem, IsNullSecSystem
from eveuniverse.security import is_high_security_solar_system

def SystemCanHaveInterference(solarsystemID):
    if is_high_security_solar_system(solarsystemID):
        return False
    if IsAbyssalSpaceSystem(solarsystemID):
        return False
    if IsVoidSpaceSystem(solarsystemID):
        return False
    if IsWormholeSystem(solarsystemID):
        return False
    if IsTriglavianSystem(solarsystemID):
        return False
    return True
