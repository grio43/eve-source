#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dynamicItem\info.py
import eveformat
from dogma.attributes.format import GetAttribute
from eve.client.script.ui.shared.dynamicItem.const import COLOR_NEGATIVE, COLOR_POSITIVE

def FormatAttributeBonusRange(attributeID, low, high):
    attribute = GetAttribute(attributeID)
    color_low = COLOR_NEGATIVE
    color_high = COLOR_POSITIVE
    if not attribute.highIsGood:
        low, high = high, low
        color_low, color_high = color_high, color_low
    return u'{} - {}'.format(eveformat.color(u'{:+.2%}'.format(low - 1.0), color=color_low if low - 1.0 < 0.0 else color_high), eveformat.color(u'{:+.2%}'.format(high - 1.0), color=color_low if high - 1.0 < 0.0 else color_high))
