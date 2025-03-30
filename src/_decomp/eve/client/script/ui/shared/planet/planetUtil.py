#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetUtil.py
import appConst
import evetypes
from eveprefs import boot
from eve.client.script.ui.shared.planet.planetConst import TYPEIDS_PROCESSORS_HIGHTECH, TYPEIDS_PROCESSORS_ADVANCED, TYPEIDS_PROCESSORS_BASIC, PIN_ADV, PIN_HIGH, PIN_BASIC, PLANET_TYPE_TO_PIN

def IsTypeBasicProcessor(pinType):
    basic = pinType in TYPEIDS_PROCESSORS_BASIC
    return basic


def IsTypeAdvancedProcessor(pinType):
    advanced = pinType in TYPEIDS_PROCESSORS_ADVANCED
    return advanced


def IsTypeHighTechProcessor(pinType):
    hightech = pinType in TYPEIDS_PROCESSORS_HIGHTECH
    return hightech


def GetTexturePath(pinGrouping, groupID = None):
    if pinGrouping == PIN_ADV:
        return 'res:/UI/Texture/Planet/icons/processorAdvanced.png'
    if pinGrouping == PIN_HIGH:
        return 'res:/UI/Texture/Planet/icons/processorHighTech.png'
    if pinGrouping == PIN_BASIC:
        return 'res:/UI/Texture/Planet/icons/processor.png'
    try:
        return iconsByGroupID[groupID]
    except StandardError:
        return ''


def ConvertPinType(pinType, planetType):
    if IsTypeBasicProcessor(pinType):
        return PLANET_TYPE_TO_PIN[planetType][PIN_BASIC]
    if IsTypeAdvancedProcessor(pinType):
        return PLANET_TYPE_TO_PIN[planetType][PIN_ADV]
    if IsTypeHighTechProcessor(pinType):
        if PIN_HIGH not in PLANET_TYPE_TO_PIN[planetType]:
            return None
        return PLANET_TYPE_TO_PIN[planetType][PIN_HIGH]
    try:
        return PLANET_TYPE_TO_PIN[planetType][evetypes.GetGroupID(pinType)]
    except:
        return None


iconsByGroupID = {appConst.groupExtractionControlUnitPins: 'res:/UI/Texture/Planet/icons/ecu.png',
 appConst.groupProcessPins: 'res:/UI/Texture/Planet/icons/processor.png',
 appConst.groupStoragePins: 'res:/UI/Texture/Planet/icons/storage.png',
 appConst.groupSpaceportPins: 'res:/UI/Texture/Planet/icons/spaceport.png',
 appConst.groupPlanetaryLinks: 'res:/UI/Texture/Planet/icons/link.png',
 appConst.groupCommandPins: 'res:/UI/Texture/Planet/icons/commandCenter.png'}
backgroundTexturePath = {appConst.typePlanetEarthlike: 'res:/UI/Texture/Planet/entryBackground/temperate.png',
 appConst.typePlanetIce: 'res:/UI/Texture/Planet/entryBackground/ice.png',
 appConst.typePlanetGas: 'res:/UI/Texture/Planet/entryBackground/gas.png',
 appConst.typePlanetPlasma: 'res:/UI/Texture/Planet/entryBackground/plasma.png',
 appConst.typePlanetOcean: 'res:/UI/Texture/Planet/entryBackground/oceanic.png',
 appConst.typePlanetLava: 'res:/UI/Texture/Planet/entryBackground/lava.png',
 appConst.typePlanetSandstorm: 'res:/UI/Texture/Planet/entryBackground/barren.png',
 appConst.typePlanetThunderstorm: 'res:/UI/Texture/Planet/entryBackground/storm.png'}

def IsSerenity():
    return boot.region == 'optic'
