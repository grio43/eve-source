#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\operations\client\eventdirector\eventdirector.py
import logging
import uthread2
from achievements.common.achievementConst import AchievementEventConst
from carbon.common.script.sys.service import Service
from operations.client.operationscontroller import GetOperationsController
from operations.client.util import are_operations_active
from operations.common.util import is_task_active
logger = logging.getLogger(__name__)
OPERATION_ACTIVATION_DELAY = 1.0

class EventLinkTypes:
    TASK_STARTED_TO_CONVERSATION = 1
    TASK_ENDED_TO_CONVERSATION = 2


class OperationsEventDirector(Service):
    __guid__ = 'svc.OperationsEventDirector'
    serviceName = 'svc.OperationsEventDirector'
    __displayname__ = 'OperationsEventDirector'
    __servicename__ = 'OperationsEventDirector'
    __startupdependencies__ = ['conversationService', 'uiHighlightingService', 'dynamicMusic']
    __notifyevents__ = ['OnOperationMadeActive',
     'OnOperationCompleted',
     'OnOperationTaskMadeActive',
     'OnIntroCompleted',
     'OnTutorialSkipped',
     'OnOperationDeactivatedUpdate']

    def OnIntroCompleted(self):
        if not are_operations_active():
            self._unregister()
            return
        operationsController = GetOperationsController()
        sm.ScatterEvent('OnOperationsInitialized', operationsController.get_active_category_id(), operationsController.get_active_operation_id())

    def _unregister(self):
        sm.UnregisterNotify(self)

    def OnTutorialSkipped(self):
        self._clear_ui_highlights_and_conversations()

    def OnOperationDeactivatedUpdate(self):
        self._clear_ui_highlights_and_conversations()

    def _clear_ui_highlights_and_conversations(self):
        self._clear_ui_highlighting()
        self.force_hide_active_conversation()

    def force_hide_active_conversation(self):
        self.conversationService.force_hiding_active_conversation()

    def OnOperationMadeActive(self, category_id, operation_id, old_category_id, old_operation_id, is_silent):
        if old_operation_id:
            self.OnOperationCompleted(old_category_id, old_operation_id)
        if not is_silent:
            uthread2.Sleep(OPERATION_ACTIVATION_DELAY)
            uthread2.StartTasklet(self._process_operation_started, category_id, operation_id)

    def OnOperationCompleted(self, category_id, operation_id):
        self.conversationService.hide_conversation()
        self._clear_ui_highlighting()

    def OnOperationTaskMadeActive(self, task_id, old_task_id, *args, **kwargs):
        if old_task_id:
            self.OnOperationTaskCompleted(old_task_id)
        duration = self._get_delay_before_task_duration(task_id)
        uthread2.Sleep(duration)
        category_id = GetOperationsController().get_active_category_id()
        operation_id = GetOperationsController().get_active_operation_id()
        if category_id is not None and operation_id is not None:
            task_state = GetOperationsController().get_task_state(category_id, operation_id, task_id)
            if is_task_active(task_state):
                uthread2.StartTasklet(self._process_task_started, task_id)

    def _get_delay_before_task_duration(self, task_id):
        task = GetOperationsController().get_task_by_id(task_id)
        return task.delayBefore

    def OnOperationTaskCompleted(self, task_id):
        conversation_id = GetOperationsController().get_conversation_on_task_start(task_id)
        if conversation_id:
            self.conversationService.hide_conversation()

    def _clear_ui_highlighting(self):
        self.uiHighlightingService.clear_all_highlighting()

    def _process_active_task_in_operation(self, category_id, operation_id):
        active_task_id = GetOperationsController().get_first_unfinished_task_in_operation(category_id, operation_id)
        if active_task_id is None:
            return
        self.OnOperationTaskMadeActive(active_task_id, None)

    def _process_operation_started(self, category_id, operation_id):
        GetOperationsController().unlock_active_operation()
        self._process_active_task_in_operation(category_id, operation_id)

    def _process_task_started(self, task_id):
        self._process_operation_entity_change_to_conversation_display(event_link_type=EventLinkTypes.TASK_STARTED_TO_CONVERSATION, get_conversation=GetOperationsController().get_conversation_on_task_start, show_conversation=self.conversationService.show_conversation, task_id=task_id)

    def _is_continue_button_shown(self, task_id):
        task = GetOperationsController().get_task_by_id(task_id)
        return task.achievementEventType == AchievementEventConst.TASK_CONTINUE_BUTTON_PRESSED

    def _process_task_ended(self, task_id):
        self._process_operation_entity_change_to_conversation_display(event_link_type=EventLinkTypes.TASK_ENDED_TO_CONVERSATION, get_conversation=GetOperationsController().get_conversation_on_task_end, show_conversation=self.conversationService.show_conversation, task_id=task_id)

    def _process_operation_entity_change_to_conversation_display(self, event_link_type, get_conversation, show_conversation, task_id):
        conversation_entity_id = get_conversation(task_id)
        if not conversation_entity_id:
            return
        try:
            show_continue_button = self._is_continue_button_shown(task_id)
            show_conversation(conversation_entity_id, show_continue_button=show_continue_button)
        except ValueError:
            error_msg = self._get_operation_entity_change_to_conversation_display_error(event_link_type, task_id, conversation_entity_id)
            self.LogError(error_msg)

    def _get_operation_entity_change_to_conversation_display_error(self, event_link_type, operation_entity_id, conversation_entity_id):
        if event_link_type == EventLinkTypes.TASK_STARTED_TO_CONVERSATION:
            return 'Failed to display conversation on task start. Task ID: %s, Conversation ID: %s' % (operation_entity_id, conversation_entity_id)
        if event_link_type == EventLinkTypes.TASK_ENDED_TO_CONVERSATION:
            return 'Failed to display conversation on task end. Task ID: %s, Conversation ID: %s' % (operation_entity_id, conversation_entity_id)
        return ''
