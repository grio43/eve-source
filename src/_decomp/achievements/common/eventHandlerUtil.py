#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\achievements\common\eventHandlerUtil.py
import evetypes

def ListContainsTypeInGivenCategories(typeIDs, categoryIDs):

    def IsCategoryInList(typeID):
        return evetypes.GetCategoryID(typeID) in categoryIDs

    return ContainsTypeInGivenCollections(typeIDs, IsCategoryInList)


def ListContainsTypeInGivenGroups(typeIDs, groupIDs):

    def IsGroupInList(typeID):
        return evetypes.GetGroupID(typeID) in groupIDs

    return ContainsTypeInGivenCollections(typeIDs, IsGroupInList)


def ContainsTypeInGivenCollections(typeIDs, checkFunc):
    for typeID in typeIDs:
        if not evetypes.Exists(typeID):
            continue
        if checkFunc(typeID):
            return True

    return False
