#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\triglavianBeam.py
from eve.client.script.environment.effects.GenericEffect import STOP_REASON_DEFAULT
from eve.client.script.environment.effects.turrets import StandardWeapon

class TriglavianBeam(StandardWeapon):

    def __init__(self, trigger, *args):
        StandardWeapon.__init__(self, trigger, *args)
        self.graphicInfo = trigger.graphicInfo
        self._laserIntensity = None
        self._startIntensity = 0.3
        self.damageMultiplierBonusCurrent = 0
        self.damageMultiplierBonusPerCycle = self.graphicInfo['mulitplierBonusPerCycle']
        self.damageMultiplierBonusMax = self.graphicInfo['multiplierBonusMax']

    def Start(self, duration):
        super(TriglavianBeam, self).Start(duration)
        self.laserIntensity = self._startIntensity

    def Repeat(self, duration):
        self.damageMultiplierBonusCurrent += self.damageMultiplierBonusPerCycle
        if self.damageMultiplierBonusCurrent > self.damageMultiplierBonusMax:
            self.damageMultiplierBonusCurrent = self.damageMultiplierBonusMax
        self.laserIntensity = self._startIntensity + self.damageMultiplierBonusCurrent / self.damageMultiplierBonusMax
        StandardWeapon.Repeat(self, duration)

    @property
    def laserIntensity(self):
        return self._laserIntensity

    @laserIntensity.setter
    def laserIntensity(self, value):
        if value != self._laserIntensity:
            self._laserIntensity = value
            for turret in self.turrets:
                turret.SetIntensity(self._laserIntensity)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        super(TriglavianBeam, self).Stop(reason)
        self.laserIntensity = None
        self.damageMultiplierBonusCurrent = 0
