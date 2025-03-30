#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\colorblind.py
import logging
from carbonui.util.color import Color
from signals import Signal
log = logging.getLogger(__name__)
on_colorblind_mode_changed = Signal('on_colorblind_mode_changed')
RED = 0.0
YELLOW = 1.0 / 6
GREEN = 2.0 / 6
AQUA = 3.0 / 6
BLUE = 4.0 / 6
PINK = 5.0 / 6
MODE_OFF = 0
MODE_DEUTERANOPIA = 1
MODE_TRITONOPIA = 2
MODE_CUSTOM = 3
H_0 = 1.0 / 24
HUES = (RED,
 YELLOW,
 GREEN,
 AQUA,
 BLUE,
 PINK)
HUES_BY_MODE = {MODE_DEUTERANOPIA: (YELLOW, BLUE),
 MODE_TRITONOPIA: (RED, AQUA)}

def GetCustomHues():
    return settings.user.ui.Get('colorBlindCustomHues', HUES[:])


def SetCustomHues(hues):
    hues = [ hue for hue in HUES if hue in hues ]
    return settings.user.ui.Set('colorBlindCustomHues', hues)


def ToggleCustomHue(hue):
    hues = list(GetCustomHues())
    if hue in hues:
        hues.remove(hue)
    else:
        hues.append(hue)
    if hues:
        SetCustomHues(hues)


def GetMode():
    try:
        return settings.user.ui.Get('colorBlindMode', MODE_OFF)
    except NameError:
        return MODE_OFF


def SetMode(mode):
    settings.user.ui.Set('colorBlindMode', mode)


def GetCurrentHues():
    mode = GetMode()
    if mode == MODE_CUSTOM:
        return GetCustomHues()
    return HUES_BY_MODE.get(mode, [])


def GetReplacementColorHex(colorHex, maintainBrightness = False, maxSaturation = None):
    col = Color.HextoRGBA(colorHex)
    col = GetReplacementColor(col, maintainBrightness, maxSaturation)
    return Color.RGBtoHex(*col)


def GetReplacementColor(color, maintainBrightness = False, maxSaturation = None):
    try:
        c = Color()
        c.SetRGB(*color)
        if not c.IsGrayscale() and c.GetBrightness() > 0.3:
            h0, s0, b0 = c.GetHSB()
            h, x = _GetHueAndRelativeXWithinHue(h0)
            b, s = _GetSaturationAndBrightness(x)
            if h == BLUE:
                s *= 0.7
            if maintainBrightness:
                b = b0
            if maxSaturation is not None:
                s = min(maxSaturation, s)
            c.SetHSB(h, s, b)
            if len(color) == 4:
                color = c.GetRGBA()
            else:
                color = c.GetRGB()
    except:
        log.exception()
    finally:
        return color


def _GetHueAndRelativeXWithinHue(hue):
    hues = GetCurrentHues()
    numSegments = len(hues)
    segmentLen = 1.0 / numSegments
    if hue <= H_0:
        hue += 1.0
    hue = round(hue, 3)
    for i in xrange(numSegments):
        hStart = round(H_0 + i * segmentLen, 3)
        hEnd = round(hStart + segmentLen, 3)
        if hStart <= hue and hue <= hEnd:
            xRel = (hue - hStart) / segmentLen
            xRel = max(0.0, min(xRel, 1.0))
            if i % 2:
                xRel = 1.0 - xRel
            try:
                hue = hues[i + 1]
            except IndexError:
                hue = hues[0]

            return (hue, xRel)

    raise ValueError


def GetSaturationConstraints():
    SAT_MIN = 0.3
    SAT_MAX = 1.0
    SAT_DIFF = SAT_MAX - SAT_MIN
    return (SAT_MIN, SAT_MAX, SAT_DIFF)


def GetBrightnessConstraints():
    BRI_MIN = 0.35 + len(GetCurrentHues()) * 0.075
    BRI_MAX = 1.0
    BRI_DIFF = BRI_MAX - BRI_MIN
    return (BRI_MIN, BRI_MAX, BRI_DIFF)


def _GetSaturationAndBrightness(x):
    if x > 1.0:
        raise ValueError('x is > 1.0')
    briMin, briMax, briDiff = GetBrightnessConstraints()
    satMin, satMax, satDiff = GetSaturationConstraints()
    if x <= 1.0 / 3:
        x = 3 * x
        s = satMin + satDiff * x
        b = briMax
    elif x <= 2.0 / 3:
        x = 3 * (x - 1.0 / 3)
        s = satMax
        b = briMax - briDiff * x
    else:
        x = 3 * (x - 2.0 / 3)
        s = satMax - satDiff * x
        b = briMin
    return (b, s)


def IsReplacementEnabled():
    return GetMode() != MODE_OFF and session.charid is not None


def CheckReplaceColor(color, maintainBrightness = False, maxSaturation = None):
    if IsReplacementEnabled():
        return GetReplacementColor(color, maintainBrightness, maxSaturation)
    return color


def CheckReplaceColorHex(colorHex, maintainBrightness = False, maxSaturation = None):
    if IsReplacementEnabled():
        colorHex = colorHex.replace('L', '')
        colorHex = GetReplacementColorHex(colorHex, maintainBrightness, maxSaturation)
    return colorHex


def GetEvenlyDistributedColor(color, i, numColors):
    x = H_0 + float(i) / numColors
    if x >= 1.0:
        x -= 1.0
    color = Color(*color)
    if not color.IsGrayscale():
        color.SetHSB(x, 1.0, 1.0)
    return color.GetRGBA()
