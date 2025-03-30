#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\provider_type.py


class ProviderType(object):
    AGENT_MISSIONS = 'agent_missions'
    COMBAT_ANOMALIES = 'combat_anomalies'
    CORPORATION_GOALS = 'corporation_goals'
    COSMIC_SIGNATURES = 'cosmic_signatures'
    DAILY_GOALS = 'daily_goals'
    DUNGEONS = 'dungeons'
    EPIC_ARCS = 'epic_arcs'
    ESCALATION_SITES = 'escalation_sites'
    FACTIONAL_WARFARE = 'factional_warfare'
    FACTIONAL_WARFARE_ENLISTMENT = 'factional_warfare_enlistment'
    PIRATE_INSURGENCIES = 'pirate_insurgencies'
    HOMEFRONT_OPERATIONS = 'homefront_operations'
    TRIGLAVIAN_SITES = 'triglavian_sites'
    ICE_BELTS = 'ice_belts'
    ORE_ANOMALIES = 'ore_anomalies'
    STORYLINES = 'storylines'
    MERCENARY_TACTICAL_OPS = 'mercenary_tactical_ops'
    SEASONS = 'seasons'
    WORLD_EVENTS = 'world_events'


DUNGEON_PROVIDERS = [ProviderType.DUNGEONS,
 ProviderType.COMBAT_ANOMALIES,
 ProviderType.COSMIC_SIGNATURES,
 ProviderType.HOMEFRONT_OPERATIONS,
 ProviderType.FACTIONAL_WARFARE,
 ProviderType.PIRATE_INSURGENCIES,
 ProviderType.ESCALATION_SITES,
 ProviderType.ICE_BELTS,
 ProviderType.ORE_ANOMALIES,
 ProviderType.TRIGLAVIAN_SITES]

def get_job_id(provider_id, instance_id):
    job_id = '{provider_id}:{instance_id}'.format(provider_id=provider_id, instance_id=instance_id)
    return job_id
