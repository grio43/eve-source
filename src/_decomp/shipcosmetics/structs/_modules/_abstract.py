#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_modules\_abstract.py
__all__ = ['AbstractShipCosmeticModule']
import abc
from shipcosmetics.structs import AbstractShipCosmeticLicense

class AbstractShipCosmeticModule(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, license, *args, **kwargs):
        self._license = license

    @property
    def license(self):
        return self._license

    def getSlotGroup(self):
        return self._license.slotGroup

    def getCosmeticType(self):
        return self._license.cosmeticType

    def getFsdTypeID(self):
        return self._license.fsdTypeID

    def getShipTypeID(self):
        return self._license.shipTypeID

    def getIconID(self):
        return self._license.iconID

    def getName(self):
        return self._license.name

    def getDescription(self):
        return self._license.description

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.getFsdTypeID() == other.getFsdTypeID()
        return False

    def __hash__(self):
        return hash('%s%d' % (self.__class__, self.getFsdTypeID()))

    def __str__(self):
        return u'<%s fsd_type_id=%d>' % (self.__class__.__name__, self.getFsdTypeID())

    def __repr__(self):
        return self.__str__()
