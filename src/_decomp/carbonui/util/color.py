#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\color.py


class Color(object):
    __guid__ = 'util.Color'
    BLACK = (0.0, 0.0, 0.0, 1.0)
    GREEN = (0.0, 0.5, 0.0, 1.0)
    SILVER = (0.75, 0.75, 0.75, 1.0)
    LIME = (0.0, 1.0, 0.0, 1.0)
    GRAY = (0.5, 0.5, 0.5, 1.0)
    OLIVE = (0.5, 0.5, 0.0, 1.0)
    WHITE = (1.0, 1.0, 1.0, 1.0)
    YELLOW = (1.0, 1.0, 0.0, 1.0)
    MAROON = (0.5, 0.0, 0.0, 1.0)
    NAVY = (0.0, 0.0, 0.5, 1.0)
    RED = (1.0, 0.0, 0.0, 1.0)
    ORANGE = (1.0, 0.65, 0.0, 1.0)
    BLUE = (0.0, 0.0, 1.0, 1.0)
    PURPLE = (0.5, 0.0, 0.5, 1.0)
    TEAL = (0.0, 0.5, 0.5, 1.0)
    FUCHSIA = (1.0, 0.0, 1.0, 1.0)
    AQUA = (0.0, 1.0, 1.0, 1.0)
    GRAY1 = (0.1, 0.1, 0.1, 1.0)
    GRAY2 = (0.2, 0.2, 0.2, 1.0)
    GRAY3 = (0.3, 0.3, 0.3, 1.0)
    GRAY4 = (0.4, 0.4, 0.4, 1.0)
    GRAY5 = (0.5, 0.5, 0.5, 1.0)
    GRAY6 = (0.6, 0.6, 0.6, 1.0)
    GRAY7 = (0.7, 0.7, 0.7, 1.0)
    GRAY8 = (0.8, 0.8, 0.8, 1.0)
    GRAY9 = (0.9, 0.9, 0.9, 1.0)

    def __init__(self, *args):
        self.r = 0.0
        self.g = 0.0
        self.b = 0.0
        self.a = 1.0
        if len(args) == 0:
            return
        if len(args) == 1:
            args = args[0]
        if isinstance(args, (str, unicode)):
            if args.startswith('#') or args.startswith('0x'):
                self.SetRGB(*self.HextoRGBA(args))
            else:
                try:
                    standardColor = getattr(self, args.upper(), None)
                    self.SetRGB(*standardColor)
                except Exception:
                    raise ValueError('Color: Invalid startup parameters')

        elif len(args) in (3, 4):
            if type(args[0]) == int:
                self.SetiRGB(*args[:3])
            else:
                self.SetRGB(*args[:3])
            if len(args) == 4:
                self.SetAlpha(args[3])
        else:
            raise ValueError('Color: Invalid startup parameters')

    def GetRGB(self):
        return (self.r, self.g, self.b)

    def GetRGBRounded(self):
        return (round(self.r, 4), round(self.g, 4), round(self.b, 4))

    def GetRGBA(self):
        r, g, b = self.GetRGB()
        return (r,
         g,
         b,
         self.a)

    def SetRGB(self, r, g, b, alpha = None):
        self.r = r
        self.g = g
        self.b = b
        if alpha is not None:
            self.SetAlpha(alpha)
        return self

    def GetiRGB(self):
        return Color.RGBtoiRGB(self.r, self.g, self.b)

    def SetiRGB(self, iR, iG, iB, alpha = None):
        SanitizeiRGBValues(iR, iG, iB)
        self.r, self.g, self.b = Color.iRGBtoRGB(iR, iG, iB)
        if alpha is not None:
            self.SetAlpha(alpha)
        return self

    def GetHSB(self):
        return Color.RGBtoHSB(self.r, self.g, self.b)

    def GetHue(self):
        return self.GetHSB()[0]

    def GetSaturation(self):
        return self.GetHSB()[1]

    def GetBrightness(self):
        return self.GetHSB()[2]

    def IsGrayscale(self):
        return self.r == self.g == self.b

    def SetHSB(self, hue, saturation, brightness, alpha = None):
        SanitizeHSBValues(hue, saturation, brightness)
        self.r, self.g, self.b = Color.HSBtoRGB(hue, saturation, brightness)
        if alpha is not None:
            self.SetAlpha(alpha)
        return self

    def SetHue(self, hue):
        h, s, b = Color.RGBtoHSB(*self.GetRGB())
        self.SetHSB(hue, s, b)
        return self

    def SetSaturation(self, saturation):
        h, s, b = Color.RGBtoHSB(*self.GetRGB())
        self.SetHSB(h, saturation, b)
        return self

    def SetBrightness(self, brightness):
        h, s, b = Color.RGBtoHSB(*self.GetRGB())
        self.SetHSB(h, s, brightness)
        return self

    def GetHex(self):
        return Color.RGBtoHex(*self.GetRGBA())

    def SetAlpha(self, alpha):
        return self.SetOpacity(alpha)

    def SetOpacity(self, opacity):
        self.a = opacity
        return self

    def __repr__(self):
        return '<Color object: RGBA: (%s, %s, %s, %s)>' % (self.r,
         self.g,
         self.b,
         self.a)

    @staticmethod
    def RGBtoiRGB(r, g, b, a = None):
        return (int(round(255 * r)), int(round(255 * g)), int(round(255 * b)))

    @staticmethod
    def iRGBtoRGB(r, g, b, a = None):
        SanitizeiRGBValues(r, g, b)
        return (round(r / 255.0, 3), round(g / 255.0, 3), round(b / 255.0, 3))

    @staticmethod
    def RGBtoHSB(r, g, b, a = None):
        SanitizeRGBValues(r, g, b)
        return Color.iRGBtoHSB(255 * r, 255 * g, 255 * b)

    @staticmethod
    def iRGBtoHSB(r, g, b):
        r = float(r)
        g = float(g)
        b = float(b)
        minVal = min(r, g, b)
        maxVal = max(r, g, b)
        c = maxVal - minVal
        bri = maxVal / 255
        if c == 0:
            hue = 0.0
            sat = 0.0
        else:
            sat = c / maxVal
            if r == maxVal:
                hue = (g - b) / c % 6 / 6
            elif g == maxVal:
                hue = ((b - r) / c + 2) / 6
            elif b == maxVal:
                hue = ((r - g) / c + 4) / 6
            if hue < 0:
                hue += 1
            if hue > 1:
                hue -= 1
        return (hue, sat, bri)

    @staticmethod
    def HSBtoiRGB(h, s, b):
        SanitizeHSBValues(h, s, b)
        r, g, b = Color.HSBtoRGB(h, s, b)
        return Color.RGBtoiRGB(r, g, b)

    @staticmethod
    def HSBtoRGB(hue, sat, bri):
        SanitizeHSBValues(hue, sat, bri)
        if sat == 0:
            r = bri
            g = bri
            b = bri
        else:
            var_h = hue * 6
            if var_h == 6:
                var_h = 0
            var_i = int(var_h)
            var_1 = bri * (1 - sat)
            var_2 = bri * (1 - sat * (var_h - var_i))
            var_3 = bri * (1 - sat * (1 - (var_h - var_i)))
            if var_i == 0:
                var_r = bri
                var_g = var_3
                var_b = var_1
            elif var_i == 1:
                var_r = var_2
                var_g = bri
                var_b = var_1
            elif var_i == 2:
                var_r = var_1
                var_g = bri
                var_b = var_3
            elif var_i == 3:
                var_r = var_1
                var_g = var_2
                var_b = bri
            elif var_i == 4:
                var_r = var_3
                var_g = var_1
                var_b = bri
            else:
                var_r = bri
                var_g = var_1
                var_b = var_2
            r = var_r
            g = var_g
            b = var_b
        return (r, g, b)

    @staticmethod
    def RGBtoHex(r, g, b, a = 1.0):
        r, g, b = Color.RGBtoiRGB(r, g, b)
        return Color.iRGBtoHex(r, g, b, a)

    @staticmethod
    def iRGBtoHex(r, g, b, a = 1.0):
        SanitizeiRGBValues(r, g, b)
        SanitizeAlphaValue(a)
        return '0x%.2X%.2X%.2X%.2X' % (int(255 * a),
         r,
         g,
         b)

    @staticmethod
    def HSBtoHex(h, s, v, a = 1.0):
        r, g, b = Color.HSBtoiRGB(h, s, v)
        return Color.iRGBtoHex(r, g, b, a)

    @staticmethod
    def HextoiRGBA(hexARGB):
        hexARGB = hexARGB.replace('#', '0x')
        SanitizeHexValue(hexARGB)
        strLen = len(hexARGB)
        hexNum = int(hexARGB, 16)
        if strLen == 8:
            r = hexNum >> 16
            g = hexNum >> 8 & 255
            b = hexNum & 255
            return (r,
             g,
             b,
             1.0)
        else:
            a = float(hexNum >> 24) / 255
            r = int(hexNum >> 16 & 255)
            g = int(hexNum >> 8 & 255)
            b = int(hexNum & 255)
            return (r,
             g,
             b,
             a)

    @staticmethod
    def HextoRGBA(hexARGB):
        r, g, b, a = Color.HextoiRGBA(hexARGB)
        iR, iG, iB = Color.iRGBtoRGB(r, g, b)
        return (iR,
         iG,
         iB,
         a)

    @staticmethod
    def HextoHSBA(hexARGB):
        r, g, b, a = Color.HextoiRGBA(hexARGB)
        h, s, b = Color.iRGBtoHSB(r, g, b)
        return (h,
         s,
         b,
         a)

    @staticmethod
    def GetGrayRGBA(brightness, alpha = 1.0):
        SanitizeRGBValues(brightness)
        SanitizeAlphaValue(alpha)
        return (brightness,
         brightness,
         brightness,
         alpha)


def SanitizeRGBValues(*values):
    for val in values:
        if val < 0.0:
            raise ValueError('Invalid value (%s). RGB values must be floats in the range [0.0-1.0]' % val)


def SanitizeAlphaValue(alpha):
    if alpha < 0.0:
        raise ValueError('Invalid value (%s). Alpha value must be a float in the range [0.0-1.0]' % alpha)


def SanitizeiRGBValues(*values):
    for val in values:
        if val < 0 or val > 255 or type(val) != int:
            raise ValueError('Invalid value (%s). iRGB values must be integers in the range [0-255]' % val)


def SanitizeHSBValues(*values):
    for val in values:
        if val < 0.0:
            val = 0.0
        elif val > 1.0:
            val = 1.0


def SanitizeHexValue(value):
    if type(value) not in (str, unicode) or not (value.startswith('0x') or value.startswith('#')):
        raise ValueError("Invalid value (%s). HexARGB value must be a string on the form '0xFF00FF00' or '#FF00FF00'" % value)


def GetColor(baseColor, alpha, brightness = None, saturation = None):
    myColor = Color(*baseColor)
    myColor.SetAlpha(alpha)
    if brightness:
        myColor.SetBrightness(brightness)
    if saturation:
        myColor.SetSaturation(saturation)
    return myColor.GetRGBA()


def GetColorIntFromRGBA(r, g, b, a = None, *args):
    newR = int(round(r * 255))
    rValue = newR * 65536
    newG = int(round(g * 255))
    gValue = newG * 256
    bValue = int(round(b * 255))
    retColor = rValue + gValue + bValue
    retColor -= 16777216
    return retColor
