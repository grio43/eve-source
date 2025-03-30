#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicitemattributes\__init__.py
from dynamicitemattributes.loader import *
from evetypes import IsDynamicType

def CalcualteDynamicAttribute(modifier, attributeID, attributeValue, mutatorTypeID):
    mutatorStaticData = GetData()
    mutatorData = mutatorStaticData[mutatorTypeID]
    min = mutatorData.attributeIDs[attributeID].min
    max = mutatorData.attributeIDs[attributeID].max
    return attributeValue * (modifier * (max - min) + min)
