#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcaster\shipcasterUtil.py
import eve.common.lib.appConst as appConst
import eveformat.client
import gametime
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from localization import GetByLabel
from menu import MenuLabel
from spacecomponents.common.componentConst import SHIPCASTER_LAUNCHER
from spacecomponents.common.helper import HasShipcasterComponent
from carbon.common.script.util.format import FmtDate
from eve.client.script.ui.eveColor import LED_GREY

def GetShipcasterText(slimItem):
    if not HasShipcasterComponent(slimItem.typeID):
        return ''
    linkedTargets = slimItem.component_shipcaster_linked_targets or []
    if not len(linkedTargets):
        return eveformat.tags.color('UI/Inflight/ShipcasterNotLinkedToTarget', LED_GREY)
    target0Info = linkedTargets[0]
    if target0Info[0] is None:
        return eveformat.tags.color(GetByLabel('UI/Inflight/ShipcasterNotLinkedToTarget'), LED_GREY)
    targetSystem, targetID, targetFactionID = target0Info[0]
    startTime = target0Info[1]
    endTime = target0Info[2]
    textList = [GetByLabel('UI/Inflight/ShipcasterLinkedToTargetSystem', solarsystem=targetSystem, securityStatus=eveformat.solar_system_security_status(targetSystem))]
    now = gametime.GetWallclockTime()
    if startTime > now:
        textList.append(GetByLabel('UI/Inflight/ShipcasterCharging', timeLeft=FmtDate(startTime - gametime.GetWallclockTime(), 'ns')))
    elif endTime > now:
        textList.append(GetByLabel('UI/Inflight/ShipcasterActive', timeLeft=FmtDate(endTime - gametime.GetWallclockTime(), 'ns')))
    return '<br>'.join(textList)


def GetTargetForShipcaster(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    shipcasterLauncherComponent = bp.componentRegistry.GetComponentForItem(itemID, SHIPCASTER_LAUNCHER)
    if shipcasterLauncherComponent:
        return (shipcasterLauncherComponent.targetSolarsystemID, shipcasterLauncherComponent.targetLandingPadID)
    return (None, None)


def GetNextTargetForShipcaster(itemID):
    bp = sm.StartService('michelle').GetBallpark()
    shipcasterLauncherComponent = bp.componentRegistry.GetComponentForItem(itemID, SHIPCASTER_LAUNCHER)
    if shipcasterLauncherComponent:
        return shipcasterLauncherComponent.nextTargetSolarsystemID


def GetFailureTextAndDisabledOption(itemID, celestial):
    if celestial.failure_label == 'UI/Menusvc/MenuHints/ShipcasterIsCharging':
        nextTargetID = GetNextTargetForShipcaster(itemID)
        if nextTargetID:
            failureText = GetByLabel('UI/Inflight/ShipcasterChargingLink', solarsystem=nextTargetID)
            med = MenuEntryData(MenuLabel('UI/Inflight/JumpByShipcasterToSystem', kw={'solarsystem': nextTargetID}), isEnabled=False, hint=failureText)
            return (failureText, med)
    text = sm.GetService('menu').GetUnavailableText(celestial)
    return (text, None)
