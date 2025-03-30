#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\data_display\table\column\solar_system.py
from .attribute import AttributeColumn
import eveformat.client

class SolarSystemColumn(AttributeColumn):

    def __init__(self, show_jumps = True, **kwargs):
        super(SolarSystemColumn, self).__init__(**kwargs)
        self.show_jumps = show_jumps

    def get_value(self, entry):
        solar_system_id = super(SolarSystemColumn, self).get_value(entry)
        if self.show_jumps:
            return eveformat.solar_system_with_security_and_jumps(solar_system_id)
        else:
            return eveformat.solar_system_with_security(solar_system_id)
