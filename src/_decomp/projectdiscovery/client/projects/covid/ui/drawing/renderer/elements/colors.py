#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\ui\drawing\renderer\elements\colors.py


class ColorTuple(tuple):

    def __new__(cls, r = 1.0, g = 1.0, b = 1.0, a = 1.0):
        return tuple.__new__(ColorTuple, (r,
         g,
         b,
         a))

    @property
    def r(self):
        return self[0]

    @property
    def g(self):
        return self[1]

    @property
    def b(self):
        return self[2]

    @property
    def a(self):
        return self[3]

    def lighten(self, ratio_of_white = 0.5):
        return self.blend(WHITE, ratio_of_white)

    def darken(self, ratio_of_black = 0.5):
        return self.blend(BLACK, ratio_of_black)

    def opaque(self, new_alpha = 1.0):
        return ColorTuple(r=self.r, g=self.g, b=self.b, a=new_alpha)

    def blend(self, other_color, ratio_of_other = 0.5):
        return ColorTuple(r=self.r * (1.0 - ratio_of_other) + other_color.r * ratio_of_other, g=self.g * (1.0 - ratio_of_other) + other_color.g * ratio_of_other, b=self.b * (1.0 - ratio_of_other) + other_color.b * ratio_of_other, a=self.a)

    def __str__(self):
        return '<ColorTuple %s>' % str(self.as_tuple)

    def __repr__(self):
        return '<ColorTuple %s>' % str(self.as_tuple)

    @property
    def as_tuple(self):
        return (self.r,
         self.g,
         self.b,
         self.a)

    @property
    def as_hex(self):
        return '#%s%s%s%s' % self.as_tuple

    @property
    def as_rgba(self):
        return (int(self.r * 255),
         int(self.g * 255),
         int(self.b * 255),
         self.a)

    @property
    def as_rgb(self):
        return (int(self.r * 255), int(self.g * 255), int(self.b * 255))

    @staticmethod
    def from_rgb(r = 255, g = 255, b = 255):
        return ColorTuple.from_rgba(r, g, b, 1.0)

    @staticmethod
    def from_rgba(r = 255, g = 255, b = 255, a = 1.0):
        return ColorTuple(r / 255.0, g / 255.0, b / 255.0, a)

    @staticmethod
    def from_hex(hex_string = '#ffffff'):
        a = 1.0
        r = 255
        g = 255
        b = 255
        if hex_string.startswith('#'):
            hex_string = hex_string[1:]
        if len(hex_string) == 8:
            a = int(hex_string[-2:], 16) / 255.0
        if len(hex_string) >= 6:
            r = int(hex_string[0:2], 16)
            g = int(hex_string[2:4], 16)
            b = int(hex_string[4:6], 16)
        return ColorTuple.from_rgba(r, g, b, a)


BLACK = ColorTuple(0.0, 0.0, 0.0, 1.0)
GRAY = ColorTuple(0.5, 0.5, 0.5, 1.0)
WHITE = ColorTuple(1.0, 1.0, 1.0, 1.0)
RED = ColorTuple(1.0, 0.0, 0.0, 1.0)
GREEN = ColorTuple(0.0, 1.0, 0.0, 1.0)
BLUE = ColorTuple(0.0, 0.0, 1.0, 1.0)
CYAN = ColorTuple(0.0, 1.0, 1.0, 1.0)
MAGENTA = ColorTuple(1.0, 0.0, 1.0, 1.0)
YELLOW = ColorTuple(1.0, 1.0, 0.0, 1.0)
AZURE = ColorTuple(0.0, 0.5, 1.0, 1.0)
PURPLE = ColorTuple(0.5, 0.0, 1.0, 1.0)
LIME = ColorTuple(0.5, 1.0, 0.0, 1.0)
TURQUOISE = ColorTuple(0.0, 1.0, 0.5, 1.0)
PINK = ColorTuple(1.0, 0.0, 0.5, 1.0)
ORANGE = ColorTuple(1.0, 0.5, 0.0, 1.0)
CLEAR = ColorTuple(0.0, 0.0, 0.0, 0.0)
PDC19_WHITE = ColorTuple.from_hex('#F5F5F5')
PDC19_BLUE = ColorTuple.from_hex('#33BCF2')
PDC19_RED = ColorTuple.from_hex('#f81622')
PDC19_SOLUTION_LINES = ColorTuple(0.81, 0.71, 0.23, 1.0)
PDC19_SOLUTION_FILL = ColorTuple(0.98, 0.98, 0.82, 0.4)
if __name__ == '__main__':
    c = ColorTuple.from_hex('#33BCF2')
    print c
    print c.blend(RED, 0.4)
    print c.blend(RED, 0.4).opaque(0.2)
    print isinstance(c, tuple)
    cr, cg, cb, ca = c
    print ('foo',
     cr,
     cg,
     cb,
     ca)
