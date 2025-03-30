#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\settings.py
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui.services.setting import UserSettingBool
_experimental_map_setting = UserSettingBool('experimental_map_default_1', default_value=True)
classic_map_enabled_setting = UserSettingBool('use_classic_starmap', default_value=lambda : not _experimental_map_setting.is_enabled())

def _on_classic_map_toggled(enabled):
    ServiceManager.Instance().GetService('neocom').UpdateNeocomButtons()


classic_map_enabled_setting.on_change.connect(_on_classic_map_toggled)
