#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\bracketSettings.py
from carbonui.services.setting import SessionSettingEnum, SessionSettingBool
from eve.client.script.parklife import bracketConst
bracket_display_override_setting = SessionSettingEnum(bracketConst.SHOW_DEFAULT, bracketConst.SHOW_OPTIONS)
bracket_showing_specials_setting = SessionSettingBool(False)

def toggle_show_no_brackets():
    currValue = bracket_display_override_setting.get()
    value = bracketConst.SHOW_NONE if currValue != bracketConst.SHOW_NONE else bracketConst.SHOW_DEFAULT
    bracket_display_override_setting.set(value)


def toggle_show_all_brackets():
    currValue = bracket_display_override_setting.get()
    value = bracketConst.SHOW_ALL if currValue != bracketConst.SHOW_ALL else bracketConst.SHOW_DEFAULT
    bracket_display_override_setting.set(value)
