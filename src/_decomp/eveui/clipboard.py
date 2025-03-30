#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\clipboard.py
import blue

def get():
    try:
        return blue.clipboard.GetClipboardUnicode()
    except (blue.error, WindowsError):
        return None


def set(text):
    blue.clipboard.SetClipboardData(text)


def is_empty():
    return not bool(get())
