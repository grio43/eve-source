#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\world_events\feature_page.py
import localization
from jobboard.client.ui.pages.content_tag_page import ContentTagPage
from jobboard.client.ui.const import HERO_CARD_MAX_WIDTH
from jobboard.client.provider_type import ProviderType

class WorldEventsFeaturePage(ContentTagPage):
    ONLY_FROM_PROVIDER_ID = ProviderType.WORLD_EVENTS
