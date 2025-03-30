#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\display.py
import localization
from dogma.attributes.format import GetFormattedAttributeAndValue
from dogma.data import get_type_attribute_or_default
COMPONENT_INFO_ORDER = ['deploy',
 'activate',
 'decay',
 'scoop',
 'warpDisruption']
TIMER_ICON = '22_16'
CYCLE_TIME_ICON = '22_21'
RANGE_ICON = '22_15'
BANNED_ICON = '77_12'
DICE_ICON = '25_13'

def EntryData(entryClass, label, text = None, iconID = 0, typeID = None):
    if isinstance(entryClass, str):
        raise TypeError('The entryClass must be a class instance, not a class name')
    return (entryClass, {'line': 1,
      'label': label,
      'text': text,
      'iconID': iconID,
      'typeID': typeID})


def DogmaEntryData(entryClass, attribute):
    return EntryData(entryClass, attribute.displayName, attribute.value, attribute.iconID)


def IterAttributeCollectionInInfoOrder(attributeCollection):
    for name in COMPONENT_INFO_ORDER:
        if name in attributeCollection:
            yield attributeCollection.pop(name)

    remainingLists = localization.util.Sort(attributeCollection.values(), key=lambda attrList: attrList[0][1]['label'])
    for attributeList in remainingLists:
        yield attributeList


def GetDogmaAttributeAndValue(typeID, attributeID):
    value = get_type_attribute_or_default(typeID, attributeID)
    return GetFormattedAttributeAndValue(attributeID, value)
