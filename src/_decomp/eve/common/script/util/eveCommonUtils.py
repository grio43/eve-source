#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\eveCommonUtils.py
import re
import xml.parsers.expat
import blue
import evetypes
import localization
import utillib
from carbon.common.script.util.format import FmtDate
from eve.common.lib import appConst as const
from eve.common.script.util.eveFormat import FmtSystemSecStatus
from eveprefs import boot
from inventorycommon.util import IsShipFittingFlag

def CombatLog_CopyText(mail, *args):
    kwargs = {'system': mail.solarSystemID,
     'target': mail.victimShipTypeID,
     'damage': mail.victimDamageTaken}
    if boot.role == 'client':
        kwargs['security'] = sm.GetService('map').GetSecurityStatus(mail.solarSystemID)
    else:
        kwargs['security'] = cfg.mapSystemCache[mail.solarSystemID].pseudoSecurity
    if mail.moonID is not None:
        kwargs['moon'] = cfg.evelocations.Get(mail.moonID).name
    else:
        kwargs['moon'] = localization.GetByLabel('UI/Common/Unknown')
    if mail.victimAllianceID is not None:
        kwargs['alliance'] = cfg.eveowners.Get(mail.victimAllianceID).name
    else:
        kwargs['alliance'] = localization.GetByLabel('UI/Common/Unknown')
    if mail.victimFactionID is not None:
        kwargs['faction'] = cfg.eveowners.Get(mail.victimFactionID).name
    else:
        kwargs['faction'] = localization.GetByLabel('UI/Common/Unknown')
    if mail.victimCharacterID is not None:
        if mail.victimCorporationID is None:
            return
        kwargs['victim'] = mail.victimCharacterID
        kwargs['corporation'] = cfg.eveowners.Get(mail.victimCorporationID).name
        headerLabel = 'UI/Util/CommonUtils/KillMailHeaderWithShip'
    elif mail.victimCorporationID is not None:
        kwargs['corporation'] = cfg.eveowners.Get(mail.victimCorporationID).name
        headerLabel = 'UI/Util/CommonUtils/KillMailHeaderWithStructure'
    else:
        return
    header = localization.GetByLabel(headerLabel, **kwargs)
    attackers, items = GetAttackersAndItemsFromKillMail(mail)
    attackerList = []
    for row in attackers:
        attacker = row[1]
        data = {'damage': attacker.damageDone}
        attackerLabel = None
        if attacker.characterID is not None:
            data['attacker'] = cfg.eveowners.Get(attacker.characterID).name
            data['security'] = attacker.secStatusText
            data['corporation'] = cfg.eveowners.Get(attacker.corporationID).name
            if attacker.allianceID is not None:
                data['alliance'] = cfg.eveowners.Get(attacker.allianceID).name
            else:
                data['alliance'] = localization.GetByLabel('UI/Common/None')
            if attacker.factionID is not None:
                data['faction'] = cfg.eveowners.Get(attacker.factionID).name
            else:
                data['faction'] = localization.GetByLabel('UI/Common/None')
            if attacker.shipTypeID is not None:
                data['ship'] = evetypes.GetName(attacker.shipTypeID)
            else:
                data['ship'] = localization.GetByLabel('UI/Common/Unknown')
            if attacker.weaponTypeID is not None:
                data['weapon'] = evetypes.GetName(attacker.weaponTypeID)
            else:
                data['weapon'] = localization.GetByLabel('UI/Common/Unknown')
            if attacker.finalBlow:
                attackerLabel = 'UI/Util/CommonUtils/KillMailPlayerAttackerWithFinalBlow'
            else:
                attackerLabel = 'UI/Util/CommonUtils/KillMailPlayerAttacker'
        elif attacker.corporationID is not None:
            if attacker.shipTypeID is not None:
                data['attacker'] = evetypes.GetName(attacker.shipTypeID)
            else:
                data['attacker'] = localization.GetByLabel('UI/Common/Unknown')
            data['owner'] = cfg.eveowners.Get(attacker.corporationID).name
            if attacker.finalBlow:
                attackerLabel = 'UI/Util/CommonUtils/KillMailMPCAttackerWithFinalBlow'
            else:
                attackerLabel = 'UI/Util/CommonUtils/KillMailNPCAttacker'
        if attackerLabel is not None:
            attackerList.append(localization.GetByLabel(attackerLabel, **data))

    droppedItemList = []
    destroyedItemList = []
    textDropped = textDestroyed = ''
    for item in items:
        qty = None
        if item.qtyDropped > 0:
            qty = item.qtyDropped
            wasDropped = True
        else:
            qty = item.qtyDestroyed
            wasDropped = False
        if item.flag == const.flagCargo:
            itemLocation = localization.GetByLabel('UI/Util/CommonUtils/KillMailItemLocation', itemLocation=localization.GetByLabel('UI/Generic/Cargo'))
        elif item.flag == const.flagDroneBay:
            itemLocation = localization.GetByLabel('UI/Util/CommonUtils/KillMailItemLocation', itemLocation=localization.GetByLabel('UI/Common/DroneBay'))
        elif item.flag == const.flagImplant:
            itemLocation = localization.GetByLabel('UI/Util/CommonUtils/KillMailItemLocation', itemLocation=localization.GetByLabel('UI/Common/Implant'))
        elif IsShipFittingFlag(item.flag) or item.flag == const.flagStructureDeed:
            itemLocation = ''
        else:
            itemLocation = localization.GetByLabel('UI/Util/CommonUtils/KillMailItemLocation', itemLocation=localization.GetByLabel('UI/Common/Other'))
        itemText = GetItemText(item, qty, itemLocation)
        if wasDropped:
            droppedItemList.append(itemText)
        else:
            destroyedItemList.append(itemText)
        if len(item.contents) > 0:
            for subitem in item.contents:
                itemLocation = localization.GetByLabel('UI/Util/CommonUtils/KillMailItemLocation', itemLocation=localization.GetByLabel('UI/Util/CommonUtils/InContainer'))
                if subitem.qtyDropped > 0:
                    qty = subitem.qtyDropped
                else:
                    qty = subitem.qtyDestroyed
                itemText = '<t>' + GetItemText(subitem, qty, itemLocation)
                if wasDropped:
                    droppedItemList.append(itemText)
                else:
                    destroyedItemList.append(itemText)

    if len(droppedItemList) > 0:
        textDropped = localization.GetByLabel('UI/Util/CommonUtils/KillMailDroppedItems', droppedItems=''.join(droppedItemList))
    if len(destroyedItemList) > 0:
        textDestroyed = localization.GetByLabel('UI/Util/CommonUtils/KillMailDestroyedItems', destroyedItems=''.join(destroyedItemList))
    killmail = localization.GetByLabel('UI/Util/CommonUtils/KillMail', timestamp=FmtDate(mail.killTime, fmt='ll'), header=header, attackers=''.join(attackerList), droppedItems=textDropped, destroyedItems=textDestroyed)
    return killmail.replace('\n', '')


def CopyTextToClipboard(text):
    blue.pyos.SetClipboardData(text)


def GetAttackersAndItemsFromKillMail(mail):
    attackers = []
    items = []
    rx = re.compile('=(-?\\d+(?:\\.\\d+)?)')
    tempBlob = rx.sub('="\\1"', mail.killBlob)

    class LameStateMachine:

        def __init__(self):
            self.state = 0
            self.lastitem = None

    pstate = LameStateMachine()

    def _xmlTagStart(tag, attrs):
        state = pstate.state
        if state == 99:
            return
        if tag == 'doc':
            return
        if tag == 'attackers':
            if state != 0:
                pstate.state = 99
                return
            pstate.state = 1
        elif tag == 'a':
            if state != 1:
                pstate.state = 99
                return
            pstate.state = 2
            attacker = utillib.KeyVal()
            attacker.characterID = attrs.get('c', None)
            attacker.corporationID = attrs.get('r', None)
            attacker.allianceID = attrs.get('a', None)
            attacker.factionID = attrs.get('f', None)
            attacker.shipTypeID = attrs.get('s', None)
            attacker.weaponTypeID = attrs.get('w', None)
            attacker.damageDone = int(float(attrs.get('d', 0)))
            if attacker.damageDone < 0:
                attacker.damageDone = 0
            attacker.secStatusText = attrs.get('t', '0.0')
            attacker.finalBlow = False
            attackers.append((attacker.damageDone, attacker))
        elif tag == 'items':
            if state != 0 and state != 3:
                pstate.state = 99
                return
            pstate.state = 4
        elif tag == 'i':
            if state != 4 and state != 5:
                pstate.state = 99
                return
            item = utillib.KeyVal()
            item.typeID = attrs.get('t', None)
            item.flag = int(float(attrs.get('f', 0)))
            item.singleton = int(float(attrs.get('s', 0)))
            item.qtyDropped = int(float(attrs.get('d', 0)))
            item.qtyDestroyed = int(float(attrs.get('x', 0)))
            item.contents = []
            if state == 4:
                pstate.state = 5
                if item.qtyDropped > 0 and item.qtyDestroyed > 0:
                    item2 = utillib.KeyVal()
                    item2.typeID = item.typeID
                    item2.flag = item.flag
                    item2.singleton = item.singleton
                    item2.qtyDropped = item.qtyDropped
                    item2.qtyDestroyed = 0
                    item2.contents = []
                    item.qtyDropped = 0
                    items.append(item)
                    items.append(item2)
                else:
                    items.append(item)
                    pstate.lastitem = item
            else:
                pstate.state = 6
                litem = pstate.lastitem
                if litem is not None:
                    litem.contents.append(item)
                    pstate.lastitem = litem
                else:
                    pstate.state = 99
        else:
            pstate.state = 99

    def _xmlTagEnd(tag):
        state = pstate.state
        if state == 99:
            return
        if tag == 'doc':
            return
        if tag == 'attackers':
            if state != 1:
                pstate.state = 99
                return
            pstate.state = 3
        elif tag == 'a':
            if state != 2:
                pstate.state = 99
                return
            pstate.state = 1
        elif tag == 'items':
            if state != 4:
                pstate.state = 99
                return
            pstate.state = 7
        elif tag == 'i':
            if state != 5 and state != 6:
                pstate.state = 99
                return
            if state == 5:
                pstate.state = 4
            else:
                pstate.state = 5
        else:
            pstate.state = 99

    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = _xmlTagStart
    parser.EndElementHandler = _xmlTagEnd
    parser.buffer_text = True
    parser.returns_unicode = False
    parser.Parse('<doc>' + tempBlob + '</doc>', 1)
    pstate.state = 0
    pstate.lastitem = None
    finalBlow = utillib.KeyVal()
    finalBlow.characterID = mail.finalCharacterID
    finalBlow.corporationID = mail.finalCorporationID
    finalBlow.allianceID = mail.finalAllianceID
    finalBlow.factionID = mail.finalFactionID
    finalBlow.shipTypeID = mail.finalShipTypeID
    finalBlow.weaponTypeID = mail.finalWeaponTypeID
    finalBlow.damageDone = mail.finalDamageDone
    if mail.finalSecurityStatus is None:
        finalBlow.secStatusText = '0.0'
    else:
        finalBlow.secStatusText = FmtSystemSecStatus(mail.finalSecurityStatus)
    finalBlow.finalBlow = True
    attackers.append((finalBlow.damageDone, finalBlow))
    attackers.sort(reverse=True)
    return (attackers, items)


def GetItemText(item, qty, itemLocation):
    if item.singleton == const.singletonBlueprintCopy and evetypes.GetCategoryID(item.typeID) == const.categoryBlueprint:
        if qty > 1:
            return localization.GetByLabel('UI/Util/CommonUtils/KillMailLostStackBPC', item=item.typeID, quantity=qty, itemLocation=itemLocation)
        else:
            return localization.GetByLabel('UI/Util/CommonUtils/KillMailLostItemBPC', item=item.typeID, itemLocation=itemLocation)
    else:
        if qty > 1:
            return localization.GetByLabel('UI/Util/CommonUtils/KillMAilLostStack', item=item.typeID, quantity=qty, itemLocation=itemLocation)
        return localization.GetByLabel('UI/Util/CommonUtils/KillMailLostItem', item=item.typeID, itemLocation=itemLocation)


def Flatten(sequence):
    if isinstance(sequence, basestring) or not hasattr(sequence, '__iter__'):
        yield sequence
        return
    for thingie in sequence:
        for dude in Flatten(thingie):
            yield dude


def GetKillMailInfo(killmail):
    attackers, items = GetAttackersAndItemsFromKillMail(killmail)
    attackers = [ (damage, utillib.KeyVal(attacker)) for damage, attacker in attackers ]
    items = [ utillib.KeyVal(item) for item in items ]
    return (attackers, items)


def AUPerSecondToDestinyWarpSpeed(auPerSecond):
    return int(auPerSecond / const.warpSpeedToAUPerSecond)


def lerp(value, maximum, start_point, end_point):
    return start_point + (end_point - start_point) * value / maximum


def lerp_color(value, maximum, start_point, end_point):
    r = lerp(value, maximum, start_point[0], end_point[0])
    g = lerp(value, maximum, start_point[1], end_point[1])
    b = lerp(value, maximum, start_point[2], end_point[2])
    return (r,
     g,
     b,
     1)
