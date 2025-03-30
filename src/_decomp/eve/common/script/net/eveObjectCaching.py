#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\net\eveObjectCaching.py
from carbon.common.script.net.objectCaching import CoreObjectCachingSvc

class EveObjectCachingSvc(CoreObjectCachingSvc):
    __guid__ = 'svc.eveObjectCaching'
    __replaceservice__ = 'objectCaching'
    __cachedsessionvariables__ = ['regionid',
     'constellationid',
     'stationid',
     'solarsystemid',
     'locationid',
     'languageID']
