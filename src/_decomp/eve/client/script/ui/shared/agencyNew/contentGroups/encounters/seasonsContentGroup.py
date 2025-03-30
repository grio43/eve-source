#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\encounters\seasonsContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.baseContentGroup import BaseContentGroup
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageSeasons import ContentPageSeasons

def IsSeasonVisible():
    return sm.GetService('seasonService').is_season_visible_in_agency()


class SeasonsContentGroup(BaseContentGroup):
    contentGroupID = contentGroupConst.contentGroupSeasons

    def GetName(self):
        return sm.GetService('seasonService').get_navigation_season_title()

    def GetDescription(self):
        return sm.GetService('seasonService').get_navigation_description()

    def GetContentGroupHint(self):
        return sm.GetService('seasonService').get_navigation_tooltip()

    @staticmethod
    def IsContentAvailable():
        return True

    def IsNewContentAvailable(self):
        return IsSeasonVisible()

    def GetBackgroundTexture(self):
        return sm.GetService('seasonService').get_navigation_card_picture_path()

    def IsEnabled(self):
        return IsSeasonVisible()

    def IsVisible(self):
        return IsSeasonVisible()

    @staticmethod
    def GetContentPageClass():
        return ContentPageSeasons
