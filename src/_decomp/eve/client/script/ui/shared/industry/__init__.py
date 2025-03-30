#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\__init__.py
import evetypes
from caching.memoize import Memoize
from industry import ACTIVITIES
from utillib import KeyVal

@Memoize
def GetTypeName(typeID):
    return evetypes.GetName(typeID)


@Memoize
def GetGroupName(typeID):
    return evetypes.GetGroupName(typeID)


@Memoize
def GetProductGroupAndCategory(typeID):
    return KeyVal(groupID=evetypes.GetGroupID(typeID), groupName=GetGroupName(typeID), categoryID=evetypes.GetCategoryID(typeID), categoryName=evetypes.GetCategoryName(typeID))


@Memoize(0.1)
def GetActivitySum(activities):
    activitySum = ''
    for activityID in ACTIVITIES:
        activitySum += '1' if activityID in activities else '0'

    return activitySum
