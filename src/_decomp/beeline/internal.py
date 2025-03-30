#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\beeline\internal.py
import beeline

def send_event():
    bl = beeline.get_beeline()
    if bl:
        return bl.send_event()


def send_all():
    bl = beeline.get_beeline()
    if bl:
        return bl.send_all()


def log(msg, *args, **kwargs):
    bl = beeline.get_beeline()
    if bl:
        bl.log(msg, *args, **kwargs)


def stringify_exception(e):
    try:
        return str(e)
    except UnicodeEncodeError:
        try:
            return u'{}'.format(e)
        except Exception:
            return 'unable to decode exception'
