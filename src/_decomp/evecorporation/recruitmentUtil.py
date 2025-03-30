#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evecorporation\recruitmentUtil.py
import evecorporation.corp_ui_recruitment_const as rConst
try:
    from evecorporation.recruitment import get_recruitment_types_for_group_id
except:
    get_recruitment_types_for_group_id = None

bitList = []
for i in range(0, 63):
    bitList.append(int(pow(2, i)))

def BitCount(bits):
    bitCount = 0
    for i in range(0, 63):
        if bitList[i] & bits:
            bitCount += 1

    return bitCount


def TypesInMask(mask):
    typesSet = set()
    for i in range(0, 63):
        if bitList[i] & mask:
            typesSet.add(i)

    return typesSet


def IsNumPlaystyleMaskValid(mask):
    playStyleTypesCount = 0
    allPlayStyleTypes = GetPlaystyles()
    for playstyle in allPlayStyleTypes:
        if IsBitSet(playstyle.typeMask, mask):
            playStyleTypesCount += 1

    if playStyleTypesCount > rConst.MAX_SELECTED_TYPES:
        return False
    return True


def GetPlaystyles():
    return get_recruitment_types_for_group_id(rConst.PLAYSTYLE_GROUPID)


def IsOnlyOnePlaystyleType(mask):
    typesInMask = TypesInMask(mask)
    combinedGroups = set()
    for eachType in typesInMask:
        group = rConst.COMBINED_GROUP_BY_TYPEID.get(eachType)
        if group:
            combinedGroups.add(group)
            if len(combinedGroups) > 1:
                return False

    return True


def IsNumAreaOfOperationsValid(mask):
    areaTypesCount = 0
    allAreas = GetAreasOfOperations()
    for playstyle in allAreas:
        if IsBitSet(playstyle.typeMask, mask):
            areaTypesCount += 1

    if areaTypesCount > rConst.MAX_SELECTED_AREAS:
        return False
    return True


def GetAreasOfOperations():
    return get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID)


def IsTimezoneValid(mask):
    bitCount = BitCount(mask)
    if bitCount > rConst.MAX_HOURS:
        return False
    return True


def RemoveBitFromMask(bit, mask):
    if mask & bit:
        newMask = mask ^ bit
    else:
        newMask = mask
    return newMask


def IsBitSet(bit, mask):
    return bit & mask > 0


def IsBitSetForTypeID(typeID, mask):
    bit = TwoToThePowerOf(typeID)
    return IsBitSet(bit, mask)


def AddBitToMask(bit, mask):
    newMask = bit | mask
    return newMask


def TwoToThePowerOf(power):
    return 1 << power


def BuildMask(from1, to1):
    mask = 0
    if from1 > to1:
        for i in xrange(24):
            if i < to1:
                mask = AddBitToMask(bit=TwoToThePowerOf(i), mask=mask)
            if i >= from1:
                mask = AddBitToMask(bit=TwoToThePowerOf(i), mask=mask)

    else:
        for i in xrange(24):
            if i >= from1 and i < to1:
                mask = AddBitToMask(bit=TwoToThePowerOf(i), mask=mask)

    return mask


def GetTimeZoneFromMask(timeMaskInt):
    if timeMaskInt <= 0:
        return (0, 24)
    toHour = 24
    fromHour = None
    counter = 0
    while timeMaskInt != 0:
        timeMaskInt, bitSet = divmod(timeMaskInt, 2)
        if bitSet == 1:
            if fromHour is None:
                fromHour = counter
            elif fromHour is not None and toHour < 24:
                fromHour = counter
                break
        elif fromHour is not None and toHour == 24:
            toHour = counter
        counter += 1

    if toHour == 24:
        toHour = counter
    return (fromHour, toHour)


def RemoveOldPlaystylesFromMask(oldMask):
    validTypes = [ x.typeID for x in get_recruitment_types_for_group_id(rConst.PLAYSTYLE_GROUPID) ]
    validTypes += [ x.typeID for x in get_recruitment_types_for_group_id(rConst.AREA_OF_OPERATIONS_GROUPID) ]
    newMask = oldMask
    typesInMask = TypesInMask(newMask)
    for eachTypeID in typesInMask:
        if eachTypeID not in validTypes:
            newMask = RemoveBitFromMask(bit=TwoToThePowerOf(eachTypeID), mask=newMask)

    return newMask
