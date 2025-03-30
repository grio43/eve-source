#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\bracketNameFormatting.py
from carbonui.util.color import Color
from eve.client.script.ui.inflight.overview.overviewConst import BASIC_LABEL_TYPES, EXTRA_LABEL_TYPES, BASIC_VARIBLES, FORMATTING_VARIBLES

def TagWithBold(labelList, isBold):
    if not isBold:
        return labelList
    return ['<b>'] + labelList + ['</b>']


def TagWithUnderLine(labelList, isUnderlined):
    if not isUnderlined:
        return labelList
    return ['<u>'] + labelList + ['</u>']


def TagWithItalic(labelList, isItalic):
    if not isItalic:
        return labelList
    return ['<i>'] + labelList + ['</i>']


def TagWithColor(labelList, color):
    if color is None:
        return labelList
    hex = Color.RGBtoHex(*color)
    return ['<color=%s>' % hex] + labelList + ['</color>']


def TagWithSize(labelList, fontsize):
    if fontsize is None:
        return labelList
    return ['<font size=%s>' % fontsize] + labelList + ['</font>']


def GetAllowedLabelTypes():
    labelTypes = BASIC_LABEL_TYPES[:]
    labelTypes += EXTRA_LABEL_TYPES
    return labelTypes


def GetAllowedVariables():
    vars = BASIC_VARIBLES[:]
    vars += FORMATTING_VARIBLES
    return vars
