#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\eventlogging\events.py


class Event(object):
    STORE_BUTTON_CLICKED = 'StoreButtonClicked'


class BaseEventLogger(object):

    def _log_event(self, event, data):
        raise NotImplementedError('Must implement _log_event in derived class')

    def log_store_button_clicked(self):
        data = {}
        self._log_event(Event.STORE_BUTTON_CLICKED, data)
