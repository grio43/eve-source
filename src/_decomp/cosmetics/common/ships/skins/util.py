#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\common\ships\skins\util.py
from itertoolsext.Enum import Enum

@Enum

class Currency(object):
    PLEX = 'PLEX'
    ISK = 'ISK'


@Enum

class SkinListingOrder(object):
    NAME = 'NAME'
    EXPIRES_AT = 'EXPIRES_AT'


@Enum

class ComponentListingOrder(object):
    NAME = 'NAME'
    EXPIRES_AT = 'EXPIRES_AT'
    PRICE = 'PRICE'
    COLOR_SHADE = 'COLOR_SHADE'


COMPONENT_LIMITED_OFFER_THRESHOLD_DAYS = 30
