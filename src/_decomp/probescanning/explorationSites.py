#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\explorationSites.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from dogma.const import attributeScanGravimetricStrength, attributeScanLadarStrength, attributeScanMagnetometricStrength, attributeScanRadarStrength, attributeScanWormholeStrength, attributeScanAllStrength
from eve.common.lib.appConst import dunArchetypeHomefrontSites
from evearchetypes import GetArchetypeTitle, GetArchetypeDescription
from evetypes import GetName
from inventorycommon.const import typeDataAnalyzer, typeRelicAnalyzer, typeGasCloudHarvester
from localization import GetByLabel, GetByMessageID
siteTypeOre = attributeScanGravimetricStrength
siteTypeGas = attributeScanLadarStrength
siteTypeRelic = attributeScanMagnetometricStrength
siteTypeData = attributeScanRadarStrength
siteTypeWormhole = attributeScanWormholeStrength
siteTypeCombat = attributeScanAllStrength
EXPLORATION_SITE_TYPES = {siteTypeOre: 'UI/Inflight/Scanner/OreSite',
 siteTypeGas: 'UI/Inflight/Scanner/GasSite',
 siteTypeRelic: 'UI/Inflight/Scanner/RelicSite',
 siteTypeData: 'UI/Inflight/Scanner/DataSite',
 siteTypeWormhole: 'UI/Inflight/Scanner/Wormhole',
 siteTypeCombat: 'UI/Inflight/Scanner/CombatSite'}
COMBAT_EXPLORATION_SITE_ARCHETYPES = [dunArchetypeHomefrontSites]

def is_exploration_site(site_type):
    return site_type in EXPLORATION_SITE_TYPES.keys()


def get_exploration_site_name_label(site_type, archetype_id):
    if site_type == siteTypeCombat and archetype_id in COMBAT_EXPLORATION_SITE_ARCHETYPES:
        return GetArchetypeTitle(archetype_id)
    return EXPLORATION_SITE_TYPES.get(site_type, None)


def get_exploration_site_name(site_type, archetype_id):
    if site_type == siteTypeCombat and archetype_id in COMBAT_EXPLORATION_SITE_ARCHETYPES:
        return GetByMessageID(GetArchetypeTitle(archetype_id))
    site_name_label = EXPLORATION_SITE_TYPES.get(site_type, None)
    if site_name_label:
        return GetByLabel(site_name_label)


def get_exploration_site_description(site_type, archetype_id):
    if site_type == siteTypeCombat and archetype_id in COMBAT_EXPLORATION_SITE_ARCHETYPES:
        return GetByMessageID(GetArchetypeDescription(archetype_id))
    site_name_label = EXPLORATION_SITE_TYPES.get(site_type, None)
    if site_name_label:
        description_label = site_name_label + 'Tooltip'
        keywords = {}
        if site_type == siteTypeData:
            keywords['data_analyzer'] = GetShowInfoLink(typeDataAnalyzer, GetName(typeDataAnalyzer))
        elif site_type == siteTypeRelic:
            keywords['relic_analyzer'] = GetShowInfoLink(typeRelicAnalyzer, GetName(typeRelicAnalyzer))
        elif site_type == siteTypeGas:
            keywords['relic_analyzer'] = GetShowInfoLink(typeGasCloudHarvester, GetName(typeGasCloudHarvester))
        return GetByLabel(description_label, **keywords)


def get_all_signature_types():
    return EXPLORATION_SITE_TYPES.keys()


def get_signature_type_label(signature_type):
    return EXPLORATION_SITE_TYPES.get(signature_type, None)
