#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evemissions\client\ui\missiongiver.py
import uthread
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
import carbon.common.script.sys.serviceConst as serviceConst
from agentinteraction.window import NpcCharacterInteractionWindow
from evemissions.client.missioncontroller import OldMissionController
from evemissions.client.ui.agentview import AgentView
from evemissions.client.ui.agentinteractionview import AgentInteractionView
from eveui.decorators import skip_if_destroyed
from localization import GetByLabel, GetByMessageID
from signals.signalUtil import ChangeSignalConnect
from uthread2 import StartTasklet
from carbonui import const as uiconst
BG_WIDTH = 2500
BG_HEIGHT = 1400
BG_PROPS = float(BG_WIDTH) / BG_HEIGHT
bg_by_division_id = {}
FALLBACK_BG = None

class MissionGiver(NpcCharacterInteractionWindow):
    __guid__ = 'MissionGiver'
    default_windowID = 'MissionGiver'
    default_isCollapseable = True
    default_isLightBackgroundConfigurable = False
    character_view_class = AgentView
    interaction_view_class = AgentInteractionView
    show_background_for_window = False

    def ApplyAttributes(self, attributes):
        self.background_sprite = None
        self._initialize_controller(attributes.npcCharacterID)
        super(MissionGiver, self).ApplyAttributes(attributes)
        self.header.show_caption = False
        self.isLoading = False

    def Prepare_Background_(self):
        self._build_background()
        super(MissionGiver, self).Prepare_Background_()

    def _build_background(self):
        if not self.show_background_for_window:
            return
        background_path = self._get_background_path()
        if not background_path:
            return
        pL, pT, pR, pB = self.GetWindowBorderPadding()
        bL, bT, bR, bB = self.GetWindowBorderSize()
        background_cont = Container(name='background_cont', parent=self, align=uiconst.TOALL, clipChildren=True, padding=(pL + bL,
         pT + bT,
         pR + bR,
         pB + bB))
        self.background_sprite = Sprite(name='sprite_background', parent=background_cont, align=uiconst.BOTTOMLEFT, texturePath=background_path, state=uiconst.UI_DISABLED)

    def _get_background_path(self):
        division_id = self.controller.npc_character.get_division_id()
        texture_path = bg_by_division_id.get(division_id, FALLBACK_BG)
        return texture_path

    def Close(self, setClosed = False, *args, **kwds):
        super(MissionGiver, self).Close(setClosed, *args, **kwds)
        ChangeSignalConnect(self.signals_and_callbacks, connect=False)

    def _initialize_controller(self, npc_character_id):
        self.controller = OldMissionController(npc_character_id)
        self.signals_and_callbacks = [(self.controller.on_mission_modified, self.InteractWithAgent), (self.controller.on_station_changed, self.InteractWithAgent), (self.controller.on_ship_changed, self.InteractWithAgent)]
        ChangeSignalConnect(self.signals_and_callbacks, connect=True)

    def ShowMissionObjectives(self, content_id):
        if self.destroyed or self.controller.mission_id != content_id:
            return
        self.controller.update_objectives()
        self._update_objectives()
        self._update_rewards()

    @skip_if_destroyed
    def InteractWithAgent(self, actionID = None):
        if self.isLoading:
            return
        self.isLoading = True
        StartTasklet(self._update_mission, actionID)

    def _update_mission(self, action_id):
        try:
            self._start_loading(action_id)
            self.controller.update_mission(action_id)
            self.controller.update_objectives()
            self._update_objectives()
            parallelCalls = [(self._update_rewards, ()), (self._update_standings, ())]
            uthread.parallel(parallelCalls)
            self._update_important_mission()
            self._update_mission_name()
            self._update_lore()
            self._update_actions()
            self._update_caption_text()
        finally:
            self._stop_loading()

    def _start_loading(self, action_id):
        if action_id:
            self.disable_buttons()
        self.container_interaction.update_loading_state(is_loading=True)

    def _stop_loading(self):
        self.isLoading = False
        self.enable_buttons()
        self.container_interaction.update_loading_state(is_loading=False)

    def _update_important_mission(self):
        is_important = self.controller.is_mission_important()
        header, text, standing_list = self.controller.get_mission_importance_text()
        self.container_interaction.update_important_mission(is_important, header, text, standing_list)

    def _update_standings(self):
        if self.controller.is_mission_completed():
            standing_gain = 0
        else:
            standing_gain = self.controller.get_standing_gain()
        show_standings = self.controller.show_standings()
        self.container_npc_character.update_standings(standing_gain, show_standings)

    def _update_mission_name(self):
        mission_name = self.controller.get_mission_title()
        self.container_interaction.update_title(mission_name)

    def _update_lore(self):
        lore = self.controller.get_lore()
        is_completed = self.controller.is_mission_completed()
        self.container_interaction.update_lore(lore, show_all=is_completed)

    def _update_actions(self):
        actions = self.controller.get_actions()
        if self.controller.mission and not self.controller.can_replay_mission():
            actions = []
        if not actions or self.controller.should_add_close_action():
            actions.append((GetByLabel('UI/Common/Buttons/Close'), self.CloseByUser, {'uiName': 'CloseAgentConversation_Button'}))
        self.container_interaction.update_buttons(actions, self.controller)

    def _update_objectives(self):
        objectives = self.controller.get_objectives()
        objectives_type = self.controller.get_objectives_type()
        self.container_interaction.update_objectives(objectives, objectives_type)
        if self.controller.is_mission_active():
            self.container_interaction.show_objectives()
        else:
            self.container_interaction.hide_objectives()

    def _update_rewards(self):
        if self.controller.is_mission_active():
            items = self.controller.get_granted_items()
            self.container_interaction.update_granted_items(items)
            items = self.controller.get_normal_rewards()
            self.container_interaction.update_normal_rewards(items)
            items = self.controller.get_bonus_rewards()
            self.container_interaction.update_bonus_rewards(items)
            items = self.controller.get_collateral()
            self.container_interaction.update_collateral(items)
            show_warning = not self.controller.can_run_in_current_ship()
            self.container_interaction.update_ship_requirements(show_warning)
            disclaimer = self.controller.get_disclaimer()
            self.container_interaction.update_disclaimer(disclaimer)
            self.container_interaction.update_ship_requirements_info(self.controller.get_dungeon_id())
        else:
            items = []
            self.container_interaction.update_granted_items(items)
            self.container_interaction.clear_rewards()
            self.container_interaction.update_collateral(items)
            self.container_interaction.update_ship_requirements(should_show=False)
            self.container_interaction.update_ship_requirements_info(None)
            self.container_interaction.update_disclaimer(disclaimer=None)

    def _update_caption_text(self):
        text = '%s: %s ' % (GetByLabel('UI/Agents/Dialogue/AgentConversation'), self._get_window_name())
        self.SetCaption(text)

    def _update_sizes(self):
        super(MissionGiver, self)._update_sizes()
        self._update_background_size()

    def _update_background_size(self):
        if self.InStack():
            available_width = self.GetStack().width
            available_height = self.GetStack().height
        else:
            available_width = self.width
            available_height = self.height
        if not available_height or not available_width:
            return
        current_props = float(available_width) / available_height
        if current_props > BG_PROPS:
            bg_width = available_width
            bg_height = available_width / BG_PROPS
        else:
            bg_height = available_height
            bg_width = available_height * BG_PROPS
        if self._has_background_sprite():
            self.background_sprite.SetSize(bg_width, bg_height)

    def _has_background_sprite(self):
        return self.background_sprite and not self.background_sprite.destroyed

    def OnCollapsed(self, wnd, *args):
        if self._has_background_sprite():
            self.background_sprite.display = False
        self.header.show_caption = True

    def _get_window_name(self):
        mission_name_id = self.controller.get_mission_name()
        if mission_name_id:
            text = GetByMessageID(mission_name_id)
        else:
            agent_name_id = self.controller.npc_character.get_name()
            text = GetByMessageID(agent_name_id) if agent_name_id else ''
        return text

    def OnExpanded(self, wnd, *args):
        if self._has_background_sprite():
            self.background_sprite.display = True
        self.header.show_caption = False

    def GetMenuMoreOptions(self):
        menuData = super(MissionGiver, self).GetMenuMoreOptions()
        if session.role & (serviceConst.ROLE_EXT_GM1_PLUS | serviceConst.ROLE_CONTENT):
            self._add_dev_options(menuData)
        return menuData

    def _add_dev_options(self, menuData):
        menuData.AddEntry(text='Reload wnd', func=self._dev_reload_wnd)
        menuData.AddEntry(text='Open old agent wnd (not fully functional)', func=self._dev_open_old_wnd)
        menuData.AddEntry(text='Set Default size', func=self._dev_set_default_size)
        menuData.AddEntry(text='Set Min size', func=self._dev_set_min_size)
        menuData.AddSeparator()
        from evemissions.client.qa_tools import get_agent_mission_context_menu
        mission_menu = get_agent_mission_context_menu(mission_content_id=self.controller.mission_id, agent_id=self.controller.npc_character_id, group=False)
        if mission_menu:
            menuData.entrylist.extend(mission_menu.entrylist)

    def _dev_reload_wnd(self):
        character_id = self.controller.npc_character_id
        self.Close()
        sm.StartService('agents').OpenDialogueWindow(character_id)

    def _dev_open_old_wnd(self):
        character_id = self.controller.npc_character_id
        windowName = 'OldAgentWnd_%s' % character_id
        from eve.client.script.ui.station.agents.agentDialogueWindow import AgentDialogueWindow
        wnd = AgentDialogueWindow.Open(windowID=windowName, agentID=character_id, npcCharacterID=character_id)
        wnd.Maximize()
        wnd.InteractWithAgent()

    def _dev_set_default_size(self):
        self.SetSize(self.default_width, self.default_height)

    def _dev_set_min_size(self):
        self.SetSize(*self.minsize)
