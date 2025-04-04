#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\paperDollUtil.py
import blue
import yaml
import localization
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import eve.common.script.paperDoll.paperDollDataManagement as pdDM
from utillib import KeyVal
FACIAL_POSE_PARAMETERS = KeyVal(PortraitPoseNumber='PortraitPoseNumber', HeadLookTarget='HeadLookTarget', HeadTilt='HeadTilt', OrientChar='OrientChar', BrowLeftCurl='BrowLeftCurl', BrowLeftTighten='BrowLeftTighten', BrowLeftUpDown='BrowLeftUpDown', BrowRightCurl='BrowRightCurl', BrowRightTighten='BrowRightTighten', BrowRightUpDown='BrowRightUpDown', EyeClose='EyeClose', EyesLookVertical='EyesLookVertical', EyesLookHorizontal='EyesLookHorizontal', SquintLeft='SquintLeft', SquintRight='SquintRight', JawSideways='JawSideways', JawUp='JawUp', PuckerLips='PuckerLips', FrownLeft='FrownLeft', FrownRight='FrownRight', SmileLeft='SmileLeft', SmileRight='SmileRight')

def CreateRandomDoll(gender, bloodline, race, doll = None):
    ml = pdDM.ModifierLoader()
    blue.synchro.Yield()
    from eve.client.script.ui.login.charcreation.eveDollRandomizer import EveDollRandomizer
    randomizer = EveDollRandomizer(ml)
    if gender is not None:
        randomizer.gender = gender
    if bloodline is not None:
        randomizer.bloodline = bloodline
    if race is not None:
        randomizer.race = race
    randomizer.SetSculptingLimits()
    doll = randomizer.GetDoll(True, doll)
    randomizer.RandomizeHairColor(doll)
    return doll


def CreateRandomDollNoClothes(gender, bloodline, race, doll = None, noRandomize = False):
    from eve.client.script.ui.login.charcreation.eveDollRandomizer import EveDollRandomizer
    ml = pdDM.ModifierLoader()
    blue.synchro.Yield()
    randomizer = EveDollRandomizer(ml)
    randomizer.isNewCharacter = True
    if gender is not None:
        randomizer.gender = gender
    if bloodline is not None:
        randomizer.bloodline = bloodline
    if race is not None:
        randomizer.race = race
    randomizer.SetSculptingLimits()
    options = randomizer.ListOptions(None)
    if doll is not None:
        randomizer.RemoveAllOptionsByCategory(doll, options)
    else:
        import eve.client.script.paperDoll.paperDollImpl as pdImp
        doll = pdImp.Doll('randomized', gender=gender)
    for x in [pdDef.DOLL_PARTS.HEAD, pdDef.BODY_CATEGORIES.SKIN]:
        randomizer.AddCategoryForWhitelistRandomization(x)

    resourceDict = randomizer.GetResources()
    randomizer.AddRandomizedResourcesToDoll(doll, resourceDict)
    if not noRandomize:
        blendshapes = randomizer.GetBlendshapeOptions()
        del blendshapes[pdDef.DOLL_EXTRA_PARTS.BODYSHAPES]
        randomizer.AddRandomizedResourcesToDoll(doll, blendshapes)
    return doll


MODIFIER_LOCATION_BY_KEY = {}
REQUIRED_MODIFICATION_LOCATIONS = set()
REQUIRED_MODIFICATION_LOCATIONS_FEMALE = {}
REQUIRED_MODIFICATION_LOCATIONS_MALE = {}

def CacheRequiredModifierLocatiosn():
    if not len(MODIFIER_LOCATION_BY_KEY):
        for row in cfg.paperdollModifierLocations:
            MODIFIER_LOCATION_BY_KEY[row.modifierKey] = row.modifierLocationID

    if not len(REQUIRED_MODIFICATION_LOCATIONS):
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.OUTER])
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.TOPOUTER])
        REQUIRED_MODIFICATION_LOCATIONS.add(MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.TOPMIDDLE])
    if not len(REQUIRED_MODIFICATION_LOCATIONS_FEMALE):
        REQUIRED_MODIFICATION_LOCATIONS_FEMALE[MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.BOTTOMOUTER]] = localization.GetByLabel('UI/CharacterCustomization/Bottom')
        REQUIRED_MODIFICATION_LOCATIONS_FEMALE[MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.FEET]] = localization.GetByLabel('UI/CharacterCustomization/Feet')
    if not len(REQUIRED_MODIFICATION_LOCATIONS_MALE):
        REQUIRED_MODIFICATION_LOCATIONS_MALE[MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.BOTTOMOUTER]] = localization.GetByLabel('UI/CharacterCustomization/Bottom')
        REQUIRED_MODIFICATION_LOCATIONS_MALE[MODIFIER_LOCATION_BY_KEY[pdDef.BODY_CATEGORIES.FEET]] = localization.GetByLabel('UI/CharacterCustomization/Feet')


def HasRequiredClothing(dollGender, dollTypes):
    CacheRequiredModifierLocatiosn()
    dollModifierLocations = set([ row.modifierLocationID for row in dollTypes ])
    missingCategoryDescriptions = {}
    for category in REQUIRED_MODIFICATION_LOCATIONS:
        if category not in dollModifierLocations:
            missingCategoryDescriptions[category] = None

    if dollGender == 'female':
        dollCategories = REQUIRED_MODIFICATION_LOCATIONS_FEMALE
    else:
        dollCategories = REQUIRED_MODIFICATION_LOCATIONS_MALE
    for category, description in dollCategories.iteritems():
        if category not in dollModifierLocations and category not in missingCategoryDescriptions:
            missingCategoryDescriptions[category] = description

    requirementExceptions = GetRequirementExceptions(dollTypes)
    coveredByOtherAssets = requirementExceptions['covers']
    notCoveredByAsset = requirementExceptions['doesntCover'] - coveredByOtherAssets
    for eachCategory in coveredByOtherAssets:
        missingCategoryDescriptions.pop(eachCategory, None)

    for eachCategory in notCoveredByAsset:
        if eachCategory in REQUIRED_MODIFICATION_LOCATIONS:
            missingCategoryDescriptions[eachCategory] = None
        elif eachCategory in dollCategories:
            missingCategoryDescriptions[eachCategory] = dollCategories[eachCategory]

    topOn = False
    for eachCategory in REQUIRED_MODIFICATION_LOCATIONS:
        if eachCategory not in missingCategoryDescriptions:
            topOn = True
        missingCategoryDescriptions.pop(eachCategory, None)

    if not topOn:
        missingCategoryDescriptions['top'] = localization.GetByLabel('UI/CharacterCustomization/Top')
    if len(missingCategoryDescriptions) > 0:
        raise UserError('MissingRequiredClothing', {'clothingList': ', '.join(missingCategoryDescriptions.values())})
    return True


def GetRequirementExceptions(dollTypes):
    assetChanges = {'covers': set(),
     'doesntCover': set()}
    typesOn = set()
    for resourceRow in dollTypes:
        rID = resourceRow.paperdollResourceID
        if rID is None:
            continue
        resource = cfg.paperdollResources.Get(rID)
        if resource.typeID is not None:
            typesOn.add((resource.typeID,
             resourceRow.modifierLocationID,
             resource.clothingAlsoCoversCategory,
             resource.clothingAlsoCoversCategory2,
             resource.clothingRuleException))

    for typeOn, category, clothingAlsoCoversCategory, clothingAlsoCoversCategory2, clothingRuleException in typesOn:
        if clothingAlsoCoversCategory is not None and clothingAlsoCoversCategory != 0:
            covers = int(clothingAlsoCoversCategory)
            assetChanges['covers'].add(covers)
        if clothingAlsoCoversCategory2 is not None and clothingAlsoCoversCategory2 != 0:
            covers = int(clothingAlsoCoversCategory2)
            assetChanges['covers'].add(covers)
        if clothingRuleException:
            assetChanges['doesntCover'].add(category)

    return assetChanges


def BuildPaperdollProcedureArgs(dollInfo):
    procargs = []
    procargs.append(yaml.dump(dollInfo.faceModifiers, Dumper=yaml.CDumper))
    procargs.append(yaml.dump(dollInfo.bodyShapes, Dumper=yaml.CDumper))
    procargs.append(yaml.dump(dollInfo.utilityShapes, Dumper=yaml.CDumper))
    procargs.append(dollInfo.typeColors['skintone'][0])
    procargs.append(dollInfo.types.get('makeup/aging'))
    procargs.append(dollInfo.types.get('makeup/freckles'))
    procargs.append(dollInfo.types.get('makeup/scarring'))
    procargs.append(dollInfo.types.get('makeup/eyes'))
    procargs.append(dollInfo.typeColors.get('makeup/eyes')[0])
    if 'makeup/eyeshadow' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/eyeshadow'])
        procargs.append(dollInfo.typeWeights['makeup/eyeshadow'])
        procargs.append(dollInfo.typeColors['makeup/eyeshadow'][0])
        procargs.append(dollInfo.typeColors['makeup/eyeshadow'][1])
    else:
        procargs.extend([None] * 4)
    if 'makeup/eyeliner' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/eyeliner'])
        procargs.append(dollInfo.typeWeights['makeup/eyeliner'])
        procargs.append(dollInfo.typeColors['makeup/eyeliner'][0])
    else:
        procargs.extend([None] * 3)
    if 'makeup/blush' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/blush'])
        procargs.append(dollInfo.typeWeights['makeup/blush'])
        procargs.append(dollInfo.typeColors['makeup/blush'][0])
    else:
        procargs.extend([None] * 3)
    if 'makeup/lipstick' in dollInfo.types:
        procargs.append(dollInfo.types['makeup/lipstick'])
        procargs.append(dollInfo.typeWeights['makeup/lipstick'])
        procargs.append(dollInfo.typeSpecularity.get('makeup/lipstick'))
        procargs.append(dollInfo.typeColors['makeup/lipstick'][0])
    else:
        procargs.extend([None] * 4)
    procargs.append(dollInfo.types['hair'])
    procargs.append(dollInfo.typeColors['hair'][0])
    procargs.append(dollInfo.typeColors['hair'][1])
    procargs.append(dollInfo.types.get('makeup/eyebrows'))
    procargs.append(dollInfo.types.get('beard'))
    procargs.append(dollInfo.hairDarkness)
    procargs.append(dollInfo.types.get('bottominner'))
    procargs.append(dollInfo.types.get('bottomouter'))
    procargs.append(dollInfo.typeTuck.get('dependants/boottucking'))
    procargs.append(dollInfo.types.get('topmiddle'))
    procargs.append(dollInfo.typeTuck.get('dependants/drape'))
    procargs.append(dollInfo.types.get('topouter'))
    procargs.append(dollInfo.types.get('feet'))
    procargs.append(dollInfo.types.get('outer'))
    procargs.append(dollInfo.typeTuck.get('dependants/hood'))
    procargs.append(dollInfo.types.get('topinner'))
    procargs.append(dollInfo.types.get('accessories/glasses'))
    procargs.append(dollInfo.types.get('makeup/implants'))
    return procargs
