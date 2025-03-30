#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sensorsuite\common.py
import math

def MapDungeonDifficulty(dungeonDifficulty = None):
    if dungeonDifficulty < 1:
        return 1
    return dungeonDifficulty
