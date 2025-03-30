#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\storylines\job.py
import caching
from carbonui.control.contextMenu.menuData import MenuData
import eveicon
from eve.client.script.ui import eveColor
import localization
from jobboard.client import job_board_signals
from jobboard.client.job import BaseJob
from .card import StorylineCard
from .page import StorylinePage
from .const import TEMP_STORYLINE_DATA

class StorylineJob(BaseJob):
    CARD_CLASS = StorylineCard
    PAGE_CLASS = StorylinePage
    __notifyevents__ = ['OnExpandedMissionChanged']

    def __init__(self, job_id, provider, mission):
        self._mission = mission
        self._data = None
        content_id = self._mission['content_id']
        super(StorylineJob, self).__init__(job_id, content_id, provider)

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        is_focused = featureID == 'opportunities' and missionID == self.job_id
        self.context.update_value('mission_focused', is_focused)
        sm.ScatterEvent('OnAirNPEFocusChanged')

    @property
    def data(self):
        if not self._data:
            self._data = TEMP_STORYLINE_DATA.get(self.content_id)
        return self._data

    @property
    def title(self):
        return localization.GetByLabel(self.data['title'])

    @property
    def subtitle(self):
        arc_title = self.data.get('arc_title', None)
        if arc_title:
            return localization.GetByLabel(arc_title)
        distributor_id = self.data.get('distributor_id', None)
        if distributor_id:
            return cfg.eveowners.Get(distributor_id).name
        return ''

    @property
    def description(self):
        return localization.GetByLabel(self.data['description'])

    @property
    def operational_intel(self):
        if 'operational_intel' in self.data:
            return localization.GetByLabel(self.data['operational_intel'])
        return ''

    @property
    def tag_line(self):
        if 'tag_line' in self.data:
            return localization.GetByLabel(self.data['tag_line'])
        return ''

    @property
    def background_image(self):
        return self.data.get('background_image', None)

    @property
    def location_id(self):
        return self.context.get_value('location_id', None)

    @property
    def solar_system_id(self):
        location_id = self.location_id
        if location_id:
            return cfg.evelocations.Get(location_id).solarSystemID

    @property
    def is_available_in_active(self):
        return not self.is_offered

    @property
    def is_linkable(self):
        return False

    @property
    def is_trackable(self):
        return not self.is_offered and not self.is_removed

    @property
    def is_offered(self):
        return self.job_info.get('state', None) == 'offered'

    @property
    def node_graph(self):
        return self._mission['node_graph']

    @property
    def context(self):
        return self.node_graph.context

    @property
    def job_info(self):
        return self.context.get_value(self.content_id, {})

    @caching.lazy_property
    def objective_chain(self):
        from objectives.client.objective_chain import ObjectiveChain
        objective_chain_id = self.data.get('objective_chain_id')
        if not objective_chain_id:
            return None
        objective_chain = ObjectiveChain(content_id=objective_chain_id, context=self.context)
        objective_chain.start()
        return objective_chain

    def get_menu(self):
        if self.is_removed:
            return []
        menu = MenuData()
        self._add_qa_menu(menu)
        if 'skip_function' in self.data:
            menu.AddEntry(localization.GetByLabel('UI/SystemMenu/SkipTutorial'), texturePath=eveicon.power_off, func=self.data['skip_function'])
            menu.AddSeparator()
        menu.entrylist.extend(super(StorylineJob, self).get_menu().entrylist)
        return menu

    def get_buttons(self):
        if 'skip_function' in self.data:
            return [{'icon': eveicon.power_off,
              'on_click': self.data['skip_function'],
              'hint': localization.GetByLabel('UI/SystemMenu/SkipTutorial')}]
        return []

    def get_cta_buttons(self):
        if self.is_offered:
            return [{'name': 'accept_opportunity_button',
              'label': localization.GetByLabel('UI/Agents/Dialogue/Buttons/AcceptMission'),
              'on_click': lambda *args, **kwargs: self._update_job_info('state', 'active')}]
        return []

    def get_state_info(self):
        if self.is_offered:
            return {'text': localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
             'color': eveColor.WARNING_ORANGE,
             'icon': eveicon.start_conversation}
        return super(StorylineJob, self).get_state_info()

    def _get_content_tag_ids(self):
        return self.data.get('content_tag_ids', [])

    def _register(self):
        self.OnExpandedMissionChanged(**sm.GetService('infoPanel').GetExpandedMission())
        sm.RegisterNotify(self)
        self.context.subscribe_to_value(self.content_id, self._job_info_changed)

    def _unregister(self):
        sm.UnregisterNotify(self)
        self.context.unsubscribe_from_value(self.content_id, self._job_info_changed)

    def _job_info_changed(self, *args, **kwargs):
        self.update()
        is_tracked = self.is_tracked
        is_offered = self.is_offered
        if is_offered and is_tracked:
            self.remove_tracked()
        elif not is_offered and not is_tracked:
            self.add_tracked()
        job_board_signals.on_job_state_changed(self)

    def _update_job_info(self, key, value):
        job_info = self.job_info
        job_info[key] = value
        self.context.update_value(key=self.content_id, value=job_info, force_update=True)

    def _add_qa_menu(self, menu):
        from objectives.client.qa_tools import is_qa, key_value_entry
        from carbonui.control.contextMenu.menuData import MenuData
        if not is_qa():
            return
        qa_menu = MenuData()
        qa_menu.AddEntry(text='Open Node Graph', func=lambda : _open_active_node_graph(self.node_graph.instance_id))
        if self.objective_chain:
            qa_menu.entrylist.extend(self.objective_chain.get_context_menu())
        qa_menu.entrylist.append(key_value_entry('Blackboard Values', self.context.values, self.context))
        menu.AddEntry('QA', subMenuData=qa_menu)


def _open_active_node_graph(node_graph_instance_id):
    from nodegraph.client.ui.window import NodeGraphEditorWindow
    NodeGraphEditorWindow.Open(node_graph_id=node_graph_instance_id)
