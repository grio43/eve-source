#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\abyss\client\abyssal_service.py
import codecs
import evetypes
import gametime
import localization
import logging
import random
import uthread2
from abyss.const import DEV_NAMES
from carbon.common.lib.const import SEC
from carbon.common.script.sys.service import CoreService
from eve.client.script.ui.shared.abyss.keyActivationWindow import KeyActivationWindow
from eve.client.script.ui.shared.abyss.AbyssJumpWindow import AbyssActivationWindow
from eve.common.script.sys.idCheckers import IsAbyssalSpaceSystem
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from pvpFilaments.common.constants import DEFAULT_PVP_CONTENT_DURATION
from threadutils.scheduler import SimTimeScheduler
from objectives.client.objective_chain import ObjectiveChain
from objectives.common.objective_context import ObjectivesContext
MAX_CRIMEWATCH_TIMER_RETRIES = 30
logger = logging.getLogger(__name__)
EXPIRATION_INDICATION_DURATION_MILLI_SECONDS = 8000
ABYSSAL_COLLAPSE_NOTIFICATION_TIMERS_SECONDS = [300, 120, 30]
ABYSS_OBJECTIVE_CHAIN_ID = 95

class AbyssalService(CoreService):
    __guid__ = 'svc.abyss'
    __displayname__ = 'Abyssal Client Service'
    __notifyevents__ = ['OnAbyssalLocationEntered',
     'OnAddExpiryDurationForAbyssalContent',
     'OnAbyssalContentFinished',
     'OnAddExpiryDurationForAbyssalPvpContent',
     'OnSessionChanged']
    __dependencies__ = ['michelle', 'sceneManager']

    def __init__(self):
        CoreService.__init__(self)
        self.nebula_graphic_id = None
        self.active_content_id = None
        self._expiry_notification_scheduler = SimTimeScheduler(name='abyss_expiry_notification')
        self._expiry_notification_scheduler.start()
        self.abyssal_fleet_disabled = None
        self.current_difficulty_tier = 0
        self.current_room_id = 0
        self._context = None
        self.objective_chain = None

    def deploy_entrance_gate(self, item_id, game_mode_id):
        abyssal_manager = sm.RemoteSvc('abyssalMgr')
        abyssal_manager.AbyssalEntranceDeployment(item_id, game_mode_id)

    def activate_entrance_gate(self, item_id):
        abyssal_manager = sm.RemoteSvc('abyssalMgr')
        abyssal_manager.AbyssalEntranceGateActivation(item_id)

    def open_key_activation_window(self, key_item):
        KeyActivationWindow.Open(item=key_item)

    def open_abyss_jump_window(self, gateID):
        AbyssActivationWindow.Open(item=gateID)

    def _GetContext(self):
        if self._context is None:
            self._context = ObjectivesContext()
            self._context.subscribe_to_message('on_objective_tasks_changed', self.on_objective_task_changed)
        return self._context

    def OnAbyssalLocationEntered(self, client_data):
        context = self._GetContext()
        logger.debug('OnAbyssalLocationEntered nebula client_data=%s', client_data)
        self.active_content_id = client_data.get('content_id', None)
        self.nebula_graphic_id = client_data.get('nebula_graphic_id', None)
        try:
            self.sceneManager.ReplaceNebulaFromResPath(self.get_nebula_res_path())
        except AttributeError:
            logger.info('Tried replacing nebula, but could not access the scene')

        self.current_difficulty_tier = client_data.get('difficulty_tier')
        self.current_room_id = client_data.get('location_id')
        context.set_values(rooms_completed=self.current_room_id - 1)
        if not self.objective_chain:
            self._start_objective_chain()
        else:
            context.send_message('stop_objective', 'destroy_lootable')
            uthread2.sleep(2)
            context.send_message('start_objective', 'destroy_lootable')

    def on_objective_task_changed(self, key, value, objective, objective_id, task_id, reason):
        if task_id == 'destroy_npcs' and reason == 'on_complete':
            context = self._GetContext()
            rooms_completed = context.get_value('rooms_completed') or 0
            if rooms_completed + 1 >= context.get_value('num_rooms'):
                context.update_value('rooms_completed', rooms_completed + 1)

    def _start_objective_chain(self):
        if self.objective_chain:
            return
        context = self._GetContext()
        self.objective_chain = ObjectiveChain(content_id=ABYSS_OBJECTIVE_CHAIN_ID, context=context)
        self.objective_chain.start()
        sm.GetService('infoPanel').UpdateAbyssPanel()

    def get_current_difficulty_tier(self):
        return self.current_difficulty_tier

    def get_current_room_id(self):
        return self.current_room_id

    def get_nebula_graphic_id(self):
        return self.nebula_graphic_id

    def get_nebula_res_path(self):
        if self.nebula_graphic_id:
            logger.debug('returning nebula respath for graphic id %s', self.nebula_graphic_id)
            return GetGraphicFile(self.nebula_graphic_id)

    def OnAddExpiryDurationForAbyssalContent(self, end_time):
        self._add_expiry_messages_to_event_scheduler(end_time)
        self._set_abyssal_timer(end_time)

    def OnAddExpiryDurationForAbyssalPvpContent(self, end_time):
        self._add_expiry_messages_to_event_scheduler(end_time)
        self._set_abyssal_pvp_timer(end_time)

    def _set_abyssal_timer(self, end_time):
        info_panel_service = sm.GetService('infoPanel')
        self._set_crimewatch_timer(info_panel_service, end_time, 'SetAbyssalTimer')

    def _set_abyssal_pvp_timer(self, end_time):
        info_panel_service = sm.GetService('infoPanel')
        self._set_crimewatch_timer(info_panel_service, end_time, 'SetAbyssalPvpTimer')

    def _set_crimewatch_timer(self, info_panel_service, end_time, set_timer_function_name):
        start_time = end_time - DEFAULT_PVP_CONTENT_DURATION
        context = self._GetContext()
        context.update_value('timer', {'end_time': end_time,
         'start_time': start_time})
        remaining_tries = MAX_CRIMEWATCH_TIMER_RETRIES
        while info_panel_service.combatTimerContainer is None and remaining_tries > 0:
            uthread2.sleep(1.0)
            remaining_tries -= 1

        if info_panel_service.combatTimerContainer:
            set_timer_function = getattr(info_panel_service.combatTimerContainer, set_timer_function_name)
            set_timer_function(end_time)

    def _add_expiry_messages_to_event_scheduler(self, end_time):
        logger.debug('adding expiry messages to event scheduler')
        self._expiry_notification_scheduler.clear_all_events()
        space_manager = sm.GetService('space')
        for notification_time_seconds in ABYSSAL_COLLAPSE_NOTIFICATION_TIMERS_SECONDS:
            message_time = gametime.GetSecondsUntilSimTime(end_time - notification_time_seconds * SEC) * SEC
            self._expiry_notification_scheduler.enter_relative_event(message_time, 0, self._display_expiry_message, (space_manager, notification_time_seconds))

    def _display_expiry_message(self, space_manager, notification_time_seconds):
        space_manager.DoSetIndicationTextForcefully(localization.GetByLabel('UI/Abyss/AbyssalCollapseWarningHeader'), localization.GetByLabel('UI/Abyss/AbyssalCollapseWarningSubject', time=notification_time_seconds), indicationTime=EXPIRATION_INDICATION_DURATION_MILLI_SECONDS)

    def OnAbyssalContentFinished(self, content_id, timer_type):
        if not self.is_active_content(content_id):
            return
        self._expiry_notification_scheduler.clear_all_events()
        self._context = None

    def get_mangled_system_name(self, solar_system_id, char_id):
        state = random.getstate()
        random.seed(solar_system_id + char_id)
        name = random.choice(DEV_NAMES)
        random.setstate(state)
        return codecs.encode(name, 'rot_13')

    def is_active_content(self, content_id):
        return self.active_content_id == content_id

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' not in change:
            return
        from_solar_system_id, to_solar_system_id = change['solarsystemid2']
        if self._is_logging_in_to_abyssal_system(from_solar_system_id, to_solar_system_id):
            abyssal_manager = sm.RemoteSvc('abyssalMgr')
            abyssal_manager.ClientIsReady()
        if not IsAbyssalSpaceSystem(to_solar_system_id):
            if self.objective_chain:
                self.objective_chain.stop()
                self.objective_chain = None
                sm.GetService('infoPanel').UpdateAbyssPanel()

    def _is_logging_in_to_abyssal_system(self, from_solar_system_id, to_solar_system_id):
        return from_solar_system_id is None and IsAbyssalSpaceSystem(to_solar_system_id)
