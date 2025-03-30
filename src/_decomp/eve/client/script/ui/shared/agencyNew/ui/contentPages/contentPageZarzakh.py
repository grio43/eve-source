#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageZarzakh.py
from carbonui import uiconst, TextBody
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import Section
from carbonui.primitives.container import Container
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.overview import OverviewPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.rules import RulesPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.hq import HQPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.zones import ZonesPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.jovian import JovianPanel
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.zarzakh.panels.shipcaster import ShipcasterPanel
from localization import GetByLabel

class Topics(object):
    OVERVIEW = 'overview'
    RULES = 'rules'
    HQ = 'hq'
    ZONES = 'zones'
    JOVIAN = 'jovian'
    SHIPCASTER = 'shipcaster'
    LABELS = {OVERVIEW: GetByLabel('UI/Agency/Zarzakh/TopicOverview'),
     RULES: GetByLabel('UI/Agency/Zarzakh/TopicRules'),
     HQ: GetByLabel('UI/Agency/Zarzakh/TopicHQ'),
     ZONES: GetByLabel('UI/Agency/Zarzakh/TopicZones'),
     JOVIAN: GetByLabel('UI/Agency/Zarzakh/TopicJovian'),
     SHIPCASTER: GetByLabel('UI/Agency/Zarzakh/TopicShipcaster')}
    ORDERED = [OVERVIEW,
     RULES,
     HQ,
     ZONES,
     JOVIAN,
     SHIPCASTER]

    @staticmethod
    def get_label(topic_id):
        return Topics.LABELS[topic_id]


class ContentPageZarzakh(BaseContentGroupPage):
    default_name = 'ContentPageZarzakh'
    default_align = uiconst.TOALL
    default_padding = 20
    contentGroupID = contentGroupConst.contentGroupZarzakh

    def ConstructLayout(self):
        super(ContentPageZarzakh, self).ConstructLayout()
        self._construct_topic_section()
        self._create_panels()
        self._populate_topic_scroll()
        self.select_topic(Topics.OVERVIEW)

    def _construct_topic_section(self):
        topic_section = Section(name='topic_section', parent=self, align=uiconst.TOLEFT_PROP, width=0.3, headerText=GetByLabel('UI/Agency/PirateIncursions/Guides/GuideBrowserSectionTitle'))
        self._topic_search = QuickFilterEdit(name='topic_search', parent=topic_section, align=uiconst.TOTOP, height=24, padTop=5)
        self._topic_search.ReloadFunction = self.on_search_changed
        self._topic_scroll = ScrollContainer(name='topic_scroll', parent=topic_section, align=uiconst.TOALL, top=5, multiSelect=False)

    def _create_panels(self):
        panel_container = Container(name='panel_container', align=uiconst.TOALL, parent=self, padLeft=20)
        self._panels = {Topics.OVERVIEW: OverviewPanel(name=Topics.OVERVIEW, parent=panel_container),
         Topics.RULES: RulesPanel(name=Topics.RULES, parent=panel_container),
         Topics.HQ: HQPanel(name=Topics.HQ, parent=panel_container),
         Topics.ZONES: ZonesPanel(name=Topics.ZONES, parent=panel_container),
         Topics.JOVIAN: JovianPanel(name=Topics.JOVIAN, parent=panel_container),
         Topics.SHIPCASTER: ShipcasterPanel(name=Topics.SHIPCASTER, parent=panel_container)}

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

    def select_topic(self, topic_id):
        for panel_topic_id, panel in self._panels.items():
            panel.state = uiconst.UI_PICKCHILDREN if panel_topic_id == topic_id else uiconst.UI_HIDDEN

    def on_search_changed(self):
        self._populate_topic_scroll()

    def on_topic_selected(self, scroll_entry):
        self.select_topic(scroll_entry.topic_id)


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
