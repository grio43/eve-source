#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\dogma\baseEffectCompiler.py
import cPickle
import dogma.data
import telemetry
from carbon.common.script.sys.service import Service
from dogma.effects import Effect
from dogma.effects.modifiereffect import ModifierEffect
from dogma.effects.util import CreateEffect
from eve.common.lib import appConst
from eveprefs import prefs
NEUTRAL_EFFECT = Effect()

class BaseEffectCompiler(Service):
    __guid__ = 'svc.baseEffectCompiler'
    __dependencies__ = ['dogmaStaticMgr']

    def __init__(self):
        self.effects = {}
        super(BaseEffectCompiler, self).__init__()

    @telemetry.ZONE_METHOD
    def SetupEffects(self):
        self.SetupDogmaEffects()
        self.SetupPythonEffects()

    @telemetry.ZONE_METHOD
    def SetupDogmaEffects(self):
        if not prefs.GetValue('enableNewStyleEffectAuthoring', True):
            return
        for effectInfo in dogma.data.get_all_effects():
            if effectInfo.modifierInfo:
                try:
                    self.effects[effectInfo.effectID] = CreateEffect(effectInfo)
                except Exception:
                    self.LogException('failed to load')
                    self.LogError('Failed to load effect', effectInfo.effectID, effectInfo.modifierInfo)
                    continue

            else:
                self.effects[effectInfo.effectID] = NEUTRAL_EFFECT

    @telemetry.ZONE_METHOD
    def SetupPythonEffects(self):
        pythonEffects = self.GetPythonEffects()
        for item in pythonEffects:
            if not hasattr(item, '__effectIDs__'):
                continue
            inst = item()
            for effectID in inst.__effectIDs__:
                if isinstance(effectID, str):
                    effectName = effectID
                    effectID = getattr(appConst, effectName, None)
                    if effectID is None:
                        self.LogError('Namespace item', item, 'has non-existant effect name reference', effectName)
                        continue
                self.effects[effectID] = inst

    def PickledSortedList(self, v):
        v.sort()
        return cPickle.dumps(v)

    def IsEffectPythonOverridden(self, effectID):
        try:
            return self.effects[effectID].isPythonEffect
        except KeyError:
            return False

    def IsEffectCreatedFromModifierInfo(self, effectID):
        try:
            return isinstance(self.effects[effectID], ModifierEffect)
        except KeyError:
            return False

    def StartEffect(self, effectID, env):
        return self.effects[effectID].Start(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)

    def PreStartEffectChecks(self, effectID, env):
        self.effects[effectID].PreStartChecks(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)

    def StartEffectChecks(self, effectID, env):
        self.effects[effectID].StartChecks(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)

    @telemetry.ZONE_METHOD
    def StopEffect(self, effectID, env, restricted = 0):
        if restricted:
            return self.effects[effectID].RestrictedStop(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)
        else:
            return self.effects[effectID].Stop(env, env.dogmaLM, env.itemID, env.shipID, env.charID, env.otherID, env.targetID)

    def IsEffectModifierOnly(self, effectID):
        return self.effects[effectID].__modifier_only__

    def IsEffectCharacterModifier(self, effectID):
        return self.effects[effectID].__modifies_character__

    def IsEffectShipModifier(self, effectID):
        return self.effects[effectID].__modifies_ship__

    def IsEffectDomainOther(self, effectID):
        return self.effects[effectID].__modifier_domain_other__

    def GetDogmaStaticMgr(self):
        return self.dogmaStaticMgr

    def GetEffect(self, effect_id):
        return self.effects[effect_id]

    def GetEffects(self):
        return self.effects

    def GetPythonEffects(self):
        from eve.common.script.dogma.fitting import LauncherFittedEffect, SubSystemFittedEffect, TurretFittedEffect, UpgradeFittedEffect
        from eve.common.script.dogma.hardPointModifierEffect import HardpointModifierEffect
        from eve.common.script.dogma.online import OnlineEffect
        from eve.common.script.dogma.pythonEffects.migratedeffects import ArmorRepairForEntities, ArmorRepairingEffect, CloakingTargetingDelayBonusPostPercentCloakingTargetingDelayBonusForShipModulesRequiringCloaking, DroneDmgBonus, MissileEMDmgBonus, MissileExplosiveDmgBonus, MissileKineticDmgBonus2, MissileThermalDmgBonus, SelfRof, ShieldBoostingEffect, TargetPassively
        from eve.common.script.dogma.slotModifier import SlotModifier
        return [ArmorRepairForEntities,
         ArmorRepairingEffect,
         CloakingTargetingDelayBonusPostPercentCloakingTargetingDelayBonusForShipModulesRequiringCloaking,
         DroneDmgBonus,
         HardpointModifierEffect,
         LauncherFittedEffect,
         MissileEMDmgBonus,
         MissileExplosiveDmgBonus,
         MissileKineticDmgBonus2,
         MissileThermalDmgBonus,
         OnlineEffect,
         SelfRof,
         ShieldBoostingEffect,
         SlotModifier,
         SubSystemFittedEffect,
         TargetPassively,
         TurretFittedEffect,
         UpgradeFittedEffect]
