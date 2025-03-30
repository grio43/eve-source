#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\epic_arcs\feature_page.py
import localization
from jobboard.client.ui.pages.content_tag_page import ContentTagPage
from jobboard.client.ui.const import HERO_CARD_MAX_WIDTH
from jobboard.client.provider_type import ProviderType

class EpicArcsFeaturePage(ContentTagPage):
    ONLY_FROM_PROVIDER_ID = ProviderType.EPIC_ARCS

    @property
    def card_max_width(self):
        return HERO_CARD_MAX_WIDTH

    @property
    def info_tooltip(self):
        return localization.GetByLabel('UI/Opportunities/VisibilityEpicArcs')
