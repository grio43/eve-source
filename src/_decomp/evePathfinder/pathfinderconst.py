#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evePathfinder\pathfinderconst.py
import math
ROUTE_TYPE_SAFE = 'safe'
ROUTE_TYPE_UNSAFE = 'unsafe'
ROUTE_TYPE_UNSAFE_AND_NULL = 'unsafe + zerosec'
ROUTE_TYPE_SHORTEST = 'shortest'
SECURITY_PENALTY_FACTOR = 0.15
DEFAULT_SECURITY_PENALTY = 50.0
DEFAULT_SECURITY_PENALTY_VALUE = math.exp(SECURITY_PENALTY_FACTOR * DEFAULT_SECURITY_PENALTY)
UNREACHABLE_JUMP_COUNT = int(2147483647L)
