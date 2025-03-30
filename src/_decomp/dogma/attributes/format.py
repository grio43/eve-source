#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\format.py
import math
import dogma.data as dogma_data
from carbon.common.script.util.mathCommon import FloatCloseEnough
from dogma.attributes import datetime
from eve.common.script.util.eveFormat import FmtDist2
import evetypes
from carbon.common.lib.const import SEC, HOUR
from localization import GetByLabel
import localization
from carbon.common.script.util import format
from dogma import const as dogmaConst, units
from itertoolsext import Bundle
SIZE_DICT = {1: 'UI/InfoWindow/SmallSize',
 2: 'UI/InfoWindow/MediumSize',
 3: 'UI/InfoWindow/LargeSize',
 4: 'UI/InfoWindow/XLargeSize'}
GENDER_DICT = {1: 'UI/Common/Gender/Male',
 2: 'UI/Common/Gender/Unisex',
 3: 'UI/Common/Gender/Female'}

def GetAttribute(attributeID):
    return dogma_data.get_attribute(attributeID)


def GetDisplayName(attributeID):
    attribute = GetAttribute(attributeID)
    return localization.GetByMessageID(attribute.displayNameID) or attribute.name


def GetIconID(attributeID):
    return GetAttribute(attributeID).iconID


def GetName(attributeID):
    return GetAttribute(attributeID).name


def FormatUnit(unitID, fmt = 'd'):
    if unitID in (dogmaConst.unitTime, dogmaConst.unitLength, dogmaConst.unitAttributeID):
        return ''
    if units.has_unit(unitID) and fmt == 'd':
        return units.get_display_name(unitID)
    return ''


def FormatValue(value, unitID = None):
    if value is None:
        return
    if unitID == dogmaConst.unitTime:
        return format.FmtDate(long(value * SEC), 'll')
    if unitID == dogmaConst.unitMilliseconds:
        return '%.2f' % (value / 1000.0)
    if unitID == dogmaConst.unitLength:
        return FmtDist2(value)
    if unitID == dogmaConst.unitHour:
        return format.FmtDate(long(value * HOUR), 'ss')
    if unitID == dogmaConst.unitMoney:
        return format.FmtAmt(value)
    if unitID == dogmaConst.unitDatetime:
        return format.FmtDate(datetime.float_as_time(value))
    if unitID in (dogmaConst.unitTeraflops, dogmaConst.unitCapacitorUnits, dogmaConst.unitMegaWatts):
        return round(value, 2)
    if unitID == dogmaConst.unitWarpSpeed:
        return format.RoundDistance(value)
    if unitID in (dogmaConst.unitInverseAbsolutePercent, dogmaConst.unitInversedModifierPercent):
        value = float(round(1.0 - value, 6)) * 100
    elif unitID == dogmaConst.unitModifierPercent:
        value = round(abs(value * 100 - 100) * (-1 if value < 1.0 else 1), 3)
    elif unitID == dogmaConst.unitAbsolutePercent:
        value *= 100
    elif unitID == dogmaConst.unitModifierRealPercent:
        return localization.formatters.FormatNumeric(value, decimalPlaces=1, useGrouping=True)
    if type(value) is str:
        value = eval(value)
    if unitID == dogmaConst.unitMass:
        return localization.formatters.FormatNumeric(value, decimalPlaces=0, useGrouping=True)
    if unitID in (dogmaConst.unitModifierRelativePercent, dogmaConst.unitPercentage, dogmaConst.unitAbsolutePercent):
        if abs(value) < 10:
            decimalPlaces = 2
        else:
            decimalPlaces = 1
        value = round(value, decimalPlaces)
        if abs(value - int(value)) < 1e-10:
            decimalPlaces = 0
        return localization.formatters.FormatNumeric(value, decimalPlaces=decimalPlaces, useGrouping=True)
    if not isinstance(value, basestring) and FloatCloseEnough(round(value), value, 1e-10):
        return format.FmtAmt(round(value))
    if unitID == dogmaConst.unitAttributePoints:
        return round(value, 1)
    if unitID == dogmaConst.unitMaxVelocity:
        return localization.formatters.FormatNumeric(value, decimalPlaces=2, useGrouping=True)
    if unitID in (dogmaConst.unitHitpoints,
     dogmaConst.unitVolume,
     dogmaConst.unitInverseAbsolutePercent,
     dogmaConst.unitInversedModifierPercent):
        if value < 1:
            significantDigits = 2 if unitID == dogmaConst.unitHitpoints else 3
            decimalPlaces = int(-math.ceil(math.log10(abs(value))) + significantDigits)
        else:
            decimalPlaces = 2
        return localization.formatters.FormatNumeric(value, decimalPlaces=decimalPlaces, useGrouping=True)
    if unitID == dogmaConst.unitModifierMultiplier:
        return round(value, 3)
    return value


def GetFormatAndValue(attributeType, value, overrideUnitID = None):
    unitID = overrideUnitID or getattr(attributeType, 'unitID', None)
    attrUnit = FormatUnit(unitID)
    if unitID == dogmaConst.unitGroupID:
        value = evetypes.GetGroupNameByGroup(value)
    elif unitID == dogmaConst.unitTypeID:
        value = evetypes.GetName(value)
    elif unitID == dogmaConst.unitSizeclass:
        value = GetByLabel(SIZE_DICT.get(int(value)))
    elif unitID == dogmaConst.unitAttributeID:
        value = GetDisplayName(value)
    elif attributeType.attributeID == dogmaConst.attributeVolume:
        value = GetByLabel('UI/InfoWindow/ValueAndUnit', value=FormatValue(value, dogmaConst.attributeVolume), unit=FormatUnit(dogmaConst.unitVolume))
    elif unitID == dogmaConst.unitModifierRealPercent:
        formattedValue = FormatValue(value)
        sign = '+'
        if value < 0:
            sign = '-'
        value = '%s%s%s' % (sign, formattedValue, attrUnit)
    elif unitID == dogmaConst.unitLevel:
        value = GetByLabel('UI/InfoWindow/TechLevelX', numLevel=format.FmtAmt(value))
    elif unitID == dogmaConst.unitBoolean:
        if int(value) == 1:
            value = GetByLabel('UI/Common/True')
        else:
            value = GetByLabel('UI/Common/False')
    elif unitID == dogmaConst.unitSlot:
        value = GetByLabel('UI/InfoWindow/SlotX', slotNum=format.FmtAmt(value))
    elif unitID == dogmaConst.unitBonus:
        if value >= 0:
            value = '%s%s' % (attrUnit, value)
    elif unitID == dogmaConst.unitGender:
        value = GetByLabel(GENDER_DICT.get(int(value)))
    elif unitID == dogmaConst.unitDatetime:
        value = FormatValue(value, unitID)
    elif attributeType.attributeID == dogmaConst.attributeMaxLockedTargets:
        value = int(math.ceil(value))
    elif attributeType.dataType == dogmaConst.attributeDataTypeTypeTypeListId:
        typeListID = int(value)
        try:
            typeListDisplayName = evetypes.GetTypeListDisplayName(typeListID)
            if not typeListDisplayName:
                typeListDisplayName = "[Unnamed Typelist '%s']" % typeListID
        except evetypes.TypeListNotFoundException:
            typeListDisplayName = "[Missing Typelist '%s']" % typeListID

        value = typeListDisplayName
    elif not attrUnit:
        value = FormatValue(value, unitID)
    else:
        value = GetByLabel('UI/InfoWindow/ValueAndUnit', value=FormatValue(value, unitID), unit=attrUnit)
    return value


def GetFormattedAttributeAndValue(attributeID, value, overrideUnitID = None):
    attribute = GetAttribute(attributeID)
    if not attribute.displayWhenZero and not value:
        return None
    return GetFormattedAttributeAndValueAllowZero(attributeID, value, overrideUnitID)


def GetFormattedAttributeAndValueAllowZero(attributeID, value, overrideUnitID = None):
    if value is None:
        return
    attribute = GetAttribute(attributeID)
    if not attribute.published:
        return
    iconID = getattr(attribute, 'iconID', None)
    infoTypeID = None
    if not iconID:
        unitID = getattr(attribute, 'unitID', None)
        if unitID == dogmaConst.unitTypeID:
            iconID = evetypes.GetIconID(value)
            infoTypeID = int(value)
        if unitID == dogmaConst.unitGroupID:
            iconID = evetypes.GetGroupIconIDByGroup(value)
        if unitID == dogmaConst.unitAttributeID:
            iconID = GetIconID(value)
    value = GetFormatAndValue(attribute, value, overrideUnitID)
    return Bundle(displayName=dogma_data.get_attribute_display_name(attributeID), value=value, iconID=iconID, infoTypeID=infoTypeID)


PERCENT_UNITS = (dogmaConst.unitInverseAbsolutePercent, dogmaConst.unitInversedModifierPercent, dogmaConst.unitModifierPercent)

def GetFormattedDiff(attributeID, diff):
    attribute = GetAttribute(attributeID)
    if not attribute.published:
        return
    if attribute.unitID in PERCENT_UNITS:
        diff += 1
    info = GetFormattedAttributeAndValueAllowZero(attributeID, diff)
    if info is None:
        return
    diffStr = unicode(info.value)
    if diffStr.startswith('+') or diffStr.startswith('-'):
        pass
    elif diff >= 0.0 and not diffStr.startswith('+'):
        diffStr = u'+{}'.format(diffStr)
    elif diff < 0.0 and not diffStr.startswith('-'):
        diffStr = u'-{}'.format(diffStr)
    return diffStr
