#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\turrets.py
import trinity
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT
from evetypes import GetGraphicID
from fighters import ABILITY_SLOT_ID_KEY
import evegraphics.settings as gfxsettings
import uthread
import collections
import random
import blue
import geo2
from fsdBuiltData.common.graphicIDs import GetControllerVariableOverrides
from fsdBuiltData.client.effects import GetSourceDamageDelay, GetSourceDamageDuration, GetSourceDamageSize, GetTargetDamageSize, GetTargetDamageDuration, GetTargetDamageDelay

class StandardWeapon(GenericEffect):
    __guid__ = 'effects.StandardWeapon'

    def __init__(self, trigger, *args):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        self.turrets = []
        if trigger.graphicInfo is not None and ABILITY_SLOT_ID_KEY in trigger.graphicInfo:
            self.moduleID = trigger.graphicInfo[ABILITY_SLOT_ID_KEY]
        else:
            self.moduleID = trigger.moduleID
        self.otherTypeID = trigger.otherTypeID
        self.fxSequencer = sm.GetService('FxSequencer')
        self.controllerVariableOverrides = {}
        if self.otherTypeID is not None:
            ammo_gid = GetGraphicID(self.otherTypeID)
            self.controllerVariableOverrides = GetControllerVariableOverrides(ammo_gid) or {}

    def Prepare(self):
        pass

    def SetupTurrets(self):
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return False
        shipBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        if targetBall is None:
            return False
        if shipBall is None:
            return False
        shipID = self.GetEffectShipID()
        if not hasattr(shipBall, 'fitted'):
            self.fxSequencer.LogError('%s: %s Turrets: Error! can not fit turrets. No fitted attribute ' % (self.__guid__, shipID))
            return False
        shipBall.FitHardpoints(blocking=True)
        if not shipBall.fitted:
            return False
        if shipBall.modules is None:
            return False
        self.PopulateTurrets(shipBall)
        if len(self.turrets) < 1:
            self.fxSequencer.LogError('StandardWeapon: Turret not fitted on shipID will retry', shipID)
            return False
        return True

    def Shoot(self, shipBall, targetID):
        for turret in self.turrets:
            turret.StartControllers()
            for name, value in self.controllerVariableOverrides.iteritems():
                turret.SetControllerVariable(name, value)

            turret.SetTarget(targetID)
            turret.StartShooting()

    def Start(self, duration):
        if self.SetupTurrets():
            uthread.worker('FxSequencer::ShootTurrets', self.Shoot, self.GetEffectShipBall(), self.GetEffectTargetID())

    def PopulateTurrets(self, shipBall):
        if len(self.turrets) != 0 or shipBall is None:
            return
        shipBall.PrepareForFiring()
        self.turrets = shipBall.modules.get(self.moduleID)
        if not isinstance(self.turrets, collections.Iterable):
            if self.turrets is None:
                self.turrets = []
            else:
                self.turrets = [self.turrets]
        self.SetAmmoColor()
        self.SetDestSpaceObject()
        self.SetSourceSpaceObject()

    def SetAmmoColor(self):
        if self.otherTypeID is None:
            return
        for turret in self.turrets:
            turret.SetAmmoColorByTypeID(self.otherTypeID)

    def SetDestSpaceObject(self):
        targetBall = self.GetEffectTargetBall()
        if targetBall is None:
            return
        for turret in self.turrets:
            turret.SetDestSpaceObject(targetBall.model)

    def SetSourceSpaceObject(self):
        sourceBall = self.GetEffectShipBall()
        if sourceBall is None:
            return
        for turret in self.turrets:
            turret.SetSourceSpaceObject(sourceBall.model)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        for turret in self.turrets:
            turret.StopShooting()
            turret.shooting = 0

        for turret in self.turrets:
            turret.SetSourceSpaceObject(None)
            turret.SetDestSpaceObject(None)

        self.turrets = []

    def _RestTurrets(self):
        for turret in self.turrets:
            turret.Rest()
            turret.shooting = 0

    def Repeat(self, duration):
        if len(self.turrets) < 1:
            shipBall = self.GetEffectShipBall()
            if shipBall is None:
                return
            self.PopulateTurrets(shipBall)
        if len(self.turrets) < 1:
            return
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        if targetBall is None or shipBall is None:
            self._RestTurrets()
            return
        shipBall.PrepareForFiring()
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)


class CloudMining(StandardWeapon):
    __guid__ = 'effects.CloudMining'

    def SetAmmoColor(self):
        targetBall = self.GetEffectTargetBall()
        targetModel = getattr(targetBall, 'model', None)
        color = (1.0, 1.0, 1.0, 1.0)
        emitters = targetModel.Find('trinity.EveEmitterStatic')
        if len(emitters):
            if len(emitters[0].particleData):
                color = emitters[0].particleData[0].color
        for turret in self.turrets:
            if hasattr(turret, 'SetAmmoColor'):
                turret.SetAmmoColor(color)


class MissileLaunch(GenericEffect):
    __guid__ = 'effects.MissileLaunch'

    def __init__(self, trigger, *args):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        self.moduleID = trigger.moduleID
        self.otherTypeID = trigger.otherTypeID
        self.fxSequencer = sm.GetService('FxSequencer')

    def Prepare(self):
        pass

    def Shoot(self, targetID):
        if getattr(self, 'turret', None) is not None:
            self.turret.SetTarget(targetID)

    def Start(self, duration):
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        if targetBall is None:
            return
        if shipBall is None:
            return
        if not hasattr(shipBall, 'fitted'):
            return
        shipBall.FitHardpoints(blocking=True)
        if not shipBall.fitted:
            return
        if shipBall.modules is None:
            return
        self.turret = shipBall.modules.get(self.moduleID)
        if self.moduleID == shipID and 0 in shipBall.modules:
            self.turret = shipBall.modules.get(0)
            if not self.turret:
                self.fxSequencer.LogError('MissileLaunch: Turret not fitted on shipID', shipID, self.moduleID)
                return
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, targetID)

    def SetAmmoColor(self):
        pass

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if getattr(self, 'turret', None) is None:
            return
        self.turret.StopShooting()
        self.turret.shooting = 0
        self.turret = None

    def Repeat(self, duration):
        if getattr(self, 'turret', None) is None:
            return
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        targetID = self.ballIDs[1]
        targetBall = self.fxSequencer.GetBall(targetID)
        if targetBall is None:
            self.turret.Rest()
            self.turret.shooting = 0
            return
        if shipBall is None:
            self.turret.Rest()
            self.turret.shooting = 0
            return
        if shipBall == targetBall:
            return
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, targetID)


class ChainWeaponEffect(StandardWeapon):
    __guid__ = 'effects.ChainWeaponEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        super(ChainWeaponEffect, self).__init__(trigger, effect, graphicFile)
        self.duration = trigger.duration
        self.graphicFile = graphicFile
        self.effects = []
        self.damageThreads = []
        self.startTime = trigger.startTime
        self.sourceDamageSize = GetSourceDamageSize(trigger.guid)
        self.sourceDamageDuration = GetSourceDamageDuration(trigger.guid)
        self.sourceDamageDelay = GetSourceDamageDelay(trigger.guid)
        self.targetDamageSize = GetTargetDamageSize(trigger.guid)
        self.targetDamageDuration = GetTargetDamageDuration(trigger.guid)
        self.targetDamageDelay = GetTargetDamageDelay(trigger.guid)
        self.controllerVariableOverrides = {}
        if trigger.moduleTypeID is not None:
            ammo_gid = GetGraphicID(trigger.moduleTypeID)
            self.controllerVariableOverrides = GetControllerVariableOverrides(ammo_gid) or {}
        self.targets = []
        try:
            self.targets = trigger.graphicInfo['targets']
        except KeyError:
            self.fxSequencer.LogError("ChainWeaponEffect: No 'targets' in graphic info... no additional targets used")

    def _add_effect(self, source_curve, target_curve, jump_index = 0):
        if source_curve is None or target_curve is None:
            return
        gfx = trinity.Load(self.graphicFile)
        gfx.source = source_curve
        gfx.dest = target_curve
        gfx.SetControllerVariable('jumpNumber', jump_index)
        self.AddToScene(gfx)
        return gfx

    def _get_damage_locator_curve(self, source_id, target_id):
        target_ball = self.fxSequencer.GetBall(target_id)
        if target_ball is None:
            return
        target_model = target_ball.model
        if target_model is not None:
            dest = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.damageLocator)
            dest.parent = target_model
            dest.alignPositionCurve = self.fxSequencer.GetBall(source_id)
            return dest
        return target_ball

    def _add_turret_to_target_effect(self, turret, target_id):
        source = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.activeTurret)
        source.turretSetObject = turret.turretSets[0]
        source.muzzleIndex = 0
        return self._add_effect(source, self._get_damage_locator_curve(self.GetEffectShipID(), target_id))

    def _add_target_to_target_effect(self, source_id, target_id, jump_index):
        if source_id == target_id:
            self.fxSequencer.LogError('ChainWeaponEffect: Trying to create a stretch between the same object %s' % source_id)
            return None
        source_curve = self._get_damage_locator_curve(target_id, source_id)
        target_curve = self._get_damage_locator_curve(source_id, target_id)
        return self._add_effect(source_curve, target_curve, jump_index)

    def setup_firing_effects(self):
        self.effects = []
        for turret in self.turrets:
            e = self._add_turret_to_target_effect(turret, self.GetEffectTargetID())
            if e is not None:
                self.effects.append(e)

        last_target = self.GetEffectTargetID()
        for index, target in enumerate(self.targets):
            e = self._add_target_to_target_effect(last_target, target, index + 1)
            if e is not None:
                self.effects.append(e)
                last_target = target

    def remove_stretch_effect(self):
        for gfx in self.effects:
            self.RemoveFromScene(gfx)

        for t in self.damageThreads:
            if t is not None and t.alive:
                t.kill()

        self.damageThreads = []
        self.effects = []

    def Start(self, duration):
        if not self.SetupTurrets():
            return
        uthread.worker('FxSequencer::ShootTurrets', self.Shoot, self.GetEffectShipID(), self.GetEffectTargetID())

    def Repeat(self, duration):
        super(ChainWeaponEffect, self).Repeat(duration)
        self.remove_stretch_effect()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        super(ChainWeaponEffect, self).Stop(reason)
        self.remove_stretch_effect()

    def Shoot(self, ship_id, target_id):
        self.setup_firing_effects()
        for turret in self.turrets:
            turret.StartControllers()
            for name, value in self.controllerVariableOverrides.iteritems():
                turret.SetControllerVariable(name, value)

            turret.SetTarget(target_id)
            turret.StartShooting()

        delay = 0
        for effect in self.effects:
            for name, value in self.controllerVariableOverrides.iteritems():
                effect.SetControllerVariable(name, value)

            effect.StartFiring(delay)
            self.damageThreads.append(uthread.new(self._apply_damage, self.sourceDamageDelay + delay, self.sourceDamageSize, self.sourceDamageDuration, effect, False))
            self.damageThreads.append(uthread.new(self._apply_damage, self.targetDamageDelay + delay, self.targetDamageSize, self.targetDamageDuration, effect, True))
            delay += 0.3 * random.random()

    def _apply_damage(self, delay, size, duration, stretch_effect, applyOnTarget):
        blue.synchro.SleepSim(delay * 1000)
        source = stretch_effect.source
        target = stretch_effect.dest
        source_pos = source.GetVectorAt(blue.os.GetSimTime())
        source_pos = (source_pos.x, source_pos.y, source_pos.z)
        target_pos = target.GetVectorAt(blue.os.GetSimTime())
        target_pos = (target_pos.x, target_pos.y, target_pos.z)
        if not applyOnTarget:
            if not isinstance(source, trinity.EveLocalPositionCurve) or source.parent is None:
                return
            if not hasattr(source.parent, 'CreateImpact'):
                return
            direction = geo2.Vec3Direction(target_pos, source_pos)
            source.parent.CreateImpact(source.damageLocatorIndex, direction, duration, size)
        elif target is not None and getattr(target, 'parent', None) is not None:
            if not isinstance(target, trinity.EveLocalPositionCurve) or target.parent is None:
                return
            if not hasattr(target.parent, 'CreateImpact'):
                return
            direction = geo2.Vec3Direction(source_pos, target_pos)
            target.parent.CreateImpact(target.damageLocatorIndex, direction, duration, size)
