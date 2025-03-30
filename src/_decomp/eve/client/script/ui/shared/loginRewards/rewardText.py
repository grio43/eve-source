#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\loginRewards\rewardText.py
import gametime
from carbon.common.script.util.format import FmtDate

def GetCountdownText(nextRewardTime):
    if not nextRewardTime:
        return
    now = gametime.GetWallclockTime()
    if now < nextRewardTime:
        text = FmtDate(nextRewardTime - now, 'ss')
    else:
        text = ''
    return text
