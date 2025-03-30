#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\messages.py
from behaviors.tasks import MonitorTask
from behaviors.utility.inventory import is_my_cargo_full

class SendMessageOnMessageMonitor(MonitorTask):

    def _get_message(self):
        return self.attributes.monitoredMessageId

    def _self_process_message(self, *args):
        if self._can_process_message():
            self.GetEventMessenger().SendMessage(self.context.myItemId, self.attributes.notifiedMessageId, *args)


class SendMessageOnMessageWhenCargoIsFullMonitor(SendMessageOnMessageMonitor):

    def _can_process_message(self):
        return is_my_cargo_full(self)
