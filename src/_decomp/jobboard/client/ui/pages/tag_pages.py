#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\pages\tag_pages.py
from metadata import ContentTags
from jobboard.client import get_primary_feature_tags, get_provider_for_feature_tag
from jobboard.client.ui.pages.browse_page import BrowsePage
from jobboard.client.ui.pages.content_tag_page import ContentTagPage
from jobboard.client.features.agent_missions.feature_page import AgentMissionsFeaturePage
from jobboard.client.features.corporation_goals.feature_page import CorporationGoalsFeaturePage
from jobboard.client.features.daily_goals.feature_page import DailyGoalsFeaturePage
from jobboard.client.features.dungeons.combat_anomalies.feature_page import CombatAnomaliesFeaturePage
from jobboard.client.features.dungeons.escalation_sites.feature_page import EscalationsFeaturePage
from jobboard.client.features.dungeons.factional_warfare.feature_page import FactionalWarfareFeaturePage
from jobboard.client.features.dungeons.homefront_operations.feature_page import HomefrontOperationsFeaturePage
from jobboard.client.features.dungeons.ice_belts.feature_page import IceBeltsFeaturePage
from jobboard.client.features.dungeons.ore_anomalies.feature_page import OreAnomaliesFeaturePage
from jobboard.client.features.dungeons.pirate_insurgencies.feature_page import PirateInsurgenciesFeaturePage
from jobboard.client.features.epic_arcs.feature_page import EpicArcsFeaturePage
from jobboard.client.features.mercenary_tactical_operations.feature_page import MTOFeaturePage
from jobboard.client.features.storylines.feature_page import StorylinesFeaturePage

def get_content_tag_page(content_tag_id):
    if content_tag_id in CONTENT_TAG_PAGES:
        return CONTENT_TAG_PAGES[content_tag_id]
    elif content_tag_id in get_primary_feature_tags():
        provider = get_provider_for_feature_tag(content_tag_id)
        return provider.FEATURE_PAGE_CLASS or ContentTagPage
    else:
        return BrowsePage


CONTENT_TAG_PAGES = {ContentTags.feature_agent_missions: AgentMissionsFeaturePage,
 ContentTags.feature_corporation_projects: CorporationGoalsFeaturePage,
 ContentTags.feature_combat_anomalies: CombatAnomaliesFeaturePage,
 ContentTags.feature_escalation_dungeon: EscalationsFeaturePage,
 ContentTags.feature_factional_warfare: FactionalWarfareFeaturePage,
 ContentTags.feature_homefront_operations: HomefrontOperationsFeaturePage,
 ContentTags.feature_ice_belts: IceBeltsFeaturePage,
 ContentTags.feature_ore_anomalies: OreAnomaliesFeaturePage,
 ContentTags.feature_pirate_insurgencies: PirateInsurgenciesFeaturePage,
 ContentTags.feature_epic_arcs: EpicArcsFeaturePage,
 ContentTags.feature_introductions: StorylinesFeaturePage,
 ContentTags.feature_daily_goals: DailyGoalsFeaturePage,
 ContentTags.feature_mercenary_tactical_ops: MTOFeaturePage}
