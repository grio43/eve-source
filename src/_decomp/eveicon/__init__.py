#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveicon\__init__.py
from .icon_data import IconData, is_icon_in_library
from .iterate import iter_icons
del icon_data
del iterate
from .icons import *

def get(icon_id, default = None):
    icon = getattr(icons, icon_id, None)
    if icon is None or not isinstance(icon, IconData):
        return default
    else:
        return icon
