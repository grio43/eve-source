#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\client\uiFormatters.py
from dbuff.storage import GetDbuffCollection, GetDisplayNameID
from dogma.attributes.format import FormatValue, FormatUnit
from dogma.const import dbuffAttributeValueMappings, unitModifierRelativePercent, dgmAssPostPercent, dbuffAttributeMultiplierMappings
import evetypes
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextSides
from eve.client.script.ui.control.entries.util import GetFromClass
from inventorycommon.const import categoryCharge
import localization

def GetDisplayNameAndValue(dbuffID, dbuffValue):
    dbuffCollection = GetDbuffCollection(dbuffID)
    displayNameID = GetDisplayNameID(dbuffID)
    if displayNameID:
        displayName = localization.GetByMessageID(displayNameID)
    else:
        displayName = None
    if dbuffCollection.operation == dgmAssPostPercent:
        unitID = unitModifierRelativePercent
    else:
        unitID = None
    if dbuffCollection.showOutputValueInUI == 'ShowInverted':
        dbuffValue = -dbuffValue
    if dbuffCollection.showOutputValueInUI == 'Hide':
        displayValue = None
    else:
        displayValue = localization.GetByLabel('UI/InfoWindow/ValueAndUnit', value=FormatValue(dbuffValue, unitID), unit=FormatUnit(unitID))
    return (displayName, displayValue)


def GetDbuffInfoEntriesForItem(itemID, typeID):
    dbuffValues = GetMappedDbuffsForItem(typeID, itemID)
    if not dbuffValues:
        return []
    dbuffAttributeEntries = [GetFromClass(Header, {'label': localization.GetByLabel('UI/Fitting/FittingWindow/BuffOutputs')})]
    for dbuffID, dbuffValue in dbuffValues:
        displayName, displayValue = GetDisplayNameAndValue(dbuffID, dbuffValue)
        if displayName is None:
            continue
        entry = GetFromClass(LabelTextSides, {'label': displayName,
         'text': displayValue,
         'iconID': 0})
        dbuffAttributeEntries.append(entry)

    return dbuffAttributeEntries


def GetMappedDbuffsForItem(typeID, itemID = None):
    GAV = sm.GetService('info').GetGAVFunc(itemID, typeID)
    dbuffIDValues = []
    for dbuffIDAttribute, dbuffValueAttribute in _GetAttributeMappings(typeID).iteritems():
        dbuffID = GAV(dbuffIDAttribute)
        if not dbuffID:
            continue
        dbuffValue = GAV(dbuffValueAttribute)
        dbuffIDValues.append((dbuffID, dbuffValue))

    return dbuffIDValues


def _GetAttributeMappings(typeID):
    if evetypes.GetCategoryID(typeID) == categoryCharge:
        attributeMappings = dbuffAttributeMultiplierMappings
    else:
        attributeMappings = dbuffAttributeValueMappings
    return attributeMappings
