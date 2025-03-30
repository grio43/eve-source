#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\location_chip.py
from eve.client.script.ui.shared.maps.solarSystemMapIcon import SolarSystemMapIcon
import eveformat.client
import eveui
import inventorycommon.const as invconst
from .chip import Chip

class SolarSystemChip(Chip):
    default_name = 'SolarSystemChip'

    def __init__(self, solar_system_id = None, **kwargs):
        super(SolarSystemChip, self).__init__(**kwargs)
        self.icon = SolarSystemMapIcon(parent=self, align=eveui.Align.center_left, width=38, height=38, opacity=0.3, left=-10)
        self._solar_system_id = None
        if solar_system_id:
            self.solar_system_id = solar_system_id

    @property
    def solar_system_id(self):
        return self._solar_system_id

    @solar_system_id.setter
    def solar_system_id(self, solar_system_id):
        if self._solar_system_id == solar_system_id:
            return
        self._solar_system_id = solar_system_id
        if solar_system_id:
            self.icon.Draw(solar_system_id, 46)
            self.text = eveformat.solar_system_with_security(solar_system_id)
        else:
            self.clear()

    def GetDragData(self):
        return [eveui.dragdata.SolarSystem(self.solar_system_id)]

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=self.solar_system_id, typeID=invconst.typeSolarSystem)
