#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\menu_charge.py
import operator
import evetypes
import uthread
import blue
from carbon.common.script.sys.service import Service
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
from carbonui.uicore import uicore
from eve.common.lib import appConst as const
from eve.common.script.sys import eveCfg

class ChargeService(Service):
    __module__ = __name__
    __doc__ = 'Insider Charge'
    __guid__ = 'svc.charge'
    __servicename__ = 'charge'
    __displayname__ = 'Insider Charges and Drone Service'
    __dependencies__ = ['invCache']

    def NA(self, name):
        return '<color=0x60ffffff>' + name + ' <color=0xffff8080>[N/A]'

    def Name(self, rec):
        if rec.published:
            return evetypes.GetName(rec.typeID, languageID='en-us')
        else:
            return self.NA(evetypes.GetName(rec.typeID, languageID='en-us'))

    def FormattedName(self, name, published):
        if published:
            return name
        else:
            return self.NA(name)

    def FitDrone(self, drone):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            result = uix.QtyPopup(maxvalue=100, minvalue=1, caption=self.Name(drone), label=u'Quantity', hint='')
            if result:
                qty = result['qty']
            else:
                return
        else:
            qty = 1
        sm.RemoteSvc('slash').SlashCmd('/fit me %d %d' % (drone.typeID, qty))

    def Fit(self, charges):
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        chargeByFlag = {}
        shipID = eveCfg.GetActiveShip()
        shipInv = self.invCache.GetInventoryFromId(shipID)
        for dogmaItem in dogmaLocation.GetDogmaItem(shipID).GetFittedItems().itervalues():
            if dogmaLocation.IsModuleSlave(dogmaItem.itemID, session.shipid):
                continue
            desiredSize = dogmaLocation.dogmaStaticMgr.GetTypeAttribute(dogmaItem.typeID, const.attributeChargeSize)
            capacity = dogmaLocation.GetAttributeValue(dogmaItem.itemID, const.attributeCapacity)
            for chargeGroupAttributeID in dogmaLocation.dogmaStaticMgr.chargeGroupAttributes:
                if not dogmaLocation.dogmaStaticMgr.TypeHasAttribute(dogmaItem.typeID, chargeGroupAttributeID):
                    continue
                chargeGroup = dogmaLocation.GetAttributeValue(dogmaItem.itemID, chargeGroupAttributeID)
                for a in charges:
                    if a.groupID != chargeGroup:
                        continue
                    if a.volume > capacity:
                        continue
                    if desiredSize is not None and getattr(a, 'chargeSize', -1) != desiredSize:
                        continue
                    slavedModules = dogmaLocation.GetSlaveModules(dogmaItem.itemID, session.shipid) or []
                    chargeByFlag[dogmaItem.flagID] = [a, int(capacity / a.volume) * (len(slavedModules) + 1)]
                    break
                else:
                    continue

                break

        tasks = {flagID:(None, '/fit me %d %d flag=%d' % (typeObj.typeID, qtyNeeded, flagID)) for flagID, (typeObj, qtyNeeded) in chargeByFlag.iteritems()}
        for dogmaItem in dogmaLocation.GetDogmaItem(shipID).GetFittedItems().itervalues():
            flagID = dogmaItem.flagID
            if flagID not in chargeByFlag:
                continue
            if dogmaItem.categoryID != const.categoryCharge:
                continue
            a, quantityNeeded = chargeByFlag[flagID]
            if isinstance(dogmaItem.itemID, tuple):
                if dogmaItem.typeID != a.typeID:
                    tasks[flagID] = [flagID]
                else:
                    quantityNeeded -= dogmaLocation.GetAttributeValue(dogmaItem.itemID, const.attributeQuantity)
                    tasks[flagID] = [None]
            else:
                tasks[flagID] = [flagID]
            if quantityNeeded > 0:
                tasks[flagID].append('/fit me %d %d flag=%d' % (a.typeID, quantityNeeded, flagID))
            else:
                tasks[flagID].append(None)

        def _change(removeFlag, addCmd):
            if removeFlag:
                shipInv.ClearCharges(removeFlag)
                count = 100
                while dogmaLocation.GetSubLocation(eveCfg.GetActiveShip(), removeFlag):
                    blue.pyos.synchro.SleepSim(50)
                    count -= 1
                    if not count:
                        raise RuntimeError('Dogma is sleeping on the job, or something worse happened!')

            if addCmd:
                sm.RemoteSvc('slash').SlashCmd(addCmd)

        uthread.parallel([ (_change, (flag, cmd)) for flag, cmd in tasks.itervalues() ])

    def Entry(self, a):
        return (self.Name(a), self.Fit, ([a],))

    def DroneMenu(self, *args, **kw):
        return self._Menu(drones=True)

    def ChargeMenu(self, *args, **kw):
        return self._Menu()

    def _Menu(self, drones = False):
        dgm = sm.GetService('godma').GetStateManager()
        chargesByChargeGroup = {}
        chargesByLauncherGroup = {}
        missileLauncherGroups = {}
        damageTypes = {'1000': ('EM', 'ui_22_32_12', 0.125),
         '0100': ('Explosive', 'ui_22_32_11', 0.125),
         '0010': ('Kinetic', 'ui_22_32_9', 0.125),
         '0001': ('Thermal', 'ui_22_32_10', 0.125),
         -1: ('Other', 'ui_7_64_15')}
        for groupID in evetypes.GetGroupIDsByCategories([const.categoryCharge, const.categoryDrone]):
            chargesByChargeGroup[groupID] = []

        for typeID in evetypes.GetTypeIDsByGroups(chargesByChargeGroup.keys()):
            chargesByChargeGroup[evetypes.GetGroupID(typeID)].append(typeID)

        for items in chargesByChargeGroup.itervalues():
            if items:
                typeID = items[0]
                a = dgm.GetType(typeID)
                if a.launcherGroup > 1:
                    chargesByLauncherGroup[a.launcherGroup] = items
                    if a.launcherGroup == const.groupMissileLauncherStandard:
                        chargesByLauncherGroup[const.groupMissileLauncherAssault] = items
                        missileLauncherGroups[const.groupMissileLauncherAssault] = True
                    if const.typeMissileLauncherOperation in (getattr(a, 'requiredSkill1', False), getattr(a, 'requiredSkill2', False)):
                        missileLauncherGroups[a.launcherGroup] = True

        def TurretSubMenu(baseName, charges):
            m = []
            ammo = {}
            damage = {}
            for a in charges:
                ammoType = ' '.join(self.Name(a).replace(baseName + ' ', '').split(' ')[:-1]).strip() or 'Standard'
                if ammoType in ammo:
                    ammo[ammoType].append(a)
                else:
                    ammo[ammoType] = [a]
                    damage[ammoType] = (a.emDamage + a.explosiveDamage + a.kineticDamage + a.thermalDamage) / (1 << a.chargeSize - 1)

            ammo = [ (damage[key], key, charges) for key, charges in ammo.iteritems() ]
            ammo.sort()
            m.append(('<color=0xff708090>Base', None))
            m.append(None)
            lastDamage = baseDamage = ammo[0][0]
            for damage, ammoType, charges in ammo:
                if damage != lastDamage:
                    m.append(None)
                    m.append(('<color=0xff708090>Base +%d%%' % int((damage / baseDamage - 1) * 100 + 0.5), None))
                    m.append(None)
                    lastDamage = damage
                m.append((ammoType, self.Fit, (charges,)))

            return m

        def TurretMenu(chargeGroups):
            m = []
            chargeGroups = [ (evetypes.GetGroupNameByGroup(x), x) for x in chargeGroups ]
            chargeGroups.sort()
            for name, groupID in chargeGroups:
                filtered = {}
                rangeMod = {}
                for typeID in chargesByChargeGroup[groupID]:
                    a = dgm.GetType(typeID)
                    if a.iconID in filtered:
                        filtered[a.iconID].append(a)
                    else:
                        filtered[a.iconID] = [a]
                        rangeMod[a.iconID] = getattr(a, 'weaponRangeMultiplier', 0.0)

                grouped = {}
                inconsistent = []
                while filtered:
                    iconID, items = filtered.popitem()
                    base = self.Name(items[0]).split(' ')
                    base.pop()
                    inconsistent = []
                    for a in items[:]:
                        words = self.Name(a).split(' ')
                        newbase = base[:]
                        for word in base:
                            if word not in words:
                                newbase.remove(word)

                        if newbase:
                            base = newbase
                        else:
                            inconsistent.append(a)
                            items.remove(a)

                    baseName = ' '.join(base)
                    if baseName in grouped:
                        g = grouped[baseName]
                    else:
                        g = grouped[baseName] = []
                    g.extend(items)

                processed = []
                while grouped:
                    baseName, items = grouped.popitem()
                    for a in inconsistent:
                        if baseName in self.Name(a):
                            items.append(a)

                    items.sort()
                    for a in items:
                        if a.chargeSize == 2:
                            break
                    else:
                        for a in items:
                            if a.chargeSize == 1:
                                break
                        else:
                            a = items[0]

                    if not a.published:
                        baseName = self.NA(baseName)
                    if len(items) <= 4:
                        processed.append((rangeMod[a.iconID], (baseName, self.Fit, (items,))))
                    else:
                        processed.append((rangeMod[a.iconID], (baseName, ('isDynamic', TurretSubMenu, (baseName, items)))))

                processed.sort()
                processed.reverse()
                if len(processed) < 5:
                    m.append(('<color=0xff708090>%s' % evetypes.GetGroupNameByGroup(groupID), None))
                    m.append(None)
                    m += zip(*processed)[1]
                else:
                    m.append(('<color=0xff708090>Long Range', None))
                    m.append(None)
                    m += zip(*processed)[1]
                    m.append(None)
                    m.append(('<color=0xff708090>High Damage', None))
                m.append(None)

            return m

        def MissileSubMenu(charges):
            m = []
            charges.sort()
            missiles = {}
            for damage, a in charges:
                if a.launcherGroup in missiles:
                    missiles[a.launcherGroup].append(a)
                else:
                    missiles[a.launcherGroup] = [a]

            for launcherGroup, items in missiles.iteritems():
                fitted = []
                label = '<color=0xff708090>%s' % evetypes.GetGroupNameByGroup(launcherGroup)
                if launcherGroup == const.groupMissileLauncherStandard:
                    for row in self.invCache.GetInventoryFromId(eveCfg.GetActiveShip()).ListHardwareModules():
                        if row.groupID in (const.groupMissileLauncherStandard, const.groupMissileLauncherAssault):
                            fitted.append(row.groupID)

                    if len(fitted) > 1:
                        label = '<color=0xff708090>%s / %s' % (evetypes.GetGroupNameByGroup(const.groupMissileLauncherStandard), evetypes.GetGroupNameByGroup(const.groupMissileLauncherAssault))
                    else:
                        label = '<color=0xff708090>%s' % evetypes.GetGroupNameByGroup(fitted[0])
                m.append((label, None))
                m.append(None)
                for a in items:
                    m.append(self.Entry(a))

                m.append(None)

            return m

        def MissileMenu(chargeGroups):
            missiles = {}
            for groupID in chargeGroups:
                for typeID in chargesByChargeGroup[groupID]:
                    a = dgm.GetType(typeID)
                    if a.launcherGroup == const.groupMissileLauncher:
                        damageSpec = '0000'
                    else:
                        damageSpec = (a.emDamage,
                         a.explosiveDamage,
                         a.kineticDamage,
                         a.thermalDamage)
                    label = damageTypes.get(''.join(map(lambda x: str(int(not not x)), damageSpec)), None)
                    if label in missiles:
                        missiles[label].append((reduce(operator.__add__, damageSpec), a))
                    else:
                        missiles[label] = [(reduce(operator.__add__, damageSpec), a)]

            missiles = missiles.items()
            missiles.sort()
            multi = False
            for label, items in missiles:
                if label and len(items) > 1:
                    multi = True

            m = []
            m.append(None)
            entry = None
            for label, items in missiles:
                if label is None:
                    if len(items) == 1:
                        entry = self.Entry(items[0][1])
                    else:
                        entry = (damageTypes[-1][0], ('isDynamic', MissileSubMenu, (items,)))
                elif multi:
                    m.append((label[0], ('isDynamic', MissileSubMenu, (items,))))
                else:
                    m.append(self.Entry(items[0][1]))

            if entry:
                m.insert(0, None)
                m.insert(0, entry)
            return m

        def GenericMenu(chargeGroups, maxVolumeByCG):
            processed = []
            processedLength = 0
            for groupID in chargeGroups:
                maxVolume = maxVolumeByCG[groupID]
                items = [ self.Entry(a) for a in map(dgm.GetType, chargesByChargeGroup[groupID]) if a.volume <= maxVolume ]
                processed.append((groupID, items))
                processedLength += len(items)

            m = []
            for groupID, items in processed:
                m.append(('<color=0xff708090>%s' % evetypes.GetGroupNameByGroup(groupID), None))
                m.append(None)
                m.extend(items)
                m.append(None)

            return m

        def GetDroneDmgType(a):
            damageSpec = (a.emDamage,
             a.explosiveDamage,
             a.kineticDamage,
             a.thermalDamage)
            return damageTypes.get(''.join(map(lambda x: str(int(not not x)), damageSpec)), None)

        def DroneSubMenu(groupID):
            m = []
            if len(chargesByChargeGroup[groupID]) > 16:
                grouped = {}
                for typeID in chargesByChargeGroup[groupID]:
                    a = dgm.GetType(typeID)
                    typ = GetDroneDmgType(a)
                    if typ in grouped:
                        grouped[typ].append(a)
                    else:
                        grouped[typ] = [a]

                for label, items in grouped.items():
                    d = {}
                    for a in items:
                        if a.marketGroupID in d:
                            d[a.marketGroupID].append(a)
                        else:
                            d[a.marketGroupID] = [a]

                    grouped[label] = mm = []
                    if not label:
                        label = damageTypes[-1]
                    for name, id in [('Light Scout Drones', 837),
                     ('Medium Scout Drones', 838),
                     ('Heavy Attack Drones', 839),
                     ('Sentry Drones', 911)]:
                        if id in d:
                            mm.append(None)
                            for a in d[id]:
                                mm.append((self.Name(a), self.FitDrone, (a,)))

                            del d[id]

                    if d:
                        mm.append(None)
                        for id, items in d.iteritems():
                            for a in items:
                                mm.append((self.Name(a), self.FitDrone, (a,)))

                if None in grouped:
                    weird = grouped[None]
                    del grouped[None]
                else:
                    weird = None
                for label, items in grouped.items():
                    m.append((label[0], items))

                m.sort()
                m.append(None)
                m.sort()
                if weird:
                    m.append(None)
                    m.append((damageTypes[-1][0], weird))
            else:
                for typeID in chargesByChargeGroup[groupID]:
                    a = dgm.GetType(typeID)
                    m.append((self.Name(a), self.FitDrone, (a,)))
                    m.sort()

            ew300 = []
            ew600 = []
            ew900 = []
            light = []
            medium = []
            heavy = []
            lists = [ew300,
             ew600,
             ew900,
             light,
             medium,
             heavy]
            for entry in m:
                try:
                    if entry[0][-3:] == '300':
                        ew300.append(entry)
                    elif entry[0][-3:] == '600':
                        ew600.append(entry)
                    elif entry[0][-3:] == '900':
                        if entry[0][-6:] != 'SW-900':
                            ew900.append(entry)
                    elif entry[0][:5] == 'Light':
                        light.append(entry)
                    elif entry[0][:6] == 'Medium':
                        medium.append(entry)
                    elif entry[0][:5] == 'Heavy':
                        heavy.append(entry)
                except:
                    None

            for val in lists:
                val.sort()

            if ew300:
                m = ew300
            if ew600:
                m.append(None)
                m += ew600
            if ew900:
                m.append(None)
                m += ew900
            if light:
                m = light
            if medium:
                m.append(None)
                m += medium
            if heavy:
                m.append(None)
                m += heavy
            return m

        def DroneMenu():
            m = []
            for groupID in chargesByChargeGroup:
                if evetypes.GetCategoryIDByGroup(groupID) == const.categoryDrone:
                    m.append((self.FormattedName(evetypes.GetGroupNameByGroup(groupID), evetypes.IsGroupPublishedByGroup(groupID)), ('isDynamic', DroneSubMenu, (groupID,))))

            m.sort()
            return m

        def GetMenu():
            m = []
            missileCG = {}
            turretCGbyLG = {const.groupEnergyWeapon: {},
             const.groupHybridWeapon: {},
             const.groupProjectileWeapon: {}}
            otherCGbyLG = {}
            maxVolumeByCG = {}
            iconIDs = {}
            for row in self.invCache.GetInventoryFromId(eveCfg.GetActiveShip()).ListHardwareModules():
                groupID = row.groupID
                if groupID in chargesByLauncherGroup:
                    a = dgm.GetType(row.typeID)
                    iconIDs[groupID] = a.iconID
                    chargeGroups = []
                    for x in range(4):
                        chargeGroup = getattr(a, 'chargeGroup%d' % (x + 1), False)
                        if chargeGroup:
                            chargeGroups.append(chargeGroup)

                    if groupID in missileLauncherGroups:
                        iconIDs[const.groupMissileLauncher] = a.iconID
                        for cg in chargeGroups:
                            missileCG[cg] = True

                    elif groupID in turretCGbyLG:
                        for cg in chargeGroups:
                            turretCGbyLG[groupID][cg] = True

                    else:
                        if groupID not in otherCGbyLG:
                            otherCGbyLG[groupID] = {}
                        for cg in chargeGroups:
                            otherCGbyLG[groupID][cg] = True
                            maxVolumeByCG[cg] = max(maxVolumeByCG.get(cg, 0), a.capacity)

            if missileCG:
                m.append((evetypes.GetGroupNameByGroup(const.groupMissileLauncher), ('isDynamic', MissileMenu, (missileCG,))))
            for groupID in (const.groupEnergyWeapon, const.groupHybridWeapon, const.groupProjectileWeapon):
                if turretCGbyLG[groupID]:
                    m.append((evetypes.GetGroupNameByGroup(groupID), ('isDynamic', TurretMenu, (turretCGbyLG[groupID],))))

            for groupID in otherCGbyLG:
                if otherCGbyLG[groupID]:
                    m.append((evetypes.GetGroupNameByGroup(groupID), ('isDynamic', GenericMenu, (otherCGbyLG[groupID], maxVolumeByCG))))

            if m:
                m.insert(0, None)
                m.insert(0, ('<color=0xff708090>Module groups accepting charges', None))
            else:
                m.insert(0, ('<color=0xff708090>No modules accepting charges', None))
            return m

        if drones:
            return DroneMenu()
        else:
            return GetMenu()

    exports = {'insider.ChargeMenu': ChargeMenu,
     'insider.DroneMenu': DroneMenu}
