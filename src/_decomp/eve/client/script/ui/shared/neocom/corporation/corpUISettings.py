#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\corpUISettings.py
from carbonui.services.setting import CharSettingEnum, CharSettingBool
from eve.client.script.ui.shared.neocom.corporation.corpPanelConst import CorpPanel
corp_window_selected_panel_setting = CharSettingEnum('corpWindowSelectedPanel', CorpPanel.MY_CORPORATION, CorpPanel.values())
corp_window_corp_tab_selected_panel_setting = CharSettingEnum('corpWindowCorpTabSelectedPanel', CorpPanel.MY_CORPORATION, CorpPanel.values())
corp_window_alliance_tab_selected_panel_setting = CharSettingEnum('corpWindowAllianceTabSelectedPanel', CorpPanel.ALLIANCES_HOME, CorpPanel.values())
corp_window_admin_tab_selected_panel_setting = CharSettingEnum('corpWindowAdminTabSelectedPanel', None, CorpPanel.values())
corp_side_navigation_always_expanded_setting = CharSettingBool('corpSideNavAlwaysExpanded', True)
