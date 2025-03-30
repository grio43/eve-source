#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\Alliances\sovHubs\filterCont.py
from caching import Memoize
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.services.setting import CharSettingEnum
from localization import GetByLabel
import carbonui
from signals import Signal

@Memoize
def GetLocationOptions():
    return [(GetByLabel('UI/Agency/ContentOfAnyDistance'), None),
     (GetByLabel('UI/Generic/CurrentSystem'), 1),
     (GetByLabel('UI/Common/WithinJumps', numJumps=2), 2),
     (GetByLabel('UI/Common/WithinJumps', numJumps=5), 5),
     (GetByLabel('UI/Common/WithinJumps', numJumps=10), 10)]


sovHubPage_selectedLocationSetting = CharSettingEnum('sovHubPageFilter_location', None, [ x[1] for x in GetLocationOptions() ])

def GetSelectedLocationOption():
    locationOption = sovHubPage_selectedLocationSetting.get()
    if locationOption not in sovHubPage_selectedLocationSetting.options:
        locationOption = sovHubPage_selectedLocationSetting.options[0]
    return locationOption


class HubPageFilterCont(Container):
    default_name = 'hubPageFilterCont'

    def ApplyAttributes(self, attributes):
        super(HubPageFilterCont, self).ApplyAttributes(attributes)
        self.on_filters_changed = Signal(signalName='on_filters_changed')
        locationOption = GetSelectedLocationOption()
        Combo(name='locationRange', parent=self, options=GetLocationOptions(), select=locationOption, callback=self.OnDistanceCombo, align=carbonui.Align.TOLEFT, label='')

    def OnDistanceCombo(self, combo, key, value):
        if value == sovHubPage_selectedLocationSetting.get():
            return
        if value not in sovHubPage_selectedLocationSetting.options:
            value = sovHubPage_selectedLocationSetting.options[-1]
        sovHubPage_selectedLocationSetting.set(value)
        self.on_filters_changed()


def IsFilteredOutByLocation(sovHubID, sovHubInfo, controller):
    locationOption = GetSelectedLocationOption()
    if locationOption is None:
        return False
    if locationOption == 1:
        return controller.solarSystemID != session.solarsystemid2
    return controller.GetNumJumps() > locationOption
