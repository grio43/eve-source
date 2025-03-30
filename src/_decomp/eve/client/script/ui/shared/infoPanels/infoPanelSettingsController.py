#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelSettingsController.py
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst

def get_info_panel_settings_id(settings_id):
    return 'InfoPanelModes_%s' % settings_id


def get_all_info_panel_settings(settings_id):
    panel_settings = settings.char.ui.Get(get_info_panel_settings_id(settings_id), [])
    if panel_settings:
        panel_settings = __remove_deleted_panel_entries(panel_settings)
    return panel_settings


def save_info_panel_setting(settings_id, panel_settings):
    settings.char.ui.Set(get_info_panel_settings_id(settings_id), panel_settings)


def __remove_deleted_panel_entries(panels):
    return [ panel for panel in panels if panel[0] in infoPanelConst.PANELTYPES ]


def save_mode_for_panel_in_setting(settings_id, panel_type_id, new_panel_mode):
    panel_settings = get_all_info_panel_settings(settings_id)
    if is_panel_type_in_panel_settings(panel_settings, panel_type_id):
        panel_settings = __modify_panel_mode_in_setting(panel_settings, panel_type_id, new_panel_mode)
    else:
        panel_settings.append([panel_type_id, new_panel_mode])
    settings.char.ui.Set(get_info_panel_settings_id(settings_id), panel_settings)
    sm.ScatterEvent('OnInfoPanelSettingChanged', panel_type_id, new_panel_mode)


def is_panel_type_in_panel_settings(panel_settings, panel_type_id):
    for panel_type, panel_mode in panel_settings:
        if panel_type == panel_type_id:
            return True

    return False


def __modify_panel_mode_in_setting(panel_settings, panel_type_id, new_panel_mode):
    for settingsEntry in panel_settings:
        if settingsEntry[0] == panel_type_id:
            settingsEntry[1] = new_panel_mode

    return panel_settings


def get_panel_mode(settings_id, panel_type_id):
    panel_settings = get_all_info_panel_settings(settings_id)
    settings_entry = get_panel_settings_entry_by_type(panel_settings, panel_type_id)
    if not settings_entry:
        default_mode = get_panel_default_mode(settings_id, panel_type_id)
        save_mode_for_panel_in_setting(settings_id, panel_type_id, default_mode)
        return default_mode
    return settings_entry[1]


def get_panel_default_mode(settings_id, panel_type_id):
    return infoPanelConst.PANEL_DEFAULT_MODE_BY_SETTINGSID.get(settings_id, {}).get(panel_type_id, infoPanelConst.MODE_NORMAL)


def get_panel_settings_entry_by_type(panel_settings, panel_type_id):
    for settings_entry in panel_settings:
        if settings_entry[0] == panel_type_id:
            return settings_entry
