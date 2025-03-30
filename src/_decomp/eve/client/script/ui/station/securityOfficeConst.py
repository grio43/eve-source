#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\securityOfficeConst.py
from collections import namedtuple
from carbonui.util.color import Color
from crimewatch.const import securityLevelsPerTagType
from inventorycommon.const import typeSecurityTagCloneSoldierNegotiator, typeSecurityTagCloneSoldierRecruiter, typeSecurityTagCloneSoldierTrainer, typeSecurityTagCloneSoldierTransporter
BOX_WIDTH = 96
BAR_WIDTH = BOX_WIDTH * 5
BAR_PADDING = 8
WINDOW_WIDTH = BAR_WIDTH + 2 * BAR_PADDING + 32
WINDOW_HEIGHT = 332
SEC_METER_HEIGHT = 19
BAR_HEIGHT = 84
SLIDER_COLOR_CURRENT = (1, 1, 1, 0.6)
SLIDER_COLOR_WANTED = (1, 1, 1, 0.5)
SLIDER_COLOR_WANTED_ALT = (1, 1, 1, 0.4)
SLIDER_COLOR_AVAILABLE = (1, 1, 1, 0.3)
SLIDER_COLOR_AVAILABLE_ALT = (1, 1, 1, 0.2)
SLIDER_COLOR_NOTAVAILABLE = (1, 0.2, 0.2, 0.5)
SLIDER_COLOR_NOTAVAILABLE_ALT = (1, 0.2, 0.2, 0.4)
DRAGBAR_COLOR_NOTAVAILABLE = (0.8, 0.2, 0.2, 1)
BucketData = namedtuple('BucketData', 'typeID, minSec, maxSec')
SecurityBandData = namedtuple('SecurityBandData', 'minSec, maxSec, color, altColor, pveHintLable, pvpHintLabel')
TAG_BUCKETS = [BucketData(typeSecurityTagCloneSoldierTrainer, *securityLevelsPerTagType[typeSecurityTagCloneSoldierTrainer]),
 BucketData(typeSecurityTagCloneSoldierRecruiter, *securityLevelsPerTagType[typeSecurityTagCloneSoldierRecruiter]),
 BucketData(typeSecurityTagCloneSoldierTransporter, *securityLevelsPerTagType[typeSecurityTagCloneSoldierTransporter]),
 BucketData(typeSecurityTagCloneSoldierNegotiator, *securityLevelsPerTagType[typeSecurityTagCloneSoldierNegotiator]),
 BucketData(None, securityLevelsPerTagType[typeSecurityTagCloneSoldierNegotiator][1], 10.0)]
SEC_BAND_DATA = [SecurityBandData(-10, -5, Color(79, 0, 0), Color(63, 0, 0), 'UI/SecurityOffice/SecBandHintPve1', 'UI/SecurityOffice/SecBandHintPvp1'),
 SecurityBandData(-5, -4.5, Color(121, 0, 0), None, 'UI/SecurityOffice/SecBandHintPve1', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(-4.5, -4, Color(157, 11, 15), None, 'UI/SecurityOffice/SecBandHintPve2', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(-4, -3.5, Color(190, 30, 45), None, 'UI/SecurityOffice/SecBandHintPve3', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(-3.5, -3, Color(238, 64, 54), None, 'UI/SecurityOffice/SecBandHintPve4', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(-3, -2.5, Color(240, 90, 40), None, 'UI/SecurityOffice/SecBandHintPve5', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(-2.5, -2, Color(246, 146, 30), None, 'UI/SecurityOffice/SecBandHintPve6', 'UI/SecurityOffice/SecBandHintPvp2'),
 SecurityBandData(0, 10, Color(0, 165, 81), Color(0, 148, 73), 'UI/SecurityOffice/SecBandHintPve7', 'UI/SecurityOffice/SecBandHintPvp2')]
