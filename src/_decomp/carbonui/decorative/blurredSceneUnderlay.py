#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\blurredSceneUnderlay.py
import mathext
import telemetry
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from carbonui.window.settings import only_tint_active_window
from chroma import Color
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.services.uiColorSettings import show_window_bg_blur_setting, window_transparency_light_mode_setting, window_transparency_noblur_setting, window_transparency_setting
from eve.client.script.ui.shared.systemMenu.theme.feature_flag import is_only_tint_active_window_setting_enabled
from evegraphics import settings as gfxsettings
BRIGHTNESS_IDLE = 0.3
BRIGHTNESS_IN_FOCUS = 0.2
BRIGHTNESS_LIGHT_IDLE = 0.85
BRIGHTNESS_LIGHT_IN_FOCUS = 0.5
DEFAULT_BRIGHTNESS = 0.04
SATURATION_MULTIPLIER_MAX = 0.3

class BlurredSceneUnderlay(Sprite):
    default_name = 'BlurredSceneUnderlay'
    default_color = (DEFAULT_BRIGHTNESS,
     DEFAULT_BRIGHTNESS,
     DEFAULT_BRIGHTNESS,
     1.0)
    default_effectOpacity = 0.5
    default_saturation = 0.5
    default_opacity = 1.0
    default_state = uiconst.UI_DISABLED
    default_spriteEffect = trinity.TR2_SFX_BLURBACKGROUNDCOLORED
    default_isLightBackground = False
    __notifyevents__ = ['OnBlurredBufferCreated', 'OnGraphicSettingsChanged', 'OnUIColorsChanged']

    def OnColorThemeChanged(self):
        super(BlurredSceneUnderlay, self).OnColorThemeChanged()
        self.UpdateColor()

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        super(BlurredSceneUnderlay, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        isWindowActive = uicore.registry.GetActive() == GetWindowAbove(self)
        self.isInFocus = attributes.Get('isInFocus', isWindowActive)
        self.isLightBackground = attributes.Get('isLightBackground', self.default_isLightBackground)
        self.isCameraDragging = False
        if uicore.uilib.blurredBackBufferAtlas:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
        trinity.device.RegisterResource(self)
        self.UpdateState(animate=False)
        window_transparency_light_mode_setting.on_change.connect(self.OnLightBackgroundTransparencySettingChanged)
        if is_only_tint_active_window_setting_enabled():
            only_tint_active_window.on_change.connect(self._on_only_tint_active_window_changed)

    def OnCreate(self, *args):
        pass

    def OnLightBackgroundTransparencySettingChanged(self, *args):
        self.UpdateState()

    def OnGraphicSettingsChanged(self, *args):
        self.UpdateState()

    def OnUIColorsChanged(self, *args):
        self.UpdateState()

    def OnWindowAboveSetActive(self):
        self.AnimEntry()

    def OnWindowAboveSetInactive(self):
        self.AnimExit()

    def OnBlurredBufferCreated(self, *args):
        if not self.destroyed:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas

    def AnimateEffectTo(self, value):
        uicore.animations.MorphScalar(self, 'effectOpacity', self.effectOpacity, value, curveType=uiconst.ANIM_LINEAR, duration=0.3)

    def AnimateBrightnessTo(self, value):
        uicore.animations.MorphScalar(self, 'saturation', self.saturation, value, curveType=uiconst.ANIM_LINEAR, duration=0.3)

    def AnimateOpacityTo(self, value):
        uicore.animations.FadeTo(self, self.opacity, value, curveType=uiconst.ANIM_LINEAR, duration=0.3)

    def AnimEntry(self):
        self.isInFocus = True
        self.UpdateState()

    def AnimExit(self):
        self.isInFocus = False
        self.UpdateState()

    def GetTransparencySetting(self):
        if show_window_bg_blur_setting.is_enabled():
            return window_transparency_setting.get()
        else:
            return window_transparency_noblur_setting.get()

    def UpdateStateBlurEnabled(self, animate = True):
        self.opacity = self.GetOpacityValue()
        self._GetSpriteEffect()
        effectOpacity = self._GetEffectOpacity()
        brightness = self._GetBrightness()
        if animate:
            self.AnimateEffectTo(effectOpacity)
            self.AnimateBrightnessTo(brightness)
        else:
            self.effectOpacity = effectOpacity
            self.saturation = brightness

    def GetOpacityValue(self):
        return self.default_opacity

    def _GetSpriteEffect(self):
        self.spriteEffect = trinity.TR2_SFX_BLURBACKGROUND

    def _GetBrightness(self):
        brightness = BRIGHTNESS_IN_FOCUS if self.isInFocus else BRIGHTNESS_IDLE
        brightness = mathext.lerp(0.0, brightness, self.GetTransparencySetting())
        if self.IsLightBackground():
            lBrightness = BRIGHTNESS_LIGHT_IN_FOCUS if self.isInFocus else BRIGHTNESS_LIGHT_IDLE
            brightness = mathext.lerp(brightness, lBrightness, window_transparency_light_mode_setting.get())
        return brightness

    def _GetEffectOpacity(self):
        if self.isInFocus:
            effectOpacity = 1.2
        elif self.IsLightBackground():
            effectOpacity = 1.0
        else:
            effectOpacity = 0.75
        return effectOpacity

    def UpdateStateBlurDisabled(self, animate = True):
        opacity = self._GetBlurDisabledOpacity()
        if animate:
            self.AnimateOpacityTo(opacity)
        else:
            self.opacity = opacity
        self.spriteEffect = trinity.TR2_SFX_FILL

    def _GetBlurDisabledOpacity(self):
        opacity = 0.95 if self.isInFocus else 0.75
        opacity = mathext.lerp(1.0, opacity, self.GetTransparencySetting())
        if self.IsLightBackground():
            lOpacity = 0.7 if self.isInFocus else 0.3
            opacity = mathext.lerp(opacity, lOpacity, window_transparency_light_mode_setting.get())
        return opacity

    @telemetry.ZONE_METHOD
    def UpdateState(self, animate = True):
        if self._IsBlurEnabled():
            self.UpdateStateBlurEnabled(animate)
        else:
            self.UpdateStateBlurDisabled(animate)
        self.UpdateColor()

    def _IsBlurEnabled(self):
        gfxQualitySupportsBlur = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) > gfxsettings.SHADER_MODEL_LOW
        return gfxQualitySupportsBlur and show_window_bg_blur_setting.is_enabled()

    def UpdateColor(self):
        if is_only_tint_active_window_setting_enabled() and only_tint_active_window.is_enabled():
            base_color = Color.from_rgba(*(eveThemeColor.THEME_TINT if self.isInFocus else self.default_color))
        else:
            base_color = Color.from_rgba(*eveThemeColor.THEME_TINT)
        t = self.GetTransparencySetting() if self._IsBlurEnabled() else 0.0
        s = SATURATION_MULTIPLIER_MAX + (1.0 - SATURATION_MULTIPLIER_MAX) * t
        final_color = Color.from_hsb(h=base_color.hue, s=base_color.saturation * s, b=base_color.brightness)
        self.SetRGB(*final_color.rgb)

    def IsLightBackground(self):
        return self.isLightBackground

    def EnableLightBackground(self, animate = True):
        self.isLightBackground = True
        self.UpdateState(animate)

    def DisableLightBackground(self, animate = True):
        self.isLightBackground = False
        self.UpdateState(animate)

    def _on_only_tint_active_window_changed(self, value):
        self.UpdateColor()
