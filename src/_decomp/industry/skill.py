#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\skill.py
import immutable
import industry
import signals

class Skill(industry.Base):
    __metaclass__ = immutable.Immutable

    def __new__(cls, *args, **kwargs):
        obj = industry.Base.__new__(cls)
        obj._typeID = None
        obj._level = None
        obj._errors = []
        obj.on_updated = signals.Signal(signalName='on_updated')
        obj.on_errors = signals.Signal(signalName='on_errors')
        return obj

    typeID = industry.Property('_typeID', 'on_updated')
    level = industry.Property('_level', 'on_updated')
    errors = industry.Property('_errors', 'on_errors')

    def __repr__(self):
        return industry.repr(self, exclude=['on_errors', '_errors'])
