#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\client\void_space_service.py
import gametime
import localization
import logging
import uthread2
from carbon.common.lib.const import SEC
from carbon.common.script.sys.service import CoreService
from eve.common.script.sys.idCheckers import IsVoidSpaceSystem
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from threadutils.scheduler import SimTimeScheduler
from voidspace.client.activation_window import VoidSpaceActivationWindow
from voidspace.common.constants import VOID_SPACE_COLLAPSE_NOTIFICATION_TIMERS_SECONDS
logger = logging.getLogger(__name__)
EXPIRATION_INDICATION_DURATION_MILLI_SECONDS = 8000
MAX_CRIME_WATCH_TIMER_RETRIES = 30
MAX_NEBULA_REPLACEMENT_RETRIES = 30

class VoidSpaceService(CoreService):
    __guid__ = 'svc.voidSpaceSvc'
    __displayname__ = 'Void Space Client Service'
    __notifyevents__ = ['OnVoidSpaceEntered',
     'OnAddExpiryDurationForVoidSpaceContent',
     'OnVoidSpaceRelog',
     'OnVoidSpaceContentFinished',
     'OnSessionChanged']
    __dependencies__ = ['michelle', 'sceneManager']

    def __init__(self):
        CoreService.__init__(self)
        self.nebula_graphic_id = None
        self.active_content_id = None
        self._expiry_notification_scheduler = SimTimeScheduler(name='void_space_expiry_notification')
        self._expiry_notification_scheduler.start()

    def open_void_space_activation_window(self, key_item):
        VoidSpaceActivationWindow.Open(item=key_item)

    def VoidSpaceJump(self, itemID, typeID):
        sm.RemoteSvc('voidSpaceMgr').VoidSpacePlayerJump(itemID, typeID)

    def OnVoidSpaceEntered(self, client_data):
        logger.debug('OnVoidSpaceEntered nebula client_data=%s', client_data)
        self.active_content_id = client_data.get('content_id', None)
        self.nebula_graphic_id = client_data.get('nebula_graphic_id', None)
        remaining_tries = MAX_NEBULA_REPLACEMENT_RETRIES
        failure = True
        while failure and remaining_tries > 0:
            uthread2.sleep(0.4)
            remaining_tries -= 1
            try:
                self.sceneManager.ReplaceNebulaFromResPath(self.get_nebula_res_path())
                failure = False
            except AttributeError:
                logger.info('Tried replacing nebula, but could not access the scene')

    def get_nebula_graphic_id(self):
        return self.nebula_graphic_id

    def get_nebula_res_path(self):
        if self.nebula_graphic_id:
            logger.debug('returning nebula respath for graphic id %s', self.nebula_graphic_id)
            return GetGraphicFile(self.nebula_graphic_id)

    def OnAddExpiryDurationForVoidSpaceContent(self, end_time):
        self._add_expiry_messages_to_event_scheduler(end_time)
        self._set_voidSpace_timer(end_time)

    def OnVoidSpaceRelog(self, client_data):
        self.OnVoidSpaceEntered(client_data)
        if client_data.get('end_time', None) is not None:
            self.OnAddExpiryDurationForVoidSpaceContent(client_data['end_time'])

    def _set_voidSpace_timer(self, end_time):
        info_panel_service = sm.GetService('infoPanel')
        self._set_crimewatch_timer(info_panel_service, end_time, 'SetVoidSpaceTimer')

    def _set_crimewatch_timer(self, info_panel_service, end_time, set_timer_function_name):
        remaining_tries = MAX_CRIME_WATCH_TIMER_RETRIES
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
        for notification_time_seconds in VOID_SPACE_COLLAPSE_NOTIFICATION_TIMERS_SECONDS:
            message_time = gametime.GetSecondsUntilSimTime(end_time - notification_time_seconds * SEC) * SEC
            self._expiry_notification_scheduler.enter_relative_event(message_time, 0, self._display_expiry_message, (space_manager, notification_time_seconds))

    def _display_expiry_message(self, space_manager, notification_time_seconds):
        space_manager.DoSetIndicationTextForcefully(localization.GetByLabel('UI/Abyss/AbyssalCollapseWarningHeader'), localization.GetByLabel('UI/Abyss/AbyssalCollapseWarningSubject', time=notification_time_seconds), indicationTime=EXPIRATION_INDICATION_DURATION_MILLI_SECONDS)

    def OnVoidSpaceContentFinished(self, content_id, timer_type):
        if not self.is_content_active(content_id):
            return
        self._expiry_notification_scheduler.clear_all_events()

    def is_content_active(self, content_id):
        return self.active_content_id == content_id

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' not in change:
            return
        from_solar_system_id, to_solar_system_id = change['solarsystemid2']
        if self._is_logging_in_to_void_space_system(from_solar_system_id, to_solar_system_id):
            void_manager = sm.RemoteSvc('voidSpaceMgr')
            void_manager.ClientIsReady()

    def _is_logging_in_to_void_space_system(self, from_solar_system_id, to_solar_system_id):
        return from_solar_system_id is None and IsVoidSpaceSystem(to_solar_system_id)
