#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\ship.py
from eve.common.lib import appConst
from .base import Event

class DamageStateChanged(Event):
    atom_id = None
    __notifyevents__ = ['OnDamageStateChanged']
    _valid_attribute = None
    _require_lower_value = None

    def OnDamageStateChanged(self, item_id, attribute_id, new_value, old_value):
        if item_id != session.shipid:
            return
        if new_value == old_value:
            return
        if attribute_id != self._valid_attribute:
            return
        if self._require_lower_value:
            if new_value > old_value:
                return
        elif new_value < old_value:
            return
        self._invoke()

    def _invoke(self):
        pass


class ArmorHealthChanged(DamageStateChanged):
    _valid_attribute = appConst.attributeArmorDamage

    def _invoke(self):
        ship = sm.GetService('godma').GetItem(session.shipid)
        armor_health = max(0.0, ship.armorHP - ship.armorDamage)
        try:
            armor_health_percentage = max(0.0, min(1.0, round(armor_health / ship.armorHP, 2))) * 100
        except ZeroDivisionError:
            armor_health_percentage = 0.0

        self.invoke(armor_health=armor_health, armor_health_percentage=armor_health_percentage)


class ArmorDamaged(ArmorHealthChanged):
    atom_id = 161
    _require_lower_value = False


class ArmorHealed(ArmorHealthChanged):
    atom_id = 162
    _require_lower_value = True


class ShieldHealthChanged(DamageStateChanged):
    _valid_attribute = appConst.attributeShieldCharge

    def _invoke(self):
        ship = sm.GetService('godma').GetItem(session.shipid)
        shield_health = ship.shieldCharge
        try:
            shield_health_percentage = max(0.0, min(1.0, round(shield_health / ship.shieldCapacity, 2))) * 100
        except ZeroDivisionError:
            shield_health_percentage = 0.0

        self.invoke(shield_health=shield_health, shield_health_percentage=shield_health_percentage)


class ShieldDamaged(ShieldHealthChanged):
    atom_id = 163
    _require_lower_value = True


class ShieldHealed(ShieldHealthChanged):
    atom_id = 164
    _require_lower_value = False


class StructureHealthChanged(DamageStateChanged):
    _valid_attribute = appConst.attributeDamage

    def _invoke(self):
        ship = sm.GetService('godma').GetItem(session.shipid)
        structure_health = max(0.0, ship.hp - ship.damage)
        try:
            structure_health_percentage = max(0.0, min(1.0, round(structure_health / ship.hp, 2))) * 100
        except ZeroDivisionError:
            structure_health_percentage = 0.0

        self.invoke(structure_health=structure_health, structure_health_percentage=structure_health_percentage)


class StructureDamaged(StructureHealthChanged):
    atom_id = 165
    _require_lower_value = False


class StructureHealed(StructureHealthChanged):
    atom_id = 166
    _require_lower_value = True


class ShipDeath(Event):
    atom_id = 237
    __notifyevents__ = ['OnShipDeath']

    def OnShipDeath(self):
        self.invoke()


class PodDeath(Event):
    atom_id = 238
    __notifyevents__ = ['OnPodDeath']

    def OnPodDeath(self):
        self.invoke()


class CapacitorChanged(Event):
    atom_id = 500
    __notifyevents__ = ['OnCapacitorChange']

    def OnCapacitorChange(self, *args, **kwargs):
        self.invoke()
