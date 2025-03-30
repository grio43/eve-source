#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\uiblinker\reference\__init__.py
import abc

class UiReference(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def resolve(self, root):
        pass
