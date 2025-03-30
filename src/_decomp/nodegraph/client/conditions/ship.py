#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\ship.py
import eve.common.script.sys.eveCfg as eveCfg
from eve.common.script.sys.idCheckers import IsCapsule
from logging import getLogger
from nodegraph.common.util import compare_values
from .parameters import ItemParameters
from .base import Condition
logger = getLogger(__name__)

class InShip(ItemParameters):
    atom_id = 132

    def validate(self, **kwargs):
        if not eveCfg.InShip():
            return False
        item = sm.GetService('godma').GetItem(session.shipid)
        if IsCapsule(item.groupID):
            return False
        return super(InShip, self).validate(item_id=session.shipid, type_id=item.typeID)


class InCapsule(Condition):
    atom_id = 169

    def validate(self, **kwargs):
        if not eveCfg.InShip():
            return False
        item = sm.GetService('godma').GetItem(session.shipid)
        return IsCapsule(item.groupID)


class ShipAttribute(Condition):
    atom_id = 170

    def __init__(self, attribute_key = None, attribute_value = None, operator = None, flipped = None, **kwargs):
        super(ShipAttribute, self).__init__(**kwargs)
        self.attribute_key = attribute_key
        self.attribute_value = attribute_value
        self.operator = self.get_atom_parameter_value('operator', operator)
        self.flipped = self.get_atom_parameter_value('flipped', flipped)

    def validate(self, **kwargs):
        if not eveCfg.InShip():
            return False
        item = sm.GetService('godma').GetItem(session.shipid)
        value = item.attributes.get(self.attribute_key, None)
        if value is None:
            item = sm.StartService('michelle').GetItem(session.shipid)
            value = getattr(item, self.attribute_key) or None
        return compare_values(value_a=value, value_b=self.attribute_value, operator=self.operator, flipped=self.flipped)

    @classmethod
    def get_subtitle(cls, attribute_key = '', attribute_value = '', operator = None, flipped = None, **kwargs):
        if attribute_key:
            return u'{} {} {} {}'.format(attribute_key, cls.get_atom_parameter_value('operator', operator), attribute_value, '(flipped)' if cls.get_atom_parameter_value('flipped', flipped) else '')
        return ''


class ShipHealth(Condition):
    atom_id = 172

    def __init__(self, health_type = None, attribute_value = None, operator = None, percentage = None, **kwargs):
        super(ShipHealth, self).__init__(**kwargs)
        self.health_type = self.get_atom_parameter_value('health_type', health_type)
        self.percentage = self.get_atom_parameter_value('percentage', percentage)
        self.attribute_value = self.get_atom_parameter_value('attribute_value', attribute_value)
        self.operator = self.get_atom_parameter_value('operator', operator)

    def validate(self, **kwargs):
        if not eveCfg.InShip():
            return False
        ship = sm.GetService('godma').GetItem(session.shipid)
        if self.health_type == 'armor':
            health, max_health = self._get_armor_values(ship)
        elif self.health_type == 'shield':
            health, max_health = self._get_shield_values(ship)
        elif self.health_type == 'structure':
            health, max_health = self._get_structure_values(ship)
        else:
            return False
        if self.percentage:
            value = max(0.0, min(1.0, round(health / max_health, 2))) * 100
        else:
            value = health
        return compare_values(value_a=value, value_b=self.attribute_value, operator=self.operator)

    def _get_armor_values(self, ship):
        return (max(0.0, ship.armorHP - ship.armorDamage), ship.armorHP)

    def _get_shield_values(self, ship):
        return (ship.shieldCharge, ship.shieldCapacity)

    def _get_structure_values(self, ship):
        return (max(0.0, ship.hp - ship.damage), ship.hp)

    @classmethod
    def get_subtitle(cls, health_type = None, percentage = None, attribute_value = None, operator = None, **kwargs):
        return u'{} {} {}{}'.format(cls.get_atom_parameter_value('health_type', health_type), cls.get_atom_parameter_value('operator', operator), cls.get_atom_parameter_value('attribute_value', attribute_value), '%' if cls.get_atom_parameter_value('percentage', percentage) else '')


class CapacitorCharges(Condition):
    atom_id = 501

    def __init__(self, attribute_value = None, operator = None, percentage = None, **kwargs):
        super(CapacitorCharges, self).__init__(**kwargs)
        self.percentage = self.get_atom_parameter_value('percentage', percentage)
        self.attribute_value = self.get_atom_parameter_value('attribute_value', attribute_value)
        self.operator = self.get_atom_parameter_value('operator', operator)

    def validate(self, **kwargs):
        if not eveCfg.InShip():
            return False
        charges, max_charges = self._get_capacitor_charges()
        if self.percentage:
            value = max(0.0, min(1.0, round(charges / max_charges, 2))) * 100
        else:
            value = charges
        return compare_values(value_a=value, value_b=self.attribute_value, operator=self.operator)

    def _get_capacitor_charges(self):
        try:
            from eve.client.script.ui.inflight.shipHud import ActiveShipController
            ship_controller = ActiveShipController()
            charges = ship_controller.GetCapacitorCapacity()
            max_charges = ship_controller.GetCapacitorCapacityMax()
            return (max(0.0, charges), max(0.0, max_charges))
        except Exception as exc:
            logger.exception('Failed to retrieve capacitor charges: %s', exc)
            return (0.0, 0.0)

    @classmethod
    def get_subtitle(cls, percentage = None, attribute_value = None, operator = None, **kwargs):
        return u'{} {}{}'.format(cls.get_atom_parameter_value('operator', operator), cls.get_atom_parameter_value('attribute_value', attribute_value), '%' if cls.get_atom_parameter_value('percentage', percentage) else '')
