#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\spaceSubway\const.py
import os
import re
import logging
AMARR_REGION = 0
CALDARI_REGION = 1
GALLENTE_REGION = 2
MINMATAR_REGION = 3
YASNA_ZAKH_REGION = 4
ABYSSAL_REGION = 5
WORMHOLE_REGION = 6
REGION_LOOKUP = {re.compile('a(?!d).*'): AMARR_REGION,
 re.compile('c.*'): CALDARI_REGION,
 re.compile('g.*'): GALLENTE_REGION,
 re.compile('m.*'): MINMATAR_REGION,
 re.compile('y.*'): YASNA_ZAKH_REGION,
 re.compile('ad.*'): ABYSSAL_REGION,
 re.compile('wormhole.*'): WORMHOLE_REGION}
log = logging.getLogger(__name__)

def GetRegionValue(nebulaPath):
    filePath = os.path.split(nebulaPath)[1]
    for regionRegEx, value in REGION_LOOKUP.iteritems():
        if regionRegEx.match(filePath):
            return value

    log.error("Got an invalid region value for nebula '%s', defaulting to caldari region" % nebulaPath)
    return CALDARI_REGION
