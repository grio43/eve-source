#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\mercenary_tactical_operations\feature_page.py
from jobboard.client.ui.pages.content_tag_page import ContentTagPage
from localization import GetByLabel

class MTOFeaturePage(ContentTagPage):

    @property
    def info_tooltip(self):
        return GetByLabel('UI/Opportunities/VisibilityMercenaryDen')
