#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\client\dotClientUtil.py
from collections import defaultdict
import evetypes
import gametime
from dotWeapons.common.dotAppInfo import DotApplicationInfo
from dotWeapons.common.dotConst import DOT_ACTIVE, DOT_IDLE
from dotWeapons.common.dotUtil import GetEffectiveDamage
from eve.client.script.ui.inflight.shipHud.buffButtonsUtil import HintRow
from gametime import GetSimTime
from localization import GetByLabel
from localization.formatters import FormatTimeIntervalShortWritten

def GetFormattedDotInfoForCurrentShip(incomingDotTracker):
    all = incomingDotTracker.GetDmgInfoForShipID(session.shipid)
    active = [ x for x in all if x.activityState == DOT_ACTIVE ]
    allPruned = PruneAndOrderDamageInfo(all)
    idle = [ x for x in allPruned if x.activityState == DOT_IDLE ]
    hpTotalMax = _GetTotalHp()
    hintList = []
    for dmgList, header in ((active, GetByLabel('UI/Inflight/DotWeaponsCurrent')), (idle, GetByLabel('UI/Inflight/DotWeaponsPending'))):
        if not dmgList:
            continue
        hintList.append(HintRow(fullRowText=header))
        for d in dmgList:
            hr = _GetHintRowForDotVictim(d, hpTotalMax)
            hintList.append(hr)

    return hintList


def GetFormattedPendingDotsAsAttacker(incomingDotTracker):
    ballpark = sm.GetService('michelle').GetBallpark()
    hintList = []
    dmgInfoByAttacker = incomingDotTracker.GetOnGridDamageInfosForAttacker(session.charid)
    if not dmgInfoByAttacker:
        return hintList
    active = [ x for x in dmgInfoByAttacker if x.activityState == DOT_ACTIVE ]
    idle = PrunePendingAttackList([ x for x in dmgInfoByAttacker if x.activityState == DOT_IDLE ])
    for dmgList, header in ((active, GetByLabel('UI/Inflight/DotWeaponsCurrent')), (idle, GetByLabel('UI/Inflight/DotWeaponsPending'))):
        if dmgList:
            hintList.append(HintRow(fullRowText=header))
        for dmgInfo in dmgList:
            hr = _GetHintRowForDotAttacker(dmgInfo, ballpark)
            if hr:
                hintList.append(hr)

    return hintList


def _GetHintRowForDotVictim(dotInfo, hpTotalMax):
    displayName = cfg.eveowners.Get(dotInfo.attackerID).name
    if dotInfo.expiryTime is not None:
        timeRemaining = max(0L, dotInfo.expiryTime - GetSimTime())
        formattedTimeRemaining = FormatTimeIntervalShortWritten(timeRemaining)
    else:
        formattedTimeRemaining = ''
    effectiveDamage = int(GetEffectiveDamage(dotInfo.maxDamage, dotInfo.maxHPNormalizedRatio, hpTotalMax))
    damageText = GetByLabel('UI/Inflight/DotWeaponsDps', dps=effectiveDamage)
    hr = HintRow(col1=damageText, col2=displayName, col3=formattedTimeRemaining)
    return hr


def _GetHintRowForDotAttacker(dotInfo, ballpark):
    slimItem = ballpark.GetInvItem(dotInfo.targetID)
    if not slimItem:
        return
    if slimItem.charID:
        displayName = cfg.eveowners.Get(slimItem.charID).name
    else:
        displayName = slimItem.name
    if dotInfo.expiryTime is not None:
        timeRemaining = max(0L, dotInfo.expiryTime - GetSimTime())
        formattedTimeRemaining = FormatTimeIntervalShortWritten(timeRemaining)
    else:
        formattedTimeRemaining = ''
    maxDamage = int(dotInfo.maxDamage)
    damageText = GetByLabel('UI/Inflight/DotWeaponsDps', dps=maxDamage)
    hr = HintRow(col1=damageText, col2=displayName, col3=formattedTimeRemaining)
    return hr


def PruneAndOrderDamageInfo(dmgInfo):
    totalHp = _GetTotalHp()
    sortedDamageInfoList = sorted(dmgInfo, key=lambda x: (x.activityState, x.GetEffectiveDamage(totalHp), x.expiryTime))
    relevant = []
    while sortedDamageInfoList:
        currentDmgInfo = sortedDamageInfoList.pop(0)
        if sortedDamageInfoList:
            if not _IsDamageInfoRelevant(currentDmgInfo, sortedDamageInfoList, totalHp):
                continue
        relevant.append(currentDmgInfo)

    relevant.reverse()
    return relevant


def _IsDamageInfoRelevant(currentDmgInfo, sortedDamageInfo, totalHp):
    for dmgInfo in sortedDamageInfo:
        if dmgInfo.attackerID == currentDmgInfo.attackerID:
            if currentDmgInfo.IsMaskedBy(dmgInfo, totalHp):
                return False

    return True


def PrunePendingAttackList(pendingDmgInfoList):
    infoByTargetID = defaultdict(list)
    for x in pendingDmgInfoList:
        infoByTargetID[x.targetID].append(x)

    ret = []
    for dmgList in infoByTargetID.itervalues():
        dmgList.sort(key=lambda x: x.expiryTime, reverse=True)
        longestLasting = dmgList[0]
        ret.append(longestLasting)

    ret.sort(key=lambda x: x.expiryTime)
    return ret


def _GetTotalHp():
    from eve.client.script.ui.inflight.shipHud import ActiveShipController
    ship_controller = ActiveShipController()
    return ship_controller.GetTotalHpMax()


def GetTotalTimeHintRow(incomingDotWeaponTracker):
    timestamp = incomingDotWeaponTracker.GetLastExpiryTimestampForCurrentShip()
    if not timestamp:
        return []
    timeRemaining = timestamp - gametime.GetSimTime()
    if timeRemaining < 0:
        return []
    formattedTimeRemaining = FormatTimeIntervalShortWritten(timeRemaining)
    text = GetByLabel('UI/Inflight/DotWeaponsPendingTotalDuration', totalTime=formattedTimeRemaining)
    hr = HintRow(fullRowText=text)
    return [hr]
