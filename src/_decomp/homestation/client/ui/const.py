#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\ui\const.py
import carbonui
from eve.client.script.ui import eveColor

class Padding(object):
    slim = 4
    normal = 8
    wide = 16
    section = 24


class TextColor(object):
    main = carbonui.TextColor.NORMAL
    secondary = carbonui.TextColor.SECONDARY


class Color(object):
    info = eveColor.CRYO_BLUE
    warning = eveColor.WARNING_ORANGE
    error = eveColor.DANGER_RED
    home_station = eveColor.CRYO_BLUE
    home_station_icon_background = home_station


PAGE_WIDTH_MAX = 480
BIG_BUTTON_HEIGHT = 32
