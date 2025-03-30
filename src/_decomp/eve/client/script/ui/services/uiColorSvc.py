#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\uiColorSvc.py
import logging
import chroma
import evetypes
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.services import uiColorThemeMixer, uiColorSettings
from eve.client.script.ui.shared import colorThemes
from eve.client.script.ui.shared.systemMenu.theme.storage import custom_color_themes
from eveexceptions.exceptionEater import ExceptionEater
logger = logging.getLogger(__name__)

class UIColor(Service):
    __guid__ = 'svc.uiColor'
    __servicename__ = 'uiColor'
    __displayname__ = 'UI Color Service'
    __startupdependencies__ = ['settings']
    __notifyevents__ = ['OnSessionChanged', 'OnSubscriptionChanged', 'ProcessActiveShipChanged']
    _noCharThemeID = colorThemes.DEFAULT_COLORTHEMEID
    _themeOverride = None

    def Run(self, memStream = None):
        self._noCharThemeID = colorThemes.DEFAULT_COLORTHEMEID
        self._ResetColorCache()
        self.TriggerUpdate()
        uiColorSettings.window_transparency_setting.on_change.connect(self._OnWindowTransparencyChanged)
        uiColorSettings.window_transparency_light_mode_setting.on_change.connect(self._OnWindowTransparencyChanged)
        uiColorSettings.window_transparency_noblur_setting.on_change.connect(self._OnWindowTransparencyChanged)
        uiColorSettings.show_window_bg_blur_setting.on_change.connect(self._OnWindowBlurSettingChanged)

    def _OnWindowTransparencyChanged(self, *args):
        self.TriggerUpdate()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'userid' in change or 'charid' in change:
            self.TriggerUpdate()
        self.SelectThemeFromShip()

    def OnSubscriptionChanged(self):
        self.TriggerUpdate()

    def _OnWindowBlurSettingChanged(self, *args):
        self.TriggerUpdate()

    def ProcessActiveShipChanged(self, *args):
        self.SelectThemeFromShip()

    def SelectThemeFromShip(self):
        if uiColorSettings.color_theme_by_ship_faction_setting.is_enabled():
            with ExceptionEater('SelectThemeFromShip'):
                typeID = sm.GetService('fleet').GetMyShipTypeID()
                if typeID:
                    themeID = colorThemes.COLOR_THEME_ID_BY_FACTION.get(evetypes.GetFactionID(typeID), None)
                    if themeID:
                        self.SetThemeID(themeID)

    def GetThemeIDForSessionRaceID(self):
        return colorThemes.COLOR_THEME_ID_BY_RACE.get(session.raceID, colorThemes.DEFAULT_COLORTHEMEID)

    def SetNoCharTheme(self, themeID):
        self._noCharThemeID = themeID
        self.TriggerUpdate()

    def SetThemeID(self, themeID):
        if themeID is None:
            raise ValueError('themeID is None')
        activeThemeID = self.GetActiveThemeID()
        settings.char.windows.Set('wndColorThemeID', themeID)
        settings.char.windows.Set('baseColorTemp', None)
        settings.char.windows.Set('hiliteColorTemp', None)
        if activeThemeID != themeID:
            self.TriggerUpdate()

    def _GetBaseColor(self):
        if self._colorBase:
            return self._colorBase
        color = settings.char.windows.Get('baseColorTemp', None)
        if color:
            return color
        colorBase = self.GetActiveTheme().tint
        self._colorBase = uiColorThemeMixer.GetBaseColor(colorBase)
        return self._colorBase

    def SetBaseColor(self, color):
        settings.char.windows.Set('baseColorTemp', color)
        self.TriggerUpdate()

    def _GetHilightColor(self):
        if self._colorHilite:
            return self._colorHilite
        color = settings.char.windows.Get('hiliteColorTemp', None)
        if color:
            return color
        self._colorHilite = self.GetActiveTheme().focus
        return self._colorHilite

    def _GetHilightGlowColor(self):
        if self._colorHiliteGlow:
            return self._colorHiliteGlow
        self._colorHiliteGlow = uiColorThemeMixer.GetHilightGlowColor(self._GetHilightColor())
        return self._colorHiliteGlow

    def _GetFlashColor(self):
        if self._colorFlash:
            return self._colorFlash
        self._colorFlash = uiColorThemeMixer.GetFlashColor(self._GetHilightColor())
        return self._colorFlash

    def _GetAccentColor(self):
        return self.GetActiveTheme().focus

    def SetHilightColor(self, color):
        settings.char.windows.Set('hiliteColorTemp', color)
        self.TriggerUpdate()

    def _GetBaseContrastColor(self):
        if self._colorBaseContrast:
            return self._colorBaseContrast
        color = chroma.Color.from_rgba(*eveColor.WHITE).with_alpha(0.05).rgba
        color = uiColorThemeMixer.GetBaseContrastColor(color)
        self._colorBaseContrast = color
        return self._colorBaseContrast

    def GetUIColor(self, colorType):
        if colorType == uiconst.COLORTYPE_UIBASE:
            color = self._GetBaseColor()
        elif colorType == uiconst.COLORTYPE_UIBASECONTRAST:
            color = self._GetBaseContrastColor()
        elif colorType == uiconst.COLORTYPE_UIHILIGHT:
            color = self._GetHilightColor()
        elif colorType == uiconst.COLORTYPE_UIHILIGHTGLOW:
            color = self._GetHilightGlowColor()
        elif colorType == uiconst.COLORTYPE_FLASH:
            color = self._GetFlashColor()
        elif colorType == uiconst.COLORTYPE_ACCENT:
            color = self._GetAccentColor()
        else:
            return None
        if hasattr(color, 'rgba'):
            return color.rgba
        else:
            return color

    def _ResetColorCache(self):
        self._colorBase = None
        self._colorBaseContrast = None
        self._colorHilite = None
        self._colorHiliteGlow = None
        self._colorHeader = None
        self._colorFlash = None

    def TriggerUpdate(self):
        self._ResetColorCache()
        theme = self.GetActiveTheme()
        eveThemeColor.SetThemeColors(tint=theme.tint, focus=theme.focus, focus_dark=theme.focus_dark, accent=theme.accent, alert=theme.alert)
        sm.ScatterEvent('OnUIColorsChanged')

    def ResetUIColors(self):
        if session.charid:
            settings.char.windows.Set('wndColorThemeID', colorThemes.DEFAULT_COLORTHEMEID)
        uiColorSettings.color_theme_by_ship_faction_setting.reset()
        uiColorSettings.window_transparency_setting.reset()
        uiColorSettings.window_transparency_noblur_setting.reset()
        self.TriggerUpdate()

    def GetThemeBaseColor(self, themeID):
        return self.GetThemeByID(themeID).tint

    def GetThemeHiliteColor(self, themeID):
        return self.GetThemeByID(themeID).focus

    def GetThemeName(self, themeID):
        return self.GetThemeByID(themeID).name

    def GetActiveTheme(self):
        return self.GetThemeByID(self._GetActiveThemeID())

    def GetActiveThemeID(self):
        return self.GetActiveTheme().id

    def GetAvailableThemes(self):
        return self._GetAvailableThemesByID().values()

    def GetThemeByID(self, themeID):
        if self._themeOverride is not None and self._themeOverride.id == themeID:
            return self._themeOverride
        available = self._GetAvailableThemesByID()
        theme = available.get(themeID, None)
        if theme is None:
            theme = available[colorThemes.DEFAULT_COLORTHEMEID]
        return theme

    def SetThemeOverride(self, theme):
        if self._themeOverride != theme:
            self._themeOverride = theme
            self.TriggerUpdate()

    def ClearThemeOverride(self):
        self.SetThemeOverride(None)

    def SaveCustomTheme(self, theme):
        if theme.is_preset:
            raise ValueError("Can't override preset color themes")
        with custom_color_themes.modify() as custom_themes:
            custom_themes.add_or_update(theme)

    def DeleteCustomTheme(self, theme):
        if self.GetActiveThemeID() == theme.id:
            self.SetThemeID(colorThemes.DEFAULT_COLORTHEMEID)
        with custom_color_themes.modify() as custom_themes:
            try:
                custom_themes.remove(theme)
            except Exception:
                logger.warning('Unable to remove theme with ID {}'.format(theme.id))

    def _GetActiveThemeID(self):
        if self._themeOverride is not None:
            return self._themeOverride.id
        if not session.charid:
            themeID = self._noCharThemeID
        else:
            themeID = settings.char.windows.Get('wndColorThemeID', self.GetThemeIDForSessionRaceID())
            if sm.GetService('cloneGradeSvc').IsOmega():
                if themeID not in self._GetAvailableThemesByID():
                    themeID = colorThemes.DEFAULT_COLORTHEMEID
            elif themeID not in self._GetAvailableThemesForAlphaByID():
                themeID = colorThemes.ALPHA_COLORTHEMEID
        return themeID

    def _GetAvailableThemesByID(self):
        themes = {theme.id:theme for theme in colorThemes.COLOR_THEME_PRESETS}
        themes.update(custom_color_themes.get().themes_by_id)
        return themes

    def _GetAvailableThemesForAlphaByID(self):
        return {theme.id:theme for theme in filter(lambda t: not t.omega_only, colorThemes.COLOR_THEME_PRESETS)}
