#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\radialMenu\broadcastRadialMenuFunctions.py
from carbonui.util.color import Color
from eve.client.script.parklife.states import flagSameFleet
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import SimpleRadialMenuAction
from evefleet import BROADCAST_ALIGN_TO, BROADCAST_HEAL_CAPACITOR, BROADCAST_HEAL_SHIELD, BROADCAST_HEAL_ARMOR, BROADCAST_WARP_TO

def GetBroadcastForShieldMenuAction(itemID):
    alwaysAvailable = IsAlwaysAvailable(itemID) and not IsTimeRestricted(BROADCAST_HEAL_SHIELD)
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/HealShield', func=BroadcastForShield, alwaysAvailable=alwaysAvailable)


def BroadcastForShield():
    sm.GetService('fleet').SendBroadcast_HealShield()


def GetBroadcastForArmorMenuAction(itemID):
    alwaysAvailable = IsAlwaysAvailable(itemID) and not IsTimeRestricted(BROADCAST_HEAL_ARMOR)
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/HealArmor', func=BroadcastForArmor, alwaysAvailable=alwaysAvailable)


def BroadcastForArmor():
    sm.GetService('fleet').SendBroadcast_HealArmor()


def GetBroadcastForCapacitorMenuAction(itemID):
    alwaysAvailable = IsAlwaysAvailable(itemID) and not IsTimeRestricted(BROADCAST_HEAL_CAPACITOR)
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/HealCapacitor', func=BroadcastForCapacitor, alwaysAvailable=alwaysAvailable)


def BroadcastForCapacitor():
    sm.GetService('fleet').SendBroadcast_HealCapacitor()


def GetBroadcastTargetMenuAction():
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/BroadcastTarget', forcedInactive=IsTimeRestricted('Target'))


def GetBroadcastAlignToMenuAction():
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/BroadcastAlignTo', forcedInactive=IsTimeRestricted(BROADCAST_ALIGN_TO))


def GetBroadcastWarpToMenuAction():
    return SimpleRadialMenuAction(option1='UI/Fleet/FleetBroadcast/Commands/BroadcastWarpTo', forcedInactive=IsTimeRestricted(BROADCAST_WARP_TO))


def IsTimeRestricted(name):
    return sm.GetService('fleet').IsTimeRestricted(name)


def IsAlwaysAvailable(itemID):
    if itemID == session.shipid:
        return True
    if itemID:
        return False
    return True


def GetBroadcastMenuColor():
    flagInfo = sm.GetService('stateSvc').GetStatePropsColorAndBlink(flagSameFleet)
    c = Color(*flagInfo.flagColor)
    bri = min(0.4, c.GetBrightness())
    return Color(*flagInfo.flagColor).SetBrightness(bri).GetRGBA()
