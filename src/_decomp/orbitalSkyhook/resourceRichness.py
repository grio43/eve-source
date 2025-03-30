#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\orbitalSkyhook\resourceRichness.py
import eveicon
from inventorycommon.const import typeColonyReagentIce, typeColonyReagentLava
RICHNESS_NONE = 1
RICHNESS_MODEST = 2
RICHNESS_AVG = 3
RICHNESS_ABUNDANT = 4
richnessLabelPaths = {RICHNESS_MODEST: 'UI/OrbitalSkyhook/RichnessModest',
 RICHNESS_AVG: 'UI/OrbitalSkyhook/RichnessAverage',
 RICHNESS_ABUNDANT: 'UI/OrbitalSkyhook/RichnessAbundant'}
RESOURCE_RICHNESS_PLANET_ICE_AVG = 36
RESOURCE_RICHNESS_PLANET_ICE_PROSPEROUS = 40
RESOURCE_RICHNESS_SYSTEM_ICE_AVG = 36
RESOURCE_RICHNESS_SYSTEM_ICE_PROSPEROUS = 41
iceTextureByRichness = {RICHNESS_MODEST: eveicon.superionic_ice_richness_modest,
 RICHNESS_AVG: eveicon.superionic_ice_richness_average,
 RICHNESS_ABUNDANT: eveicon.superionic_ice_richness_prosperous}
iceRichnessLabelPaths = {RICHNESS_MODEST: 'UI/OrbitalSkyhook/ResourcesIoniciceLow',
 RICHNESS_AVG: 'UI/OrbitalSkyhook/ResourcesIoniciceMid',
 RICHNESS_ABUNDANT: 'UI/OrbitalSkyhook/ResourcesIoniciceHigh'}
RESOURCE_RICHNESS_PLANET_LAVA_AVG = 763
RESOURCE_RICHNESS_PLANET_LAVA_PROSPEROUS = 946
RESOURCE_RICHNESS_SYSTEM_LAVA_AVG = 835
RESOURCE_RICHNESS_SYSTEM_LAVA_PROSPEROUS = 1436
lavaTextureByRichness = {RICHNESS_MODEST: eveicon.magmatic_gas_richness_modest,
 RICHNESS_AVG: eveicon.magmatic_gas_richness_average,
 RICHNESS_ABUNDANT: eveicon.magmatic_gas_richness_prosperous}
lavaRichnessLabelPaths = {RICHNESS_MODEST: 'UI/OrbitalSkyhook/ResourcesMagmaticgasLow',
 RICHNESS_AVG: 'UI/OrbitalSkyhook/ResourcesMagmaticgasMid',
 RICHNESS_ABUNDANT: 'UI/OrbitalSkyhook/ResourcesMagmaticgasHigh'}
RESOURCE_RICHNESS_PLANET_WORKFORCE_AVG = 2831
RESOURCE_RICHNESS_PLANET_WORKFORCE_PROSPEROUS = 5671
RESOURCE_RICHNESS_SYSTEM_WORKFORCE_AVG = 11840
RESOURCE_RICHNESS_SYSTEM_WORKFORCE_PROSPEROUS = 22060
workforceTextureByRichness = {RICHNESS_MODEST: eveicon.workforce_richness_modest,
 RICHNESS_AVG: eveicon.workforce_richness_average,
 RICHNESS_ABUNDANT: eveicon.workforce_richness_prosperous}
workforceRichnessLabelPaths = {RICHNESS_MODEST: 'UI/OrbitalSkyhook/ResourcesWorkforceLow',
 RICHNESS_AVG: 'UI/OrbitalSkyhook/ResourcesWorkforceMid',
 RICHNESS_ABUNDANT: 'UI/OrbitalSkyhook/ResourcesWorkforceHigh'}
RESOURCE_RICHNESS_PLANET_POWER_AVG = 271
RESOURCE_RICHNESS_PLANET_POWER_PROSPEROUS = 481
RESOURCE_RICHNESS_SYSTEM_POWER_AVG = 921
RESOURCE_RICHNESS_SYSTEM_POWER_PROSPEROUS = 1381
powerTextureByRichness = {RICHNESS_MODEST: eveicon.power_richenss_modest,
 RICHNESS_AVG: eveicon.power_richness_average,
 RICHNESS_ABUNDANT: eveicon.power_richness_prosperous}
powerRichnessLabelPaths = {RICHNESS_MODEST: 'UI/OrbitalSkyhook/ResourcesPowerLow',
 RICHNESS_AVG: 'UI/OrbitalSkyhook/ResourcesPowerMid',
 RICHNESS_ABUNDANT: 'UI/OrbitalSkyhook/ResourcesPowerHigh'}
RESOURCE_RICHNESS_STAR_POWER_AVG = 241
RESOURCE_RICHNESS_STAR_POWER_PROSPEROUS = 371

def GetIceRichnessForPlanet(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_PLANET_ICE_AVG, RESOURCE_RICHNESS_PLANET_ICE_PROSPEROUS)


def GetIceRichnessForSystem(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_SYSTEM_ICE_AVG, RESOURCE_RICHNESS_SYSTEM_ICE_PROSPEROUS)


def GetLavaRichnessForPlanet(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_PLANET_LAVA_AVG, RESOURCE_RICHNESS_PLANET_LAVA_PROSPEROUS)


def GetLavaRichnessForSystem(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_SYSTEM_LAVA_AVG, RESOURCE_RICHNESS_SYSTEM_LAVA_PROSPEROUS)


def GetWorkforceRichnessForPlanet(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_PLANET_WORKFORCE_AVG, RESOURCE_RICHNESS_PLANET_WORKFORCE_PROSPEROUS)


def GetWorkforceRichnessForSystem(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_SYSTEM_WORKFORCE_AVG, RESOURCE_RICHNESS_SYSTEM_WORKFORCE_PROSPEROUS)


def GetPowerRichnessForPlanet(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_PLANET_POWER_AVG, RESOURCE_RICHNESS_PLANET_POWER_PROSPEROUS)


def GetPowerRichnessForSystem(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_SYSTEM_POWER_AVG, RESOURCE_RICHNESS_SYSTEM_POWER_PROSPEROUS)


def GetPowerRichnessForStar(amount):
    return GetRichness(amount, RESOURCE_RICHNESS_STAR_POWER_AVG, RESOURCE_RICHNESS_STAR_POWER_PROSPEROUS)


def GetRichness(amount, avg, prosperous):
    if amount <= 0:
        return RICHNESS_NONE
    if amount < avg:
        return RICHNESS_MODEST
    if amount < prosperous:
        return RICHNESS_AVG
    return RICHNESS_ABUNDANT


def GetPlanetReagentRichnessTexturePathAndHint(amount, reagentTypeID):
    if reagentTypeID == typeColonyReagentIce:
        richness = GetIceRichnessForPlanet(amount)
        texturePath = iceTextureByRichness.get(richness, None)
        labelPath = iceRichnessLabelPaths.get(richness, None)
    elif reagentTypeID == typeColonyReagentLava:
        richness = GetLavaRichnessForPlanet(amount)
        texturePath = lavaTextureByRichness.get(richness, None)
        labelPath = lavaRichnessLabelPaths.get(richness, None)
    else:
        return (None, '')
    return (texturePath, labelPath)


def GetSystemReagentRichnessTexturePathAndHint(amount, reagentTypeID):
    if reagentTypeID == typeColonyReagentIce:
        richness = GetIceRichnessForSystem(amount)
        return (iceTextureByRichness.get(richness), iceRichnessLabelPaths.get(richness, ''))
    elif reagentTypeID == typeColonyReagentLava:
        richness = GetLavaRichnessForSystem(amount)
        return (lavaTextureByRichness.get(richness), lavaRichnessLabelPaths.get(richness, ''))
    else:
        return (None, '')


def GetSystemPowerRichnessTexturePath(amount):
    richness = GetPowerRichnessForSystem(amount)
    return (powerTextureByRichness.get(richness), powerRichnessLabelPaths.get(richness, ''))


def GetSystemWorkforceRichnessTexturePath(amount):
    richness = GetWorkforceRichnessForSystem(amount)
    return (workforceTextureByRichness.get(richness), workforceRichnessLabelPaths.get(richness, ''))


def GetPlanetWorkforceRichnessTexturePath(amount):
    richness = GetWorkforceRichnessForPlanet(amount)
    return (workforceTextureByRichness.get(richness), workforceRichnessLabelPaths.get(richness, ''))


def GetPlanetPowerRichnessTexturePath(amount):
    richness = GetPowerRichnessForPlanet(amount)
    return (powerTextureByRichness.get(richness), powerRichnessLabelPaths.get(richness, ''))
