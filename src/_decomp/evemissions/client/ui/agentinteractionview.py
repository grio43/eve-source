#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\ui\agentinteractionview.py
from agentinteraction.importantmission import ImportantMissionContainer
from agentinteraction.npcinteractionview import NpcInteractionView
from agentinteraction.objectivesview import ObjectivesView
from carbon.common.script.util.commonutils import StripTags
from carbonui import ButtonStyle, ButtonVariant, uiconst
from jobboard.client import get_agent_mission_job
from jobboard.client.ui.track_button import TrackJobButton
from localization import GetByLabel

class AgentInteractionView(NpcInteractionView):
    IMPORTANT_MISSION_ICON_SIZE = 32
    BUTTON_UI_TEMPLATE = {'AcceptMission_Button': {'order': 1,
                              'variant': ButtonVariant.PRIMARY},
     'RequestMission_Button': {'order': 0,
                               'variant': ButtonVariant.PRIMARY},
     'DeferMission_Button': {'order': 2},
     'CompleteMission_Button': {'order': 3,
                                'style': ButtonStyle.SUCCESS},
     'DeclineMission_Button': {'order': 4,
                               'hint': StripTags(GetByLabel('UI/Agents/StandardMission/DeclineMessageGeneric'))}}

    def ApplyAttributes(self, attributes):
        super(AgentInteractionView, self).ApplyAttributes(attributes)
        self.agent_id = self.npc_character.get_id()

    def _build_objectives(self):
        self.container_objectives = ObjectivesView(name='container_objectives', parent=self.inner_scroll_cont, align=uiconst.TOTOP)
        self.container_objectives.Hide()

    def update_objectives(self, objectives, objectives_type):
        self.container_objectives.update_objectives(objectives, objectives_type)

    def _add_button(self, button, button_info):
        self.buttonGroup.AddButton(button['label'], button['func'], style=button_info.get('style', ButtonStyle.NORMAL), variant=button_info.get('variant', ButtonVariant.NORMAL), hint=button_info.get('hint', None), **(button['kwargs'] or {}))

    def _create_button_dict(self, actions):
        button_dict = {}
        for label, func, kwargs in actions:
            name = kwargs.get('uiName', None)
            button_dict.update({name: {'label': label,
                    'func': func,
                    'kwargs': kwargs}})

        return button_dict

    def _order_buttons(self, action_dict):
        known_buttons = []
        unknown_buttons = []
        for action in action_dict.keys():
            if action in self.BUTTON_UI_TEMPLATE:
                known_buttons.append(action)
            else:
                unknown_buttons.append(action)

        known_buttons = sorted(known_buttons, key=lambda button: self.BUTTON_UI_TEMPLATE[button]['order'])
        return known_buttons + unknown_buttons

    def update_buttons(self, actions, controller):
        self.buttonGroup.FlushButtons()
        action_dict = self._create_button_dict(actions)
        ordered_actions = self._order_buttons(action_dict)
        for action in ordered_actions:
            if action not in self.BUTTON_UI_TEMPLATE:
                self._add_button(action_dict[action], {})
            else:
                self._add_button(action_dict[action], self.BUTTON_UI_TEMPLATE[action])

        job = get_agent_mission_job(controller.npc_character_id, wait=False)
        if job:
            TrackJobButton(parent=self.buttonGroup, job=job)

    def _build_title(self):
        self._build_important_mission()
        super(AgentInteractionView, self)._build_title()

    def _build_important_mission(self):
        self.important_mission_container = ImportantMissionContainer(parent=self.container_title, width=self.IMPORTANT_MISSION_ICON_SIZE, size=self.IMPORTANT_MISSION_ICON_SIZE)
        self.important_mission_container.Hide()

    def update_important_mission(self, is_important, header = '', text = '', standing_list = None):
        if is_important:
            self.important_mission_container.Show()
        else:
            self.important_mission_container.Hide()
        self.important_mission_container.update_header_text(header, text, standing_list)
