#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\storylines\page.py
import carbonui
import eveui
from carbonui.uiconst import PickState
import localization
from jobboard.client.ui.pages.details_page import JobPage, DetailsSection

class StorylinePage(JobPage):

    def _construct_body(self, parent_container):
        self._construct_description(parent_container)

    def _construct_description(self, parent_container):
        tag_line = self.job.tag_line
        if tag_line:
            carbonui.TextBody(parent=parent_container, align=eveui.Align.to_top, text=self.job.tag_line, padTop=12, padBottom=12, italic=True)
        description_card = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Common/Description'))
        container = description_card.content_container
        carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=self.job.description, pickState=PickState.ON)
        operational_intel = self.job.operational_intel
        if operational_intel:
            description_card = DetailsSection(parent=parent_container, title=localization.GetByLabel('UI/Opportunities/Storylines/IntroductionHeader'))
            container = description_card.content_container
            carbonui.TextBody(parent=container, align=eveui.Align.to_top, text=operational_intel, pickState=PickState.ON)
