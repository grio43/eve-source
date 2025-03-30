#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\character.py
import character_colorLocationsLoader
import character_colorNamesLoader
import character_modifierLocationsLoader
import character_resourcesLoader
import character_sculptingLocationsLoader
import character_portraitresourcesLoader
import character_avatarbehaviorsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class CharacterModifierLocation(object):

    def __init__(self, modifierLocationID, modifierKey, variationKey):
        self.modifierLocationID = modifierLocationID
        self.modifierKey = modifierKey
        self.variationKey = variationKey


class CharacterResource(object):

    def __init__(self, paperdollResourceID, resGender, resPath, empireRestrictions, typeID, clothingAlsoCoversCategory, clothingAlsoCoversCategory2, clothingRemovesCategory, clothingRemovesCategory2, clothingRuleException):
        self.paperdollResourceID = paperdollResourceID
        self.resGender = resGender
        self.resPath = resPath
        self.empireRestrictions = empireRestrictions
        self.typeID = typeID
        self.clothingAlsoCoversCategory = clothingAlsoCoversCategory
        self.clothingAlsoCoversCategory2 = clothingAlsoCoversCategory2
        self.clothingRemovesCategory = clothingRemovesCategory
        self.clothingRemovesCategory2 = clothingRemovesCategory2
        self.clothingRuleException = clothingRuleException


class CharacterSculptingLocation(object):

    def __init__(self, sculptLocationID, weightKeyCategory, weightKeyPrefix):
        self.sculptLocationID = sculptLocationID
        self.weightKeyCategory = weightKeyCategory
        self.weightKeyPrefix = weightKeyPrefix


class CharacterColorLocation(object):

    def __init__(self, colorID, colorKey, hasSecondary, hasWeight, hasGloss):
        self.colorID = colorID
        self.colorKey = colorKey
        self.hasSecondary = hasSecondary
        self.hasWeight = hasWeight
        self.hasGloss = hasGloss


class CharacterColorName(object):

    def __init__(self, colorNameID, colorName):
        self.colorNameID = colorNameID
        self.colorName = colorName


class CharacterPortraitResource(object):

    def __init__(self, portraitResourceID, resPath, typeID, resourceCategoryID):
        self.portraitResourceID = portraitResourceID
        self.resPath = resPath
        self.typeID = typeID
        self.resourceCategoryID = resourceCategoryID


class CharacterAvatarBehavior(object):

    def __init__(self, avatarBehaviorID, name, resGender, resPathList):
        self.avatarBehaviorID = avatarBehaviorID
        self.name = name
        self.resGender = resGender
        self.resPathList = resPathList


class CharacterRows(object):

    def __init__(self, key_attr_name):
        self.row_dict = {}
        self.rows = []
        self.key_attr_name = key_attr_name
        self.header = []

    def __iter__(self):
        return iter(self.rows)

    def keys(self):
        return self.row_dict.keys()

    def append(self, row):
        self.row_dict[getattr(row, self.key_attr_name)] = row
        self.rows.append(row)

    def GetIfExists(self, key):
        return self.row_dict.get(key, None)

    def Get(self, key):
        return self.row_dict.get(key, None)

    def get(self, key, default):
        result = [ x for x in self.rows if getattr(x, self.key_attr_name) == key ]
        if not result:
            return default
        return result


def GetColorLocationRows():
    colorLocations = Character_ColorLocations.GetData()
    rows = CharacterRows('colorID')
    for i in colorLocations:
        row = CharacterColorLocation(colorID=i, colorKey=colorLocations[i].colorKey, hasSecondary=colorLocations[i].hasSecondary, hasWeight=colorLocations[i].hasWeight, hasGloss=colorLocations[i].hasGloss)
        rows.append(row)

    return rows


def GetColorNameRows():
    colorNames = Character_ColorNames.GetData()
    rows = CharacterRows('colorNameID')
    for i in colorNames:
        row = CharacterColorName(colorNameID=i, colorName=colorNames[i].colorName)
        rows.append(row)

    return rows


def GetModifierLocationRows():
    modifierLocations = Character_ModifierLocations.GetData()
    rows = CharacterRows('modifierLocationID')
    for i in modifierLocations:
        row = CharacterModifierLocation(modifierLocationID=i, modifierKey=modifierLocations[i].modifierKey, variationKey=modifierLocations[i].variationKey)
        rows.append(row)

    return rows


def GetResourceRows():
    resources = Character_Resources.GetData()
    rows = CharacterRows('paperdollResourceID')
    for i in resources:
        empireRestrictions = None
        if resources[i].empireRestrictions is not None:
            empireRestrictions = [ restriction for restriction in resources[i].empireRestrictions ]
        row = CharacterResource(paperdollResourceID=i, resGender=resources[i].resGender, resPath=resources[i].resPath, empireRestrictions=empireRestrictions, typeID=resources[i].typeID, clothingAlsoCoversCategory=resources[i].clothingAlsoCoversCategory, clothingAlsoCoversCategory2=resources[i].clothingAlsoCoversCategory2, clothingRemovesCategory=resources[i].clothingRemovesCategory, clothingRemovesCategory2=resources[i].clothingRemovesCategory2, clothingRuleException=resources[i].clothingRuleException)
        rows.append(row)

    return rows


def GetSculptingLocationRows():
    sculptLocations = Character_SculptingLocations.GetData()
    rows = CharacterRows('sculptLocationID')
    for i in sculptLocations:
        row = CharacterSculptingLocation(sculptLocationID=i, weightKeyCategory=sculptLocations[i].weightKeyCategory, weightKeyPrefix=sculptLocations[i].weightKeyPrefix)
        rows.append(row)

    return rows


def GetPortraitResourceRows():
    resources = Character_Portrait_Resources.GetData()
    rows = CharacterRows('portraitResourceID')
    for i in resources:
        r = resources[i]
        row = CharacterPortraitResource(portraitResourceID=i, resPath=r.resPath, typeID=r.typeID, resourceCategoryID=r.resourceCategory)
        rows.append(row)

    return rows


def GetAvatarBehaviorRows():
    resources = Character_Avatar_Behaviors.GetData()
    rows = CharacterRows('avatarBehaviorID')
    for i in resources:
        r = resources[i]
        row = CharacterAvatarBehavior(avatarBehaviorID=i, name=r.name, resGender=r.resGender, resPathList=r.resPathList)
        rows.append(row)

    return rows


class Character_ColorLocations(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_colorLocations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_colorLocations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_colorLocations.fsdbinary'
    __loader__ = character_colorLocationsLoader


class Character_ColorNames(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_colorNames.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_colorNames.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_colorNames.fsdbinary'
    __loader__ = character_colorNamesLoader


class Character_ModifierLocations(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_modifierLocations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_modifierLocations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_modifierLocations.fsdbinary'
    __loader__ = character_modifierLocationsLoader


class Character_Resources(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_resources.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_resources.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_resources.fsdbinary'
    __loader__ = character_resourcesLoader


class Character_SculptingLocations(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_sculptingLocations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_sculptingLocations.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_sculptingLocations.fsdbinary'
    __loader__ = character_sculptingLocationsLoader


class Character_Portrait_Resources(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_portraitresources.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_portraitresources.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_portraitresources.fsdbinary'
    __loader__ = character_portraitresourcesLoader


class Character_Avatar_Behaviors(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/character_avatarbehaviors.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/character_avatarbehaviors.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/character_avatarbehaviors.fsdbinary'
    __loader__ = character_avatarbehaviorsLoader
