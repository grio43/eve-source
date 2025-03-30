#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dotWeapons\common\dotAppsOnTarget.py
import dogma.const as dogmaConst
import gametime
from carbon.common.script.util.mathCommon import FloatCloseEnough
from dotWeapons.common.dotConst import DOT_IDLE, DOT_ACTIVE
from dotWeapons.common.dotPriorityQueue import DotPriorityQueue
from utillib import KeyVal
FLOAT_TOLERANCE_DAMAGE_CHANGES = 0.001

class DotAppsOnTarget(object):

    def __init__(self, itemID, dogmaLM):
        self._itemID = itemID
        self.dogmaLM = dogmaLM
        self._dotApplications = DotPriorityQueue()
        self._damageHpFractionOnLastUpdate = None
        self._lastAppliedDamageApp = None

    def AddDotApplication(self, dotApplication):
        self._dotApplications.Add(dotApplication)

    def GetHighestDamageDotApplication(self, dogmaLM):
        if self._dotApplications.IsEmpty():
            return
        totalHp = self._GetTotalHp(dogmaLM)
        if totalHp is None:
            return
        currentMaxDmg = 0
        currentMaxDmgApp = None
        for dotApplication in self._dotApplications.IterateDotApplications():
            effectiveDamage = dotApplication.GetEffectiveDamage(totalHp)
            if self._ReplaceCurrentMax(currentMaxDmgApp, currentMaxDmg, dotApplication, effectiveDamage):
                currentMaxDmg = effectiveDamage
                currentMaxDmgApp = dotApplication

        damageHpFraction = float(currentMaxDmg) / totalHp
        hdi = HighestDamageInfo(currentMaxDmgApp, currentMaxDmg, damageHpFraction)
        return hdi

    def _ReplaceCurrentMax(self, maxDamageApplication, currentMaxDamage, dotApplication, damage):
        if maxDamageApplication is None:
            return True
        if damage > currentMaxDamage:
            return True
        if damage == currentMaxDamage:
            if dotApplication == self._lastAppliedDamageApp:
                return True
        return False

    def _GetTotalHp(self, dogmaLM):
        targetDogmaItem = dogmaLM.SafeGetDogmaItem(self._itemID)
        if not targetDogmaItem:
            return None
        shieldHp = dogmaLM.GetAttributeValue(self._itemID, dogmaConst.attributeShieldCapacity)
        armorHP = dogmaLM.GetAttributeValue(self._itemID, dogmaConst.attributeArmorHP)
        hullHp = dogmaLM.GetAttributeValue(self._itemID, dogmaConst.attributeHp)
        totalHp = shieldHp + armorHP + hullHp
        return totalHp

    def ExpireDotApplications(self):
        self._dotApplications.ExpireDotApplications(gametime.GetSimTime())

    def HasValidApplications(self):
        self.ExpireDotApplications()
        return not self._dotApplications.IsEmpty()

    def IsDifferentHpFraction(self, newDamageHpFracation):
        if not self._damageHpFractionOnLastUpdate:
            return True
        if FloatCloseEnough(self._damageHpFractionOnLastUpdate, newDamageHpFracation, FLOAT_TOLERANCE_DAMAGE_CHANGES):
            return False
        return True

    def UpdateLastUpdatedHpFraction(self, newDamageHpFracation):
        self._damageHpFractionOnLastUpdate = newDamageHpFracation

    def UpdateLastDamageApp(self, damgeApp):
        attackersToNotify = set()
        if self._lastAppliedDamageApp == damgeApp:
            return (False, attackersToNotify)
        if self._lastAppliedDamageApp:
            self._lastAppliedDamageApp.activityState = DOT_IDLE
            attackersToNotify.add(self._lastAppliedDamageApp.charID)
        if damgeApp:
            damgeApp.activityState = DOT_ACTIVE
            attackersToNotify.add(damgeApp.charID)
        self._lastAppliedDamageApp = damgeApp
        return (True, attackersToNotify)

    def GetSimpleVersion(self):
        b = KeyVal(targetID=self._itemID, dotApplications=[])
        for dotApplications in self._dotApplications.IterateDotApplications():
            b.dotApplications.append(dotApplications.GetValues())

        return b

    def GetDataForDotUpdates(self):
        return {x.GetBasicInfoForClientUpdate() for x in self._dotApplications.IterateDotApplications()}


class HighestDamageInfo(object):

    def __init__(self, dmgApplication, currentMax, damageHpFraction):
        self.dmgApplication = dmgApplication
        self.damage = currentMax
        self.damageHpFraction = damageHpFraction
