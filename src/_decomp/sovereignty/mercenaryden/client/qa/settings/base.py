#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\mercenaryden\client\qa\settings\base.py
import abc

class BaseQASetting(object):
    __metaclass__ = abc.ABCMeta

    def is_enabled(self):
        return NotImplementedError("Must implement 'is_enabled' in derived class")

    def register_to_updates(self, callback):
        return NotImplementedError("Must implement 'register_to_updates' in derived class")

    def unregister_from_updates(self, callback):
        return NotImplementedError("Must implement 'unregister_from_updates' in derived class")


class QASettingMock(BaseQASetting):

    def is_enabled(self):
        return True

    def register_to_updates(self, callback):
        pass

    def unregister_from_updates(self, callback):
        pass
