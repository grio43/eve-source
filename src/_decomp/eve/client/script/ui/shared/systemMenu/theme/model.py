#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\theme\model.py
import uuid

def generate_theme_id():
    return str(uuid.uuid4())


def focus_dark_from_focus(color):
    return color.with_brightness(color.brightness * 0.5)
