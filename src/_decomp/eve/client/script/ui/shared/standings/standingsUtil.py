#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingsUtil.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.standings import standingUIConst

def RoundStandingTo10(standing):
    if standing >= 9.995:
        effectiveStanding = 10.0
    else:
        effectiveStanding = standing
    return effectiveStanding


def GetStandingChangeFormatted(standingDiff):
    if standingDiff > 0.0:
        color = standingUIConst.COLOR_GOOD
        standingDiff = '+%s' % standingDiff
    elif standingDiff == 0.0:
        color = standingUIConst.COLOR_NEUTRAL
        standingDiff = '%s' % standingDiff
    else:
        color = standingUIConst.COLOR_BAD
        standingDiff = '%s' % standingDiff
    color = Color.RGBtoHex(*color)
    return '<color=%s>%s</color>' % (color, standingDiff)
