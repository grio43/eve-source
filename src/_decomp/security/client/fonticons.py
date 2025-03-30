#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\security\client\fonticons.py
import localization
from eveuniverse.security import securityClassHighSec, securityClassLowSec, securityClassZeroSec, SecurityClassFromLevel
FONT_ICON_HIGH_TO_NULL = u'<hint=\'{hint}\'><font color=red file="Iconography.ttf">a</font></hint>'
FONT_ICON_LOW_TO_NULL = u'<hint=\'{hint}\'><font color=red file="Iconography.ttf">b</font></hint>'
FONT_ICON_HIGH_TO_LOW = u'<hint=\'{hint}\'><font color=orange file="Iconography.ttf">b</font></hint>'
FONT_ICON_NULL_TO_LOW = u'<hint=\'{hint}\'><font color=orange file="Iconography.ttf">c</font></hint>'
FONT_ICON_LOW_TO_HIGH = u'<hint=\'{hint}\'><font color=aqua file="Iconography.ttf">c</font></hint>'
FONT_ICON_NULL_TO_HIGH = u'<hint=\'{hint}\'><font color=aqua file="Iconography.ttf">d</font></hint>'
FONT_ICON_UNCHANGED = u'<hint=\'{hint}\'><font color=grey file="Iconography.ttf">e</font></hint>'

def _get_font_icon_hint(base_security_level, modified_security_level):
    delta = round(modified_security_level, 1) - round(base_security_level, 1)
    modified_security_level = round(modified_security_level, 1)
    if delta > 0:
        return localization.GetByLabel('UI/Map/StarMap/SecurityStatusPositiveModifier', increase=delta, modifiedStatus=modified_security_level)
    if delta < 0:
        return localization.GetByLabel('UI/Map/StarMap/SecurityStatusNegativeModifier', decrease=abs(delta), modifiedStatus=modified_security_level)
    return ''


def _construct_font_icon_text_for_security_class_change(base_security_class, modified_security_class, hint):
    if base_security_class == modified_security_class:
        return ''
    if base_security_class == securityClassHighSec:
        if modified_security_class == securityClassLowSec:
            return FONT_ICON_HIGH_TO_LOW.format(hint=hint)
        if modified_security_class == securityClassZeroSec:
            return FONT_ICON_HIGH_TO_NULL.format(hint=hint)
    elif base_security_class == securityClassLowSec:
        if modified_security_class == securityClassHighSec:
            return FONT_ICON_LOW_TO_HIGH.format(hint=hint)
        if modified_security_class == securityClassZeroSec:
            return FONT_ICON_LOW_TO_NULL.format(hint=hint)
    elif base_security_class == securityClassZeroSec:
        if modified_security_class == securityClassHighSec:
            return FONT_ICON_NULL_TO_HIGH.format(hint=hint)
        if modified_security_class == securityClassLowSec:
            return FONT_ICON_NULL_TO_LOW.format(hint=hint)
    return ''


def get_font_icon_text(base_security_level, modified_security_level):
    base_security_class = SecurityClassFromLevel(base_security_level)
    modified_security_class = SecurityClassFromLevel(modified_security_level)
    hint = _get_font_icon_hint(base_security_level, modified_security_level)
    icon_text = _construct_font_icon_text_for_security_class_change(base_security_class, modified_security_class, hint)
    if hint and not icon_text:
        return FONT_ICON_UNCHANGED.format(hint=hint)
    return icon_text
