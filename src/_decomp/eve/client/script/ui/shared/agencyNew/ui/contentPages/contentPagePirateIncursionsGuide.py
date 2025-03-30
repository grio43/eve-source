#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPagePirateIncursionsGuide.py
from carbonui import uiconst, TextBody
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import Section
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.activitiesoverview import ActivitiesOverviewPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.activity import ActivityPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.ambition import AmbitionPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.base import BasePanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.corruptionsuppression import CorruptionSuppressionPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.fob_lp import FOBPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.insurgencies import InsurgenciesPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.overview import OverviewPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.pirateIncursions.panels.factions import FactionsPanel
from localization import GetByLabel

class Topics(object):
    OVERVIEW = 'overview'
    FACTIONS = 'factions'
    INCURSIONS = 'incursions'
    FOB_AND_LP = 'fob_and_lp'
    CORRUPTION = 'corruption'
    AMBITION = 'ambition'
    ACTIVITIES = 'activities'
    ACTIVITY1 = 'activity1'
    ACTIVITY2 = 'activity2'
    ACTIVITY3 = 'activity3'
    ACTIVITY4 = 'activity4'
    ACTIVITY5 = 'activity5'
    LABELS = {OVERVIEW: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicOverview'),
     FACTIONS: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicFactions'),
     INCURSIONS: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicIncursions'),
     FOB_AND_LP: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicFOBandLP'),
     CORRUPTION: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicCorruption'),
     AMBITION: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicAmbition'),
     ACTIVITIES: GetByLabel('UI/Agency/PirateIncursions/Guides/TopicActivities'),
     ACTIVITY1: '    ' + GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityNameOutpost'),
     ACTIVITY2: '    ' + GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/MiningFleetName'),
     ACTIVITY3: '    ' + GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/LaunderingCenterName'),
     ACTIVITY4: '    ' + GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/SecurityPostName'),
     ACTIVITY5: '    ' + GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/IceRefineryHeistName')}
    ACTIVITY_HEADER_IMAGES = {ACTIVITY1: 'res:/ui/texture/classes/agency/pirateIncursions/CorporateOutpostRaid.png',
     ACTIVITY2: 'res:/ui/texture/classes/agency/pirateIncursions/MiningFleetAmbush.png',
     ACTIVITY3: 'res:/ui/texture/classes/agency/pirateIncursions/LaunderingCenter.png',
     ACTIVITY4: 'res:/ui/texture/classes/agency/pirateIncursions/SecurityPost.png',
     ACTIVITY5: 'res:/ui/texture/classes/agency/pirateIncursions/IceRefineryHeist.png'}
    ACTIVITY_SCALE_LABELS = {ACTIVITY1: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/corporateOutpostRaidActivityScaling'),
     ACTIVITY2: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/MiningOpAmbushActivityScaling'),
     ACTIVITY3: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/PirateLaunderingFacilitiesActivityScaling'),
     ACTIVITY4: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/CounterInsurgencyOutpostActivityScaling'),
     ACTIVITY5: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/IceRefineryHeistActivityScaling')}
    ACTIVITY_REWARD_TYPE = {ACTIVITY1: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityRewardTypeShared'),
     ACTIVITY2: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityRewardTypeShared'),
     ACTIVITY3: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityRewardTypeIndividual'),
     ACTIVITY4: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityRewardTypeIndividual'),
     ACTIVITY5: GetByLabel('UI/Agency/PirateIncursions/Guides/Activities/ActivityRewardTypeShared')}
    ORDERED = [OVERVIEW,
     FACTIONS,
     INCURSIONS,
     FOB_AND_LP,
     CORRUPTION,
     AMBITION,
     ACTIVITIES,
     ACTIVITY1,
     ACTIVITY2,
     ACTIVITY3,
     ACTIVITY4,
     ACTIVITY5]

    @staticmethod
    def get_label(topic_id):
        return Topics.LABELS[topic_id]


class ContentPagePirateIncursionsGuide(Container):
    default_name = 'ContentPagePirateIncursionsGuide'
    default_padding = 20

    def __init__(self, *args, **kwargs):
        super(ContentPagePirateIncursionsGuide, self).__init__(*args, **kwargs)
        self._panels = {}
        self._topic_search = None
        self._topic_scroll = None
        self._construct_layout()
        self._select_topic(Topics.OVERVIEW)

    def _construct_layout(self):
        self._construct_topic_section()
        self._create_panels()
        self._populate_topic_scroll()

    def _construct_topic_section(self):
        topic_section = Section(name='topic_section', parent=self, align=uiconst.TOLEFT_PROP, width=0.3, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/GuideBrowserSectionTitle'))
        self._topic_search = QuickFilterEdit(name='topic_search', parent=topic_section, align=uiconst.TOTOP, height=24, padTop=5)
        self._topic_search.ReloadFunction = self.on_search_changed
        self._topic_scroll = ScrollContainer(name='topic_scroll', parent=topic_section, align=uiconst.TOALL, top=5, multiSelect=False)

    def _create_panels(self):
        panel_container = Container(name='panel_container', align=uiconst.TOALL, parent=self, padLeft=20)
        self._panels = {Topics.OVERVIEW: OverviewPanel(name=Topics.OVERVIEW, parent=panel_container),
         Topics.FACTIONS: FactionsPanel(name=Topics.FACTIONS, parent=panel_container),
         Topics.INCURSIONS: InsurgenciesPanel(name=Topics.INCURSIONS, parent=panel_container),
         Topics.FOB_AND_LP: FOBPanel(name=Topics.FOB_AND_LP, parent=panel_container),
         Topics.CORRUPTION: CorruptionSuppressionPanel(name=Topics.CORRUPTION, parent=panel_container),
         Topics.AMBITION: AmbitionPanel(name=Topics.AMBITION, parent=panel_container),
         Topics.ACTIVITIES: ActivitiesOverviewPanel(name=Topics.ACTIVITIES, parent=panel_container),
         Topics.ACTIVITY1: ActivityPanel(name=Topics.ACTIVITY1, parent=panel_container, activity='OUTPOST', constructRewards=True, headerTexturePath=Topics.ACTIVITY_HEADER_IMAGES[Topics.ACTIVITY1], activityScaleText=Topics.ACTIVITY_SCALE_LABELS[Topics.ACTIVITY1], activityRewardTypeText=Topics.ACTIVITY_REWARD_TYPE[Topics.ACTIVITY1]),
         Topics.ACTIVITY2: ActivityPanel(name=Topics.ACTIVITY2, parent=panel_container, activity='MINING', constructRewards=True, headerTexturePath=Topics.ACTIVITY_HEADER_IMAGES[Topics.ACTIVITY2], activityScaleText=Topics.ACTIVITY_SCALE_LABELS[Topics.ACTIVITY2], activityRewardTypeText=Topics.ACTIVITY_REWARD_TYPE[Topics.ACTIVITY2]),
         Topics.ACTIVITY3: ActivityPanel(name=Topics.ACTIVITY3, parent=panel_container, activity='LAUNDERING', constructRewards=False, headerTexturePath=Topics.ACTIVITY_HEADER_IMAGES[Topics.ACTIVITY3], activityScaleText=Topics.ACTIVITY_SCALE_LABELS[Topics.ACTIVITY3], activityRewardTypeText=Topics.ACTIVITY_REWARD_TYPE[Topics.ACTIVITY3]),
         Topics.ACTIVITY4: ActivityPanel(name=Topics.ACTIVITY4, parent=panel_container, activity='SECURITYPOST', constructRewards=False, headerTexturePath=Topics.ACTIVITY_HEADER_IMAGES[Topics.ACTIVITY4], activityScaleText=Topics.ACTIVITY_SCALE_LABELS[Topics.ACTIVITY4], activityRewardTypeText=Topics.ACTIVITY_REWARD_TYPE[Topics.ACTIVITY4]),
         Topics.ACTIVITY5: ActivityPanel(name=Topics.ACTIVITY5, parent=panel_container, activity='ICEREFINERYHEIST', constructRewards=False, headerTexturePath=Topics.ACTIVITY_HEADER_IMAGES[Topics.ACTIVITY5], activityScaleText=Topics.ACTIVITY_SCALE_LABELS[Topics.ACTIVITY5], activityRewardTypeText=Topics.ACTIVITY_REWARD_TYPE[Topics.ACTIVITY5])}

    def _populate_topic_scroll(self):
        self._topic_scroll.Flush()
        topics_to_display = self._get_filtered_topics()
        for topic_id in topics_to_display:
            entry = TopicScrollEntry(parent=self._topic_scroll, topic_id=topic_id, label_text=Topics.get_label(topic_id))
            entry.on_clicked.connect(self.on_topic_selected)

    def _get_filtered_topics(self):
        search_text = self._topic_search.GetValue().lower()
        if len(search_text) < 3:
            return Topics.ORDERED
        filtered_topics = []
        for topic_id in Topics.ORDERED:
            if topic_id in filtered_topics:
                continue
            topic_label = Topics.get_label(topic_id).lower()
            if search_text in topic_label:
                filtered_topics.append(topic_id)
                continue
            panel_texts = self._panels[topic_id].get_searchable_strings()
            for text in panel_texts:
                if topic_id not in filtered_topics and search_text in text.lower():
                    filtered_topics.append(topic_id)
                    continue

        return filtered_topics

    def _select_topic(self, topic_id):
        for panel_topic_id, panel in self._panels.items():
            panel.state = uiconst.UI_PICKCHILDREN if panel_topic_id == topic_id else uiconst.UI_HIDDEN

    def on_search_changed(self):
        self._populate_topic_scroll()

    def on_topic_selected(self, scroll_entry):
        self._select_topic(scroll_entry.topic_id)


class TopicScrollEntry(BaseScrollContEntry):
    default_height = 30

    def __init__(self, *args, **kwargs):
        self._topic_id = None
        self._label_text = ''
        super(TopicScrollEntry, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        super(TopicScrollEntry, self).ApplyAttributes(attributes)
        self._topic_id = attributes.Get('topic_id', None)
        self._label_text = attributes.Get('label_text', None)
        self._construct_layout()

    def _construct_layout(self):
        TextBody(parent=self, name='label', align=uiconst.TOLEFT, text=self._label_text, padding=5)

    @property
    def topic_id(self):
        return self._topic_id
