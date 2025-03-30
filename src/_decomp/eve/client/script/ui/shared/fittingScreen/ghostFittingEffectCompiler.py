#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\ghostFittingEffectCompiler.py
import telemetry
from eve.client.script.dogma.clientEffectCompiler import ClientEffectCompiler

class GhostFittingEffectCompiler(ClientEffectCompiler):
    __guid__ = 'svc.ghostFittingEffectCompiler'
    __dependencies__ = ['clientEffectCompiler']

    @telemetry.ZONE_METHOD
    def SetupDogmaEffects(self):
        for effectID, effect in self.clientEffectCompiler.GetEffects().iteritems():
            self.effects[effectID] = effect

    def GetPythonEffects(self):
        from eve.client.script.ui.shared.fittingScreen import pythonEffects
        from eve.common.script.dogma.pythonEffects.adaptiveHardener import BaseAdaptiveHardener
        from eve.common.script.dogma.pythonEffects.bastionMode import BaseBastionMode
        from eve.common.script.dogma.pythonEffects.emergencyHullEnergizer import EmergencyHullEnergizer
        from eve.common.script.dogma.pythonEffects.microJumpDrive import BaseMicroJumpDrive
        from eve.common.script.dogma.pythonEffects.microJumpPortalDrive import BaseMicroJumpPortalDrive
        from eve.common.script.dogma.pythonEffects.propulsionModules import Afterburner, Microwarpdrive
        from eve.common.script.dogma.pythonEffects.warpDisruptSphere import BaseWarpDisruptSphere
        effects = super(GhostFittingEffectCompiler, self).GetPythonEffects()
        effects.extend([Afterburner,
         BaseAdaptiveHardener,
         BaseBastionMode,
         BaseMicroJumpDrive,
         BaseMicroJumpPortalDrive,
         BaseWarpDisruptSphere,
         EmergencyHullEnergizer,
         Microwarpdrive,
         pythonEffects.Attack,
         pythonEffects.CommandBurstArmorEffect,
         pythonEffects.CommandBurstInfoEffect,
         pythonEffects.CommandBurstMiningEffect,
         pythonEffects.CommandBurstShieldEffect,
         pythonEffects.CommandBurstSkirmishEffect,
         pythonEffects.FakeCargoScan,
         pythonEffects.FakeCloaking,
         pythonEffects.FakeEmergencyHullEnergizer,
         pythonEffects.FakeEmpWave,
         pythonEffects.FakeEntosisLinkEffect,
         pythonEffects.FakeGuidanceDisruption,
         pythonEffects.FakeIndustrialInvulnerability,
         pythonEffects.FakePointDefense,
         pythonEffects.FakeRemoteTargetPaintFalloff,
         pythonEffects.FakeRemoteTrackingComputer,
         pythonEffects.FakeRemoteWebifierFalloff,
         pythonEffects.FakeSensorFalloffEffect,
         pythonEffects.FakeShipScan,
         pythonEffects.FakeSurveyScan,
         pythonEffects.FakeTargetABCAttack,
         pythonEffects.FakeTargetHostile,
         pythonEffects.FakeTitanBurstEffect,
         pythonEffects.FakeTrackingDisruption,
         pythonEffects.FakeWeaponDisruption,
         pythonEffects.Mine,
         pythonEffects.OnlineEffect,
         pythonEffects.Powerboost])
        return effects
