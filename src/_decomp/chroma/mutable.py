#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\chroma\mutable.py
from __future__ import division
import collections
import mathext
from chroma.color import Color
COLORS = {'aqua': (240, 248, 255),
 'black': (0, 0, 0),
 'blue': (0, 0, 255),
 'fuchsia': (255, 0, 255),
 'gray': (128, 128, 128),
 'green': (0, 128, 0),
 'lime': (0, 255, 0),
 'maroon': (128, 0, 0),
 'navy': (0, 0, 128),
 'olive': (128, 128, 0),
 'purple': (128, 0, 128),
 'red': (255, 0, 0),
 'silver': (192, 192, 192),
 'teal': (0, 128, 128),
 'white': (255, 255, 255),
 'yellow': (255, 255, 0)}

def _get_rgb_by_name(name):
    return tuple((x / 255.0 for x in COLORS[name]))


class ColorMutable(collections.Sequence):
    COMBINED_KWARGS = [('rgb', [('red', 'r'), ('green', 'g'), ('blue', 'b')]), ('rgba', [('red', 'r'),
       ('green', 'g'),
       ('blue', 'b'),
       ('alpha', 'a')]), ('hsl', [('hue', 'h'), ('saturation', 's'), ('lightness', 'l')])]

    def __init__(self, *args, **kwargs):
        rgb = _get_rgb_by_name('black')
        a = 1.0
        if len(args) == 1:
            args = args[0]
            if isinstance(args, (ColorMutable, Color)):
                args = args.rgba
            elif isinstance(args, (str, unicode)):
                if args in COLORS:
                    args = _get_rgb_by_name(args.lower())
                else:
                    args = hex_to_rgb(args)
            elif isinstance(args, collections.Sequence):
                pass
            else:
                raise TypeError('ColorMutable value should be a color name, hex value, or a Coloror ColorMutable instance')
        if len(args) == 3:
            rgb = tuple(args)
        elif len(args) == 4:
            rgb = tuple(args[:3])
            a = args[3]
        elif args:
            raise ValueError('Invalid number of color components')
        self.rgb = rgb
        self.a = a
        for key, components in self.COMBINED_KWARGS:
            changed = False
            if key in kwargs:
                value = list(kwargs.pop(key))
                changed = True
            else:
                value = list(getattr(self, key))
            for i, names in enumerate(components):
                if len([ name for name in names if name in kwargs ]) > 1:
                    raise TypeError('Duplicate argument found for {}'.format(names[0]))
                for name in names:
                    if name in kwargs:
                        value[i] = kwargs.pop(name)
                        changed = True

            if changed:
                setattr(self, key, value)

        if 'hex' in kwargs:
            self.hex = kwargs.pop('hex')
        if kwargs:
            raise TypeError("'{}' is an invalid keyword argument for this function".format(kwargs.keys()[0]))

    @property
    def red(self):
        return self._rgb[0]

    @red.setter
    def red(self, red):
        if 0.0 > red or red > 1.0:
            raise ValueError('Red should be in the range [0, 1]')
        self._rgb[0] = red

    r = red

    @property
    def green(self):
        return self._rgb[1]

    @green.setter
    def green(self, green):
        if 0.0 > green or green > 1.0:
            raise ValueError('Green should be in the range [0, 1]')
        self._rgb[1] = green

    g = green

    @property
    def blue(self):
        return self._rgb[2]

    @blue.setter
    def blue(self, blue):
        if 0.0 > blue or blue > 1.0:
            raise ValueError('Blue should be in the range [0, 1]')
        self._rgb[2] = blue

    b = blue

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        if 0.0 > alpha or alpha > 1.0:
            raise ValueError('Alpha should be in the range [0, 1]')
        self._alpha = alpha

    a = alpha

    @property
    def rgb(self):
        return tuple(self._rgb)

    @rgb.setter
    def rgb(self, rgb):
        _validate_rgb(rgb)
        self._rgb = list(rgb)

    @property
    def rgba(self):
        r, g, b = self.rgb
        return (r,
         g,
         b,
         self.a)

    @rgba.setter
    def rgba(self, rgba):
        r, g, b, a = rgba
        self.rgb = [r, g, b]
        self.a = a

    @property
    def hsl(self):
        return rgb_to_hsl(self.rgb)

    @hsl.setter
    def hsl(self, hsl):
        self.rgb = hsl_to_rgb(hsl)

    @property
    def hue(self):
        return rgb_to_hsl(self._rgb)[0]

    @hue.setter
    def hue(self, hue):
        if 0.0 > hue or hue > 1.0:
            raise ValueError('Hue should be in the range [0, 1]')
        _, saturation, lightness = self.hsl
        self.hsl = (hue, saturation, lightness)

    h = hue

    @property
    def saturation(self):
        return rgb_to_hsl(self._rgb)[1]

    @saturation.setter
    def saturation(self, saturation):
        print 'set s to', saturation
        if 0.0 > saturation or saturation > 1.0:
            raise ValueError('Saturation should be in the range [0, 1]')
        hue, _, lightness = self.hsl
        self.hsl = (hue, saturation, lightness)

    s = saturation

    @property
    def lightness(self):
        return rgb_to_hsl(self._rgb)[2]

    @lightness.setter
    def lightness(self, lightness):
        if 0.0 > lightness or lightness > 1.0:
            raise ValueError('Lightness should be in the range [0, 1]')
        hue, saturation, _ = self.hsl
        self.hsl = (hue, saturation, lightness)

    l = lightness

    @property
    def hex(self):
        return _rgb_to_hex(self.rgb)

    @hex.setter
    def hex(self, hex):
        self.rgb = hex_to_rgb(hex)

    @property
    def hex_rgba(self):
        r, g, b, a = map(lambda x: int(round(x * 255.0)), self.rgba)
        return u'#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)

    @property
    def hex_argb(self):
        r, g, b, a = map(lambda x: int(round(x * 255.0)), self.rgba)
        return u'#{:02x}{:02x}{:02x}{:02x}'.format(a, r, g, b)

    def __eq__(self, other):
        if isinstance(other, ColorMutable):
            return self.hex == other.hex
        return NotImplemented

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return equal
        return not equal

    def __str__(self):
        return self.hex

    def __repr__(self):
        return '<chroma.ColorMutable {}>'.format(self.hex)

    def __getitem__(self, item):
        return self.rgba[item]

    def __len__(self):
        return len(self.rgba)


def _validate_rgb(rgb):
    r, g, b = rgb
    for name, value in {'Red': r,
     'Green': g,
     'Blue': b}.items():
        if value > 1.0 or value < 0.0:
            raise ValueError('{name} must be between 0 and 1. You provided {value}.'.format(name=name, value=value))


def rgb_to_hsl(rgb):
    _validate_rgb(rgb)
    r, g, b = [ float(value) for value in rgb ]
    value_min = min(r, g, b)
    value_max = max(r, g, b)
    diff = value_max - value_min
    value_sum = value_min + value_max
    lightness = value_sum / 2
    if mathext.is_close(diff, 0.0, abs_tol=1e-07):
        return (0.0, 0.0, lightness)
    if lightness < 0.5:
        saturation = diff / value_sum
    else:
        saturation = diff / (2.0 - value_sum)
    dr = ((value_max - r) / 6 + diff / 2) / diff
    dg = ((value_max - g) / 6 + diff / 2) / diff
    db = ((value_max - b) / 6 + diff / 2) / diff
    if r == value_max:
        hue = db - dg
    elif g == value_max:
        hue = 0.3333333333333333 + dr - db
    elif b == value_max:
        hue = 0.6666666666666666 + dg - dr
    if hue < 0:
        hue += 1
    if hue > 1:
        hue -= 1
    return (hue, saturation, lightness)


def hsl_to_rgb(hsl):
    h, s, l = [ float(value) for value in hsl ]
    for name, value in {'Hue': h,
     'Saturation': s,
     'Lightness': l}.items():
        if value < 0.0 or 1.0 < value:
            raise ValueError('{} must be between 0 and 1'.format(name))

    if mathext.is_close(s, 0.0, abs_tol=1e-07):
        return (l, l, l)
    if l < 0.5:
        v2 = l * (1.0 + s)
    else:
        v2 = l + s - s * l
    v1 = 2.0 * l - v2
    r = _hue_to_rgb(v1, v2, h + 0.3333333333333333)
    g = _hue_to_rgb(v1, v2, h)
    b = _hue_to_rgb(v1, v2, h - 0.3333333333333333)
    return (r, g, b)


def _hue_to_rgb(v1, v2, vH):
    while vH < 0:
        vH += 1

    while vH > 1:
        vH -= 1

    if 6 * vH < 1:
        return v1 + (v2 - v1) * 6 * vH
    if 2 * vH < 1:
        return v2
    if 3 * vH < 2:
        return v1 + (v2 - v1) * (0.6666666666666666 - vH) * 6
    return v1


def rgb_to_hex(rgb):
    _validate_rgb(rgb)
    r, g, b = [ float(value) for value in rgb ]
    return _rgb_to_hex((r, g, b))


def _rgb_to_hex(rgb):
    r, g, b = [ int(round(value * 255)) for value in rgb ]
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def hex_to_rgb(color):
    try:
        if not isinstance(color, (str, unicode)):
            raise ValueError()
        hex_value = color
        if color.startswith('#'):
            hex_value = color[1:]
        if len(hex_value) == 6:
            r, g, b = hex_value[0:2], hex_value[2:4], hex_value[4:6]
        elif len(hex_value) == 3:
            r, g, b = hex_value[0] * 2, hex_value[1] * 2, hex_value[2] * 2
        else:
            raise ValueError()
    except Exception:
        raise ValueError('Invalid hex color value provided: {!r}'.format(color))

    return tuple([ float(int(x, 16)) / 255 for x in (r, g, b) ])


def hex_to_hsl(color):
    return rgb_to_hsl(hex_to_rgb(color))


def hsl_to_hex(hsl):
    return _rgb_to_hex(hsl_to_rgb(hsl))
