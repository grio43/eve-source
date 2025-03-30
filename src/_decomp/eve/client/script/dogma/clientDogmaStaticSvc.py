#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\dogma\clientDogmaStaticSvc.py
from collections import defaultdict
from eve.common.lib import appConst as const
import dogma.data as dogma_data
import evetypes
from eve.common.script.dogma.baseDogmaStaticSvc import BaseDogmaStaticSvc

class AttributesByTypeLookupDict(defaultdict):

    def __init__(self, typeID, *args, **kwargs):
        defaultdict.__init__(self, *args, **kwargs)
        self.typeID = typeID

    def __missing__(self, attributeID):
        for attribute in dogma_data.get_type_attributes(self.typeID):
            if attribute.attributeID == attributeID:
                return attribute.value

        ret = None
        if attributeID == const.attributeMass:
            ret = evetypes.GetMass(self.typeID)
        elif attributeID == const.attributeCapacity:
            ret = evetypes.GetCapacity(self.typeID)
        elif attributeID == const.attributeVolume:
            ret = evetypes.GetVolume(self.typeID)
        if ret is None:
            raise KeyError(attributeID)
        else:
            self[attributeID] = ret
            return ret


class AttributesByTypeAttribute(defaultdict):

    def __missing__(self, typeID):
        if not dogma_data.has_type_attributes(typeID) and not evetypes.Exists(typeID):
            raise KeyError(typeID)
        return AttributesByTypeLookupDict(typeID)


class ClientDogmaStaticSvc(BaseDogmaStaticSvc):
    __guid__ = 'svc.clientDogmaStaticSvc'

    def LoadTypeAttributes(self, *args, **kwargs):
        self.attributesByTypeAttribute = AttributesByTypeAttribute()

    def TypeHasAttribute(self, typeID, attributeID):
        try:
            for row in dogma_data.get_type_attributes(typeID):
                if row.attributeID == attributeID:
                    return True

            return False
        except KeyError:
            return False
