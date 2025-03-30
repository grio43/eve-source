#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chroma\color.py
from __future__ import division
import collections
import mathext
from chroma.conversion import hsb_to_rgb, rgb_to_hsb

class Color(collections.Sequence):

    def __init__(self, r, g, b, a = 1.0):
        for arg in (r,
         g,
         b,
         a):
            if not isinstance(arg, (float, int)):
                raise TypeError('Color components should be floats, not {}'.format(type(arg).__name__))

        self._r = float(r)
        self._g = float(g)
        self._b = float(b)
        self._a = float(a)

    @classmethod
    def from_rgba(cls, r, g, b, a = 1.0):
        return cls(r, g, b, a)

    @classmethod
    def from_rgba_8bit(cls, r, g, b, a = 255):
        return cls(mathext.clamp(r, 0, 255) / 255, mathext.clamp(g, 0, 255) / 255, mathext.clamp(b, 0, 255) / 255, mathext.clamp(a, 0, 255) / 255)

    @classmethod
    def from_hex(cls, value):
        if not isinstance(value, (str, unicode)):
            raise ValueError('Hex color value must be a string')
        if value.startswith('#'):
            value = value[1:]
        if len(value) == 8:
            a = int(value[0:2], 16) / 255
            r = int(value[2:4], 16) / 255
            g = int(value[4:6], 16) / 255
            b = int(value[6:8], 16) / 255
        elif len(value) == 6:
            a = 1.0
            r = int(value[0:2], 16) / 255
            g = int(value[2:4], 16) / 255
            b = int(value[4:6], 16) / 255
        elif len(value) == 3:
            a = 1.0
            r = int(value[0] * 2, 16) / 255
            g = int(value[1] * 2, 16) / 255
            b = int(value[2] * 2, 16) / 255
        else:
            raise ValueError('Invalid hex color value provided: {!r}'.format(value))
        return cls(r, g, b, a)

    @classmethod
    def from_hsb(cls, h, s, b, a = 1.0):
        red, green, blue = hsb_to_rgb(h, s, b)
        return cls(red, green, blue, a)

    @classmethod
    def from_any(cls, value):
        if isinstance(value, Color) or hasattr(value, 'rgba'):
            return cls(*value.rgba)
        if isinstance(value, (str, unicode)):
            return cls.from_hex(value)
        try:
            return cls(*value)
        except Exception:
            pass

        raise ValueError('Unknown color value: {!r}'.format(value))

    @property
    def r(self):
        return self._r

    @property
    def red(self):
        return self._r

    @property
    def g(self):
        return self._g

    @property
    def green(self):
        return self._g

    @property
    def b(self):
        return self._b

    @property
    def blue(self):
        return self._b

    @property
    def a(self):
        return self._a

    @property
    def alpha(self):
        return self._a

    @property
    def opacity(self):
        return self._a

    @property
    def rgb(self):
        return (self._r, self._g, self._b)

    @property
    def rgb_8bit(self):
        return (int(round(self._r * 255.0)), int(round(self._g * 255.0)), int(round(self._b * 255.0)))

    @property
    def rgba(self):
        return (self._r,
         self._g,
         self._b,
         self._a)

    @property
    def rgba_8bit(self):
        return (int(round(self._r * 255.0)),
         int(round(self._g * 255.0)),
         int(round(self._b * 255.0)),
         int(round(self._a * 255.0)))

    @property
    def hex_argb(self):
        r, g, b, a = self.rgba_8bit
        return u'#{:02x}{:02x}{:02x}{:02x}'.format(a, r, g, b)

    @property
    def hex_rgb(self):
        return u'#{:02x}{:02x}{:02x}'.format(*self.rgb_8bit)

    @property
    def hsb(self):
        return rgb_to_hsb(self._r, self._g, self._b)

    @property
    def hue(self):
        hue, _, _ = rgb_to_hsb(self._r, self._g, self._b)
        return hue

    @property
    def saturation(self):
        _, saturation, _ = rgb_to_hsb(self._r, self._g, self._b)
        return saturation

    @property
    def brightness(self):
        _, _, brightness = rgb_to_hsb(self._r, self._g, self._b)
        return brightness

    @property
    def is_grayscale(self):
        _, saturation, _ = self.hsb
        return mathext.is_almost_zero(saturation)

    def as_argb_int32(self):
        return int(round(mathext.clamp(self._a, 0.0, 1.0) * 255)) << 24 | int(round(mathext.clamp(self._r, 0.0, 1.0) * 255)) << 16 | int(round(mathext.clamp(self._g, 0.0, 1.0) * 255)) << 8 | int(round(mathext.clamp(self._b, 0.0, 1.0) * 255))

    def with_red(self, red):
        return Color(red, self._g, self._b, self._a)

    def with_green(self, green):
        return Color(self._r, green, self._b, self._a)

    def with_blue(self, blue):
        return Color(self._r, self._g, blue, self._a)

    def with_alpha(self, alpha):
        return Color(self._r, self._g, self._b, alpha)

    def with_hue(self, hue):
        hue = mathext.clamp(hue, 0.0, 1.0)
        _, saturation, brightness = rgb_to_hsb(self._r, self._g, self._b)
        r, g, b = hsb_to_rgb(hue, saturation, brightness)
        return Color(r, g, b, a=self._a)

    def with_saturation(self, saturation):
        saturation = mathext.clamp(saturation, 0.0, 1.0)
        hue, _, brightness = rgb_to_hsb(self._r, self._g, self._b)
        r, g, b = hsb_to_rgb(hue, saturation, brightness)
        return Color(r, g, b, a=self._a)

    def with_brightness(self, brightness):
        brightness = mathext.clamp(brightness, 0.0, 1.0)
        hue, saturation, _ = rgb_to_hsb(self._r, self._g, self._b)
        r, g, b = hsb_to_rgb(hue, saturation, brightness)
        return Color(r, g, b, a=self._a)

    def __eq__(self, other):
        if not isinstance(other, Color):
            try:
                other = Color.from_any(other)
            except ValueError:
                return NotImplemented

        return mathext.is_close(self._r, other.r) and mathext.is_close(self._g, other.g) and mathext.is_close(self._b, other.b) and mathext.is_close(self._a, other.a)

    def __ne__(self, other):
        if not isinstance(other, Color):
            try:
                other = Color.from_any(other)
            except ValueError:
                return NotImplemented

        return not mathext.is_close(self._r, other.r) or not mathext.is_close(self._g, other.g) or not mathext.is_close(self._b, other.b) or not mathext.is_close(self._a, other.a)

    def __hash__(self):
        return hash(self.rgba)

    def __str__(self):
        return self.hex_argb

    def __repr__(self):
        return u'Color(r={!r}, g={!r}, b={!r}, a={!r})'.format(*self.rgba)

    def __getitem__(self, item):
        return self.rgba[item]

    def __len__(self):
        return 4
