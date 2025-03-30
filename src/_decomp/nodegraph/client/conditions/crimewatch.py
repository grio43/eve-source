#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\crimewatch.py
from .base import Condition

class IsCrimewatchTimerActive(Condition):
    atom_id = 407

    def __init__(self, timer_type = None, **kwargs):
        super(IsCrimewatchTimerActive, self).__init__(**kwargs)
        self.timer_type = self.get_atom_parameter_value('timer_type', timer_type)

    def validate(self, **kwargs):
        try:
            from eve.client.script.ui.crimewatch.crimewatchTimers import TimerType
            combatTimers = sm.GetService('infoPanel').combatTimerContainer
            return combatTimers.GetExistingTimer(TimerType[self.timer_type]) is not None
        except:
            return False

    @classmethod
    def get_subtitle(cls, timer_type = None, **kwargs):
        if timer_type:
            from eve.client.script.ui.crimewatch.crimewatchTimers import TimerType
            timer_type_enum = TimerType[timer_type]
            return u'{} ({})'.format(timer_type_enum.name, timer_type_enum.value)
        return ''
