#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\moonmining\util.py
from moonmining.const import YIELD_PER_DAY

def CalculateExtractionTotalYield(duration, yieldMultiplier = 1):
    extractionYield = YIELD_PER_DAY * duration / 86400.0
    return extractionYield * yieldMultiplier
