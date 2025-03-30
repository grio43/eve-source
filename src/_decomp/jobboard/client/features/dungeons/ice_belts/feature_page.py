#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\dungeons\ice_belts\feature_page.py
import localization
from jobboard.client.ui.pages.content_tag_page import ContentTagPage

class IceBeltsFeaturePage(ContentTagPage):

    @property
    def info_tooltip(self):
        return localization.GetByLabel('UI/Opportunities/VisibilityIceBelts')
