#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\pirateIncursions\panels\activitiesoverview.py
from carbonui.control.scrollContainer import ScrollContainer
from eveui import Sprite
from eve.client.script.ui import eveColor
from carbonui.util.color import Color
from carbonui.primitives.container import Container
from carbonui.primitives.gridcontainer import GridContainer
from carbonui import uiconst, TextBody
from carbonui.control.section import SectionAutoSize
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from localization import GetByLabel

class ActivitiesOverviewPanel(BasePanel):

    def __init__(self, *args, **kwargs):
        super(ActivitiesOverviewPanel, self).__init__(*args, **kwargs)
        self._construct_layout()

    def _construct_layout(self):
        self._activities_section = SectionAutoSize(name='activities_section', parent=self, align=uiconst.TOTOP, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/ActivityOverview/InsurgenceActivitiesSectionTitle'))
        scroll = ScrollContainer(parent=self._activities_section, align=uiconst.TOTOP, height=160)
        self._activities_label = TextBody(name='activities_label', parent=scroll, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/PirateIncursions/Guides/ActivityOverview/InsurgenceActivitiesSectionText'), padding=5)

    def get_searchable_strings(self):
        return [self._activities_section.headerText, self._activities_label.GetText()]
