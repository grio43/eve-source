#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\primaryButton.py
import abc
import contextlib
import functools
import math
import weakref
import caching
import proper
import signals
import threadutils
import trinity
from carbon.common.script.util.commonutils import StripTags
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
from carbonui.control.button import Button

def optional(value, default):
    if value is not None:
        return value
    return default


def skip_if_destroyed(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.destroyed:
            return
        f(*args, **kwargs)

    return wrapper


class PrimaryButton(Button):
    ARROW_ANIMATION_DURATION = 2.0
    LABEL_PAD_HORIZONTAL = 30
    LABEL_PAD_VERTICAL = 6
    MIN_HEIGHT = 32
    MIN_WIDTH = 64
    RES_ARROWS = 'res:/UI/Texture/Classes/Industry/CenterBar/arrows.png'
    RES_ARROWS_BAR_COUNT = 6
    RES_ARROWS_MASK = 'res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png'
    RES_BUTTON_BACKGROUND = 'res:/UI/Texture/Classes/Industry/CenterBar/buttonBg.png'
    RES_BUTTON_PATTERN = 'res:/UI/Texture/Classes/Industry/CenterBar/buttonPattern.png'
    default_bold = True
    default_fontsize = 13
    default_uppercase = True

    def __init__(self, controller = None, color = None, colorType = None, label = None, func = None, args = None, **kwargs):
        if controller is None:
            controller = self._create_default_controller(label=label, func=func, args=args, color=color, color_type=colorType)
        self.controller = controller
        self._is_updating_label = False
        self._original_args = args
        super(PrimaryButton, self).__init__(func=self.controller.click, args=(), busy=self.controller.is_arrow_animated, **kwargs)
        self._update_enabled()
        self._update_label()
        self.controller.bind(is_arrow_animated=self._update_arrow, is_enabled=self._update_enabled, label=self._update_label_animated)

    def Close(self):
        self.controller.close()
        super(PrimaryButton, self).Close()

    def Disable(self):
        self.controller.is_enabled = False

    def Enable(self):
        self.controller.is_enabled = True

    def SetColor(self, color):
        self.controller.style = FixedColorStyle(color)

    def SetFunc(self, func):
        self.controller.on_clicked = self._create_default_callback(func, self._original_args)

    def SetLabel(self, text):
        super(PrimaryButton, self).SetLabel(text)

    def Update_Size_(self):
        super(PrimaryButton, self).Update_Size_()

    def _align_text(self, text):
        return StripTags(text, stripOnly=['center'])

    def _create_default_controller(self, label, color, color_type, func, args):
        controller = PrimaryButtonController(label=label, style=self._create_default_style(color, color_type))
        controller.on_clicked = self._create_default_callback(func, args)
        return controller

    def _create_default_callback(self, function, arguments):
        if function is None:
            return
        elif isinstance(arguments, tuple):
            return functools.partial(function, *arguments)
        elif arguments is not None:
            return functools.partial(function, arguments)
        else:
            return functools.partial(function, weakref.proxy(self))

    def _create_default_style(self, color, color_type):
        if color is not None:
            return FixedColorStyle(base_color=color)
        else:
            return ThemeColorStyle(color_type)

    @skip_if_destroyed
    def _update_arrow(self, *args):
        self.busy = self.controller.is_arrow_animated

    @skip_if_destroyed
    def _update_enabled(self, *args):
        self.enabled = self.controller.is_enabled

    @skip_if_destroyed
    def _update_label(self):
        if self._is_updating_label:
            return
        self.SetLabel(self.controller.label)

    @threadutils.threaded
    @skip_if_destroyed
    def _update_label_animated(self, *args):
        self.label = self.controller.label


class PrimaryButtonStyle(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def color_arrow(self):
        pass

    @abc.abstractproperty
    def color_frame(self):
        pass

    @abc.abstractproperty
    def color_highlight(self):
        pass

    @abc.abstractproperty
    def color_label(self):
        pass

    @abc.abstractproperty
    def color_underlay(self):
        pass

    @caching.lazy_property
    def on_update(self):
        return signals.Signal(signalName='on_update')


def rgba_color(color):
    return Color(*color).GetRGBA()


class FixedColorStyle(proper.Observable, PrimaryButtonStyle):
    default_base_color = Color.GRAY2

    def __init__(self, **kwargs):
        super(FixedColorStyle, self).__init__(**kwargs)

    @proper.ty(coerce=rgba_color)
    def base_color(self):
        pass

    def on_base_color(self, color):
        self.on_update()

    @proper.alias
    def color_arrow(self):
        return clamp_color_brightness(self.base_color, brightness_min=0.4)

    @proper.alias
    def color_frame(self):
        return clamp_color_brightness(self.base_color, brightness_min=0.1)

    @proper.alias
    def color_highlight(self):
        return clamp_color_brightness(self.base_color, 0.1, 0.2)

    @proper.alias
    def color_label(self):
        return clamp_color_saturation(clamp_color_brightness(self.base_color, brightness_min=1.0), saturation_max=0.1)

    @proper.alias
    def color_underlay(self):
        return clamp_color_brightness(self.base_color, 0.1, 0.6)


def clamp_color_brightness(color, brightness_min = 0.0, brightness_max = 1.0):
    color = Color(*color)
    color.SetBrightness(max(brightness_min, min(color.GetBrightness(), brightness_max)))
    return color.GetRGBA()


def clamp_color_saturation(color, saturation_min = 0.0, saturation_max = 1.0):
    color = Color(*color)
    color.SetSaturation(max(saturation_min, min(color.GetSaturation(), saturation_max)))
    return color.GetRGBA()


class ThemeColorStyle(FixedColorStyle):

    def __init__(self, color_type = None):
        self._color_type = color_type or uiconst.COLORTYPE_UIHILIGHT
        super(ThemeColorStyle, self).__init__(base_color=self._get_theme_color())

    @property
    def color_type(self):
        return self._color_type

    @property
    def ui_color_service(self):
        return sm.GetService('uiColor')

    def _get_theme_color(self):
        return self.ui_color_service.GetUIColor(self.color_type)

    def UpdateColor(self):
        self.base_color = self._get_theme_color()


class PrimaryButtonController(proper.Observable):
    default_is_arrow_animated = False
    default_is_enabled = True
    default_label = None

    def __init__(self, **kwargs):
        super(PrimaryButtonController, self).__init__(**kwargs)
        self._is_clicking = False
        self.style.on_update.connect(self.on_style_update)

    @proper.ty(coerce=bool)
    def is_arrow_animated(self):
        pass

    @proper.ty(coerce=bool)
    def is_enabled(self):
        pass

    @proper.ty(default=False, coerce=bool)
    def is_hovered(self):
        pass

    @proper.ty
    def label(self):
        pass

    @proper.ty
    def style(self):
        pass

    @style.before_change
    def _reconnect_style_signal(self, style):
        self.style.on_update.disconnect(self.on_style_update)
        style.on_update.connect(self.on_style_update)

    @style.default
    def style_default(self):
        return self.default_style

    @caching.lazy_property
    def default_style(self):
        return ThemeColorStyle()

    def on_style_update(self):
        self.dispatch('style')

    @contextlib.contextmanager
    def arrow_animated(self):
        was_arrow_animated = self.is_arrow_animated
        self.is_arrow_animated = True
        try:
            yield
        finally:
            if self.is_arrow_animated:
                self.is_arrow_animated = was_arrow_animated

    def click(self):
        if self._is_clicking:
            return
        self._is_clicking = True
        try:
            self.on_clicked()
        finally:
            self._is_clicking = False

    def close(self):
        self.unbind_all()

    def on_clicked(self):
        pass
