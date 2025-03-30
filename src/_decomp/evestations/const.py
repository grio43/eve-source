#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evestations\const.py
from collections import namedtuple
NPCStationProps = ['stationID',
 'stationName',
 'x',
 'y',
 'z',
 'stationTypeID',
 'solarSystemID',
 'orbitID',
 'ownerID']
NPCStation = namedtuple('NPCStation', NPCStationProps)
DOOMHEIM_STATION = NPCStation(stationID=60000001, stationName='Doomheim Station', x=666.0, y=666.0, z=-666.0, stationTypeID=54, solarSystemID=1, orbitID=1, ownerID=1000001)
