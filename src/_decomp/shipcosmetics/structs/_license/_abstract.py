#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\structs\_license\_abstract.py
__all__ = ['AbstractShipCosmeticLicense']
import abc

class AbstractShipCosmeticLicense(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def licenseID(self):
        pass

    @abc.abstractproperty
    def slotGroup(self):
        pass

    @abc.abstractproperty
    def cosmeticType(self):
        pass

    @abc.abstractproperty
    def fsdTypeID(self):
        pass

    @abc.abstractproperty
    def fsdType(self):
        pass

    @abc.abstractproperty
    def shipTypeID(self):
        pass

    @abc.abstractproperty
    def shipType(self):
        pass

    @abc.abstractproperty
    def iconID(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def description(self):
        pass

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.fsdTypeID == other.fsdTypeID
        return False

    def __hash__(self):
        return hash('%s%d' % (self.__class__, self.fsdTypeID))

    def __str__(self):
        return u'<%s:"%s" fsd_type_id=%d>' % (self.__class__.__name__, self.name, self.fsdTypeID)

    def __repr__(self):
        return self.__str__()
