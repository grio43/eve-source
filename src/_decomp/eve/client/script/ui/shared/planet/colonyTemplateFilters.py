#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\colonyTemplateFilters.py
from carbonui.services.setting import UserSettingBool
from eve.client.script.ui.shared.planet.planetConst import SettingsHideInappropriateRadius
from eveplanet.client.templates.templateConst import ExtractionTypes, ProcessedTypes, RefinedTypes, SpecializedTypes, AdvancedTypes, PlanetTypes
SETTING_KEY_CMD_CNTR = 'ShowCmdCenterLV{0}'
SETTING_KEY_PLANET_TYPE = 'ShowPlanetType{0}'
SETTING_KEY_EXTRACT_TYPE = 'ShowExtractType{0}'
SETTING_KEY_PROCESSED = 'ShowProcessedType{0}'
SETTING_KEY_REFINED = 'ShowRefinedType{0}'
SETTING_KEY_SPECIALIZED = 'ShowSpecializedType{0}'
SETTING_KEY_ADVANCED = 'ShowAdvancedType{0}'
CMD_CTR_LELVES = list(range(1, 7))

def GetSetOfSelections(iterable, settingString):
    resultSet = set()
    for single in iterable:
        settingBool = UserSettingBool(settings_key=settingString.format(str(single)), default_value=False)
        if settingBool.get():
            resultSet.add(single)

    return resultSet


def GetValidTemplates(allTemplates, currentPlanetRadius, filterText):
    cmdCenterLVToShow = GetSetOfSelections(CMD_CTR_LELVES, SETTING_KEY_CMD_CNTR)
    planetTypesToShow = GetSetOfSelections(PlanetTypes.itervalues(), SETTING_KEY_PLANET_TYPE)
    extractTypesToShow = GetSetOfSelections(ExtractionTypes.itervalues(), SETTING_KEY_EXTRACT_TYPE)
    processedTypesToShow = GetSetOfSelections(ProcessedTypes.itervalues(), SETTING_KEY_PROCESSED)
    refinedTypesToShow = GetSetOfSelections(RefinedTypes.itervalues(), SETTING_KEY_REFINED)
    specializedTypesToShow = GetSetOfSelections(SpecializedTypes.itervalues(), SETTING_KEY_SPECIALIZED)
    advancedTypesToShow = GetSetOfSelections(AdvancedTypes.itervalues(), SETTING_KEY_ADVANCED)
    allProducedTypesToShow = set()
    allProducedTypesToShow.update(processedTypesToShow)
    allProducedTypesToShow.update(refinedTypesToShow)
    allProducedTypesToShow.update(specializedTypesToShow)
    allProducedTypesToShow.update(advancedTypesToShow)
    hideInappropriateRadius = SettingsHideInappropriateRadius.get()
    validTemplates = []
    for temp in allTemplates:
        if FilterOnPlanetRadius(temp, currentPlanetRadius, hideInappropriateRadius):
            continue
        if FilterOnCmdCtr(temp, cmdCenterLVToShow):
            continue
        if FilterOnPlanetType(temp, planetTypesToShow):
            continue
        if FilterOnExtractType(temp, extractTypesToShow):
            continue
        if FilterOnProduct(temp, allProducedTypesToShow):
            continue
        if FilterOnDescription(temp, filterText):
            continue
        validTemplates.append(temp)

    return validTemplates


def FilterOnPlanetRadius(template, currentPlanetRadius, hideInappropriateRadius):
    if not hideInappropriateRadius:
        return False
    if not currentPlanetRadius:
        return False
    if template.radiusOfPlanet >= currentPlanetRadius:
        return False
    return True


def FilterOnCmdCtr(template, cmdCenterLVToShow):
    if not cmdCenterLVToShow:
        return False
    if template.commandCenterLV + 1 in cmdCenterLVToShow:
        return False
    return True


def FilterOnPlanetType(template, planetTypesToShow):
    if not planetTypesToShow:
        return False
    if template.originalPlanetType in planetTypesToShow:
        return False
    return True


def FilterOnExtractType(template, extractTypesToShow):
    if not extractTypesToShow:
        return False
    if set(template.extractTypes).intersection(extractTypesToShow):
        return False
    return True


def FilterOnProduct(template, allProducedTypesToShow):
    if not allProducedTypesToShow:
        return False
    if template.productTypes.intersection(allProducedTypesToShow):
        return False
    return True


def FilterOnDescription(template, filterText):
    if not filterText:
        return False
    if template.description.lower().find(filterText) >= 0:
        return False
    return True
