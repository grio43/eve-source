#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\observable.py
import abc

class Observable(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def value(self):
        pass

    @abc.abstractproperty
    def on_changed(self):
        pass
