#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evetypes\__init__.py
from collections import defaultdict
import inventorycommon.const
from caching import Memoize
from evetypes.const import *
from evetypes.data import Categories, Groups, TypeListLoader, Types
from evetypes.localizationUtils import GetLocalizedCategoryName, GetLocalizedCategoryName, GetLocalizedGroupName, GetLocalizedGroupName, GetLocalizedTypeDescription, GetLocalizedTypeDescription, GetLocalizedTypeName, GetLocalizedTypeName, GetLocalizedTypeListName
from fsdBuiltData.common.errors import NoBinaryLoaderError
try:
    import blue

    def BeNice():
        blue.pyos.BeNice()


except ImportError:

    def BeNice():
        pass


class TypeNotFoundException(Exception):
    pass


class GroupNotFoundException(Exception):
    pass


class CategoryNotFoundException(Exception):
    pass


class TypeAttributeNotFoundException(Exception):
    pass


class GroupAttributeNotFoundException(Exception):
    pass


class CategoryAttributeNotFoundException(Exception):
    pass


class TypeListNotFoundException(Exception):
    pass


def GetTypes():
    return Types.GetData()


def GetGroups():
    return Groups.GetData()


def GetCategories():
    return Categories.GetData()


def GetType(typeID):
    try:
        return GetTypes()[int(typeID)]
    except (KeyError, TypeError, ValueError) as e:
        raise TypeNotFoundException(e)


def GetGroup(groupID):
    try:
        return GetGroups()[int(groupID)]
    except (KeyError, TypeError, ValueError) as e:
        raise GroupNotFoundException(e)


def GetCategory(categoryID):
    try:
        return GetCategories()[int(categoryID)]
    except (KeyError, TypeError, ValueError) as e:
        raise CategoryNotFoundException(e)


def _GetAttributeForType(typeID, attribute):
    try:
        return getattr(GetType(typeID), attribute)
    except AttributeError as e:
        raise TypeAttributeNotFoundException(e)


def _GetAttributeForGroup(groupID, attribute):
    try:
        return getattr(GetGroup(groupID), attribute)
    except AttributeError as e:
        raise GroupAttributeNotFoundException(e)


def _GetAttributeForCategory(categoryID, attribute):
    try:
        return getattr(GetCategory(categoryID), attribute)
    except AttributeError as e:
        raise CategoryAttributeNotFoundException(e)


def GetAttributeForType(typeID, attribute):
    if attribute == 'radius':
        return GetRadius(typeID)
    return _GetAttributeForType(typeID, attribute)


def GetRawAttributeForType(typeID, attribute):
    try:
        return _GetAttributeForType(typeID, attribute)
    except TypeAttributeNotFoundException:
        return None


def GetTotalTypeCount():
    return len(GetTypes())


def GetTotalGroupCount():
    return len(GetGroups())


def GetTotalCategoryCount():
    return len(GetCategories())


def Exists(typeID):
    try:
        return int(typeID) in GetTypes()
    except (TypeError, ValueError):
        return False


def GroupExists(groupID):
    try:
        return int(groupID) in GetGroups()
    except (TypeError, ValueError):
        return False


def CategoryExists(categoryID):
    try:
        return int(categoryID) in GetCategories()
    except (TypeError, ValueError):
        return False


def Iterate():
    for typeID in GetTypes().iterkeys():
        yield typeID


def IterateGroups():
    for groupID in GetGroups().iterkeys():
        yield groupID


def IterateCategories():
    for categoryID in GetCategories().iterkeys():
        yield categoryID


def GetAllTypeIDs():
    return GetTypes().keys()


def GetAllGroupIDs():
    return GetGroups().keys()


def GetAllCategoryIDs():
    return GetCategories().keys()


def RaiseIFNotExists(typeID):
    try:
        if int(typeID) not in GetTypes():
            raise TypeNotFoundException(typeID)
    except (TypeError, ValueError):
        raise TypeNotFoundException(typeID)


def GetRaceID(typeID):
    return _GetAttributeForType(typeID, 'raceID')


def GetGroupID(typeID):
    return _GetAttributeForType(typeID, 'groupID')


def GetVolume(typeID):
    return float(_GetAttributeForType(typeID, 'volume'))


def GetIconID(typeID):
    return _GetAttributeForType(typeID, 'iconID')


def GetGraphicID(typeID):
    return _GetAttributeForType(typeID, 'graphicID')


def GetFactionID(typeID):
    return _GetAttributeForType(typeID, 'factionID')


def GetOwnerID(typeID):
    return _GetAttributeForType(typeID, 'factionID')


def GetShipGroupID(typeID):
    return _GetAttributeForType(typeID, 'isisGroupID')


def GetNameID(typeID):
    return _GetAttributeForType(typeID, 'typeNameID')


def GetDescriptionID(typeID):
    return _GetAttributeForType(typeID, 'descriptionID')


def GetCapacity(typeID):
    return float(_GetAttributeForType(typeID, 'capacity'))


def GetBasePrice(typeID):
    return _GetAttributeForType(typeID, 'basePrice')


def GetPortionSize(typeID):
    return _GetAttributeForType(typeID, 'portionSize')


def GetMarketGroupID(typeID):
    return _GetAttributeForType(typeID, 'marketGroupID')


def GetSoundID(typeID):
    return _GetAttributeForType(typeID, 'soundID')


def GetMass(typeID):
    return float(_GetAttributeForType(typeID, 'mass'))


def IsDynamicType(typeID):
    return bool(_GetAttributeForType(typeID, 'isDynamicType'))


def GetMetaLevel(typeID):
    return _GetAttributeForType(typeID, 'metaLevel')


def GetTechLevel(typeID):
    return _GetAttributeForType(typeID, 'techLevel')


def GetMetaGroupID(typeID):
    return _GetAttributeForType(typeID, 'metaGroupID')


def GetMetaGroupIDOrNone(typeID):
    try:
        return _GetAttributeForType(typeID, 'metaGroupID')
    except TypeNotFoundException:
        return None


def GetDesigners(typeID):
    try:
        designers = _GetAttributeForType(typeID, 'designerIDs')
        if not designers:
            return []
        return [ designer for designer in designers ]
    except TypeNotFoundException:
        return []


def GetQuoteID(typeID):
    return _GetAttributeForType(typeID, 'quoteID')


def GetQuoteAuthorID(typeID):
    try:
        quoteAuthorID = _GetAttributeForType(typeID, 'quoteAuthorID')
        if quoteAuthorID is not None:
            return quoteAuthorID
    except TypeNotFoundException:
        return


def GetSofBuildClassOrNone(typeID):
    try:
        categoryID = GetCategoryID(typeID)
        return _GetAttributeForCategory(categoryID, 'sofBuildClass')
    except (TypeAttributeNotFoundException, CategoryAttributeNotFoundException):
        return None


def GetWreckTypeIDOrNone(typeID):
    try:
        wreckTypeID = _GetAttributeForType(typeID, 'wreckTypeID')
        if wreckTypeID is not None:
            return wreckTypeID
    except TypeNotFoundException:
        return


def IsPublished(typeID):
    return _GetAttributeForType(typeID, 'published')


def IsBasePriceNotZero(typeID):
    return _GetAttributeForType(typeID, 'basePrice') > 0


def GetRadius(typeID):
    radius = _GetAttributeForType(typeID, 'radius')
    return float(radius or 1.0)


def IsGroupPublished(typeID):
    groupID = GetGroupID(typeID)
    return IsGroupPublishedByGroup(groupID)


def GetCategoryID(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'categoryID')


def GetCategoryNameID(typeID):
    categoryID = GetCategoryID(typeID)
    return _GetAttributeForCategory(categoryID, 'categoryNameID')


def GetDescription(typeID, languageID = None):
    descriptionID = GetDescriptionID(typeID)
    return GetLocalizedTypeDescription(descriptionID, languageID)


def GetDescriptionOrNone(typeID):
    try:
        return GetDescription(typeID)
    except TypeNotFoundException:
        return None


def GetName(typeID, languageID = None, important = True):
    nameID = GetNameID(typeID)
    return GetLocalizedTypeName(nameID, languageID, important)


def GetNameOrNone(typeID):
    try:
        return GetName(typeID)
    except TypeNotFoundException:
        return None


def GetEnglishName(typeID):
    return GetName(typeID, 'en-us', important=False)


def IsCategoryPublished(typeID):
    categoryID = GetCategoryID(typeID)
    return _GetAttributeForCategory(categoryID, 'published')


def GetCategoryName(typeID, languageID = None):
    categoryID = GetCategoryID(typeID)
    categoryNameID = _GetAttributeForCategory(categoryID, 'categoryNameID')
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID)


def UseGroupBasePrice(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'useBasePrice')


def GetGroupName(typeID, languageID = None, important = True):
    groupID = GetGroupID(typeID)
    groupNameID = _GetAttributeForGroup(groupID, 'groupNameID')
    return GetLocalizedGroupName(groupNameID, languageID=languageID, important=important)


def GetGroupNameID(typeID):
    groupID = GetGroupID(typeID)
    return _GetAttributeForGroup(groupID, 'groupNameID')


def GetCertificateTemplate(typeID):
    return _GetAttributeForType(typeID, 'certificateTemplate')


def GetTypeIDsByMarketGroup(marketGroupID):
    typeIDsByMarketGroupID = getattr(GetTypeIDsByMarketGroup, '_typeIDsByMarketGroupID', defaultdict(set))
    if not typeIDsByMarketGroupID:
        for typeID, typeData in GetTypes().iteritems():
            typeIDsByMarketGroupID[typeData.marketGroupID].add(typeID)

        GetTypeIDsByMarketGroup._typeIDsByMarketGroupID = typeIDsByMarketGroupID
    return set(typeIDsByMarketGroupID.get(marketGroupID, []))


def _GetTypeIDsByGroupID():
    typeIDsByGroupID = getattr(_GetTypeIDsByGroupID, '_typeIDsByGroupID', defaultdict(set))
    if not typeIDsByGroupID:
        for typeID, typeData in GetTypes().iteritems():
            typeIDsByGroupID[typeData.groupID].add(typeID)

        _GetTypeIDsByGroupID._typeIDsByGroupID = typeIDsByGroupID
    return typeIDsByGroupID


def GetTypeIDsByGroup(groupID):
    typeIDsByGroupID = _GetTypeIDsByGroupID()
    return set(typeIDsByGroupID.get(groupID, []))


def GetTypeIDsByGroups(groupIDs):
    types = set()
    typeIDsByGroup = _GetTypeIDsByGroupID()
    for groupID in groupIDs:
        types.update(typeIDsByGroup.get(groupID, []))

    return types


def UseGroupBasePriceByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'useBasePrice')


def GetGroupNameByGroup(groupID, languageID = None, important = True):
    groupNameID = _GetAttributeForGroup(int(groupID), 'groupNameID')
    return GetLocalizedGroupName(groupNameID, languageID=languageID, important=important)


def GetCategoryIDByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'categoryID')


def GetGroupNameIDByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'groupNameID')


def GetIsGroupFittableNonSingletonByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'fittableNonSingleton')


def GetIsGroupAnchorableByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'anchorable')


def GetIsGroupAnchoredByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'anchored')


def IsGroupPublishedByGroup(groupID):
    return _GetAttributeForGroup(groupID, 'published')


def IsGroupBasePriceUsed(groupID):
    return _GetAttributeForGroup(groupID, 'useBasePrice')


def GetGroupIconIDByGroup(groupID):
    return _GetAttributeForGroup(int(groupID), 'iconID')


def GetCategoryNameByGroup(groupID, languageID = None):
    categoryID = GetCategoryIDByGroup(groupID)
    categoryNameID = _GetAttributeForCategory(categoryID, 'categoryNameID')
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID)


def IsCategoryPublishedByGroup(groupID):
    categoryID = GetCategoryIDByGroup(groupID)
    return _GetAttributeForCategory(categoryID, 'published')


def IsCategoryPublishedByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'published')


def GetCategoryIconIDByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'iconID')


def GetCategorySofBuildClass(categoryID):
    return _GetAttributeForCategory(categoryID, 'sofBuildClass')


def IsCategoryHardwareByCategory(categoryID):
    return categoryID in (inventorycommon.const.categoryModule,
     inventorycommon.const.categoryStructureModule,
     inventorycommon.const.categoryImplant,
     inventorycommon.const.categorySubSystem)


def GetTypeIDsByCategory(categoryID):
    return GetTypeIDsByGroups(GetGroupIDsByCategory(categoryID))


def GetTypeIDsByCategories(categoryIDs):
    return GetTypeIDsByGroups(GetGroupIDsByCategories(categoryIDs))


def GetCategoryNameIDByCategory(categoryID):
    return _GetAttributeForCategory(categoryID, 'categoryNameID')


def GetCategoryNameByCategory(categoryID, languageID = None, important = True):
    categoryNameID = GetCategoryNameIDByCategory(categoryID)
    return GetLocalizedCategoryName(categoryNameID, languageID=languageID, important=important)


def _GetGroupIDsByCategoryID():
    groupIDsByCategory = getattr(_GetGroupIDsByCategoryID, '_groupIDsByCategory', defaultdict(set))
    if not groupIDsByCategory:
        for groupID, groupData in GetGroups().iteritems():
            groupIDsByCategory[groupData.categoryID].add(groupID)

        _GetGroupIDsByCategoryID._groupIDsByCategory = groupIDsByCategory
    return groupIDsByCategory


def GetGroupIDsByCategory(categoryID):
    groupIDsByCategoryID = _GetGroupIDsByCategoryID()
    return set(groupIDsByCategoryID.get(categoryID, []))


def GetGroupIDsByCategories(categoryIDs):
    groups = set()
    groupIDsByCategoryID = _GetGroupIDsByCategoryID()
    for categoryID in categoryIDs:
        groups.update(groupIDsByCategoryID.get(categoryID, []))

    return groups


def GetTypeIDByNameDict(forceReload = False):
    typeIDsByName = getattr(GetTypeIDByNameDict, '_typeIDsByName', {})
    if not typeIDsByName or forceReload:
        types = GetTypes()
        for typeID in Iterate():
            BeNice()
            name = GetLocalizedTypeName(types[typeID].typeNameID, None, important=False)
            if name is not None:
                typeIDsByName[name.lower()] = typeID

        GetTypeIDByNameDict._typeIDsByName = typeIDsByName
    return typeIDsByName


def GetTypeIDByName(typeName):
    try:
        return GetTypeIDByNameDict()[typeName.lower()]
    except KeyError as e:
        raise TypeNotFoundException(e)


def GetGroupIDByGroupNameDict(foreReload = False):
    groupIDsByName = getattr(GetGroupIDByGroupName, '_groupIDsByName', {})
    if not groupIDsByName or foreReload:
        storage = GetGroups()
        for groupID in IterateGroups():
            name = GetLocalizedGroupName(storage[groupID].groupNameID, None)
            if name is not None:
                groupIDsByName[name.lower()] = groupID

        GetGroupIDByGroupName._groupIDsByName = groupIDsByName
    return groupIDsByName


def GetGroupIDByGroupName(groupName):
    try:
        return GetGroupIDByGroupNameDict()[groupName.lower()]
    except KeyError as e:
        raise GroupNotFoundException(e)


def ClearMemoized():
    GetTypeIDsByListID.clear_memoized()


def GetTypeList(listID):
    try:
        return TypeListLoader.GetData()[int(listID)]
    except (KeyError, ValueError, TypeError) as e:
        raise TypeListNotFoundException(e)


@Memoize
def GetTypeIDsByListID(listID):
    return GetTypeIDsFromTypeList(GetTypeList(listID))


@Memoize
def GetTypeIDsByListIDs(listIDs):
    typeIDs = []
    for listID in listIDs:
        typeIDs += GetTypeIDsByListID(listID)

    return typeIDs


def GetTypeListInternalName(listID):
    return GetTypeList(listID).name


def GetTypeListInternalDescription(listID):
    return GetTypeList(listID).description


def GetTypeListDisplayName(listID):
    messageID = GetTypeListDisplayNameMessageID(listID)
    if messageID:
        return GetLocalizedTypeListName(messageID)


def GetTypeListDisplayNameMessageID(listID):
    return GetTypeList(listID).displayNameID


def GetTypeListDescriptionMessageID(listID):
    return GetTypeList(listID).displayDescriptionID


def GetTypeIDsFromTypeList(typelist):
    includedCategories = GetTypeIDsByCategories(typelist.includedCategoryIDs)
    includedGroups = GetTypeIDsByGroups(typelist.includedGroupIDs)
    includedTypes = set(typelist.includedTypeIDs)
    excludedCategories = GetTypeIDsByCategories(typelist.excludedCategoryIDs)
    excludedGroups = GetTypeIDsByGroups(typelist.excludedGroupIDs)
    excludedTypes = set(typelist.excludedTypeIDs)
    finalTypes = includedCategories - excludedCategories
    finalTypes = finalTypes.union(includedGroups) - excludedGroups
    finalTypes = finalTypes.union(includedTypes) - excludedTypes
    return finalTypes


def IsWeaponModule(type_id):
    return type_id in GetTypeIDsByListID(TYPE_LIST_WEAPON_MODULES)


TypeListLoader.ConnectToOnReload(ClearMemoized)

def IsRenderable(typeID):
    return typeID in GetTypeIDsByListID(TYPE_LIST_RENDERABLE_IDS)


def IsCapitalShip(typeID):
    return typeID in GetTypeIDsByListID(TYPE_LIST_CAPITAL_SHIPS)


def IsStructureAlwaysGlobal(typeID):
    from structures.types import IsFlexStructure
    return IsFlexStructure(typeID) or IsPirateInsurgencyFOB(typeID)


def IsPirateInsurgencyFOB(typeID):
    return GetGroupID(typeID) == inventorycommon.const.groupStructurePirateForwardOperatingBase


def IsUpwellStargate(typeID):
    return GetGroupID(typeID) == inventorycommon.const.groupStructureJumpBridge


def IsSkill(typeID):
    return GetCategoryID(typeID) == inventorycommon.const.categorySkill


def IsSkillAvailableForPurchase(typeID):
    if not IsPublished(typeID):
        return False
    return typeID in GetTypeIDsByListID(TYPE_LIST_SKILLS_AVAILABLE_FOR_PURCHASE)


_typeVariations = {}

def ClearVariationCache(categoryID = None):
    if categoryID is not None:
        if categoryID in _typeVariations:
            del _typeVariations[categoryID]
    else:
        _typeVariations.clear()


def _LoadVariationCategory(categoryID):
    if categoryID not in _typeVariations:
        _typeVariations[categoryID] = defaultdict(list)
        for typeID in GetTypeIDsByCategory(categoryID):
            parentID = GetVariationParentTypeIDOrNone(typeID)
            if parentID is not None:
                _typeVariations[categoryID][parentID].append(typeID)


def _LoadAllVariationCategories():
    categories = GetAllCategoryIDs()
    for categoryID in categories:
        _LoadVariationCategory(categoryID)


def GetVariationParentTypeID(typeID):
    return _GetAttributeForType(typeID, 'variationParentTypeID')


def GetDevNotes(typeID):
    return _GetAttributeForType(typeID, 'devNotes')


def GetVariationParentTypeIDOrNone(typeID):
    try:
        return GetVariationParentTypeID(typeID)
    except (TypeNotFoundException, TypeAttributeNotFoundException):
        return None


def GetVariationChildren(typeID):
    categoryID = GetCategoryID(typeID)
    if categoryID is not None:
        if categoryID not in _typeVariations:
            _LoadVariationCategory(categoryID)
        return _typeVariations[categoryID].get(typeID, None)


def GetAllVariationParents():
    _LoadAllVariationCategories()
    parentList = []
    for parents in _typeVariations.values():
        parentList.extend(parents.keys())

    return parentList


def GetVariationParentsByCategory(categoryID):
    _LoadVariationCategory(categoryID)
    return _typeVariations[categoryID].keys()


def GetAllVariationChildren():
    _LoadAllVariationCategories()
    childList = []
    for parents in _typeVariations.values():
        for children in parents.values():
            childList.extend(children)

    return childList


def GetVariationChildrenByCategory(categoryID):
    _LoadVariationCategory(categoryID)
    childList = []
    for children in _typeVariations[categoryID].values():
        childList.extend(children)

    return childList


def GetVariations(typeID):
    variations = []
    parentID = GetVariationParentTypeIDOrNone(typeID)
    if parentID is None:
        parentID = typeID
    children = GetVariationChildren(parentID)
    if children is not None:
        variations = children + [parentID]
    return variations


def GetParentIDOfVariations(typeID):
    parentTypeID = None
    parentID = GetVariationParentTypeIDOrNone(typeID)
    if parentID is not None:
        parentTypeID = parentID
    elif GetVariationChildren(typeID):
        parentTypeID = typeID
    return parentTypeID


def GetSellPrice(typeID):
    category = GetCategoryID(typeID)
    base_price = GetCalculatedBasePrice(typeID)
    portion_size = GetPortionSize(typeID)
    if category in (inventorycommon.const.categoryShip,
     inventorycommon.const.categoryModule,
     inventorycommon.const.categoryCharge,
     inventorycommon.const.categoryDrone):
        if portion_size == 1:
            return 2 * round(base_price / portion_size, 2)
        else:
            return 3 * round(base_price / portion_size, 2)
    else:
        return base_price


def GetCalculatedBasePrice(typeID):
    if UseGroupBasePrice(typeID):
        return GetBasePrice(typeID)
    else:
        return GetCalculatedMaterialBasePrice(typeID)


def GetCalculatedMaterialBasePrice(typeID):
    import typematerials.data as typeMaterials
    try:
        materials = typeMaterials.get_type_materials_by_id(typeID)
        builtDataAvailable = True
    except NoBinaryLoaderError:
        materials = GetTypeMaterialsByIdStatic(typeID)
        builtDataAvailable = False

    price = 0
    for material in materials:
        materialTypeId = material.materialTypeID if builtDataAvailable else material['materialTypeID']
        materialQuantity = material.quantity if builtDataAvailable else material['quantity']
        price += GetMaterialBasePrice(materialTypeId, materialQuantity, builtDataAvailable, typeMaterials.get_type_materials_by_id)

    return round(price, 2)


def GetMaterialBasePrice(typeID, quantity, builtDataAvailable, getTypeMaterialsByID):
    if UseGroupBasePrice(typeID):
        return GetBasePrice(typeID) * quantity / float(GetPortionSize(typeID))
    materials = getTypeMaterialsByID(typeID) if builtDataAvailable else GetTypeMaterialsByIdStatic(typeID)
    price = 0
    for material in materials:
        materialTypeId = material.materialTypeID if builtDataAvailable else material['materialTypeID']
        materialQuantity = material.quantity if builtDataAvailable else material['quantity']
        price += GetMaterialBasePrice(materialTypeId, quantity / float(GetPortionSize(typeID)) * materialQuantity, builtDataAvailable, getTypeMaterialsByID)

    return price


def GetTypeMaterialsByIdStatic(typeID):
    import yaml
    from fsd import AbsJoin, GetBranchRoot
    _path = AbsJoin(GetBranchRoot(), 'eve', 'staticData', 'typeMaterials', 'data', '{}.staticdata'.format(typeID))
    try:
        with open(_path, 'r') as fd:
            data = yaml.load(fd, yaml.Loader)
            return data[typeID]['materials']
    except IOError:
        return []


def _OnReloadTypes():
    if hasattr(GetTypeIDByNameDict, '_typeIDsByName'):
        delattr(GetTypeIDByNameDict, '_typeIDsByName')
    if hasattr(_GetTypeIDsByGroupID, '_typeIDsByGroupID'):
        delattr(_GetTypeIDsByGroupID, '_typeIDsByGroupID')
    if hasattr(GetTypeIDsByMarketGroup, '_typeIDsByMarketGroupID'):
        delattr(GetTypeIDsByMarketGroup, '_typeIDsByMarketGroupID')


def _OnReloadGroups():
    if hasattr(GetGroupIDByGroupNameDict, '_groupIDsByName'):
        delattr(GetGroupIDByGroupNameDict, '_groupIDsByName')
    if hasattr(_GetGroupIDsByCategoryID, '_groupIDsByCategory'):
        delattr(_GetGroupIDsByCategoryID, '_groupIDsByCategory')


Types.ConnectToOnReload(_OnReloadTypes)
Groups.ConnectToOnReload(_OnReloadGroups)
