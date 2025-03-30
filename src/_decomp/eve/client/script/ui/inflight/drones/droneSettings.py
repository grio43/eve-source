#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\drones\droneSettings.py
import appConst
import dogma.data
from carbonui.services.setting import CharSettingBool, CharSettingEnum
drones_aggressive_setting = CharSettingBool('droneAggression', lambda : dogma.data.get_attribute_default_value(appConst.attributeDroneIsAggressive))
drones_focus_fire_setting = CharSettingBool('droneFocusFire', lambda : dogma.data.get_attribute_default_value(appConst.attributeDroneFocusFire))
VIEW_MODE_ICONS = 1
VIEW_MODE_LIST = 2
VIEW_MODES = (VIEW_MODE_ICONS, VIEW_MODE_LIST)
drones_view_mode_setting = CharSettingEnum('dronesViewMode', VIEW_MODE_ICONS, VIEW_MODES)
drones_view_mode_compact_setting = CharSettingEnum('dronesViewModeCompact', VIEW_MODE_LIST, VIEW_MODES)

def on_aggressive_changed(is_enabled):
    sm.GetService('godma').GetStateManager().ChangeDroneSettings({appConst.attributeDroneIsAggressive: is_enabled})


drones_aggressive_setting.on_change.connect(on_aggressive_changed)

def on_focus_fire_changed(is_enabled):
    sm.GetService('godma').GetStateManager().ChangeDroneSettings({appConst.attributeDroneFocusFire: is_enabled})


drones_focus_fire_setting.on_change.connect(on_focus_fire_changed)
