#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\regionalui\utils.py
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalWritten
from gametime import MIN
from regionalui.const import ADDICTION_WARNING_TEXT_PATH, SESSION_PLAYTIME_TEXT_PATH

def get_session_playtime():
    try:
        minutes = sm.RemoteSvc('userSvc').GetSessionPlaytimeMinutes()
    except Exception:
        minutes = 0

    return FormatTimeIntervalWritten(minutes * MIN, showFrom='hour', showTo='minute')


def get_addiction_warning_text():
    return GetByLabel(ADDICTION_WARNING_TEXT_PATH)


def get_playtime_text():
    return GetByLabel(SESSION_PLAYTIME_TEXT_PATH, playtime=get_session_playtime().upper())
