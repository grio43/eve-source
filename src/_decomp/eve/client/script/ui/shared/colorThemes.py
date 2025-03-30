#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\colorThemes.py
import carbonui
import localization
from eve.common.lib import appConst

class ColorTheme(object):

    def __init__(self, theme_id, name, tint, focus, focus_dark, accent, alert, omega_only = True):
        self._id = theme_id
        self._name = name
        self._tint = carbonui.Color.from_any(tint)
        self._focus = carbonui.Color.from_any(focus)
        self._focus_dark = carbonui.Color.from_any(focus_dark)
        self._accent = carbonui.Color.from_any(accent)
        self._alert = carbonui.Color.from_any(alert)
        self._omega_only = omega_only

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        if callable(self._name):
            return self._name()
        return self._name

    @property
    def tint(self):
        return self._tint

    @property
    def focus(self):
        return self._focus

    @property
    def focus_dark(self):
        return self._focus_dark

    @property
    def accent(self):
        return self._accent

    @property
    def alert(self):
        return self._alert

    @property
    def is_preset(self):
        return self.id in COLOR_THEME_PRESET_BY_ID

    @property
    def omega_only(self):
        return self._omega_only

    def copy_with(self, theme_id = None, name = None, tint = None, focus = None, focus_dark = None, accent = None, alert = None):
        return ColorTheme(theme_id=theme_id if theme_id is not None else self.id, name=name if name is not None else self.name, tint=tint if tint is not None else self.tint, focus=focus if focus is not None else self.focus, focus_dark=focus_dark if focus_dark is not None else self.focus_dark, accent=accent if accent is not None else self.accent, alert=alert if alert is not None else self.alert)

    def __eq__(self, other):
        return isinstance(other, ColorTheme) and self.id == other.id and self.name == other.name and self.tint.hex_argb == other.tint.hex_argb and self.focus.hex_argb == other.focus.hex_argb and self.focus_dark.hex_argb == other.focus_dark.hex_argb and self.accent.hex_argb == other.accent.hex_argb and self.alert.hex_argb == other.alert.hex_argb

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return u'ColorTheme(theme_id={!r}, name={!r}, tint={!r}, focus={!r}, focus_dark={!r}, accent={!r}, alert={!r})'.format(self.id, self.name, self.tint.hex_argb, self.focus.hex_argb, self.focus_dark.hex_argb, self.accent.hex_argb, self.alert.hex_argb)


COLOR_THEME_PRESETS = (ColorTheme(theme_id='UI/ColorThemes/Photon', name=lambda : localization.GetByLabel('UI/ColorThemes/Photon'), tint='#060a0c', focus='#58A7BF', focus_dark='#305665', accent='#58A7BF', alert='#F39058', omega_only=False),
 ColorTheme(theme_id='UI/ColorThemes/Amarr', name=lambda : localization.GetByLabel('UI/ColorThemes/Amarr'), tint='#07030d', focus='#A38264', focus_dark='#7F6744', accent='#FFEE93', alert='#F39058', omega_only=False),
 ColorTheme(theme_id='UI/ColorThemes/Caldari', name=lambda : localization.GetByLabel('UI/ColorThemes/Caldari'), tint='#030e0e', focus='#9AD2E3', focus_dark='#5790A1', accent='#48C7BF', alert='#DC8C2E', omega_only=False),
 ColorTheme(theme_id='UI/ColorThemes/Gallente', name=lambda : localization.GetByLabel('UI/ColorThemes/Gallente'), tint='#0A090F', focus='#58BF9A', focus_dark='#479377', accent='#6DB09E', alert='#F39058', omega_only=False),
 ColorTheme(theme_id='UI/ColorThemes/Minmatar', name=lambda : localization.GetByLabel('UI/ColorThemes/Minmatar'), tint='#030909', focus='#D05C3B', focus_dark='#9D452D', accent='#9D452D', alert='#F39058', omega_only=False),
 ColorTheme(theme_id='UI/ColorThemes/ORE', name=lambda : localization.GetByLabel('UI/ColorThemes/ORE'), tint='#030805', focus='#DDB825', focus_dark='#8E7100', accent='#55999C', alert='#DE8B78'),
 ColorTheme(theme_id='UI/ColorThemes/SOE', name=lambda : localization.GetByLabel('UI/ColorThemes/SOE'), tint='#070d11', focus='#E55252', focus_dark='#853C3C', accent='#A1DDE0', alert='#C0B337'),
 ColorTheme(theme_id='UI/ColorThemes/Carbon', name=lambda : localization.GetByLabel('UI/ColorThemes/Carbon'), tint='#000000', focus='#e5e5e5', focus_dark='#4d4d4d', accent='#e0e0e0', alert='#F39058'))
COLOR_THEME_PRESET_BY_ID = {theme.id:theme for theme in COLOR_THEME_PRESETS}
DEFAULT_COLORTHEMEID = 'UI/ColorThemes/Photon'
ALPHA_COLORTHEMEID = 'UI/ColorThemes/Photon'
COLOR_THEME_ID_BY_RACE = {appConst.raceCaldari: 'UI/ColorThemes/Caldari',
 appConst.raceMinmatar: 'UI/ColorThemes/Minmatar',
 appConst.raceAmarr: 'UI/ColorThemes/Amarr',
 appConst.raceGallente: 'UI/ColorThemes/Gallente'}
COLOR_THEME_ID_BY_FACTION = {appConst.factionAmarrEmpire: 'UI/ColorThemes/Amarr',
 appConst.factionCaldariState: 'UI/ColorThemes/Caldari',
 appConst.factionGallenteFederation: 'UI/ColorThemes/Gallente',
 appConst.factionMinmatarRepublic: 'UI/ColorThemes/Minmatar',
 appConst.factionORE: 'UI/ColorThemes/ORE',
 appConst.factionGuristasPirates: 'UI/ColorThemes/Guristas',
 appConst.factionSanshasNation: 'UI/ColorThemes/SanshasNation',
 appConst.factionTheBloodRaiderCovenant: 'UI/ColorThemes/BloodRaiders',
 appConst.factionAngelCartel: 'UI/ColorThemes/AngelCartel',
 appConst.factionSerpentis: 'UI/ColorThemes/Serpentis',
 appConst.factionSistersOfEVE: 'UI/ColorThemes/SOE',
 appConst.factionMordusLegion: 'UI/ColorThemes/MordusLegion'}
