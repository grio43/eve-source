#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\client\apis\fittingsgateway.py
__all__ = ['IClientShipCosmeticFittingGateway']
import abc
from shipcosmetics.structs import *

class IClientShipCosmeticFittingGateway(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def getShipCosmeticFitting(self, ship_item_id):
        pass

    @abc.abstractmethod
    def setShipCosmeticFittingModule(self, ship_cosmetic_module, slot_index, group_index, ship_item_id):
        pass
